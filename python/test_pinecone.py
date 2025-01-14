from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone

# Load environment variables
load_dotenv()

# Initialize Pinecone
pc = Pinecone()
print("Pinecone initialized")

# Initialize embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
print("Embeddings initialized")

# Try to access the index
try:
    vectorstore = PineconeVectorStore(
        index_name="messages",
        embedding=embeddings,
    )
    print("Successfully connected to Pinecone index 'messages'")
except Exception as e:
    print(f"Error connecting to Pinecone: {str(e)}") 