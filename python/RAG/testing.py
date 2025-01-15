from langchain_openai import ChatOpenAI, OpenAIEmbeddings 
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from langchain.prompts import PromptTemplate
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set required environment variables
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY") 
os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGSMITH_PROJECT"] = "chattie-testing"
os.environ["LANGSMITH_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")

def classify_query(query: str, llm: ChatOpenAI) -> str:
    # Create prompt template for classification
    classify_prompt = PromptTemplate(
        input_variables=["query"],
        template="""Classify the following query into one of these categories and extract the relevant information:
        - 'channel:CHANNEL_ID' if asking about a specific chat channel or conversation (use the provided channel ID)
        - 'person:NAME' if asking about a specific person/user (extract the person's name)
        - 'theme:TOPIC' if asking about topics, ideas or concepts (extract the main topic)
        
        Query: {query}
        
        Return ONLY the classification and extracted info in the format specified above (e.g. 'channel:123', 'person:John', 'theme:density')."""
    )
    # Get classification from LLM
    response = llm.invoke(classify_prompt.format(query=query))
    return response.content.strip().lower()

def get_similar_documents(query: str):
    # Initialize embeddings and LLM
    embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # Get query classification
    query_type = classify_query(query, llm)
    
    # Create vector store
    vector_store = PineconeVectorStore(
        index_name="messages",
        embedding=embeddings
    )
    
    # Apply filters based on classification
    filters = {}
    if query_type == "person":
        # Filter by sender name
        filters["sender_name"] = query.strip()
    elif query_type == "channel":
        # Filter by channel ID
        filters["channel_id"] = query.strip()
    # No filters for theme-based queries
    
    # Perform search with filters
    similar_docs = vector_store.similarity_search_with_relevance_scores(
        query, 
        filter=filters if filters else None
    )
    
    # Convert results to JSON-serializable format
    results = []
    for doc, score in similar_docs:
        results.append({
            "page_content": doc.page_content,
            "metadata": doc.metadata,
            "relevance_score": score
        })
    
    # Save results to JSON file
    with open('search_results.json', 'w') as f:
        json.dump(results, f, indent=2)
        
    return similar_docs

# Example usage
if __name__ == "__main__":
    sample_query = "When did dynamo say he was pro urban housing?"
    results = get_similar_documents(sample_query)
    
    # Print query and results
    print(f"\nQuery: {sample_query}")
    print(f"Results saved to search_results.json")