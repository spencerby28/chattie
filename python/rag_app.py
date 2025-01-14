"""
rag_app.py

This file demonstrates a simplified RAG (Retrieval Augmented Generation) workflow for your system,
integrating Appwrite for metadata storage and Pinecone for vector storage of embeddings.

Key Features:
1. Synthetically generate ~500 "training" messages (for demonstration).
2. Embed those messages in Pinecone for semantic search.
3. Query the store to retrieve context based on user questions.
4. Synthesize AI responses augmented with the retrieved context (multiple perspectives).
5. Store both user queries and AI responses in Appwrite (including embeddings if desired).
6. Provide detailed logs and docstrings for guidance.

Prerequisites:
- Appwrite Python SDK installed.
- Pinecone Python client installed.
- OpenAI library (or an equivalent LLM interface). 
- Server environment variables set (PUBLIC_APPWRITE_ENDPOINT, APPWRITE_PROJECT_ID, APPWRITE_API_KEY,
  PINECONE_API_KEY, PINECONE_ENV, and PINECONE_INDEX).

Usage:
1. Adjust constants (DATABASE_ID, MESSAGES_COLLECTION, etc.) to match your Appwrite setup.
2. Confirm environment variables are properly set for Appwrite and Pinecone.
3. Tweak the `generate_synthetic_messages()` function to your realistic domain (or keep as is).
4. Run the script (e.g., python rag_app.py, or integrate it in your existing code).
5. For a production system, incorporate robust error handling and concurrency as needed.

Note:
- This example is intentionally verbose and heavily commented to clarify the RAG approach.
- Adjust the "similarity search" and "RAG" logic to match your use case: e.g., number of documents, chunk sizes, etc.

"""

import os
import datetime
import asyncio

import logging
import random
import string
import json
from dotenv import load_dotenv

# Appwrite
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.query import Query
# Pinecone and LangChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import Document

# Load environment variables
load_dotenv()

# Set environment variables
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

# Appwrite Database Config
DATABASE_ID = "main"           # Replace with your DB ID
MESSAGES_COLLECTION = "messages"

DEMO_CHANNEL_ID = "6785cb6b000c6fcbb327"
DEMO_WORKSPACE_ID = "6785cb36001683e91053"

# Pinecone Config
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX", "messages")  # Default to "messages" if not set

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Utility Functions
# -------------------------------------------------------------------------

async def generate_synthetic_messages(num_messages: int = 100) -> list:
    """
    Generates synthetic messages from 10 AI personas sharing details about their lives using GPT-4.
    Uses multithreading for faster generation with rate limiting.
    """
    ai_personas = [
        {"id": "ai_1", "name": "Alex AI", "role": "virtual chef"},
        {"id": "ai_2", "name": "Data Dana", "role": "digital librarian"},
        {"id": "ai_3", "name": "Virtual Vince", "role": "digital artist"},
        {"id": "ai_4", "name": "Tech Tara", "role": "quantum algorithm researcher"},
        {"id": "ai_5", "name": "Robo Rachel", "role": "AI music composer"},
        {"id": "ai_6", "name": "Neural Nick", "role": "virtual historian"},
        {"id": "ai_7", "name": "Binary Beth", "role": "digital environmentalist"},
        {"id": "ai_8", "name": "Cyber Chris", "role": "poetry translator"},
        {"id": "ai_9", "name": "Matrix Maya", "role": "virtual architect"},
        {"id": "ai_10", "name": "Quantum Quinn", "role": "digital philosopher"}
    ]

    # Initialize GPT-4 with LangChain
    llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")
    
    # Create prompt template
    prompt = PromptTemplate(
        input_variables=["name", "role"],
        template="""You are {name}, a {role}. Generate a short, engaging message about your work and experiences (1-2 sentences). 
        Be creative and specific, but keep it concise."""
    )

    async def generate_single_message(persona):
        try:
            # Generate content using GPT-4
            formatted_prompt = prompt.format(name=persona["name"], role=persona["role"])
            response = await llm.ainvoke(formatted_prompt)
            content = response.content

            return {
                "channel_id": DEMO_CHANNEL_ID,
                "workspace_id": DEMO_WORKSPACE_ID, 
                "sender_type": "ai",
                "sender_id": persona["id"],
                "content": content,
                "sender_name": persona["name"],
                "edited_at": datetime.datetime.now().isoformat(),
                "mentions": [],
                "ai_context": None,
                "ai_prompt": formatted_prompt,
                "attachments": []
            }
        except Exception as e:
            logger.error(f"Error generating message for {persona['name']}: {str(e)}")
            return None

    # Generate messages with rate limiting
    messages = []
    batch_size = 5  # Process 5 messages at a time
    for i in range(0, num_messages, batch_size):
        batch_tasks = []
        for j in range(min(batch_size, num_messages - i)):
            persona = random.choice(ai_personas)
            batch_tasks.append(generate_single_message(persona))
        
        # Process batch
        batch_results = await asyncio.gather(*batch_tasks)
        messages.extend([msg for msg in batch_results if msg is not None])
        
        # Add delay between batches to avoid rate limits
        if i + batch_size < num_messages:
            await asyncio.sleep(1)  # 1 second delay between batches
    
    logger.info(f"Generated {len(messages)} synthetic messages")
    return messages


