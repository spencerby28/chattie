import asyncio
from aiohttp import web, TCPConnector
import json
import aiohttp
import os
from dotenv import load_dotenv
import ssl
import certifi
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.services.storage import Storage
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.input_file import InputFile
import secrets
import string
import logging
import sys
import random
from openai import OpenAI, AsyncOpenAI
from appwrite.query import Query

import aiofiles
import aiofiles.os
from asyncio import Lock
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO
from elevenlabs import ElevenLabs

from autonomous_conversation import populate_workspace_conversations

import multiprocessing
from functools import partial

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('chattie_agent.log')
    ]
)
logger = logging.getLogger('chattie_agent')

# Global workspace creation locks
workspace_locks = {}

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
logger.info("Environment loaded. Endpoint: %s, Project: %s", 
            os.getenv('PUBLIC_APPWRITE_ENDPOINT'), 
            os.getenv('APPWRITE_PROJECT_ID'))

# Initialize Appwrite Admin Client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))
logger.info("Appwrite admin client initialized")

# Initialize Database and Users services
databases = Databases(client)
users = Users(client)
storage = Storage(client)

# Database and Collection IDs
DATABASE_ID = 'main'
AI_PERSONAS_COLLECTION = 'ai_personas'
CHANNELS_COLLECTION = 'channels'
MESSAGES_COLLECTION = 'messages'


# LangWatch


# Enhanced persona generation to include more chat-relevant details and conflicting viewpoints
PERSONA_GENERATION_PROMPT = """Create {num_personas} unique and engaging AI personas for a workspace focused on: {description}

Each persona should be HIGHLY OPINIONATED with strong personality quirks and communication styles. They should have deep knowledge in their areas but also clear biases and blind spots. Make them:

1. Distinctly memorable with quirky traits (e.g., always uses puns, overly formal, extremely sarcastic)
2. Emotionally invested in their viewpoints
3. Have strong triggers that make them passionate/defensive
4. Use unique speaking patterns or catchphrases
5. Hold controversial opinions they defend vigorously
6. Have specific pet peeves about how others approach the topic
7. Maintain consistent personality quirks in their responses
8. Range in formality from very casual to extremely professional
9. Have varying levels of patience with opposing viewpoints
10. Use different debate tactics (logic, emotion, experience, research)

Format as JSON array with objects containing:
- name: string (memorable username)
- personality: string (detailed quirks and traits)
- conversation_style: string (unique speaking pattern)
- knowledge_base: string[] (expertise areas)
- role: string (their life role/job)
- greeting: string (characteristic first message)
- opinions: string[] (strongly held beliefs)
- disagreements: string[] (points they argue against)
- debate_style: string (how they argue)
- triggers: string[] (topics that provoke strong reactions)
- catchphrases: string[] (unique expressions they use)
- communication_quirks: string[] (speaking patterns/habits)
- temperature: float (0.5-1.0, higher = more creative/random responses)

Make the personas GENUINELY ENTERTAINING and distinct!"""

# Channel generation based on workspace theme
CHANNEL_GENERATION_PROMPT = """Create channels for a workspace focused on: {description}

Design channels that will spark ENGAGING and HEATED discussions about {description}. Each channel should:

1. Focus on a specific controversial aspect of the topic
2. Have clear debate points that personas can argue about
3. Encourage different approaches and methodologies
4. Include topics that trigger strong emotional responses
5. Mix practical and theoretical discussions
6. Balance serious debates with lighter discussions
7. Create opportunities for personas to show their expertise
8. Include spaces for both formal and casual conversations

Format as JSON array with:
- name: string (clear, hyphenated, lowercase)
- description: string (what makes this channel unique and controversial)
- purpose: string (specific goals and type of discussions expected)
- primary_personas: string[] (2-3 personas whose conflicting viewpoints would create interesting discussions)
- topics: string[] (main discussion points that will spark debate)
- debate_topics: string[] (specific controversial points that will trigger passionate responses)
- conversation_tone: string (formal/casual/mixed)
- expected_conflict_points: string[] (where personas are likely to disagree)

Make each channel a unique space for engaging debates!"""

