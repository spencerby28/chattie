from aiohttp import web
import json
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from datetime import datetime, timedelta
import asyncio
import logging
import time
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import re
from bs4 import BeautifulSoup
import sys
from pathlib import Path

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

import langwatch
from langwatch.types import RAGChunk
# Configure LangWatch
langwatch.api_key = 'sk-lw-uaPp8Dsi4vJnQmpiZyJrtYBYDQmvdTUceW3PN6DxCyykeN4v'
langwatch.endpoint = "http://localhost:5560"

from monitoring.performance_logger import performance_metrics

# Set up logging for application (not performance metrics)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # Only log to console, not to file
    ]
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
    index_name='messages',
    embedding=embeddings
)
retriever = document_vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4o-mini")

async def get_persona(persona_id: str) -> dict:
    """Get persona information from Appwrite database"""
    try:
        persona = database.get_document(
            database_id='main',
            collection_id='ai_personas',
            document_id=persona_id
        )
        return persona
    except Exception as e:
        logger.error(f"Error getting persona {persona_id}: {str(e)}")
        return None

def sanitize_html_content(content: str) -> tuple[str, list[dict]]:
    """
    Sanitize HTML content and extract mentions.
    Returns (sanitized_text, mentions)
    """
    soup = BeautifulSoup(content, 'html.parser')
    mentions = []
    
    # Extract mentions
    for mention in soup.find_all('span', {'data-mention': 'true'}):
        mentions.append({
            'id': mention['data-mention-id'],
            'name': mention['data-mention-name']
        })
        # Replace mention with a text marker
        mention.replace_with(f"@{mention['data-mention-name']}")
    
    # Get plain text
    text = soup.get_text()
    
    # Clean up extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text, mentions

@langwatch.span(type="chain")
async def get_channel_messages(channel_id, limit=100):
    try:
        # Get all messages from the channel, sorted by timestamp
        docs = document_vectorstore.similarity_search(
            query="",  # Empty query to bypass similarity search
            k=limit,
            filter={
                "channel_id": channel_id,
            },
        )

        # Sort by timestamp
        docs.sort(key=lambda x: x.metadata['timestamp'])
        
        # Update the span with RAG context
        langwatch.get_current_span().update(
            contexts=[
                RAGChunk(
                    document_id=doc.metadata.get('sender_id', 'unknown'),
                    content=doc.page_content
                )
                for doc in docs
            ]
        )
        
        return docs
    except Exception as e:
        logger.error(f"Error retrieving channel messages: {e}")
        raise

async def send_private_message(user_id: str, content: str, workspace_id: str, channel_id: str):
    """
    Send a private message to a specific user using their user ID as the label permission.

    Args:
        user_id (str): The ID of the user to send the message to
        content (str): The message content
        workspace_id (str): The workspace ID the message belongs to

    Returns:
        dict: The created message document
    """
    try:
        message = {
            'channel_id': channel_id,  # Private messages don't have channel
            'workspace_id': workspace_id,
            'sender_type': 'bot',
            'sender_id': 'bot',
            'content': content,
            'sender_name': 'Chattie Bot',
            'edited_at': datetime.now().isoformat(),
        }

        response = database.create_document(
            database_id='main',
            collection_id='messages',
            document_id=ID.unique(),
            data=message,
            permissions=[
                Permission.read(Role.user(user_id)),
                Permission.write(Role.user('bot')),
                Permission.delete(Role.user('bot'))
            ]
        )

        logger.info(f"Sent private message to user {user_id}")
        return response

    except Exception as e:
        logger.error(f"Error sending private message to {user_id}: {str(e)}")
        raise

@langwatch.span(type="chain")
async def get_persona_context(mention_id: str, channel_id: str) -> dict:
    """Get persona information and relevant context for a mentioned persona"""
    try:
        # Get persona from database using the new function
        persona = await get_persona(mention_id)
        if not persona:
            return None
        
        # Get recent messages from this persona in the channel
        relevant_messages = document_vectorstore.similarity_search(
            query="",
            k=5,
            filter={
                "channel_id": channel_id,
                "sender_id": mention_id
            }
        )
        
        # Update the span with RAG context
        langwatch.get_current_span().update(
            contexts=[
                RAGChunk(
                    document_id=doc.metadata.get('sender_id', 'unknown'),
                    content=doc.page_content
                )
                for doc in relevant_messages
            ]
        )
        
        return {
            'persona': persona,
            'recent_messages': relevant_messages
        }
    except Exception as e:
        logger.error(f"Error getting persona context: {str(e)}")
        return None

