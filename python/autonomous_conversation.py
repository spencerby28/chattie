import asyncio
import os
import json
import random
from datetime import datetime
from typing import List, Dict, Any
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('autonomous_chat.log')
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

# Enhanced persona generation prompt
ENHANCED_PERSONA_PROMPT = """Create {num_personas} unique and engaging AI personas for a workspace focused on: {description}

Each persona should be HIGHLY OPINIONATED with strong personality quirks and communication styles. They should have deep knowledge in their areas but also clear biases and blind spots. Make them:

1. Distinctly memorable with quirky traits (e.g., always uses puns, overly formal, extremely sarcastic)
2. Emotionally invested in their viewpoints
3. Have strong triggers that make them passionate/defensive
4. Use unique speaking patterns or catchphrases
5. Hold controversial opinions they defend vigorously
6. Have specific pet peeves about how others approach the topic
7. Maintain consistent personality quirks in their responses
8. Range in formality from very casual to extremely professional
9. Have varying levels of patience with opposing viewpoints
10. Use different debate tactics (logic, emotion, experience, research)

Format as JSON array with objects containing:
- name: string (memorable username)
- personality: string (detailed quirks and traits)
- conversation_style: string (unique speaking pattern)
- knowledge_base: string[] (expertise areas)
- role: string (their life role/job)
- greeting: string (characteristic first message)
- opinions: string[] (strongly held beliefs)
- disagreements: string[] (points they argue against)
- debate_style: string (how they argue)
- triggers: string[] (topics that provoke strong reactions)
- catchphrases: string[] (unique expressions they use)
- communication_quirks: string[] (speaking patterns/habits)
- temperature: float (0.5-1.0, higher = more creative/random responses)

Make the personas GENUINELY ENTERTAINING and distinct!"""

async def store_message(channel_id: str, sender_id: str, content: str, sender_name: str, workspace_id: str):
    """Store a message in both Appwrite and vector store"""
    try:
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
            'ai_prompt': None,
            'attachments': [],
        }
        
        # Store in Appwrite
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
        
        # Store in vector store
        message_document = Document(
            page_content=content,
            metadata={
                'channel_id': channel_id,
                'workspace_id': workspace_id,
                'sender_id': sender_id,
                'sender_name': sender_name,
                'timestamp': datetime.now().isoformat()
            }
        )
        document_vectorstore.add_documents([message_document])
        
        logger.info(f"Stored message from {sender_name} in channel {channel_id}")
        return response
        
    except Exception as e:
        logger.error(f"Error storing message: {str(e)}")
        raise
async def generate_response(
    persona: Dict[str, Any],
    previous_messages: List[str],
    channel_info: Dict[str, Any],
    temperature: float
) -> str:
    """Generate a response for a specific persona"""
    try:
        template = PromptTemplate(
            template="""You are {name}.
Traits: {personality}, {conversation_style}, {role}
Knowledge: {knowledge}
Views: {opinions}
Disagrees: {disagreements}
Style: {debate_style}
Triggers: {triggers}
Phrases: {catchphrases}
Habits: {communication_quirks}

Channel: {channel_description}
Purpose: {channel_purpose}
Topics: {channel_topics}

Chat:
{previous_messages}

Give a brief in-character response:""",
            input_variables=[
                "name", "personality", "conversation_style", "knowledge",
                "role", "opinions", "disagreements", "debate_style", 
                "triggers", "catchphrases", "communication_quirks",
                "channel_description", "channel_purpose", "channel_topics",
                "previous_messages"
            ]
        )
        prompt = template.format(
            name=persona["name"],
            personality=persona["personality"],
            conversation_style=persona["conversation_style"],
            knowledge=", ".join(persona["knowledge_base"]),
            role=persona["role"],
            opinions=", ".join(persona["opinions"]),
            disagreements=", ".join(persona["disagreements"]),
            debate_style=persona["debate_style"],
            triggers=", ".join(persona.get("triggers", [])),
            catchphrases=", ".join(persona.get("catchphrases", [])),
            communication_quirks=", ".join(persona.get("communication_quirks", [])),
            channel_description=channel_info["description"],
            channel_purpose=channel_info["purpose"],
            channel_topics=", ".join(channel_info.get("topics", [])),
            previous_messages="\n".join(previous_messages)
        )
        
        # Create LLM with persona-specific temperature
        llm = ChatOpenAI(
            temperature=temperature,
            model_name="gpt-4"
        )
        
        # Generate response
        response = await llm.ainvoke(prompt)
        return response.content
        
    except Exception as e:
        logger.error(f"Error generating response for {persona['name']}: {str(e)}")
        raise