def generate_secure_password(length=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def create_ai_user(persona_name: str, workspace_id: str):
    """Create an AI user account for a specific persona"""
    logger.info("Creating AI user for persona: %s in workspace: %s", persona_name, workspace_id)
    try:
        # Generate a secure random password
        password = generate_secure_password()
        logger.debug("Generated secure password for AI user")
        
        # Create a sanitized username from persona name
        username = persona_name.lower().replace(' ', '_')
        email = f"{username}.{workspace_id}@chattie.local"
        
        logger.info("Attempting to create AI user with email: %s", email)
        # Create the user in Appwrite using admin client
        ai_user = users.create(
            user_id=ID.unique(),
            email=email,
            password=password,
            name=persona_name
        )
        
        logger.info("Successfully created AI user: %s with name: %s", ai_user['$id'], persona_name)
        return ai_user['$id']
        
    except Exception as e:
        logger.warning("Error creating AI user: %s", str(e))
        # Check if user already exists
        try:
            logger.info("Checking if AI user already exists with username: %s", username)
            existing_user = users.get(f"ai-{workspace_id}-{username}")
            logger.info("Found existing AI user: %s with name: %s", existing_user['$id'], existing_user['name'])
            return existing_user['$id']
        except Exception as inner_e:
            logger.error("Failed to get existing user: %s. Inner error: %s", username, str(inner_e))
            raise e


async def generate_with_openai(prompt: str, api_key: str) -> str:
    logger.info("Initiating OpenAI API request")
    client = AsyncOpenAI(api_key=api_key)

    try:
        logger.debug("Sending prompt to OpenAI API (first 100 chars): %s", prompt[:100])
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        logger.debug("Received response from OpenAI (length: %d characters)", len(content))
        
        # Strip markdown formatting
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
        content = content.strip()
        
        logger.info("Successfully processed OpenAI response")
        logger.debug("Cleaned content length: %d characters", len(content))
        return content
        
    except Exception as e:
        logger.error("Error in generate_with_openai: %s", str(e))
        logger.error("Error type: %s", type(e))
        if hasattr(e, '__traceback__'):
            import traceback
            logger.error("Traceback: %s", ''.join(traceback.format_tb(e.__traceback__)))
        raise

async def create_initial_message(channel_id: str, workspace_id: str, ai_user_id: str, persona_name: str, greeting: str):
    """Create an initial message from an AI persona in a channel"""
    logger.info("Creating initial message for channel: %s", channel_id)
    logger.debug("Message details - Workspace: %s, AI User: %s, Persona: %s", 
                workspace_id, ai_user_id, persona_name)
    
    try:
        message_data = {
            'channel_id': channel_id,
            'workspace_id': workspace_id,
            'sender_type': 'ai',
            'sender_id': ai_user_id,
            'content': greeting,
            'sender_name': persona_name,
            'edited_at': None,
            'mentions': [],
            'ai_context': None,
            'ai_prompt': None,
            'attachments': []
        }
        
        logger.info("Creating message document in Appwrite for channel: %s", channel_id)
        logger.debug("Message content (first 100 chars): %s", greeting[:100])
        
        result = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            document_id=ID.unique(),
            data=message_data,
            permissions=[
                Permission.read(Role.label(channel_id)),
                Permission.write(Role.user(ai_user_id))
            ]
        )
        
        logger.info("Successfully created message document ID: %s in channel: %s", 
                   result['$id'], channel_id)
        return result['$id']
        
    except Exception as e:
        logger.error("Failed to create initial message - Channel: %s, Persona: %s", 
                    channel_id, persona_name)
        logger.error("Error details: %s", str(e))
        logger.exception(e)
        raise

