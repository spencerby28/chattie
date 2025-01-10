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
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Label
import secrets
import string
import logging
import sys

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
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
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

# Database and Collection IDs
DATABASE_ID = 'main'
AI_PERSONAS_COLLECTION = 'ai_personas'
CHANNELS_COLLECTION = 'channels'

# Enhanced persona generation to include more chat-relevant details
PERSONA_GENERATION_PROMPT = """Create {num_personas} unique and engaging AI personas for a workspace focused on: {description}

Each persona should have strong opinions and perspectives related to this workspace's focus. They should feel like real people with distinct viewpoints and approaches to {description}. Each persona should have:

1. A memorable name or username (professional but approachable)
2. A distinct personality and communication style
3. Areas of expertise/knowledge base specifically relevant to {description}
4. A brief backstory that explains their perspective and why they care about {description}
5. Their typical way of interacting with users
6. Their role in the way they live their life
7. Strong opinions about {description} and how things should be done

Format the response as a JSON array with objects containing:
- name: string
- personality: string (detailed description including their strong opinions)
- conversation_style: string (formal/casual/technical etc)
- knowledge_base: string[] (areas of expertise)
- role: string (their role in life)
- greeting: string (their typical first message that shows their personality)
- opinions: string[] (list of strong beliefs they hold about {description})

The response MUST be a valid JSON array.
"""

# Channel generation based on workspace theme
CHANNEL_GENERATION_PROMPT = """Create channels for a workspace focused on: {description}

Create channels that would facilitate meaningful discussions about different aspects of {description}. Each channel should have:
1. A clear name (no spaces, lowercase, use hyphens if needed)
2. A specific purpose related to {description}
3. The type of discussions that should happen there
4. Which personas would be most active here (based on their roles and opinions)

Format as JSON array with:
- name: string
- description: string
- purpose: string
- primary_personas: string[] (names of personas who should be most active here)
- topics: string[] (key discussion points for this channel)
"""

def generate_secure_password(length=32):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(length))

async def create_ai_user(workspace_id: str):
    """Create an AI user account for the workspace"""
    logger.info("Creating AI user for workspace: %s", workspace_id)
    try:
        # Generate a secure random password
        password = generate_secure_password()
        email = f"ai.{workspace_id}@chattie.local"
        name = f"AI Assistant - {workspace_id}"
        
        logger.info("Attempting to create AI user with email: %s", email)
        # Create the user in Appwrite using admin client
        ai_user = users.create(
            user_id=f"ai-{workspace_id}",
            email=email,
            password=password,
            name=name
        )
        
        logger.info("Successfully created AI user: %s", ai_user['$id'])
        return ai_user['$id']
        
    except Exception as e:
        logger.warning("Error creating AI user: %s", str(e))
        # Check if user already exists
        try:
            logger.info("Checking if AI user already exists")
            existing_user = users.get(f"ai-{workspace_id}")
            logger.info("Found existing AI user: %s", existing_user['$id'])
            return existing_user['$id']
        except Exception as inner_e:
            logger.error("Failed to get existing user: %s", str(inner_e))
            raise e

async def generate_with_deepseek(prompt: str, api_key: str) -> str:
    # Create SSL context with certifi certificates
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    
    # Create connector with SSL context
    connector = TCPConnector(ssl=ssl_context)
    
    async with aiohttp.ClientSession(connector=connector) as session:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            print("\nMaking request to Deepseek API...")
            print("Headers:", json.dumps(headers, indent=2))
            print("Request Data:", json.dumps(data, indent=2))
            
            async with session.post("https://api.deepseek.com/v1/chat/completions", 
                                  headers=headers, json=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"Deepseek API error: Status {response.status}, Response: {error_text}")
                    raise Exception(f"Deepseek API error: {error_text}")
                
                raw_response = await response.text()
                print("\nRaw API Response Text:")
                print("=" * 50)
                print(raw_response)
                print("=" * 50)
                
                result = json.loads(raw_response)
                content = result["choices"][0]["message"]["content"]
                
                # Strip markdown formatting
                content = content.strip()
                if content.startswith("```json"):
                    content = content[7:]  # Remove ```json
                elif content.startswith("```"):
                    content = content[3:]  # Remove ```
                if content.endswith("```"):
                    content = content[:-3]  # Remove trailing ```
                content = content.strip()
                
                print("\nCleaned Content:")
                print("=" * 50)
                print(content)
                print("=" * 50)
                
                return content
                
        except Exception as e:
            print(f"\nError in generate_with_deepseek: {str(e)}")
            print(f"Error type: {type(e)}")
            if hasattr(e, '__traceback__'):
                import traceback
                print("Traceback:")
                traceback.print_tb(e.__traceback__)
            raise

