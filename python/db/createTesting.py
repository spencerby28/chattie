import asyncio
import time
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('message_perf.log')
    ]
)
logger = logging.getLogger('message_perf')

# Load environment variables
load_dotenv()

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('CHATTIE_PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('CHATTIE_APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('CHATTIE_APPWRITE_API_KEY'))

# Initialize Database service
databases = Databases(client)

DATABASE_ID = 'main'
MESSAGES_COLLECTION = 'messages'

async def create_test_message(workspace_id: str, channel_id: str, sender_id: str):
    """Create a single test message and return creation time"""
    message_data = {
        'channel_id': channel_id,
        'workspace_id': workspace_id,
        'sender_type': 'user',
        'sender_id': sender_id,
        'content': 'This is a test message for performance testing',
        'sender_name': 'Test User',
        'mentions': [],
        'attachments': []
    }

    start_time = time.time()
    
    try:
        message = databases.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            document_id=ID.unique(),
            data=message_data,
            permissions=[
                Permission.read(Role.users()),
                Permission.update(Role.user(sender_id)),
                Permission.delete(Role.user(sender_id))
            ]
        )
        end_time = time.time()
        return end_time - start_time
    except Exception as e:
        logger.error(f"Error creating message: {str(e)}")
        raise

async def run_performance_test(num_messages: int = 100):
    """Run performance test creating multiple messages"""
    test_workspace_id = "test_workspace"
    test_channel_id = "test_channel"
    test_sender_id = "test_user"
    
    creation_times = []
    logger.info(f"Starting performance test - creating {num_messages} messages")
    
    for i in range(num_messages):
        try:
            creation_time = await create_test_message(
                test_workspace_id,
                test_channel_id,
                test_sender_id
            )
            creation_times.append(creation_time)
            logger.info(f"Message {i+1}/{num_messages} created in {creation_time:.3f} seconds")
        except Exception as e:
            logger.error(f"Failed to create message {i+1}: {str(e)}")
    
    avg_time = sum(creation_times) / len(creation_times)
    min_time = min(creation_times)
    max_time = max(creation_times)
    
    logger.info("Performance Test Results:")
    logger.info(f"Total messages created: {len(creation_times)}")
    logger.info(f"Average creation time: {avg_time:.3f} seconds")
    logger.info(f"Minimum creation time: {min_time:.3f} seconds")
    logger.info(f"Maximum creation time: {max_time:.3f} seconds")
    logger.info(f"Messages per second: {1/avg_time:.2f}")

if __name__ == "__main__":
    asyncio.run(run_performance_test())