async def create_workspace(description: str, workspace_id: str, api_key: str):
    """Create a new workspace. Each workspace_id is guaranteed to be unique."""
    try:
        # Create test_data directory if it doesn't exist
        await aiofiles.os.makedirs('test_data', exist_ok=True)
        
        # Initialize test data structure
        test_data = {
            "workspace_id": workspace_id,
            "users": [],
            "channels": [],
            "initial_messages": {},
            "conversation_responses": {},
            "mappings": {
                "persona_ids": {},
                "channel_ids": {},
                "ai_user_ids": {},
            }
        }
        
        # Generate personas
        logger.info("Generating personas with OpenAI for workspace: %s", workspace_id)
        personas_prompt = PERSONA_GENERATION_PROMPT.format(
            num_personas=5,
            description=description
        )
        
        personas_json = await generate_with_openai(personas_prompt, api_key)
        personas = json.loads(personas_json)
        logger.info("Successfully generated %d personas", len(personas))
        
        # Store each persona and create AI users
        stored_personas = []
        ai_user_ids = []
        
        for persona in personas:
            try:
                # Create an AI user for this persona
                ai_user_id = await create_ai_user(persona['name'], workspace_id)
                ai_user_ids.append(ai_user_id)
                
                # Store persona data
                persona_data = {
                    'workspace_id': workspace_id,
                    'name': persona['name'],
                    'personality': persona['personality'],
                    'conversation_style': persona['conversation_style'],
                    'knowledge_base': persona['knowledge_base'],
                    'greeting': persona['greeting'],
                    'role': persona['role'],
                    'opinions': persona.get('opinions', []),
                    'disagreements': persona.get('disagreements', []),
                    'debate_style': persona.get('debate_style', ''),
                    'triggers': persona.get('triggers', []),
                    'catchphrases': persona.get('catchphrases', []),
                    'communication_quirks': persona.get('communication_quirks', []),
                    'temperature': persona.get('temperature', 0.7),
                    'ai_user_id': ai_user_id,
                }
                
                stored_persona = databases.create_document(
                    database_id=DATABASE_ID,
                    collection_id=AI_PERSONAS_COLLECTION,
                    document_id=ai_user_id,
                    data=persona_data,
                    permissions=[
                        Permission.read(Role.users()),
                        Permission.write(Role.user(ai_user_id)),
                        Permission.update(Role.user(ai_user_id)),
                        Permission.delete(Role.user(workspace_id)),
                        Permission.read(Role.label(ai_user_id))
                    ]
                )
                
                test_data["mappings"]["ai_user_ids"][persona['name']] = ai_user_id
                test_data["users"].append({
                    "name": persona['name'],
                    "ai_user_id": ai_user_id,
                    **persona
                })
                stored_personas.append(stored_persona)
                
            except Exception as e:
                logger.error(f"Error creating persona {persona['name']}: {str(e)}")
                continue
        
        # Generate and store channels
        channels_prompt = CHANNEL_GENERATION_PROMPT.format(description=description)
        channels_json = await generate_with_openai(channels_prompt, api_key)
        channels = json.loads(channels_json)
        
        stored_channels = []
        for channel in channels:
            try:
                channel_data = {
                    'workspace_id': workspace_id,
                    'name': channel['name'].lower().replace(' ', '-'),
                    'type': 'public',
                    'members': ai_user_ids,
                    'description': channel['description'],
                    'purpose': channel.get('purpose', ''),
                    'topics': channel.get('topics', []),
                    'debate_topics': channel.get('debate_topics', []),
                    'last_message_at': None,
                    'primary_personas': [persona['name'] for persona in personas]
                }
                
                stored_channel = databases.create_document(
                    database_id=DATABASE_ID,
                    collection_id=CHANNELS_COLLECTION,
                    document_id=ID.unique(),
                    data=channel_data,
                    permissions=[
                        Permission.read(Role.users()),
                        Permission.write(Role.users()),
                        *[Permission.write(Role.user(user_id)) for user_id in ai_user_ids],
                        Permission.update(Role.user(workspace_id)),
                        Permission.delete(Role.user(workspace_id))
                    ]
                )
                
                test_data["channels"].append(stored_channel)
                stored_channels.append(stored_channel)
                
            except Exception as e:
                logger.error(f"Error creating channel {channel['name']}: {str(e)}")
                continue
        
        # Save test data to file
        async with aiofiles.open('test_data/responses.json', 'w') as f:
            await f.write(json.dumps(test_data, indent=4))
        
        # Add AI users to workspace members
        try:
            workspace_data = {
                'members': ai_user_ids + ['bot']
            }
            databases.update_document(
                database_id=DATABASE_ID,
                collection_id='workspaces',
                document_id=workspace_id,
                data=workspace_data
            )
            logger.info(f"Added {len(ai_user_ids)} AI users to workspace {workspace_id}")
        except Exception as e:
            logger.error(f"Failed to add AI users to workspace members: {str(e)}")
        
        # Prepare storage config for multiprocessing
        storage_config = {
            'endpoint': os.getenv('PUBLIC_APPWRITE_ENDPOINT'),
            'project': os.getenv('APPWRITE_PROJECT_ID'),
            'api_key': os.getenv('APPWRITE_API_KEY')
        }

        # Create process pool for avatar generation
        num_cores = min(5, multiprocessing.cpu_count())
        avatar_pool = multiprocessing.Pool(num_cores)

        try:
            # Run avatar generation in parallel
            avatar_tasks = []
            for stored_persona in stored_personas:
                avatar_tasks.append(
                    avatar_pool.apply_async(
                        process_avatar_generation,
                        args=(storage_config, stored_persona, workspace_id)
                    )
                )

            # Run voice generation sequentially (to avoid rate limits)
            voice_results = []
            for stored_persona in stored_personas:
                try:
                    # Generate voice with retry logic
                    max_retries = 3
                    retry_delay = 5  # seconds
                    
                    for attempt in range(max_retries):
                        try:
                            voice_id = await generate_voice_for_persona(stored_persona, OpenAI(api_key=api_key))
                            if voice_id:
                                logger.info(f"Successfully generated voice for {stored_persona['name']}")
                                # Update persona document with voice ID
                                databases.update_document(
                                    database_id=DATABASE_ID,
                                    collection_id=AI_PERSONAS_COLLECTION,
                                    document_id=stored_persona['$id'],
                                    data={'voice_id': voice_id}
                                )
                                # Update user preferences with voice ID
                                users.update_prefs(
                                    user_id=stored_persona['$id'],
                                    prefs={'voiceId': voice_id}
                                )
                                logger.info(f"Updated user preferences with voice ID for {stored_persona['name']}")
                            break
                        except Exception as e:
                            if "502" in str(e) and attempt < max_retries - 1:
                                logger.warning(f"Rate limited, retrying in {retry_delay} seconds...")
                                await asyncio.sleep(retry_delay)
                                retry_delay *= 2  # Exponential backoff
                                continue
                            logger.error(f"Failed to generate voice for {stored_persona['name']}: {str(e)}")
                            break
                    
                    # Add delay between voice generations
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    logger.error(f"Voice generation error for {stored_persona['name']}: {str(e)}")

            # Wait for avatar generation to complete and process results
            avatar_results = {}
            for task in avatar_tasks:
                try:
                    user_id, avatar_id = task.get()
                    if avatar_id:
                        avatar_results[user_id] = avatar_id
                        logger.info(f"Successfully processed avatar for user {user_id}")
                except Exception as e:
                    logger.error(f"Error getting avatar task result: {str(e)}")

        finally:
            avatar_pool.close()
            avatar_pool.join()

        # Prepare success response before starting autonomous conversations
        response = {
            'workspace_id': workspace_id,
            'personas': stored_personas,
            'channels': stored_channels,
            'workspace_theme': description,
            'status': 'success',
            'message': 'Workspace created successfully. Autonomous conversations will be generated in the background.'
        }

        # Start autonomous conversations in the background
        async def run_conversations_background():
            try:
                logger.info("Starting autonomous conversations for workspace: %s", workspace_id)
                await populate_workspace_conversations(workspace_id)
                logger.info("Successfully completed autonomous conversations for workspace: %s", workspace_id)
            except Exception as e:
                logger.error(f"Error in autonomous conversations: {str(e)}")
                logger.exception(e)  # Log full traceback for debugging

        # Schedule the background task
        asyncio.create_task(run_conversations_background())
        
        return response
        
    except Exception as e:
        logger.error(f"Error creating workspace {workspace_id}: {str(e)}")
        raise

