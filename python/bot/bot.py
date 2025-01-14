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
    index_name='messages',
    embedding=embeddings
)
retriever = document_vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")

async def get_gpt4_response(prompt, channel_id, sender_id):
    try:
        start_time = time.time()
        
        # First, get relevant context across ALL channels based on the query
        context_start = time.time()
        all_context = retriever.get_relevant_documents(
            prompt,
            k=5  # Get top 5 most relevant messages overall
        )
        
        # Split the context into channel-specific and other channels
        channel_context = []
        other_context = []
        
        for doc in all_context:
            if doc.metadata['channel_id'] == channel_id:
                channel_context.append(doc)
            else:
                other_context.append(doc)
        
        logger.info(f"Context retrieval took {time.time() - context_start:.2f}s")
        
        # Create prompt template with enhanced context separation
        template = PromptTemplate(
            template="""Based on the following context and chat history, provide a response:

Current Channel Context: {channel_context}

Related Conversations from Other Channels: {other_context}

Current Query: {query}""",
            input_variables=["query", "channel_context", "other_context"]
        )
        
        prompt_with_context = template.invoke({
            "query": prompt,
            "channel_context": "\n".join([f"{doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" for doc in channel_context]),
            "other_context": "\n".join([f"From channel {doc.metadata.get('channel_id', 'unknown')} - {doc.metadata.get('sender_name', 'Unknown User')}: {doc.page_content}" for doc in other_context])
        })
        
        # Get response
        llm_start = time.time()
        response = await llm.ainvoke(prompt_with_context)
        logger.info(f"LLM response took {time.time() - llm_start:.2f}s")
        
        return response.content
                
    except Exception as e:
        logger.error(f"Error getting GPT-4 response: {str(e)}")
        logger.exception(e)
        raise

async def handle_message(request):
    try:
        start_time = time.time()
        
        data = await request.json()
        logger.info(f"Received message data: {data}")
        content = data.get('content', '')
        
        # ----------------------------------------------------------------------------------
        # /summarize command logic (placeholder for demonstration)
        # ----------------------------------------------------------------------------------
        if '/summarize' in content.lower():
            logger.info(f"Detected /summarize command in message `{content}`")
            
            try:
                # Get last 100 messages from the channel
                channel_docs = await get_channel_messages(data['channel_id'])
                
                # Format messages chronologically for the summary
                messages_text = "\n".join([
                    f"[{doc.metadata['timestamp']}] {doc.metadata['sender_name']}: {doc.page_content}"
                    for doc in channel_docs
                ])
                
                # Create a summarization prompt
                summary_prompt = PromptTemplate(
                    template="""Please provide a concise summary of the following conversation, highlighting key points and decisions:

{messages}

Summary:""",
                    input_variables=["messages"]
                )
                
               ## summary_response = await llm.ainvoke(
                #    summary_prompt.format(messages=messages_text)
                #)
               # summary_result = summary_response.content
                
                # If you'd like to feed them into the LLM for an actual summary:
                prompt_for_summary = f"Summarize the following messages:\n{messages_text}"
                summary_response = await llm.ainvoke(prompt_for_summary)
                summary_result = summary_response.content
                logger.info(f"Suggested summary: {summary_result}")

                # For now, we just log a placeholder:
                logger.info("Suggested summary: [Placeholder summary based on retrieved channel docs]")
            except Exception as e:
                logger.error(f"Error retrieving documents for /summarize: {e}")
        
        # ----------------------------------------------------------------------------------
        # /respond command logic (placeholder for demonstration)
        # ----------------------------------------------------------------------------------
        if '/respond' in content.lower():
            logger.info(f"Detected /respond command in message `{content}`")

            # Example: we might look up the user's recent messages to glean their style/tone
            # Then craft a response in that style. For now, we just log that we'd do this.
            user_id = data.get('sender_id', 'unknown')
            logger.info(f"Would analyze user_id={user_id} message history for style...")

            # Possibly search Pinecone for messages from user in same channel, etc.
            # Then feed them to LLM to generate a style-based answer. We'll skip that
            # and just do a placeholder log:
            logger.info("Suggested style-based response: [Placeholder response in user’s style]")

        # ----------------------------------------------------------------------------------
        # Existing message logic below (unchanged)
        # ----------------------------------------------------------------------------------

        # Skip embedding if the message is from the bot
        if data.get('sender_id') != 'bot':
            pinecone_start = time.time()
            message_document = Document(
                page_content=content,
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
            logger.info(f"Pinecone storage took {time.time() - pinecone_start:.2f}s")
        
        # Only generate bot response if @bot is mentioned
        if '@bot' in content:
            # Get GPT-4 response with enhanced context
            gpt_start = time.time()
            response_content = await get_gpt4_response(
                content,
                data['channel_id'],
                data['sender_id']
            )
            
            # Store bot response in Pinecone immediately
            bot_message_document = Document(
                page_content=response_content,
                metadata={
                    'channel_id': data['channel_id'],
                    'workspace_id': data['workspace_id'],
                    'sender_id': 'bot',
                    'sender_name': 'Chattie Bot',
                    'timestamp': datetime.now().isoformat()
                }
            )
            document_vectorstore.add_documents([bot_message_document])
            
            # Create message document for Appwrite
            message = {
                'channel_id': data['channel_id'],
                'workspace_id': data['workspace_id'],
                'sender_type': 'bot',
                'sender_id': 'bot',
                'content': response_content,
                'sender_name': 'Chattie Bot',
                'edited_at': datetime.now().isoformat(),
                'mentions': [],
                'ai_context': None,
                'ai_prompt': content,
                'attachments': [],
            }
            
            # Store bot response in database
            db_start = time.time()
            response = database.create_document(
                database_id='main',
                collection_id='messages',
                document_id=ID.unique(),
                data=message,
                permissions=[
                    Permission.read(Role.label(data['channel_id'])),
                    Permission.write(Role.user('bot')),
                    Permission.delete(Role.user('bot'))
                ]
            )
            logger.info(f"Database storage took {time.time() - db_start:.2f}s")
            logger.info(f"Created message document with ID: {response['$id']}")
        
        logger.info("Message processed successfully")
        logger.info(f"Total request processing time: {time.time() - start_time:.2f}s")
        return web.Response(text='Message processed successfully', status=200)
        
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        logger.exception(e)
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

async def main():
    app = web.Application()
    app.router.add_post('/', handle_message)
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8000)
    
    logger.info("Bot server started at http://localhost:8000")
    await site.start()
    
    # Keep the server running
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    asyncio.run(main())
