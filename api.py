from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

# Initialize the API
app = FastAPI(title="Real-Time RAG API")

# 1. Connect to the EXACT SAME local database and model
print("Loading Database and AI Model...")
qdrant = QdrantClient(url="http://qdrant:6333")
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# Define the format of the user's request
class UserQuery(BaseModel):
    question: str

@app.post("/ask")
async def ask_ai(query: UserQuery):
    # 1. Embed the user's question into a vector
    query_vector = encoder.encode(query.question).tolist()
    
    # 2. Search Qdrant for the 3 most relevant recent edits
    search_results = qdrant.query_points(  # <--- Changed this line
        collection_name="wiki_edits",
        query=query_vector,                # <--- Changed 'query_vector' to 'query'
        limit=3
    )
    
    # 3. Extract the metadata
    retrieved_data = []
    # In newer Qdrant versions, the results are stored in a 'points' attribute
    for hit in search_results.points:      # <--- Added '.points'
        retrieved_data.append(hit.payload)
        
    # 4. Build the RAG Prompt
    rag_prompt = f"""
You are an expert AI assistant. Answer the user's question using ONLY the latest real-time data provided below.

Real-Time Data:
{retrieved_data}

User Question: {query.question}
"""
    
    return {
        "status": "Success",
        "retrieved_edits": retrieved_data,
        "final_llm_prompt": rag_prompt
    }