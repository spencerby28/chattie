from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from appwrite.exception import AppwriteException
import os
import json
from datetime import datetime, timedelta
import logging
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import re
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize LangChain components
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
document_vectorstore = PineconeVectorStore(
    index_name='messages',
    embedding=embeddings
)
retriever = document_vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4-turbo-preview")

def sanitize_html_content(content: str) -> tuple[str, list[dict]]:
    """Sanitize HTML content and extract mentions."""
    soup = BeautifulSoup(content, 'html.parser')
    mentions = []
    
    # Extract mentions
    for mention in soup.find_all('span', {'data-mention': 'true'}):
        mentions.append({
            'id': mention['data-mention-id'],
            'name': mention['data-mention-name']
        })
        mention.replace_with(f"@{mention['data-mention-name']}")
    
    text = soup.get_text()
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text, mentions

async def get_persona(database: Databases, persona_id: str) -> dict:
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

async def get_persona_context(database: Databases, mention_id: str, channel_id: str) -> dict:
    """Get persona information and relevant context for a mentioned persona"""
    try:
        persona = await get_persona(database, mention_id)
        if not persona:
            logger.warning(f"Could not find persona with ID {mention_id}")
            return None
        
        relevant_messages = document_vectorstore.similarity_search(
            query="",
            k=5,
            filter={
                "channel_id": channel_id,
                "sender_id": mention_id,
                "sender_name": persona["name"]
            }
        )
        
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

async def handle_summarize_command(channel_id: str) -> str:
    """Handle /summarize command"""
    try:
        channel_docs = document_vectorstore.similarity_search(
            query="",
            k=100,
            filter={"channel_id": channel_id}
        )
        
        messages_text = "\n".join([
            f"[{doc.metadata['timestamp']}] {doc.metadata['sender_name']}: {doc.page_content}"
            for doc in sorted(channel_docs, key=lambda x: x.metadata['timestamp'])
        ])
        
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

async def handle_analyze_command(channel_id: str) -> str:
    """Handle /analyze command"""
    try:
        channel_docs = document_vectorstore.similarity_search(
            query="",
            k=100,
            filter={"channel_id": channel_id}
        )
        
        messages_text = "\n".join([
            f"[{doc.metadata['timestamp']}] {doc.metadata['sender_name']}: {doc.page_content}"
            for doc in sorted(channel_docs, key=lambda x: x.metadata['timestamp'])
        ])
        
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
        
        return analysis_response.content
    except Exception as e:
        logger.error(f"Error in analyze command: {str(e)}")
        return "Sorry, I encountered an error while trying to analyze the conversation."

async def get_persona_response(prompt: str, persona_context: dict, channel_id: str, sender_name: str, sender_id: str) -> str:
    """Generate a response from a specific persona"""
    try:
        combined_context = retriever.get_relevant_documents(
            prompt,
            k=5,
            filter={
                "channel_id": channel_id,
                "$or": [
                    {"sender_id": persona_context['persona']['$id']}
                ]
            }
        )
        
        own_messages = []
        other_messages = []
        for doc in combined_context:
            if doc.metadata['sender_id'] == persona_context['persona']['$id']:
                own_messages.append(doc)
            else:
                other_messages.append(doc)
        
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

        prompt_with_context = template.format(
            name=persona_context['persona']['name'],
            role=persona_context['persona']['role'],
            personality=persona_context['persona']['personality'],
            conversation_style=persona_context['persona']['conversation_style'],
            knowledge_base=", ".join(persona_context['persona']['knowledge_base']),
            opinions=", ".join(persona_context['persona'].get('opinions', [])),
            disagreements=", ".join(persona_context['persona'].get('disagreements', [])),
            channel_context="\n".join([f"{doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" 
                                     for doc in other_messages[-3:]]),
            own_messages="\n".join([f"You: {doc.page_content}" 
                                  for doc in own_messages[-2:]]),
            sender_name=sender_name,
            sender_id=sender_id,
            prompt=prompt
        )

        response = await llm.ainvoke(prompt_with_context)
        return response.content

    except Exception as e:
        logger.error(f"Error getting persona response: {str(e)}")
        raise

