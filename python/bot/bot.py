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
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from monitoring.performance_logger import performance_metrics

# Load environment variables
load_dotenv()

# Set required environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")

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

async def get_persona_context(mention_id: str, channel_id: str) -> dict:
    """Get persona information and relevant context for a mentioned persona"""
    try:
        # Get persona from database using the new function
        persona = await get_persona(mention_id)
        if not persona:
            logger.warning(f"Could not find persona with ID {mention_id}")
            return None
        
        # Get recent messages from this persona in the channel
        relevant_messages = document_vectorstore.similarity_search(
            query="",
            k=5,
            filter={
                "channel_id": channel_id,
                "sender_id": mention_id,
                "sender_name": persona["name"] # Ensure messages match persona name
            }
        )
        
        # Validate that retrieved messages match the persona
        validated_messages = []
        for msg in relevant_messages:
            if (msg.metadata.get("sender_id") == mention_id and 
                msg.metadata.get("sender_name") == persona["name"]):
                validated_messages.append(msg)
            else:
                logger.warning(f"Found message with mismatched sender details for persona {mention_id}")
        
        return {
            'persona': persona,
            'recent_messages': validated_messages
        }
    except Exception as e:
        logger.error(f"Error getting persona context for {mention_id}: {str(e)}")
        return None

async def handle_summarize_command(channel_id: str, user_id: str, workspace_id: str) -> str:
    """Handle /summarize command"""
    try:
        # Get last 100 messages from the channel
        channel_docs = await get_channel_messages(channel_id)
        
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
        
        summary_response = await llm.ainvoke(
            summary_prompt.format(messages=messages_text)
        )
        
        return summary_response.content
    except Exception as e:
        logger.error(f"Error in summarize command: {str(e)}")
        return "Sorry, I encountered an error while trying to summarize the conversation."

async def handle_analyze_command(channel_id: str, user_id: str, workspace_id: str) -> str:
    """Handle /analyze command"""
    try:
        # Get last 100 messages from the channel
        channel_docs = await get_channel_messages(channel_id)
        
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
        
        analysis_response = await llm.ainvoke(
            analysis_prompt.format(messages=messages_text)
        )
        # Convert markdown style formatting to HTML tags
        content = analysis_response.content
        
        return content
    except Exception as e:
        logger.error(f"Error in analyze command: {str(e)}")
        return "<strong><i>Sorry, I encountered an error while trying to analyze the conversation.</i></strong>"

async def get_persona_response(prompt: str, persona_context: dict, channel_id: str, sender_name: str, sender_id: str) -> str:
    """Generate a response from a specific persona"""
    try:
        # Get relevant channel context - combine persona history and relevant messages in one search
        context_start = time.time()
        combined_context = retriever.get_relevant_documents(
            prompt,
            k=5,
            filter={
                "channel_id": channel_id,
                "$or": [
                    {"sender_id": persona_context['persona']['$id']}  # Persona's own messages
                  # Recent messages
                ]
            }
        )
        
        logger.info(f"Context retrieval took {time.time() - context_start:.2f}s")
        
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

You are responding to {sender_name} ({sender_id}).
Please respond to their following message in your unique voice and style briefly, maintaining your personality and viewpoints:
{prompt}""",
            input_variables=["name", "role", "personality", "conversation_style", "knowledge_base", 
                           "opinions", "disagreements", "channel_context", "own_messages", 
                           "sender_name", "sender_id", "prompt"]
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
            sender_name=sender_name,
            sender_id=sender_id,
            prompt=prompt
        )

        # Get response
        llm_start = time.time()
        response = await llm.ainvoke(prompt_with_context)
        logger.info(f"LLM response took {time.time() - llm_start:.2f}s")

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
                response_content = await handle_summarize_command(
                    data['channel_id'],
                    data['sender_id'],
                    data['workspace_id']
                )
            elif command == '/analyze':
                response_content = await handle_analyze_command(
                    data['channel_id'],
                    data['sender_id'],
                    data['workspace_id']
                )
            
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
                response_content = await get_gpt4_response(
                    clean_content,
                    data['workspace_id'],
                    data['sender_name'],
                    data['sender_id']
                )
            else:
                # Handle direct persona mention
                persona_context = await get_persona_context(
                    mention['id'],
                    data['channel_id']
                )
                if persona_context:
                    mention_contexts = [persona_context]
                    response_content = await get_persona_response(
                        clean_content,
                        persona_context,
                        data['channel_id'],
                        data['sender_name'],
                        data['sender_id']
                    )
            
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


async def get_channel_messages(channel_id, limit=100):
    try:
        # Get all messages from the channel, sorted by timestamp
        docs = document_vectorstore.similarity_search(
            query="",  # Empty query to bypass similarity search
            k=limit,
            filter={
                "channel_id": channel_id,
                # Optionally add time filter, e.g., last 24 hours
                # "timestamp": {"$gte": (datetime.now() - timedelta(days=1)).isoformat()}
            },
        )

        # Sort by timestamp
        docs.sort(key=lambda x: x.metadata['timestamp'])
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

async def get_gpt4_response(prompt, workspace_id, sender_name, sender_id):
    try:
        start_time = time.time()

        # Create a more focused query combining user context and prompt
        enhanced_query = f"Context from {sender_name} ({sender_id}): {prompt}"
        
        # Get relevant context only from current channel and last 24 hours
        context_start = time.time()
        channel_context = retriever.get_relevant_documents(
            enhanced_query,
            k=5,  # Increased number of relevant docs
            filter={
                "workspace_id": workspace_id,
                "$or": [
                    {"sender_id": sender_id},  # Get messages from this user
                ]
            }
        )

        logger.info(f"Context retrieval took {time.time() - context_start:.2f}s")

        # Create prompt template focusing on helpful responses with context
        template = PromptTemplate(
            template="""You are Chattie Bot, a helpful AI assistant. You are responding to {sender_name} (ID: {sender_id}).

Recent Thread Context:
{channel_context}

{sender_name}'s Current Query: {query}

When responding:
- Directly address {sender_name}
- Reference relevant points from their conversation history
- Provide clear, helpful information
- Stay focused on their specific question
- Be friendly and professional
- If the context shows previous interactions with {sender_name}, maintain continuity""",
            input_variables=["query", "channel_context", "sender_name", "sender_id"]
        )

        prompt_with_context = template.format(
            query=prompt,
            channel_context="\n".join([
                f"[{doc.metadata.get('timestamp', 'Unknown Time')}] {doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" 
                for doc in sorted(channel_context, key=lambda x: x.metadata.get('timestamp', ''))
            ]),
            sender_name=sender_name,
            sender_id=sender_id
        )

        # Get response with higher temperature for more creative/snarky responses
        llm_start = time.time()
        response = await llm.ainvoke(
            prompt_with_context, 
            temperature=0.8  # Increased temperature for more personality
        )
        logger.info(f"LLM response took {time.time() - llm_start:.2f}s")

        return response.content

    except Exception as e:
        logger.error(f"Error getting GPT-4 response: {str(e)}")
        logger.exception(e)
        raise


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