async def create_workspace(description: str, workspace_id: str, api_key: str):
    logger.info("Starting workspace creation for ID: %s", workspace_id)
    logger.info("Workspace description: %s", description)
    
    # First, create an AI user for this workspace
    ai_user_id = await create_ai_user(workspace_id)
    logger.info("AI user created/retrieved: %s", ai_user_id)
    
    # Generate personas first
    logger.info("Generating personas with Deepseek")
    personas_prompt = PERSONA_GENERATION_PROMPT.format(
        num_personas=5,
        description=description
    )
    personas_json = await generate_with_deepseek(personas_prompt, api_key)
    personas = json.loads(personas_json)
    logger.info("Generated %d personas", len(personas))
    
    # Store each persona in Appwrite
    stored_personas = []
    for idx, persona in enumerate(personas, 1):
        try:
            logger.info("Processing persona %d/%d: %s", idx, len(personas), persona['name'])
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
                'ai_user_id': ai_user_id
            }
            
            logger.info("Storing persona in Appwrite: %s", persona['name'])
            # Create or update the persona in Appwrite using admin client
            stored_persona = databases.create_document(
                database_id=DATABASE_ID,
                collection_id=AI_PERSONAS_COLLECTION,
                document_id=ID.unique(),
                data=persona_data,
                permissions=[
                    Permission.read(Role.users()),
                    Permission.write(Role.user(ai_user_id)),
                    Permission.update(Role.user(ai_user_id)),
                    Permission.delete(Role.user(workspace_id)),
                    Permission.read(Label.user(ai_user_id))
                ]
            )
            
            logger.info("Successfully stored persona: %s with ID: %s", 
                       persona['name'], stored_persona['$id'])
            stored_personas.append(stored_persona)
            
        except Exception as e:
            logger.error("Failed to store persona %s: %s", persona['name'], str(e))
            logger.exception(e)
    
    # Generate channels
    logger.info("Generating channels with Deepseek")
    channels_prompt = CHANNEL_GENERATION_PROMPT.format(
        description=description
    )
    channels_json = await generate_with_deepseek(channels_prompt, api_key)
    channels = json.loads(channels_json)
    logger.info("Generated %d channels", len(channels))
    
    # Store channels in Appwrite
    stored_channels = []
    for idx, channel in enumerate(channels, 1):
        try:
            logger.info("Processing channel %d/%d: %s", idx, len(channels), channel['name'])
            # Get AI members for this channel
            ai_members = [ai_user_id]
            
            # Prepare channel data according to our schema
            channel_data = {
                'workspace_id': workspace_id,
                'name': channel['name'].lower().replace(' ', '-'),
                'type': 'public',
                'members': ai_members,
                'description': channel['description'],
                'purpose': channel.get('purpose', ''),
                'topics': channel.get('topics', []),
                'last_message_at': None,
                'primary_personas': [
                    persona['name'] for persona in personas 
                    if persona['name'] in channel['primary_personas']
                ]
            }
            
            logger.info("Storing channel in Appwrite: %s", channel_data['name'])
            # Create channel in Appwrite using admin client
            stored_channel = databases.create_document(
                database_id=DATABASE_ID,
                collection_id=CHANNELS_COLLECTION,
                document_id=ID.unique(),
                data=channel_data,
                permissions=[
                    Permission.read(Role.users()),
                    Permission.write(Role.users()),
                    Permission.write(Role.user(ai_user_id)),
                    Permission.update(Role.user(workspace_id)),
                    Permission.delete(Role.user(workspace_id))
                ]
            )
            
            logger.info("Successfully stored channel: %s with ID: %s", 
                       channel_data['name'], stored_channel['$id'])
            stored_channels.append(stored_channel)
            
        except Exception as e:
            logger.error("Failed to store channel %s: %s", channel['name'], str(e))
            logger.exception(e)
    
    logger.info("Workspace creation completed. Personas: %d, Channels: %d", 
                len(stored_personas), len(stored_channels))
    return {
        'ai_user_id': ai_user_id,
        'personas': stored_personas,
        'channels': stored_channels,
        'workspace_theme': description
    }

async def handle_request(request):
    try:
        # Get workspace description and ID from query params
        description = request.query.get('description', 'A general workspace for team collaboration')
        workspace_id = request.query.get('workspace_id')
        
        if not workspace_id:
            return web.Response(text="workspace_id is required", status=400)
        
        if not DEEPSEEK_API_KEY:
            return web.Response(text="DEEPSEEK_API_KEY not found in environment", status=500)
        
        # Create workspace with personas and store in Appwrite
        workspace = await create_workspace(description, workspace_id, DEEPSEEK_API_KEY)
        
        # Return the complete workspace initialization data
        return web.Response(
            text=json.dumps(workspace, indent=2),
            content_type='application/json',
            status=200
        )
        
    except Exception as e:
        print(f"\nRequest handler error: {str(e)}")
        return web.Response(text=f"Error: {str(e)}", status=500)

async def main():
    app = web.Application()
    app.router.add_get('/', handle_request)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    print("Server started at http://localhost:8080")
    await site.start()
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
