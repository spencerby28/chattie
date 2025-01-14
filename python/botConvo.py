import random
from aiohttp import web
import json
import os
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from datetime import datetime
import asyncio
import logging
import time
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import Document
from appwrite.query import Query
from collections import deque

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
retriever = document_vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")

# Message queue for each channel
channel_queues = {}

class PersonaManager:
    def __init__(self):
        # Load personas and channels from responses.json
        with open('test_data/responses.json', 'r') as f:
            data = json.load(f)
            self.personas = {user['name']: user for user in data['users']}
            self.channels = {channel['name']: channel for channel in data['channels']}
            self.ai_user_ids = data['mappings']['ai_user_ids']
            self.channel_ids = data['mappings']['channel_ids']

    def get_persona_prompt(self, persona_name, previous_messages, current_channel):
        persona = self.personas[persona_name]
        channel = self.channels[current_channel]
        
        return PromptTemplate(
            template="""You are {name}, {role}. Your personality is: {personality}

Your conversation style is: {conversation_style}
Your core knowledge areas are: {knowledge}
Your key opinions are: {opinions}
You disagree with: {disagreements}
Your debate style is: {debate_style}

Current channel topic: {channel_description}
Channel purpose: {channel_purpose}

Previous messages in conversation:
{previous_messages}

Respond naturally as {name}, maintaining your personality and viewpoints. Keep responses concise and conversational.""",
            input_variables=["name", "role", "personality", "conversation_style", "knowledge", 
                           "opinions", "disagreements", "debate_style", "channel_description", 
                           "channel_purpose", "previous_messages"]
        ).format(
            name=persona['name'],
            role=persona['role'],
            personality=persona['personality'],
            conversation_style=persona['conversation_style'],
            knowledge=", ".join(persona['knowledge_base']),
            opinions=", ".join(persona['opinions']),
            disagreements=", ".join(persona['disagreements']),
            debate_style=persona['debate_style'],
            channel_description=channel['description'],
            channel_purpose=channel['purpose'],
            previous_messages="\n".join(previous_messages)
        )

async def get_recent_messages(channel_id, limit=5):
    """Get recent messages from the channel"""
    try:
        response = database.list_documents(
            database_id='main',
            collection_id='messages',
            queries=[
                Query.equal('channel_id', channel_id),
                Query.order_desc('$createdAt'),
                Query.limit(limit)
            ]
        )
        return response['documents']
    except Exception as e:
        logger.error(f"Error getting recent messages: {str(e)}")
        return []

async def get_persona_response(persona_name, channel_name, previous_messages, persona_manager):
    """Generate a response from a specific persona"""
    try:
        # Create prompt using persona manager
        prompt = persona_manager.get_persona_prompt(
            persona_name=persona_name,
            previous_messages=previous_messages,
            current_channel=channel_name
        )
        
        # Get response from LLM
        response = await llm.ainvoke(prompt)
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating persona response: {str(e)}")
        return "I apologize, but I'm having trouble formulating a response right now."

async def process_message_queue(channel_id, persona_manager):
    if channel_id not in channel_queues:
        channel_queues[channel_id] = deque()
    
    while True:
        if channel_queues[channel_id]:
            message = channel_queues[channel_id].popleft()
            
            # Get recent context
            recent_messages = await get_recent_messages(channel_id)
            previous_messages = [msg['content'] for msg in recent_messages]
            
            # Generate response from a random persona
            channel_name = next(name for name, id in persona_manager.channel_ids.items() 
                              if id == channel_id)
            channel = persona_manager.channels[channel_name]
            
            # Select random persona that hasn't spoken recently
            available_personas = [p for p in channel.get('primary_personas', [])
                                if p not in [msg.get('sender_name') for msg in recent_messages[-2:]]]
            
            if available_personas:
                current_persona = random.choice(available_personas)
                
                response_content = await get_persona_response(
                    current_persona,
                    channel_name,
                    previous_messages,
                    persona_manager
                )

                # Store message in database
                await store_message(
                    channel_id=channel_id,
                    workspace_id=message['workspace_id'],
                    sender_id=persona_manager.ai_user_ids[current_persona],
                    content=response_content,
                    sender_name=current_persona,
                    thread_id=message.get('thread_id')
                )

                # Create embedding
                message_document = Document(
                    page_content=response_content,
                    metadata={
                        'channel_id': channel_id,
                        'workspace_id': message['workspace_id'],
                        'sender_id': current_persona,
                        'sender_name': current_persona,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                await document_vectorstore.aadd_documents([message_document])

        await asyncio.sleep(2)  # Natural conversation pacing

async def store_message(channel_id, workspace_id, sender_id, content, sender_name, thread_id=None):
    message = {
        'channel_id': channel_id,
        'workspace_id': workspace_id,
        'sender_type': 'ai_persona',
        'sender_id': sender_id,
        'content': content,
        'sender_name': sender_name,
        'edited_at': datetime.now().isoformat(),
        'mentions': [],
        'ai_context': None,
        'thread_id': thread_id,
        'thread_count': None,
        'attachments': []
    }
    
    return await database.create_document(
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

async def handle_message(request):
    try:
        data = await request.json()
        logger.info(f"Received message data: {data}")
        
        # Skip if message is from an AI persona
        if data.get('sender_type') == 'ai_persona':
            return web.Response(text='Skipping AI persona message', status=200)
            
        # Add message to channel queue
        if data['channel_id'] not in channel_queues:
            channel_queues[data['channel_id']] = deque()
        channel_queues[data['channel_id']].append(data)
        
        return web.Response(text='Message queued successfully', status=200)
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        logger.exception(e)
        return web.Response(text=str(e), status=500)

async def main():
    persona_manager = PersonaManager()
    
    app = web.Application()
    app.router.add_post('/', handle_message)
    
    # Start message queue processors for each channel
    for channel_id in persona_manager.channel_ids.values():
        asyncio.create_task(process_message_queue(channel_id, persona_manager))
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    
    logger.info("Conversation server started at http://localhost:8000")
    await site.start()
    
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())