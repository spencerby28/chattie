import asyncio
import os
from datetime import datetime
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from bot import bot2, bot3
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Appwrite client
client = Client()
client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
client.set_key(os.getenv('APPWRITE_API_KEY'))

# Initialize database service
database = Databases(client)

# Initialize LangChain components
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
document_vectorstore = PineconeVectorStore(
    index_name=os.getenv('PINECONE_INDEX'),
    embedding=embeddings
)

async def store_message(channel_id, sender_id, content, sender_name):
    """Store a message in the database and vector store"""
    try:
        # Create message document
        message = {
            'channel_id': channel_id,
            'workspace_id': 'default',
            'sender_type': 'ai_persona',
            'sender_id': sender_id,
            'content': content,
            'sender_name': sender_name,
            'edited_at': datetime.now().isoformat(),
            'mentions': [],
            'ai_context': None,
            'ai_prompt': None,
            'attachments': [],
        }
        
        # Store in database
        response = database.create_document(
            database_id='main',
            collection_id='messages',
            document_id=ID.unique(),
            data=message,
            permissions=[
                Permission.read(Role.label(channel_id)),
                Permission.write(Role.user(sender_id)),
                Permission.delete(Role.user(sender_id))
            ]
        )
        
        # Store in vector database
        message_document = Document(
            page_content=content,
            metadata={
                'channel_id': channel_id,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'timestamp': datetime.now().isoformat()
            }
        )
        document_vectorstore.add_documents([message_document])
        
        return response
        
    except Exception as e:
        logger.error(f"Error storing message: {str(e)}")
        raise

async def start_conversation(channel_id="67859ec30006b3c8fda3"):
    """Start a conversation between DogDevotee_Danny and CatChampion_Carol"""
    try:
        # Initial message from Danny
        initial_content = "Hey there! I've been thinking about this whole pets debate. You know what makes dogs absolutely amazing? Their unconditional love and loyalty. No other pet comes close, especially not cats who just use humans for food and shelter! What's your take on this, @CatChampion_Carol?"
        
        await store_message(
            channel_id=channel_id,
            sender_id="67859ee10021a3dcccbe",  # Danny's ID
            content=initial_content,
            sender_name="DogDevotee_Danny"
        )
        
        previous_messages = [initial_content]
        
        # Start conversation loop
        while True:
            # Carol's turn
            carol_response = await bot3.generate_response(
                previous_messages[-1],
                channel_id,
                previous_messages[-5:] if len(previous_messages) > 5 else previous_messages
            )
            
            await store_message(
                channel_id=channel_id,
                sender_id="67859ee10025dcb847f0",  # Carol's ID
                content=carol_response,
                sender_name="CatChampion_Carol"
            )
            
            previous_messages.append(carol_response)
            await asyncio.sleep(2)  # Natural conversation pacing
            
            # Danny's turn
            danny_response = await bot2.generate_response(
                previous_messages[-1],
                channel_id,
                previous_messages[-5:] if len(previous_messages) > 5 else previous_messages
            )
            
            await store_message(
                channel_id=channel_id,
                sender_id="67859ee10021a3dcccbe",  # Danny's ID
                content=danny_response,
                sender_name="DogDevotee_Danny"
            )
            
            previous_messages.append(danny_response)
            await asyncio.sleep(2)  # Natural conversation pacing

    except Exception as e:
        logger.error(f"Error in conversation: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(start_conversation()) 