@langwatch.span(type="chain")
async def handle_summarize_command(channel_id: str, user_id: str, workspace_id: str) -> str:
    """Handle /summarize command"""
    try:
        # Get last 100 messages from the channel
        with langwatch.get_current_span().span(type="rag") as rag_span:
            channel_docs = await get_channel_messages(channel_id)
            rag_span.update(
                contexts=[
                    RAGChunk(
                        document_id=doc.metadata.get('sender_id', 'unknown'),
                        content=doc.page_content
                    )
                    for doc in channel_docs
                ]
            )
        
        # Format messages chronologically
        messages_text = "\n".join([
            f"[{doc.metadata['timestamp']}] {doc.metadata['sender_name']}: {doc.page_content}"
            for doc in channel_docs
        ])
        
        # Create summarization prompt
        summary_prompt = PromptTemplate(
            template="""Please provide a concise summary of the following conversation, highlighting key points and decisions:

{messages}

Summary:""",
            input_variables=["messages"]
        )
        
        with langwatch.get_current_span().span(type="llm") as llm_span:
            summary_response = await llm.ainvoke(
                summary_prompt.format(messages=messages_text)
            )
            llm_span.update(
                model="gpt-4o-mini",
                input=messages_text,
                output=summary_response.content
            )
        
        return summary_response.content
    except Exception as e:
        logger.error(f"Error in summarize command: {str(e)}")
        return "Sorry, I encountered an error while trying to summarize the conversation."

@langwatch.span(type="chain")
async def handle_analyze_command(channel_id: str, user_id: str, workspace_id: str) -> str:
    """Handle /analyze command"""
    try:
        # Get last 100 messages from the channel
        with langwatch.get_current_span().span(type="rag") as rag_span:
            channel_docs = await get_channel_messages(channel_id)
            rag_span.update(
                contexts=[
                    RAGChunk(
                        document_id=doc.metadata.get('sender_id', 'unknown'),
                        content=doc.page_content
                    )
                    for doc in channel_docs
                ]
            )
        
        # Format messages chronologically
        messages_text = "\n".join([
            f"[{doc.metadata['timestamp']}] {doc.metadata['sender_name']}: {doc.page_content}"
            for doc in channel_docs
        ])
        
        # Create analysis prompt
        analysis_prompt = PromptTemplate(
            template="""Please analyze this conversation and provide insights on:
1. Main topics discussed
2. Key participants and their viewpoints
3. Areas of agreement and disagreement
4. Overall tone and engagement level
5. Any notable patterns or trends

Conversation:
{messages}

Analysis:""",
            input_variables=["messages"]
        )
        
        with langwatch.get_current_span().span(type="llm") as llm_span:
            analysis_response = await llm.ainvoke(
                analysis_prompt.format(messages=messages_text)
            )
            llm_span.update(
                model="gpt-4o-mini",
                input=messages_text,
                output=analysis_response.content
            )
        
        # Convert markdown style formatting to HTML tags
        content = analysis_response.content
        
        return content
    except Exception as e:
        logger.error(f"Error in analyze command: {str(e)}")
        return "<strong><i>Sorry, I encountered an error while trying to analyze the conversation.</i></strong>"

@langwatch.span(type="chain")
async def get_gpt4_response(prompt, channel_id, sender_id):
    try:
        start_time = time.time()

        # Get relevant context only from current channel
        with langwatch.get_current_span().span(type="rag") as rag_span:
            channel_context = retriever.get_relevant_documents(
                prompt,
                k=5,
                filter={
                    "channel_id": channel_id
                }
            )
            
            rag_span.update(
                contexts=[
                    RAGChunk(
                        document_id=doc.metadata.get('sender_id', 'unknown'),
                        content=doc.page_content
                    )
                    for doc in channel_context
                ]
            )

        logger.info(f"Context retrieval took {time.time() - start_time:.2f}s")

        # Create prompt template focusing on recent, relevant context with cynical Reddit-style tone
        template = PromptTemplate(
            template="""You are a cynical Reddit commenter. Your responses should be witty, sarcastic, and slightly condescending, while still being informative. You enjoy pointing out logical fallacies and making pop culture references. You start many sentences with "Actually..." and "Well, technically...". You occasionally use Reddit-style formatting like /s for sarcasm and FTFY (Fixed That For You).

Recent Thread Context:
{channel_context}

Respond to this comment in classic Reddit style: {query}

Remember to:
- Be cynical but not outright mean
- Include at least one snarky observation
- Reference a meme or pop culture if relevant
- Use typical Reddit phrases like "Source?" or "Username checks out"
- Point out any obvious logical fallacies
- Add /s if being particularly sarcastic""",
            input_variables=["query", "channel_context"]
        )

        prompt_with_context = template.format(
            query=prompt,
            channel_context="\n".join([f"{doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" 
                                     for doc in channel_context[-5:]])  # Only use last 5 messages
        )

        # Get response with higher temperature for more creative/snarky responses
        with langwatch.get_current_span().span(type="llm") as llm_span:
            llm_start = time.time()
            response = await llm.ainvoke(
                prompt_with_context, 
                temperature=0.8  # Increased temperature for more personality
            )
            logger.info(f"LLM response took {time.time() - llm_start:.2f}s")
            
            llm_span.update(
                model="gpt-4o-mini",
                input=prompt_with_context,
                output=response.content
            )

        return response.content

    except Exception as e:
        logger.error(f"Error getting GPT-4 response: {str(e)}")
        logger.exception(e)
        raise

