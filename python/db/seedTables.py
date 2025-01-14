from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
import os
from dotenv import load_dotenv
import datetime

# Load environment variables
load_dotenv()

# Initialize Appwrite Client
client = Client()
client.set_endpoint(os.getenv('CHATTIE_PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('CHATTIE_APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('CHATTIE_APPWRITE_API_KEY'))

# Initialize Database service
databases = Databases(client)

# Database and Collection IDs
DATABASE_ID = 'main'
WORKSPACES_COLLECTION = 'workspaces'
CHANNELS_COLLECTION = 'channels'
MESSAGES_COLLECTION = 'messages'
AI_PERSONAS_COLLECTION = 'ai_personas'
MESSAGE_THREADS_COLLECTION = 'message_threads'
ATTACHMENTS_COLLECTION = 'attachments'
REACTIONS_COLLECTION = 'reactions'
PRESENCE_COLLECTION = 'presence'

def create_collections():
    """Create all necessary collections with appropriate attributes"""
    try:
        # Create Workspaces Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=WORKSPACES_COLLECTION,
            name='Workspaces',
        )
        
        # Workspace Attributes
        databases.create_string_attribute(DATABASE_ID, WORKSPACES_COLLECTION, 'name', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, WORKSPACES_COLLECTION, 'owner_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, WORKSPACES_COLLECTION, 'ai_persona', 255, required=False)
        databases.create_integer_attribute(DATABASE_ID, WORKSPACES_COLLECTION, 'message_frequency', required=False)
        databases.create_string_attribute(DATABASE_ID, WORKSPACES_COLLECTION, 'members', 255, required=True, array=True)

        # Create Channels Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=CHANNELS_COLLECTION,
            name='Channels',
        )
        
        # Channel Attributes
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'workspace_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'name', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'type', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'members', 255, required=True, array=True)
        databases.create_datetime_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'last_message_at', required=False)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'description', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'purpose', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'topics', 255, required=False, array=True)
        databases.create_string_attribute(DATABASE_ID, CHANNELS_COLLECTION, 'primary_personas', 255, required=False, array=True)

        # Create Messages Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            name='Messages',
        )
        
        # Message Attributes
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'channel_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'workspace_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'sender_type', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'sender_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'content', 65535, required=True)
        databases.create_datetime_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'edited_at', required=False)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'mentions', 255, required=False, array=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'ai_context', 65535, required=False)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'ai_prompt', 65535, required=False)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'sender_name', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'thread_id', 255, required=False)
        databases.create_integer_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'thread_count', required=False)
        databases.create_string_attribute(DATABASE_ID, MESSAGES_COLLECTION, 'attachments', 255, required=False, array=True)

        # Create AI Personas Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=AI_PERSONAS_COLLECTION,
            name='AI Personas',
        )
        
        # AI Persona Attributes
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'workspace_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'name', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'personality', 65535, required=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'avatar_url', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'conversation_style', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'knowledge_base', 255, required=False, array=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'greeting', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'role', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'opinions', 255, required=False, array=True)
        databases.create_string_attribute(DATABASE_ID, AI_PERSONAS_COLLECTION, 'ai_user_id', 255, required=False)

        # Create Message Threads Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=MESSAGE_THREADS_COLLECTION,
            name='Message Threads',
        )
        
        # Message Thread Attributes
        databases.create_string_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'parent_message_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'channel_id', 255, required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'workspace_id', 255, required=True)
        databases.create_datetime_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'last_reply_at', required=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'participant_ids', 255, required=True, array=True)
        databases.create_string_attribute(DATABASE_ID, MESSAGE_THREADS_COLLECTION, 'ai_participants', 255, required=False, array=True)

        # Create Attachments Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=ATTACHMENTS_COLLECTION,
            name='Attachments',
        )

        # Attachments Attributes
        databases.create_string_attribute(DATABASE_ID, ATTACHMENTS_COLLECTION, 'type', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, ATTACHMENTS_COLLECTION, 'url', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, ATTACHMENTS_COLLECTION, 'name', 255, required=False)
        databases.create_integer_attribute(DATABASE_ID, ATTACHMENTS_COLLECTION, 'size', required=False)
        databases.create_string_attribute(DATABASE_ID, ATTACHMENTS_COLLECTION, 'message_id', 255, required=False)

        # Create Reactions Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=REACTIONS_COLLECTION,
            name='Reactions',
        )

        # Reactions Attributes
        databases.create_string_attribute(DATABASE_ID, REACTIONS_COLLECTION, 'emoji', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, REACTIONS_COLLECTION, 'message_id', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, REACTIONS_COLLECTION, 'user_id', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, REACTIONS_COLLECTION, 'user_name', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, REACTIONS_COLLECTION, 'channel_id', 255, required=False)

        # Create Presence Collection
        databases.create_collection(
            database_id=DATABASE_ID,
            collection_id=PRESENCE_COLLECTION,
            name='Presence',
        )

        # Presence Attributes
        databases.create_string_attribute(DATABASE_ID, PRESENCE_COLLECTION, 'userId', 255, required=True)
        databases.create_datetime_attribute(DATABASE_ID, PRESENCE_COLLECTION, 'lastSeen', required=False)
        databases.create_string_attribute(DATABASE_ID, PRESENCE_COLLECTION, 'workspaceId', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, PRESENCE_COLLECTION, 'baseStatus', 255, required=False)
        databases.create_string_attribute(DATABASE_ID, PRESENCE_COLLECTION, 'customStatus', 255, required=False)

        print("Successfully created all collections and attributes!")

    except Exception as e:
        print(f"Error creating collections: {str(e)}")

