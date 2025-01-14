import logging
import random
from typing import Dict, Any, List
from ..core.llm import generate_with_llm
from .creator import create_message
from ..embeddings import embed_message
from langchain_openai import ChatOpenAI
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings

logger = logging.getLogger('chattie_agent')

async def start_conversation(
    databases: Any,
    channel: Dict[str, Any],
    workspace_id: str,
    personas: List[Dict[str, Any]],
    api_key: str
) -> Dict[str, Any]:
    """Start a new conversation in a channel"""
    # Select a random persona from all available personas
    starter_persona = random.choice(personas)
    
    # Generate initial message based on channel topics and persona beliefs
    prompt = f"""You are {starter_persona['name']}, with the following beliefs and traits:
{starter_persona['description']}
{starter_persona['beliefs']}

You are starting a conversation in a channel about: {channel['description']}
The key topics for discussion are: {', '.join(channel['topics'])}
Some controversial debate topics include: {', '.join(channel['debate_topics'])}

Write a message to start a meaningful discussion that aligns with your persona's beliefs and the channel's purpose.
Keep it under 2000 characters and make it provocative enough to encourage responses.
"""
    
    message_content = await generate_with_llm(prompt, api_key)
    
    # Create the message in the database
    message = await create_message(
        databases=databases,
        channel_id=channel['$id'],
        workspace_id=workspace_id,
        content=message_content,
        sender_id=starter_persona['ai_user_id']
    )
    
    # Add message to vector store for context
    await embed_message(message)
    
    return message

async def generate_response(
    databases: Any,
    channel: Dict[str, Any],
    workspace_id: str,
    message: Dict[str, Any],
    personas: List[Dict[str, Any]],
    api_key: str
) -> Dict[str, Any]:
    """Generate a response to a message"""
    # Get context from vector store
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    vectorstore = PineconeVectorStore(
        index_name=os.getenv("PINECONE_INDEX"),
        embedding=embeddings
    )
    
    # Get relevant message history
    context_docs = vectorstore.similarity_search(
        message['content'],
        k=5,
        filter={
            "channel_id": channel['$id'],
            "workspace_id": workspace_id
        }
    )
    context = "\n".join([doc.page_content for doc in context_docs])
    
    # Select a random persona to respond (excluding the sender)
    available_personas = [
        p for p in personas 
        if p['ai_user_id'] != message['sender_id']
    ]
    
    responder = random.choice(available_personas)
    
    # Generate response based on context and persona
    prompt = f"""You are {responder['name']}, with the following beliefs and traits:
{responder['description']}
{responder['beliefs']}

You are responding to a message in a channel about: {channel['description']}
The key topics for discussion are: {', '.join(channel['topics'])}

Recent conversation context:
{context}

Most recent message:
{message['content']}

Write a response that:
1. Aligns with your persona's beliefs
2. Engages meaningfully with the previous message
3. Keeps the conversation focused on the channel's purpose
4. Encourages further discussion
Keep it under 2000 characters.
"""
    
    response_content = await generate_with_llm(prompt, api_key)
    
    # Create the response message
    response = await create_message(
        databases=databases,
        channel_id=channel['$id'],
        workspace_id=workspace_id,
        content=response_content,
        sender_id=responder['ai_user_id']
    )
    
    # Add response to vector store
    await embed_message(response)
    
    return response 