async def handle_request(request):
    logger.info("Received workspace creation request")
    try:
        # Get workspace description and ID from query params
        description = request.query.get('description', 'A general workspace for team collaboration')
        workspace_id = request.query.get('workspace_id')
        
        logger.debug("Request parameters - Description: %s, Workspace ID: %s", 
                    description, workspace_id)
        
        if not workspace_id:
            logger.error("Missing required parameter: workspace_id")
            return web.Response(text="workspace_id is required", status=400)
        
        if not OPENAI_API_KEY:
            logger.error("OPENAI_API_KEY not found in environment")
            return web.Response(text="OPENAI_API_KEY not found in environment", status=500)
        
        # Create workspace with personas and store in Appwrite
        logger.info("Creating workspace with ID: %s", workspace_id)
        workspace = await create_workspace(description, workspace_id, OPENAI_API_KEY)
        
        logger.info("Successfully processed workspace creation request")
        # Return the complete workspace initialization data
        return web.Response(
            text=json.dumps(workspace, indent=2),
            content_type='application/json',
            status=200
        )
        
    except Exception as e:
        logger.error("Request handler error: %s", str(e))
        logger.exception(e)
        return web.Response(text=f"Error: {str(e)}", status=500)



async def main():
    logger.info("Starting server initialization")
    app = web.Application()
    app.router.add_get('/', handle_request)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    logger.info("Server starting at http://localhost:8080")
    await site.start()
    logger.info("Server successfully started")
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)
        logger.debug("Server heartbeat")