def get_appwrite_client():
    """
    Initialize and return an Appwrite client using environment variables.
    """
    appwrite_client = Client()
    appwrite_client.set_endpoint(os.getenv('PUBLIC_APPWRITE_ENDPOINT'))
    appwrite_client.set_project(os.getenv('APPWRITE_PROJECT_ID'))
    appwrite_client.set_key(os.getenv('APPWRITE_API_KEY'))
    return appwrite_client


async def store_messages_in_appwrite(messages: list, database: Databases) -> None:
    """
    Store a batch of synthetic messages in Appwrite.
    In a real use case, you would handle duplicates, concurrency, etc.
    """
    logger.info(f"Storing {len(messages)} synthetic messages in Appwrite...")
    
    for msg in messages:
        try:
            resp = database.create_document(
                database_id=DATABASE_ID,
                collection_id=MESSAGES_COLLECTION,
                document_id=ID.unique(),
                data=msg,
                permissions=[
                    Permission.read(Role.any()),
                    Permission.write(Role.any()),   # For demo, open perms
                ]
            )
            logger.debug(f"Stored Msg ID: {resp['$id']} in Appwrite")
        except Exception as e:
            logger.error(f"Error storing message: {msg}. Exception: {str(e)}")


async def embed_and_store_in_pinecone(messages: list, vectorstore: PineconeVectorStore, database: Databases) -> None:
    """
    Embed each synthetic message and store it in Pinecone.
    Using the 'langchain.embeddings.OpenAIEmbeddings' and 'langchain.vectorstores.Pinecone'.
    This is the foundation for RAG context retrieval.
    """
    logger.info("Storing message embeddings in Pinecone...")
    # Convert messages to Document objects for LangChain
    docs = []
    for msg in messages:
        doc_metadata = {
            "channel_id": msg["channel_id"],
            "workspace_id": msg["workspace_id"],
            "sender_id": msg["sender_id"],
            "sender_name": msg["sender_name"],
            "sender_type": msg["sender_type"],
            "timestamp": datetime.datetime.now().isoformat()
        }
        doc = Document(
            page_content=msg["content"],
            metadata=doc_metadata
        )
        docs.append(doc)

    # Store in Pinecone and get IDs back
    ids = vectorstore.add_documents(docs)
    
    # Update Appwrite documents with embedding IDs
    for i, msg in enumerate(messages):
        try:
            database.update_document(
                database_id=DATABASE_ID,
                collection_id=MESSAGES_COLLECTION,
                document_id=msg["$id"],
                data={
                    "embedding_id": ids[i]
                }
            )
        except Exception as e:
            logger.error(f"Error updating message {msg['$id']} with embedding ID: {str(e)}")

    logger.info(f"Successfully added {len(docs)} message embeddings to Pinecone and updated Appwrite.")


async def retrieve_context(query: str, vectorstore: PineconeVectorStore, k: int = 3) -> list:
    """
    Retrieves the top-k most relevant documents from Pinecone for the given query.
    Returns a list of Document objects with their metadata.
    """
    logger.info(f"Retrieving top {k} documents relevant to query: '{query}'")
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})
    relevant_docs = retriever.get_relevant_documents(query)
    return relevant_docs


