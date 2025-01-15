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
from openai import AsyncOpenAI
from appwrite.query import Query
from titanGenerate import generate_images, OBJECTS, generate_profile_prompt
from PIL import Image
from io import BytesIO
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
    logger.info("=== Starting Workspace Creation ===")
    logger.info("Workspace ID: %s", workspace_id)
    logger.info("Description: %s", description)
    
    # Create test_data directory if it doesn't exist
    os.makedirs('test_data', exist_ok=True)
    logger.debug("Ensured test_data directory exists")
    
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
    logger.debug("Initialized test data structure")
    
    # Generate personas first
    logger.info("Generating personas with OpenAI for workspace: %s", workspace_id)
    personas_prompt = PERSONA_GENERATION_PROMPT.format(
        num_personas=5,
        description=description
    )
    logger.debug("Generated persona prompt (first 100 chars): %s", personas_prompt[:100])
    
    personas_json = await generate_with_openai(personas_prompt, api_key)
    personas = json.loads(personas_json)
    logger.info("Successfully generated %d personas", len(personas))
    
    # Store each persona in Appwrite
    stored_personas = []
    ai_user_ids = []  # Track all AI user IDs
    
    for idx, persona in enumerate(personas, 1):
        try:
            logger.info("Processing persona %d/%d: %s", idx, len(personas), persona['name'])
            logger.debug("Persona details - Role: %s, Style: %s", 
                        persona['role'], persona['conversation_style'])
            
            # Create an AI user for this specific persona
            ai_user_id = await create_ai_user(persona['name'], workspace_id)
            ai_user_ids.append(ai_user_id)
            logger.info("Created AI user ID: %s for persona: %s", ai_user_id, persona['name'])
            
            # Generate and store avatar
            avatar_file_id = await generate_and_store_avatar(storage, persona, workspace_id)
            if avatar_file_id:
                # Update user preferences with the avatar file ID
                users.update_prefs(
                    user_id=ai_user_id,
                    prefs={'avatarId': avatar_file_id}
                )
                logger.info("Updated user preferences with avatar: %s", avatar_file_id)
            
            # Save AI user ID mapping and user info
            test_data["mappings"]["ai_user_ids"][persona['name']] = ai_user_id
            test_data["users"].append({
                "name": persona['name'],
                "ai_user_id": ai_user_id,
                "email": f"{persona['name'].lower().replace(' ', '_')}.{workspace_id}@chattie.local",
                "personality": persona['personality'],
                "conversation_style": persona['conversation_style'],
                "knowledge_base": persona['knowledge_base'],
                "role": persona['role'],
                "greeting": persona['greeting'],
                "opinions": persona.get('opinions', []),
                "disagreements": persona.get('disagreements', []),
                "debate_style": persona.get('debate_style', ''),
                "triggers": persona.get('triggers', []),
                "catchphrases": persona.get('catchphrases', []),
                "communication_quirks": persona.get('communication_quirks', []),
                "temperature": persona.get('temperature', 0.7)
            })
            logger.debug("Added persona data to test_data structure")
            
            # Prepare the persona data according to our schema
            persona_data = {
                'workspace_id': workspace_id,
                'name': persona['name'],
                'personality': persona['personality'],
                'avatar_url': f"https://api.dicebear.com/7.x/avataaars/svg?seed={persona['name']}",
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
            
            logger.info("Storing persona in Appwrite: %s", persona['name'])
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
            
            logger.info("Successfully stored persona: %s with ID: %s", 
                       persona['name'], stored_persona['$id'])
            
            # Save persona ID mapping
            test_data["mappings"]["persona_ids"][persona['name']] = stored_persona['$id']
            stored_personas.append(stored_persona)
            
        except Exception as e:
            logger.error("Failed to store persona %s: %s", persona['name'], str(e))
            logger.exception(e)
    
    # Generate channels
    logger.info("Generating channels with OpenAI for workspace: %s", workspace_id)
    channels_prompt = CHANNEL_GENERATION_PROMPT.format(
        description=description
    )
    logger.debug("Generated channels prompt (first 100 chars): %s", channels_prompt[:100])
    
    channels_json = await generate_with_openai(channels_prompt, api_key)
    channels = json.loads(channels_json)
    logger.info("Successfully generated %d channels", len(channels))
    
    # Store channels in Appwrite and create initial messages
    stored_channels = []
    for idx, channel in enumerate(channels, 1):
        try:
            logger.info("Processing channel %d/%d: %s", idx, len(channels), channel['name'])
            logger.debug("Channel details - Description: %s", channel['description'][:100])
            
            # Include all AI persona users as members
            ai_members = ai_user_ids
            
            # Prepare channel data according to our schema
            channel_data = {
                'workspace_id': workspace_id,
                'name': channel['name'].lower().replace(' ', '-'),
                'type': 'public',
                'members': ai_members,
                'description': channel['description'],
                'purpose': channel.get('purpose', ''),
                'topics': channel.get('topics', []),
                'debate_topics': channel.get('debate_topics', []),
                'last_message_at': None,
                'primary_personas': [persona['name'] for persona in personas]
            }
            
            logger.info("Storing channel in Appwrite: %s", channel_data['name'])
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
            logger.info("Successfully stored channel: %s with ID: %s", 
                       channel_data['name'], stored_channel['$id'])
            
            # Save channel with its ID to test data
            test_data["channels"].append({
                "name": channel['name'],
                "$id": stored_channel['$id'],
                "description": channel['description'],
                "purpose": channel.get('purpose', ''),
                "topics": channel.get('topics', []),
                "debate_topics": channel.get('debate_topics', []),
                "conversation_tone": channel.get('conversation_tone', 'mixed'),
                "expected_conflict_points": channel.get('expected_conflict_points', []),
                "type": "public",
                "members": ai_members,
                "primary_personas": [persona['name'] for persona in personas],
                "workspace_id": workspace_id
            })
            logger.debug("Added channel data to test_data structure")
            
            # Save channel ID mapping
            test_data["mappings"]["channel_ids"][channel['name']] = stored_channel['$id']
            stored_channels.append(stored_channel)
            
        except Exception as e:
            logger.error("Failed to store channel %s: %s", channel['name'], str(e))
            logger.exception(e)
    
    # Update workspace members with channel access - moved outside the loop
    async def update_workspace_members():
        try:
            logger.info("Starting workspace member updates for workspace: %s", workspace_id)
            
            # First get the workspace document to get the owner_id
            workspace = databases.get_document(
                database_id=DATABASE_ID,
                collection_id='workspaces',
                document_id=workspace_id
            )
            owner_id = workspace['owner_id']
            logger.debug("Retrieved workspace owner ID: %s", owner_id)
            
            # Get all channels for the workspace
            channels = databases.list_documents(
                database_id=DATABASE_ID,
                collection_id=CHANNELS_COLLECTION,
                queries=[
                    Query.equal('workspace_id', workspace_id)
                ]
            )
            
            channel_ids = [channel['$id'] for channel in channels['documents']]
            logger.info("Found %d channels for workspace", len(channel_ids))
            
            # Combine AI users, workspace owner, and bot user (only once)
            all_member_ids = [*ai_user_ids, owner_id, 'bot']
            logger.info("Updating workspace with %d total members", len(all_member_ids))
            
            # Update workspace members array with AI personas and bot (only once)
            workspace_data = {
                'members': list(set([*workspace.get('members', []), *ai_user_ids, 'bot']))
            }
            logger.debug("Updating workspace document with %d members", 
                       len(workspace_data['members']))
            
            databases.update_document(
                database_id=DATABASE_ID,
                collection_id='workspaces',
                document_id=workspace_id,
                data=workspace_data
            )
            # Update each member's labels with all channel IDs
            for member_id in all_member_ids:
                logger.debug("Processing member: %s", member_id)
                # Get existing labels first
                user = users.get(member_id)
                existing_labels = user.get('labels', [])
                
                # Combine existing labels with new channel IDs
                updated_labels = list(set(existing_labels + channel_ids))
                
                logger.info("Updating labels for member: %s", member_id)
                users.update_labels(
                    user_id=member_id,
                    labels=updated_labels
                )
            logger.info("Completed workspace member updates")
            
        except Exception as e:
            logger.error("Error in workspace member updates: %s", str(e))
            logger.exception(e)
    
    # Call update_workspace_members once after all channels are created
    await update_workspace_members()
    
    # Save test data to file
    logger.info("Saving test data to test_data/responses.json")
    with open('test_data/responses.json', 'w') as f:
        json.dump(test_data, f, indent=4)
    logger.debug("Successfully saved test data to file")
    
    logger.info("Workspace creation completed - Personas: %d, Channels: %d", 
                len(stored_personas), len(stored_channels))

    # Start autonomous conversations in background task
    logger.info("Starting autonomous conversations in background")
    from autonomous_conversation import populate_workspace_conversations
    asyncio.create_task(populate_workspace_conversations(workspace_id))
    
    logger.info("=== Workspace Creation Complete ===")
    return {
        'workspace_id': workspace_id,
        'personas': stored_personas,
        'channels': stored_channels,
        'workspace_theme': description,
        'status': 'success',
        'message': 'Workspace created successfully. Autonomous conversations starting in background.'
    }

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
        
        # Map personality traits to safe, positive descriptors
        style_mapping = {
            'formal': 'business attire, confident pose',
            'professional': 'polished appearance, warm expression',
            'casual': 'relaxed style, approachable look',
            'friendly': 'welcoming smile, bright eyes',
            'analytical': 'thoughtful expression, smart attire',
            'creative': 'artistic style, imaginative look',
            'tech': 'modern style, innovative look',
            'academic': 'scholarly appearance, wise expression'
        }
        
        # Find matching style descriptors
        style_elements = []
        for key, value in style_mapping.items():
            if key in personality_traits or key in conversation_style or key in role:
                style_elements.append(value)
        
        # If no specific style matches, use default professional style
        if not style_elements:
            style_elements = ['professional appearance, friendly expression']
            
        # Create a safe but personalized prompt
        prompt = (
            f"Professional portrait in minimalist cartoon style, "
            f"{', '.join(style_elements[:2])}, "  # Limit to 2 style elements
            "clean background, high quality digital art"
        )
        
        logger.debug(f"Generated prompt: {prompt}")
        logger.debug(f"Prompt length: {len(prompt)} characters")
        
        try:
            # First attempt with personalized prompt
            generated_images = generate_images(
                prompt=prompt,
                num_images=1,
                seed=random.randint(1000, 9999),
                width=512,
                height=512,
                cfg_scale=8,
                quality="standard"
            )
        except Exception as img_error:
            logger.warning(f"Failed with personalized prompt: {str(img_error)}. Trying fallback prompt...")
            # Fallback to a very safe, generic prompt
            fallback_prompt = "Simple professional headshot avatar, minimalist cartoon style, neutral background"
            generated_images = generate_images(
                prompt=fallback_prompt,
                num_images=1,
                seed=random.randint(1000, 9999),
                width=512,
                height=512,
                cfg_scale=8,
                quality="standard"
            )
        
        if not generated_images:
            raise Exception("No image generated")
            
        # Convert PNG bytes to WebP
        image_bytes = generated_images[0]
        image = Image.open(BytesIO(image_bytes))
        
        # Create a BytesIO object to store the WebP image
        webp_buffer = BytesIO()
        # Convert to WebP with high quality
        image.save(webp_buffer, format="WebP", quality=90, method=6)
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
        return file_id
        
    except Exception as e:
        logger.error(f"Failed to generate/store avatar for {persona['name']}: {str(e)}")
        logger.exception(e)
        return None

if __name__ == "__main__":
    logger.info("=== Application Starting ===")
    asyncio.run(main())