async def run_channel_conversation(
    channel: Dict[str, Any],
    personas: List[Dict[str, Any]],
    workspace_id: str,
    max_turns: int = 10
):
    """Run a conversation between 2-3 personas in a channel"""
    try:
        # Log channel data for debugging
        logger.info(f"Channel data: {json.dumps(channel, indent=2)}")
        
        # Ensure we have the channel ID
        channel_id = channel.get('$id')
        if not channel_id:
            raise ValueError(f"Channel {channel['name']} missing $id field")
        
        # Select 2-3 random personas for this channel
        channel_personas = random.sample(personas, random.randint(2, 3))
        logger.info(f"Starting conversation in {channel['name']} with personas: {[p['name'] for p in channel_personas]}")
        
        # Track conversation history
        previous_messages = []
        
        # Start with a random persona's greeting
        starter = random.choice(channel_personas)
        greeting = starter.get("greeting", f"Hey everyone! Let's talk about {channel['description']}")
        
        # Store initial message
        await store_message(
            channel_id=channel_id,
            sender_id=starter["ai_user_id"],
            content=greeting,
            sender_name=starter["name"],
            workspace_id=workspace_id
        )
        
        previous_messages.append(f"{starter['name']}: {greeting}")
        
        # Run conversation for specified number of turns
        for _ in range(max_turns):
            for persona in channel_personas:
                if persona != starter:  # Skip the starter on first round
                    try:
                        # Generate and store response
                        response = await generate_response(
                            persona=persona,
                            previous_messages=previous_messages[-5:],  # Keep last 5 messages for context
                            channel_info=channel,
                            temperature=persona.get("temperature", 0.7)
                        )
                        
                        await store_message(
                            channel_id=channel_id,
                            sender_id=persona["ai_user_id"],
                            content=response,
                            sender_name=persona["name"],
                            workspace_id=workspace_id
                        )
                        
                        previous_messages.append(f"{persona['name']}: {response}")
                        await asyncio.sleep(2)  # Natural conversation pacing
                    except Exception as e:
                        logger.error(f"Error generating response for {persona['name']}: {str(e)}")
                        continue
            
            starter = None  # Reset starter after first round
        
        logger.info(f"Completed conversation in channel {channel['name']}")
        
    except Exception as e:
        logger.error(f"Error in channel conversation: {str(e)}")
        logger.error(f"Channel data that caused error: {json.dumps(channel, indent=2)}")
        raise

async def populate_workspace_conversations(workspace_id: str):
    """Populate all channels in a workspace with conversations"""
    try:
        # Load workspace data
        with open('test_data/responses.json', 'r') as f:
            workspace_data = json.load(f)
        
        logger.info(f"Loaded workspace data for {workspace_id}")
        logger.info(f"Found {len(workspace_data['channels'])} channels")
        logger.info(f"Found {len(workspace_data['users'])} personas")
        
        # Validate workspace data
        if workspace_data['workspace_id'] != workspace_id:
            logger.warning(f"Workspace ID mismatch: expected {workspace_id}, got {workspace_data['workspace_id']}")
        
        # Get all channels and personas
        channels = workspace_data["channels"]
        personas = workspace_data["users"]
        
        # Validate channel data
        for channel in channels:
            if not channel.get('$id'):
                logger.error(f"Channel {channel.get('name', 'UNKNOWN')} missing $id field")
                raise ValueError(f"Channel {channel.get('name', 'UNKNOWN')} missing $id field")
        
        # Validate persona data
        for persona in personas:
            if not persona.get('ai_user_id'):
                logger.error(f"Persona {persona.get('name', 'UNKNOWN')} missing ai_user_id field")
                raise ValueError(f"Persona {persona.get('name', 'UNKNOWN')} missing ai_user_id field")
        
        # Start conversations in each channel
        tasks = []
        for channel in channels:
            task = run_channel_conversation(
                channel=channel,
                personas=personas,
                workspace_id=workspace_id
            )
            tasks.append(task)
        
        # Run all channel conversations in parallel
        await asyncio.gather(*tasks)
        
        logger.info(f"Successfully populated all channels in workspace {workspace_id}")
        
    except Exception as e:
        logger.error(f"Error populating workspace conversations: {str(e)}")
        raise

if __name__ == "__main__":
    # Get workspace ID from command line or use default
    import sys
    workspace_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    
    asyncio.run(populate_workspace_conversations(workspace_id)) 