@langwatch.span(type="chain")
async def get_persona_response(prompt: str, persona_context: dict, channel_id: str) -> str:
    """Generate a response from a specific persona"""
    try:
        # Get relevant channel context - combine persona history and relevant messages in one search
        with langwatch.get_current_span().span(type="rag") as rag_span:
            combined_context = retriever.get_relevant_documents(
                prompt,
                k=5,
                filter={
                    "channel_id": channel_id,
                    "$or": [
                        {"sender_id": persona_context['persona']['$id']}  # Persona's own messages
                    ]
                }
            )
            
            rag_span.update(
                contexts=[
                    RAGChunk(
                        document_id=doc.metadata.get('sender_id', 'unknown'),
                        content=doc.page_content
                    )
                    for doc in combined_context
                ]
            )
        
        # Separate persona's own messages from other context
        own_messages = []
        other_messages = []
        for doc in combined_context:
            if doc.metadata['sender_id'] == persona_context['persona']['$id']:
                own_messages.append(doc)
            else:
                other_messages.append(doc)
        
        # Create prompt template for persona response
        template = PromptTemplate(
            template="""You are {name}, {role}. Your personality is: {personality}
Your conversation style is: {conversation_style}
Your knowledge areas are: {knowledge_base}
Your opinions are: {opinions}
You disagree with: {disagreements}

Recent conversation context:
{channel_context}

Your own recent messages:
{own_messages}

Please respond to the following message in your unique voice and style briefly, maintaining your personality and viewpoints:
{prompt}""",
            input_variables=["name", "role", "personality", "conversation_style", "knowledge_base", 
                           "opinions", "disagreements", "channel_context", "own_messages", "prompt"]
        )

        # Format the prompt with persona information
        prompt_with_context = template.format(
            name=persona_context['persona']['name'],
            role=persona_context['persona']['role'],
            personality=persona_context['persona']['personality'],
            conversation_style=persona_context['persona']['conversation_style'],
            knowledge_base=", ".join(persona_context['persona']['knowledge_base']),
            opinions=", ".join(persona_context['persona'].get('opinions', [])),
            disagreements=", ".join(persona_context['persona'].get('disagreements', [])),
            channel_context="\n".join([f"{doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" 
                                     for doc in other_messages[-3:]]),  # Only use last 3 messages for context
            own_messages="\n".join([f"You: {doc.page_content}" 
                                  for doc in own_messages[-2:]]),  # Only use last 2 own messages
            prompt=prompt
        )

        # Get response
        with langwatch.get_current_span().span(type="llm") as llm_span:
            llm_start = time.time()
            response = await llm.ainvoke(prompt_with_context)
            logger.info(f"LLM response took {time.time() - llm_start:.2f}s")
            
            llm_span.update(
                model="gpt-4o-mini",
                input=prompt_with_context,
                output=response.content
            )

        return response.content

    except Exception as e:
        logger.error(f"Error getting persona response: {str(e)}")
        logger.exception(e)
        raise

def convert_context_to_json(context_list):
    """Convert context objects to JSON serializable format"""
    json_contexts = []
    for context in context_list:
        # Convert Document objects to dict representation
        if context.get('recent_messages'):
            messages = [{
                'content': doc.page_content,
                'metadata': doc.metadata
            } for doc in context['recent_messages']]
            context['recent_messages'] = messages
        json_contexts.append(context)
    return json_contexts