def seed_sample_data(owner_id: str):
    """Seed some sample data for testing"""
    try:
        # Create a workspace
        workspace = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=WORKSPACES_COLLECTION,
            document_id=ID.unique(),
            data={
                'name': 'Sample Workspace',
                'owner_id': owner_id,
                'ai_persona': 'friendly_assistant',
                'message_frequency': 5,
                'members': [owner_id]
            }
        )

        # Create a general channel
        channel = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=CHANNELS_COLLECTION,
            document_id=ID.unique(),
            data={
                'workspace_id': workspace['$id'],
                'name': 'general',
                'type': 'public',
                'members': [owner_id],
                'last_message_at': datetime.datetime.now().isoformat(),
                'description': 'General discussion channel',
                'purpose': 'Team-wide communication',
                'topics': ['general', 'announcements'],
                'primary_personas': []
            }
        )

        # Create an AI persona
        ai_persona = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=AI_PERSONAS_COLLECTION,
            document_id=ID.unique(),
            data={
                'workspace_id': workspace['$id'],
                'name': 'Friendly Assistant',
                'personality': 'Helpful and friendly AI assistant',
                'avatar_url': 'https://example.com/avatar.png',
                'conversation_style': 'casual',
                'knowledge_base': ['general', 'tech', 'productivity'],
                'greeting': 'Hello! How can I help you today?',
                'role': 'General Assistant',
                'opinions': ['Productivity is important', 'Teamwork makes the dream work'],
                'ai_user_id': 'ai_assistant_1'
            }
        )

        # Create a welcome message
        message = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            document_id=ID.unique(),
            data={
                'channel_id': channel['$id'],
                'workspace_id': workspace['$id'],
                'sender_type': 'ai',
                'sender_id': ai_persona['$id'],
                'content': 'Welcome to your new workspace! I\'m here to help you get started.',
                'mentions': [owner_id],
                'ai_context': 'workspace_creation',
                'ai_prompt': 'Generate a friendly welcome message',
                'sender_name': ai_persona['name'],
                'attachments': []
            }
        )

        print("Successfully seeded sample data!")
        return workspace['$id']

    except Exception as e:
        print(f"Error seeding data: {str(e)}")
        return None

if __name__ == "__main__":
    # First create all collections
    create_collections()
    
    # Then seed with sample data (replace with actual owner ID)
    owner_id = "user123"  # Replace with actual user ID when testing
    workspace_id = seed_sample_data(owner_id)
    
    if workspace_id:
        print(f"Created workspace with ID: {workspace_id}")
