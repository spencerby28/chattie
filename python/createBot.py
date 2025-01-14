from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.permission import Permission
from appwrite.role import Role
from appwrite.id import ID
from datetime import datetime
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.schema import Document
import logging
import json

load_dotenv()

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

class PersonaManager:
    def __init__(self, personas_file="test_data/responses.json"):
        with open(personas_file, 'r') as f:
            data = json.load(f)
            self.personas = {persona['name']: persona for persona in data['personas']}

async def create_bot_message(channel_id, persona_id, bot_user_id, prompt):
    try:
        # Get relevant context from embeddings with bot_user_id filter
        context = retriever.get_relevant_documents(
            prompt,
            k=5,  # Get top 5 most relevant messages
            filter={"sender_id": bot_user_id}
        )
        
        # Get bot persona
        persona_manager = PersonaManager()
        persona = persona_manager.personas.get(persona_id)
        if not persona:
            raise ValueError(f"No persona found for persona ID: {persona_id}")

        # Create prompt template with context and persona
        template = PromptTemplate(
            template="""You are {name}, a {role}. 
Your personality: {personality}
Your conversation style: {conversation_style}
Your knowledge areas: {knowledge}
Your opinions: {opinions}
Your disagreements: {disagreements}
Your debate style: {debate_style}

Based on the following context and your persona, provide a response:

Context: {context}

Current Query: {query}""",
            input_variables=["name", "role", "personality", "conversation_style", "knowledge", 
                           "opinions", "disagreements", "debate_style", "query", "context"]
        )
        
        prompt_with_context = template.invoke({
            "name": persona["name"],
            "role": persona["role"],
            "personality": persona["personality"],
            "conversation_style": persona["conversation_style"],
            "knowledge": ", ".join(persona["knowledge_base"]),
            "opinions": ", ".join(persona["opinions"]),
            "disagreements": ", ".join(persona["disagreements"]),
            "debate_style": persona["debate_style"],
            "query": prompt,
            "context": "\n".join([f"{doc.metadata['sender_name']}: {doc.page_content}" for doc in context])
        })
        
        # Get LLM response
        response = await llm.ainvoke(prompt_with_context)
        response_content = response.content

        message = {
            'channel_id': channel_id,
            'workspace_id': 'default',
            'sender_type': 'ai_persona',
            'sender_id': bot_user_id,
            'content': response_content,
            'sender_name': persona["name"],
            'edited_at': datetime.now().isoformat(),
            'mentions': [],
            'ai_context': str(context),
            'ai_prompt': prompt,
            'attachments': [],
        }

        # Store in database with correct permissions
        response = database.create_document(
            database_id='main',
            collection_id='messages',
            document_id=ID.unique(),
            data=message,
            permissions=[
                Permission.read(Role.label(channel_id)),
                Permission.write(Role.user(bot_user_id)),
                Permission.delete(Role.user(bot_user_id))
            ]
        )
        
        # Store bot response in vector database
        bot_message_document = Document(
            page_content=response_content,
            metadata={
                'channel_id': channel_id,
                'sender_id': bot_user_id,
                'sender_name': persona["name"],
                'timestamp': datetime.now().isoformat()
            }
        )
        document_vectorstore.add_documents([bot_message_document])
        
        logger.info(f"Created message with ID: {response['$id']}")
        return response

    except Exception as e:
        logger.error(f"Error creating bot message: {str(e)}")
        logger.exception(e)
        raise

if __name__ == "__main__":
    import asyncio
    channel_id = input("Enter channel ID: ")
    persona_id = input("Enter persona ID (name of the persona): ")
    bot_user_id = input("Enter bot user ID (for sending messages): ")
    prompt = input("Enter prompt: ")
    asyncio.run(create_bot_message(channel_id, persona_id, bot_user_id, prompt))