async def get_gpt4_response(prompt: str, workspace_id: str, sender_name: str, sender_id: str) -> str:
    """Generate a response using GPT-4"""
    try:
        enhanced_query = f"Context from {sender_name} ({sender_id}): {prompt}"
        
        channel_context = retriever.get_relevant_documents(
            enhanced_query,
            k=5,
            filter={
                "workspace_id": workspace_id,
                "$or": [
                    {"sender_id": sender_id}
                ]
            }
        )

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

        response = await llm.ainvoke(prompt_with_context, temperature=0.8)
        return response.content

    except Exception as e:
        logger.error(f"Error getting GPT-4 response: {str(e)}")
        raise

def convert_context_to_json(context_list):
    """Convert context objects to JSON serializable format"""
    json_contexts = []
    for context in context_list:
        if context.get('recent_messages'):
            messages = [{
                'content': doc.page_content,
                'metadata': doc.metadata
            } for doc in context['recent_messages']]
            context['recent_messages'] = messages
        json_contexts.append(context)
    return json.dumps(json_contexts)  # Convert to JSON string here

async def main(context):
    """Main function handler for Appwrite"""
    try:
        # Initialize Appwrite client
        client = (
            Client()
            .set_endpoint(os.environ["APPWRITE_FUNCTION_API_ENDPOINT"])
            .set_project(os.environ["APPWRITE_FUNCTION_PROJECT_ID"])
            .set_key(context.req.headers["x-appwrite-key"])
        )
        database = Databases(client)

        # Log request details
        context.log(f"Request method: {context.req.method}")
        context.log(f"Request path: {context.req.path}")
        context.log(f"Request headers: {context.req.headers}")
        
        if not context.req.body:
            return context.res.json({"error": "No message body provided"}, 400)
            
        # Handle the body based on its type
        data = context.req.body if isinstance(context.req.body, dict) else json.loads(context.req.body)
        logger.info(f"Received message data: {data}")
        
        # Sanitize content and extract mentions
        content = data.get('content', '')
        clean_content, mentions = sanitize_html_content(content)
        logger.info(f"User message: {clean_content}")
        logger.info(f"Detected mentions: {mentions}")
        
        # Handle commands
        if clean_content.startswith('/'):
            command = clean_content.split()[0].lower()
            response_content = None
            
            if command == '/summarize':
                logger.info(f"Processing summarize command for channel {data['channel_id']}")
                response_content = await handle_summarize_command(data['channel_id'])
            elif command == '/analyze':
                logger.info(f"Processing analyze command for channel {data['channel_id']}")
                response_content = await handle_analyze_command(data['channel_id'])
            
            if response_content:
                logger.info(f"Command response: {response_content}")
                message = {
                    'channel_id': data['channel_id'],
                    'workspace_id': data['workspace_id'],
                    'sender_type': 'bot',
                    'sender_id': 'bot',
                    'content': response_content,
                    'sender_name': 'Chattie Bot',
                    'edited_at': datetime.now().isoformat(),
                }
                
                database.create_document(
                    database_id='main',
                    collection_id='messages',
                    document_id=ID.unique(),
                    data=message,
                    permissions=[
                        Permission.read(Role.user(data['sender_id'])),
                        Permission.write(Role.user('bot')),
                        Permission.delete(Role.user('bot'))
                    ]
                )
                return context.res.json({"status": "Command processed successfully"})
        
        # Skip embedding if message is from bot
        if data.get('sender_id') != 'bot':
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
            document_vectorstore.add_documents([message_document])
            logger.info("Message embedded in vector store")
        
        # Process mentions
        for mention in mentions:
            response_content = None
            mention_contexts = []
            
            if mention['id'] == 'bot':
                logger.info(f"Processing bot mention from {data['sender_name']}")
                response_content = await get_gpt4_response(
                    clean_content,
                    data['workspace_id'],
                    data['sender_name'],
                    data['sender_id']
                )
            else:
                logger.info(f"Processing persona mention for {mention['name']}")
                persona_context = await get_persona_context(
                    database,
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
            
            if response_content:
                logger.info(f"Bot response: {response_content}")
                
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
                
                # Convert context to JSON serializable format and stringify
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
                    'ai_context': json_contexts,  # Already a JSON string
                    'ai_prompt': clean_content,
                    'attachments': [],
                }
                
                database.create_document(
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
        
        return context.res.json({"status": "Message processed successfully"})
    
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        context.error(f"Error: {str(e)}")
        return context.res.json({"error": str(e)}, 500)