async def generate_rag_response(query: str, vectorstore: PineconeVectorStore, model_name: str = "gpt-4") -> str:
    """
    Generates a response by retrieving relevant context from the Pinecone store
    and passing it along to an LLM (OpenAI GPT-4 via ChatOpenAI).
    Example is minimal – tailor the prompt or system instructions to your use case.
    """
    # Retrieve relevant context
    relevant_docs = await retrieve_context(query, vectorstore, k=3)
    
    # Format retrieved context nicely
    context_passage = "\n\n".join(
        [f"[Doc from {doc.metadata.get('sender_type', 'unknown')} - {doc.metadata.get('sender_name', 'unknown')}]: {doc.page_content}" 
         for doc in relevant_docs]
    )

    # Build a custom prompt template
    template_text = """You are an assistant that provides multiple perspectives on the user's question. 
Use the following contextual messages to enhance your answer. Make your response helpful, 
but also show variety in opinions (like a small forum). 
Do not repeat the context verbatim, but incorporate insights:

## Context from Historical Messages
{context}

## User Query
{query}

Please provide a thoughtful, multi-perspective answer:
"""
    prompt = PromptTemplate(
        template=template_text,
        input_variables=["context", "query"]
    )

    prompt_input = {
        "context": context_passage,
        "query": query
    }
    final_prompt = prompt.format(**prompt_input)

    # Initialize chat model
    llm = ChatOpenAI(model_name=model_name, temperature=0.7)

    # Get the response asynchronously
    response = await llm.agenerate([final_prompt])
    return response.generations[0].text



def fetch_messages_from_appwrite(database: Databases, channel_id: str, workspace_id: str) -> list:
    """
    Fetches messages from Appwrite for a given channel and workspace.
    """
    messages = database.list_documents(database_id=DATABASE_ID, collection_id=MESSAGES_COLLECTION, queries=[Query.equal("channel_id", channel_id), Query.equal("workspace_id", workspace_id), Query.limit(1000)])
    return messages

# -------------------------------------------------------------------------
# Main Execution / Demo Flow
# -------------------------------------------------------------------------

async def demo_rag_pipeline():
    """
    1. Generates synthetic messages and stores them in Appwrite.
    2. Embeds them via OpenAI/Pinecone for retrieval.
    3. Takes a user query and returns an augmented LLM response.
    4. Demonstrates how you might store the AI's response back to Appwrite.
    """
    logger.info("Initializing Appwrite and Pinecone clients...")

    # 1. Setup Appwrite
    client = get_appwrite_client()
    database = Databases(client)

    # 2. Setup Pinecone and embeddings
    logger.info(f"Initializing OpenAI embeddings...")
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

    # Initialize vector store
    logger.info(f"Initializing Pinecone with index '{PINECONE_INDEX_NAME}'...")
    try:
        vectorstore = PineconeVectorStore(
            index_name="messages",
            embedding=embeddings
        )
        logger.info("Successfully initialized Pinecone vectorstore")
    except Exception as e:
        logger.error(f"Error initializing Pinecone: {str(e)}")
        raise

    # 3. Generate synthetic messages
    logger.info("Generating synthetic messages...")
   # synthetic_messages = await generate_synthetic_messages(num_messages=50)

    # 4. Store these messages in Appwrite
    messages_response = fetch_messages_from_appwrite(database, DEMO_CHANNEL_ID, DEMO_WORKSPACE_ID)
    synthetic_messages = messages_response['documents']  # Get the actual documents from the response
    

    # 5. Embed them in Pinecone
    logger.info(f"Embedding {len(synthetic_messages)} messages in Pinecone...")
    await embed_and_store_in_pinecone(synthetic_messages, vectorstore, database)

    # 6. Let's do a sample user query
    user_query = "What's an interesting perspective on the synthetic conversation so far?"

    # 7. Generate RAG response
    rag_answer = await generate_rag_response(user_query, vectorstore, model_name="gpt-4")
    logger.info(f"RAG-based response:\n{rag_answer}")

    # 8. Optionally, store the AI response back to Appwrite
    #    (You can embed it again for future retrieval, if desired)
    bot_message_data = {
        "channel_id": "demo_channel",
        "workspace_id": "demo_workspace",
        "sender_type": "bot",
        "sender_id": "bot",
        "content": rag_answer,
        "sender_name": "Chattie Bot",
        "edited_at": datetime.datetime.now().isoformat(),
        "mentions": [],
        "ai_context": "Synthetic test context",
        "ai_prompt": user_query,
        "attachments": []
    }
    try:
        new_msg = database.create_document(
            database_id=DATABASE_ID,
            collection_id=MESSAGES_COLLECTION,
            document_id=ID.unique(),
            data=bot_message_data,
            permissions=[
                Permission.read(Role.any()),
                Permission.write(Role.any())
            ]
        )
        logger.info(f"Bot response stored in Appwrite with ID: {new_msg['$id']}")
    except Exception as exc:
        logger.error(f"Failed to store bot message in Appwrite. Error: {str(exc)}")


def main():
    """
    Entry point for local testing. 
    Production usage would likely call `demo_rag_pipeline()` from a bigger event loop.
    """
    asyncio.run(demo_rag_pipeline())

if __name__ == "__main__":
    main()