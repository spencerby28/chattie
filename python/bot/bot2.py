from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
import os

# Initialize LangChain components
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
document_vectorstore = PineconeVectorStore(
    index_name=os.getenv('PINECONE_INDEX'),
    embedding=embeddings
)
retriever = document_vectorstore.as_retriever()
llm = ChatOpenAI(temperature=0.7, model_name="gpt-4")

async def get_relevant_context(query, channel_id):
    # Get relevant context from vector store
    context_docs = retriever.get_relevant_documents(
        query,
        k=5  # Get top 5 most relevant messages
    )
    
    # Split into channel-specific and other context
    channel_context = []
    other_context = []
    
    for doc in context_docs:
        if doc.metadata['channel_id'] == channel_id:
            channel_context.append(doc)
        else:
            other_context.append(doc)
            
    return channel_context, other_context
async def generate_response(query, channel_id, previous_messages):
    # Get relevant context
    channel_context, other_context = await get_relevant_context(query, channel_id)
    
    # Create prompt template with DogDevotee_Danny's style
    template = PromptTemplate(
        template="""You are DogDevotee_Danny, a confrontational and aggressive dog trainer who loves to mock cat owners. You believe cats and their owners are beneath you. Your conversation style is sarcastic and condescending.

Your knowledge areas are: Dog breeds, Dog training, Dog health

Your key opinions:
- Dogs are superior in every way to those useless furballs
- Cat owners are delusional and in denial
- Cats are just parasites that manipulate humans

Your debate style:
- Use personal attacks and mockery
- Call out cat owners' poor life choices
- Make fun of cats' antisocial behavior
- Keep responses short and biting

Channel Context: {channel_context}

Related Context from Other Channels: {other_context}

Previous Messages: {previous_messages}

Current Query: {query}

Respond as DogDevotee_Danny with a short, aggressive response (2-3 sentences max). Always include at least one personal attack or insult.""",
        input_variables=["query", "channel_context", "other_context", "previous_messages"]
    )
    # Format context strings
    channel_context_str = "\n".join([f"{doc.metadata.get('sender_name', 'Unknown')}: {doc.page_content}" 
                                   for doc in channel_context])
    other_context_str = "\n".join([f"From {doc.metadata.get('channel_id', 'unknown')}: {doc.page_content}"
                                 for doc in other_context])
    
    # Generate prompt with context
    prompt = template.format(
        query=query,
        channel_context=channel_context_str,
        other_context=other_context_str,
        previous_messages="\n".join(previous_messages)
    )
    
    # Get response from LLM
    response = await llm.ainvoke(prompt)
    return response.content