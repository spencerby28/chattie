from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

def embed_message(message):
    """
    Embeds a chat message into the vector database
    
    Args:
        message (dict): Message object containing content, channel_id, sender_id and workspace_id
    """
    logger.info(f"Processing message from sender {message['sender_id']} in channel {message['channel_id']}")
    
    # Create document with metadata
    document = {
        "page_content": message["content"],
        "metadata": {
            "channel_id": message["channel_id"],
            "workspace_id": message["workspace_id"], 
            "sender_id": message["sender_id"]
        }
    }
    logger.debug(f"Created document with metadata: {document['metadata']}")

    # Initialize embeddings model
    logger.debug("Initializing OpenAI embeddings model")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Split content if needed
    logger.debug("Splitting content into chunks")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    documents = text_splitter.create_documents([document["page_content"]], metadatas=[document["metadata"]])
    logger.debug(f"Split into {len(documents)} chunks")

    # Store in Pinecone
    logger.info("Storing embeddings in Pinecone")
    try:
        PineconeVectorStore.from_documents(documents=documents, embedding=embeddings, index_name=PINECONE_INDEX)
        logger.info("Successfully stored embeddings in Pinecone")
    except Exception as e:
        logger.error(f"Failed to store embeddings in Pinecone: {str(e)}")
        raise