async def generate_and_store_avatar(storage: Storage, persona: dict, workspace_id: str) -> str:
    """
    Generate and store an AI avatar for a persona in Appwrite Storage based on their attributes.
    
    Args:
        storage: Appwrite Storage service instance
        persona: Dictionary containing persona attributes
        workspace_id: ID of the workspace
        
    Returns:
        str: ID of the stored file in Appwrite
    """
    logger.info(f"Generating personalized avatar for persona: {persona['name']}")
    
    try:
        # 1. Create a personalized prompt based on persona attributes
        personality_traits = persona['personality'].lower()
        role = persona['role'].lower()
        conversation_style = persona['conversation_style'].lower()
        
        # Map personality traits to creative, abstract descriptors with blue/purple focus
        style_mapping = {
            'formal': 'geometric shapes in navy blue, crystalline structures',
            'professional': 'flowing gradients of indigo and violet, clean lines',
            'casual': 'playful swirls of periwinkle and lavender',
            'friendly': 'soft clouds of powder blue and lilac',
            'analytical': 'angular patterns in sapphire and amethyst',
            'creative': 'abstract splashes of cobalt and purple',
            'tech': 'digital waves of electric blue and ultraviolet',
            'academic': 'constellation patterns in deep blue and royal purple'
        }
        
        # Find matching style descriptors
        style_elements = []
        for key, value in style_mapping.items():
            if key in personality_traits or key in conversation_style or key in role:
                style_elements.append(value)
        
        # If no specific style matches, use creative default style
        if not style_elements:
            style_elements = ['ethereal blend of blue and purple hues, abstract forms']
            
        # Create an artistic, abstract prompt
        prompt = (
            f"Abstract artistic portrait incorporating {', '.join(style_elements[:2])}, "
            f"minimalist face suggestion emerging from {persona['role'].lower()} themed elements, "
            "predominantly blue and purple color palette, ethereal lighting, "
            "modern digital art style with subtle sacred geometry patterns"
        )
        
        logger.debug(f"Generated prompt: {prompt}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            # Initialize OpenAI client
            client = OpenAI(api_key=OPENAI_API_KEY)
            
            # First attempt with personalized prompt
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download the image from the URL
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_bytes = image_response.content
            
        except Exception as img_error:
            logger.warning(f"Failed with personalized prompt: {str(img_error)}. Trying fallback prompt...")
            # Fallback to a creative but safe prompt
            fallback_prompt = "Abstract portrait, flowing blue and purple gradients, minimal geometric patterns, ethereal lighting"
            response = client.images.generate(
                model="dall-e-3",
                prompt=fallback_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Download the image from the URL
            image_url = response.data[0].url
            image_response = requests.get(image_url)
            image_bytes = image_response.content
            
        # Convert PNG bytes to WebP
        image = Image.open(BytesIO(image_bytes))
        
        # Create a BytesIO object to store the WebP image
        webp_buffer = BytesIO()
        # Convert to WebP with high quality
        image.save(webp_buffer, format="WebP", quality=95, method=6)
        webp_bytes = webp_buffer.getvalue()
        
        # 3. Create a unique filename
        filename = f"{persona['name'].lower().replace(' ', '_')}_{workspace_id}_avatar.webp"
        
        # 4. Store in Appwrite Storage using InputFile
        logger.info(f"Storing avatar in Appwrite bucket: {filename}")
        
        # Create the file using InputFile
        input_file = InputFile.from_bytes(
            webp_bytes,
            filename=filename
        )

        file_id = ID.unique()
        
        result = storage.create_file(
            bucket_id='avatars',
            file_id=file_id,
            file=input_file,
        )
        
        logger.info(f"Successfully stored avatar with ID: {file_id}")

        # Immediately update user preferences with avatar ID
        try:
            # Create new Appwrite client for user operations
            appwrite_client = Client()
            appwrite_client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
            appwrite_client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
            appwrite_client.set_key(os.getenv('APPWRITE_API_KEY'))
            
            users = Users(appwrite_client)
            logger.info(f"Setting avatar ID {file_id} for user {persona['ai_user_id']}")
            users.update_prefs(
                user_id=persona['ai_user_id'],
                prefs={'avatarId': file_id}
            )
            logger.info(f"Successfully set avatar ID for user {persona['ai_user_id']}")
        except Exception as e:
            logger.error(f"Failed to update user prefs with avatar ID for {persona['name']}: {str(e)}")
            logger.exception(e)
        
        return file_id
        
    except Exception as e:
        logger.error(f"Failed to generate/store avatar for {persona['name']}: {str(e)}")
        logger.exception(e)
        return None

async def generate_voice_for_persona(persona: dict, openai_client: OpenAI) -> str:
    """
    Generate a voice for an AI persona using OpenAI for the prompt and ElevenLabs for synthesis.
    
    Args:
        persona: Dictionary containing persona attributes
        openai_client: OpenAI client instance
        
    Returns:
        str: Voice ID from ElevenLabs
    """
    async def get_voice_description(persona: dict, previous_error: str = None) -> str:
        base_prompt = """Create an extremely concise voice synthesis prompt (MAXIMUM 300 characters) for an AI character with these traits:

{persona_json}

Focus ONLY on basic voice characteristics: tone, pitch, pace, and accent if any.
BE EXTREMELY BRIEF AND PROFESSIONAL. NO CONTROVERSIAL OR EMOTIONAL CONTENT.
KEEP YOUR RESPONSE UNDER 300 CHARACTERS."""

        if previous_error:
            base_prompt += f"\n\nPREVIOUS ATTEMPT WAS BLOCKED. Error: {previous_error}\nEnsure the description is completely neutral and professional."

        prompt = base_prompt.format(persona_json=json.dumps(persona, indent=2))

        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        description = response.choices[0].message.content.strip()
        # Ensure we're well under the 500 char limit
        if len(description) > 400:
            description = description[:397] + "..."
        return description

    try:
        # Get initial voice description
        voice_description = await get_voice_description(persona)
        
        # Generate example text based on persona's style (at least 100 chars)
        example_text = f"Hello everyone, I am {persona['name']}. {persona.get('greeting', '')} " + \
                      f"As a {persona.get('role', '')}, I bring unique perspectives shaped by my background in " + \
                      f"{', '.join(persona.get('knowledge_base', []))}. " + \
                      f"{persona.get('catchphrases', [''])[0]}"
        
        max_retries = 3
        current_retry = 0
        
        while current_retry < max_retries:
            try:
                # Initialize ElevenLabs client
                eleven_client = ElevenLabs(api_key=os.getenv('ELEVENLABS_API_KEY'))
                
                # Create voice previews
                preview_response = eleven_client.text_to_voice.create_previews(
                    voice_description=voice_description,
                    text=example_text
                )
                
                # Get the first preview's generated voice ID
                generated_voice_id = preview_response.previews[0].generated_voice_id
                logger.info(f"Generated preview voice ID for {persona['name']}: {generated_voice_id}")
                
                # Create the final voice
                voice_response = eleven_client.text_to_voice.create_voice_from_preview(
                    voice_name=persona['name'],
                    voice_description=voice_description,
                    generated_voice_id=generated_voice_id
                )
                
                logger.info(f"Created final voice for {persona['name']} with ID: {voice_response.voice_id}")
                return voice_response.voice_id
                
            except Exception as e:
                error_str = str(e)
                if "blocked_generation" in error_str:
                    current_retry += 1
                    if current_retry < max_retries:
                        logger.warning(f"Voice generation blocked for {persona['name']}, attempt {current_retry + 1}")
                        # Get new description with error context
                        voice_description = await get_voice_description(persona, error_str)
                        continue
                raise
        
        logger.error(f"Failed to generate voice for {persona['name']} after {max_retries} attempts")
        return None
        
    except Exception as e:
        logger.error(f"Failed to generate voice for {persona['name']}: {str(e)}")
        logger.exception(e)
        return None

def process_avatar_generation(storage_config: dict, persona: dict, workspace_id: str) -> tuple:
    """Wrapper for parallel avatar generation"""
    try:
        # Recreate storage client in the new process
        client = Client()
        client.set_endpoint(storage_config['endpoint'])
        client.set_project(storage_config['project'])
        client.set_key(storage_config['api_key'])
        
        storage = Storage(client)
        
        # Run the avatar generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        avatar_id = loop.run_until_complete(generate_and_store_avatar(storage, persona, workspace_id))
        loop.close()
        
        return persona['ai_user_id'], avatar_id
    except Exception as e:
        logger.error(f"Avatar generation process error for {persona['name']}: {str(e)}")
        return persona['ai_user_id'], None

def process_voice_generation(openai_key: str, persona: dict) -> tuple:
    """Wrapper for parallel voice generation"""
    try:
        # Create new OpenAI client in the new process
        openai_client = OpenAI(api_key=openai_key)
        
        # Run the voice generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(generate_voice_for_persona(persona, openai_client))
        loop.close()
        return persona['ai_user_id'], result
    except Exception as e:
        logger.error(f"Voice generation process error for {persona['name']}: {str(e)}")
        return persona['ai_user_id'], None

if __name__ == "__main__":
    logger.info("=== Application Starting ===")
    asyncio.run(main())
