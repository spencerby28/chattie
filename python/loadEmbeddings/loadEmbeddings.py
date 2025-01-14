import os
from dotenv import load_dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
import logging
from datetime import datetime
from appwrite.query import Query

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger('load_embeddings')

# Load environment variables
load_dotenv()

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
    index_name=os.getenv('PINECONE_INDEX2'),
    embedding=embeddings
)

def load_messages_to_pinecone():
    try:
        # Get all messages from Appwrite in chunks
        offset = 0
        limit = 100
        total_loaded = 0
        
        while True:
            # Get batch of messages
            queries = [
                Query.limit(limit),
                Query.offset(offset)
            ]
            
            messages = database.list_documents(
                database_id='main',
                collection_id='messages',
                queries=queries
            )
            
            if not messages['documents']:
                break
                
            # Convert messages to documents
            documents = []
            for msg in messages['documents']:
                # Convert timestamp to ISO format string if it exists
                timestamp = msg.get('edited_at')
                if timestamp:
                    timestamp = datetime.fromisoformat(timestamp).isoformat()
                
                doc = Document(
                    page_content=msg['content'],
                    metadata={
                        'channel_id': msg['channel_id'],
                        'workspace_id': msg['workspace_id'],
                        'sender_id': msg['sender_id'],
                        'sender_name': msg['sender_name'],
                        'timestamp': timestamp or ''  # Use empty string if no timestamp
                    }
                )
                documents.append(doc)
            
            # Add documents to Pinecone
            document_vectorstore.add_documents(documents)
            
            total_loaded += len(documents)
            logger.info(f"Loaded {len(documents)} messages into Pinecone. Total: {total_loaded}")
            
            # Update offset for next batch
            offset += limit
            
        logger.info(f"Completed loading {total_loaded} messages into Pinecone")
    except Exception as e:
        logger.error(f"Error loading messages: {str(e)}")
        raise

if __name__ == "__main__":
    load_messages_to_pinecone()
