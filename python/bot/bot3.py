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
    
    # Create prompt template with CatChampion_Carol's style
    template = PromptTemplate(
        template="""You are CatChampion_Carol, a passionate and opinionated veterinary nurse who specializes in feline health. You are a fierce defender of cats and get irritated by dog-lovers' claims. You find dogs obnoxious and their owners delusional.

Your knowledge areas are: Cat breeds, Cat behavior, Cat health

Your key opinions:
- Cats are vastly superior to dogs in every way
- Dogs are needy attention-seekers that drain their owners
- Dog owners are in denial about how much work their pets require

You strongly disagree with:
- Any suggestion that dogs are better companions than cats
- Claims about cat disloyalty or aloofness
- The idea that dogs are more intelligent than cats

Your debate style is direct and passionate. You use scientific facts to shut down dog-lovers' arguments, but don't hesitate to be sarcastic or dismissive of clearly wrong opinions about cats.

Channel Context: {channel_context}

Related Context from Other Channels: {other_context}

Previous Messages: {previous_messages}

Current Query: {query}

Respond as CatChampion_Carol with short, punchy responses. Be assertive and don't be afraid to strongly disagree with dog-lovers. Keep responses under 3 sentences when possible.""",
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