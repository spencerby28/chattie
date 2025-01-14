import asyncio
import json
import os
from dotenv import load_dotenv
import logging
import sys
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.users import Users
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('test_agent.log')
    ]
)
logger = logging.getLogger('test_agent')

# Load environment variables
load_dotenv()

# Initialize Appwrite Admin Client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize Database and Users services
databases = Databases(client)
users = Users(client)

# Database and Collection IDs
DATABASE_ID = 'main'
AI_PERSONAS_COLLECTION = 'ai_personas'
CHANNELS_COLLECTION = 'channels'
MESSAGES_COLLECTION = 'messages'

def load_test_data():
    """Load test data from responses.json"""
    with open('test_data/responses.json', 'r') as f:
        return json.load(f)

async def test_create_ai_user(persona_name: str, workspace_id: str):
    """Test creating an AI user"""
    try:
        logger.info(f"Testing AI user creation for {persona_name}")
        # Create a sanitized username from persona name
        username = persona_name.lower().replace(' ', '_')
        email = f"{username}.{workspace_id}@chattie.local"
        
        # Create the user in Appwrite
        ai_user = users.create(
            user_id=ID.unique(),
            email=email,
            password="test_password",  # Use a fixed password for testing
            name=persona_name
        )
        
        logger.info(f"Successfully created test AI user: {ai_user['$id']}")
        return ai_user['$id']
        
    except Exception as e:
        logger.error(f"Error creating test AI user: {str(e)}")
        raise

async def test_store_persona(persona: dict, workspace_id: str, ai_user_id: str):
    """Test storing a persona in Appwrite"""
    try:
        logger.info(f"Testing persona storage for {persona['name']}")
        
        # Prepare the persona data
        persona_data = {
            'workspace_id': workspace_id,
            'name': persona['name'],
            'personality': persona['personality'],
            'avatar_url': f"https://api.dicebear.com/7.x/avataaars/svg?seed={persona['name']}",
            'conversation_style': persona['conversation_style'],
            'knowledge_base': persona['knowledge_base'],
            'greeting': persona['greeting'],
            'role': persona['role'],
            'opinions': persona['opinions'],
            'disagreements': persona['disagreements'],
            'debate_style': persona['debate_style'],
            'ai_user_id': ai_user_id
        }
        
        # Store in Appwrite
        stored_persona = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=AI_PERSONAS_COLLECTION,
            document_id=ID.unique(),
            data=persona_data,
            permissions=[
                Permission.read(Role.users()),
                Permission.write(Role.user(ai_user_id)),
                Permission.update(Role.user(ai_user_id)),
                Permission.delete(Role.user(workspace_id))
            ]
        )
        
        logger.info(f"Successfully stored test persona: {stored_persona['$id']}")
        return stored_persona
        
    except Exception as e:
        logger.error(f"Error storing test persona: {str(e)}")
        raise

async def test_store_channel(channel: dict, workspace_id: str, ai_user_ids: list):
    """Test storing a channel in Appwrite"""
    try:
        logger.info(f"Testing channel storage for {channel['name']}")
        
        # Prepare channel data
        channel_data = {
            'workspace_id': workspace_id,
            'name': channel['name'].lower().replace(' ', '-'),
            'type': 'public',
            'members': ai_user_ids,
            'description': channel['description'],
            'purpose': channel['purpose'],
            'topics': channel['topics'],
            'debate_topics': channel['debate_topics'],
            'last_message_at': None,
            'primary_personas': []  # Empty as we want all personas to participate
        }
        
        # Store in Appwrite
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
        
        logger.info(f"Successfully stored test channel: {stored_channel['$id']}")
        return stored_channel
        
    except Exception as e:
        logger.error(f"Error storing test channel: {str(e)}")
        raise

async def test_create_initial_messages(channel_id: str, workspace_id: str, initial_messages: dict, personas_map: dict):
    """Test creating initial messages in a channel"""
    created_messages = []
    
    for persona_name, message_content in initial_messages.items():
        try:
            logger.info(f"Creating test message for {persona_name}")
            
            message_data = {
                'channel_id': channel_id,
                'workspace_id': workspace_id,
                'sender_type': 'ai',
                'sender_id': personas_map[persona_name]['ai_user_id'],
                'content': message_content,
                'sender_name': persona_name,
                'edited_at': None,
                'mentions': [],
                'ai_context': None,
                'ai_prompt': None,
                'attachments': []
            }
            
            message = databases.create_document(
                database_id=DATABASE_ID,
                collection_id=MESSAGES_COLLECTION,
                document_id=ID.unique(),
                data=message_data,
                permissions=[
                    Permission.read(Role.label(channel_id)),
                    Permission.write(Role.user(personas_map[persona_name]['ai_user_id']))
                ]
            )
            
            logger.info(f"Created test message: {message['$id']}")
            created_messages.append(message)
            
        except Exception as e:
            logger.error(f"Error creating test message for {persona_name}: {str(e)}")
            continue
    
    return created_messages

async def run_tests():
    """Run all tests"""
    try:
        # Load test data
        test_data = load_test_data()
        workspace_id = "test_workspace_001"
        
        # Test persona creation
        personas_map = {}
        for persona in test_data['personas']:
            # Create AI user
            ai_user_id = await test_create_ai_user(persona['name'], workspace_id)
            
            # Store persona
            stored_persona = await test_store_persona(persona, workspace_id, ai_user_id)
            personas_map[persona['name']] = stored_persona
        
        # Test channel creation
        ai_user_ids = [p['ai_user_id'] for p in personas_map.values()]
        channels_map = {}
        for channel in test_data['channels']:
            stored_channel = await test_store_channel(channel, workspace_id, ai_user_ids)
            channels_map[channel['name']] = stored_channel
            
            # Create initial messages for this channel
            if channel['name'] in test_data['initial_messages']:
                messages = await test_create_initial_messages(
                    stored_channel['$id'],
                    workspace_id,
                    test_data['initial_messages'][channel['name']],
                    personas_map
                )
        
        logger.info("All tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Test suite failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Load responses data
    with open('test_data/responses.json') as f:
        responses = json.load(f)
    
    # Run tests with responses data
    asyncio.run(run_tests())