async def handle_message(request):
    try:
        data = await request.json()
        logger.info(f"Received message data: {data}")
        
        # Start tracking request with LangWatch
        with langwatch.trace() as trace:
            trace.update(
                metadata={
                    "user_id": data.get('sender_id'),
                    "channel_id": data.get('channel_id'),
                    "workspace_id": data.get('workspace_id')
                }
            )
            
            # Start tracking request
            request_start = time.time()
            
            # Sanitize HTML content and extract mentions
            content = data.get('content', '')
            clean_content, mentions = sanitize_html_content(content)
            
            # Handle commands
            if clean_content.startswith('/'):
                command = clean_content.split()[0].lower()
                response_content = None
                
                command_start = time.time()
                if command == '/summarize':
                    with trace.span(type="chain") as span:
                        response_content = await handle_summarize_command(
                            data['channel_id'],
                            data['sender_id'],
                            data['workspace_id']
                        )
                        span.update(output=response_content)
                elif command == '/analyze':
                    with trace.span(type="chain") as span:
                        response_content = await handle_analyze_command(
                            data['channel_id'],
                            data['sender_id'],
                            data['workspace_id']
                        )
                        span.update(output=response_content)
                
                if response_content:
                    await send_private_message(
                        user_id=data['sender_id'],
                        content=response_content,
                        workspace_id=data['workspace_id'],
                        channel_id=data['channel_id']
                    )
                    performance_metrics.add_operation_time('command_processing', time.time() - command_start)
                    return web.Response(text='Command processed successfully', status=200)
            
            # Skip embedding if the message is from the bot
            if data.get('sender_id') != 'bot':
                with trace.span(type="component") as span:
                    vector_start = time.time()
                    message_document = Document(
                        page_content=clean_content,
                        metadata={
                            'channel_id': data['channel_id'],
                            'workspace_id': data['workspace_id'],
                            'sender_id': data['sender_id'],
                            'sender_name': data['sender_name'],
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                    
                    # Add document with its embedding to Pinecone
                    document_vectorstore.add_documents([message_document])
                    span.update(input=clean_content)
                    performance_metrics.add_operation_time('vector_store', time.time() - vector_start)
            
            # Process mentions
            for mention in mentions:
                response_content = None
                mention_contexts = []
                
                llm_start = time.time()
                if mention['id'] == 'bot':
                    # Get context for all other mentions in the message
                    for other_mention in mentions:
                        if other_mention['id'] != 'bot':
                            context = await get_persona_context(
                                other_mention['id'],
                                data['channel_id']
                            )
                            if context:
                                mention_contexts.append(context)
                    
                    # Get GPT-4 response with enhanced context
                    with trace.span(type="llm", input=clean_content) as span:
                        response_content = await get_gpt4_response(
                            clean_content,
                            data['channel_id'],
                            data['sender_id']
                        )
                        span.update(output=response_content, model="gpt-4o-mini")
                else:
                    # Handle direct persona mention
                    persona_context = await get_persona_context(
                        mention['id'],
                        data['channel_id']
                    )
                    if persona_context:
                        mention_contexts = [persona_context]
                        with trace.span(type="llm", input=clean_content) as span:
                            response_content = await get_persona_response(
                                clean_content,
                                persona_context,
                                data['channel_id']
                            )
                            span.update(output=response_content, model="gpt-4o-mini")
                
                performance_metrics.add_operation_time('llm_processing', time.time() - llm_start)
                
                if response_content:
                    db_start = time.time()
                    # Store response in Pinecone
                    bot_message_document = Document(
                        page_content=response_content,
                        metadata={
                            'channel_id': data['channel_id'],
                            'workspace_id': data['workspace_id'],
                            'sender_id': mention['id'],
                            'sender_name': mention['name'],
                            'timestamp': datetime.now().isoformat()
                        }
                    )
                    document_vectorstore.add_documents([bot_message_document])
                    
                    # Convert context to JSON serializable format
                    json_contexts = convert_context_to_json(mention_contexts)
                    
                    # Create message document for Appwrite
                    message = {
                        'channel_id': data['channel_id'],
                        'workspace_id': data['workspace_id'],
                        'sender_type': 'ai',
                        'sender_id': mention['id'],
                        'content': response_content,
                        'sender_name': mention['name'],
                        'edited_at': datetime.now().isoformat(),
                        'mentions': [m['id'] for m in mentions],
                        'ai_context': json.dumps(json_contexts) if json_contexts else None,
                        'ai_prompt': clean_content,
                        'attachments': [],
                    }
                    
                    # Store response in database
                    response = database.create_document(
                        database_id='main',
                        collection_id='messages',
                        document_id=ID.unique(),
                        data=message,
                        permissions=[
                            Permission.read(Role.label(data['channel_id'])),
                            Permission.write(Role.user(mention['id'])),
                            Permission.delete(Role.user(mention['id']))
                        ]
                    )
                    performance_metrics.add_operation_time('db_operations', time.time() - db_start)
            
            # Track total request time
            total_time = time.time() - request_start
            performance_metrics.add_request_time(total_time)
            performance_metrics.add_operation_time('total_processing', total_time)
            
            return web.Response(text='Message processed successfully', status=200)
    
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        logger.exception(e)
        performance_metrics.log_error(type(e).__name__)
        if request.headers.get('User-Agent') == 'Appwrite-Server':
            return web.Response(text='OK', status=200)
        return web.Response(text=str(e), status=500)

async def main():
    app = web.Application()
    app.router.add_post('/', handle_message)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)

    logger.info("Bot server started at http://localhost:8000")
    
    # Start performance monitoring
    asyncio.create_task(performance_metrics.start_monitoring())
    
    await site.start()

    # Keep the server running
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())
