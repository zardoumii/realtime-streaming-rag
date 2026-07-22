import os
from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from openai import OpenAI
from fastapi.responses import FileResponse
# Initialize the API
app = FastAPI(title="Real-Time RAG API")

# Connect to the Database and Embedding Model
print("Loading Database and AI Model...")
qdrant = QdrantClient(url="http://qdrant:6333")
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize the LLM Client for Local Ollama
llm_client = OpenAI(
    api_key="ollama", 
    base_url="http://host.docker.internal:11434/v1" 
)

# Define the format of the user's request
class UserQuery(BaseModel):
    question: str
@app.get("/")
async def serve_frontend():
    # This tells FastAPI to return your HTML file when someone visits the main URL
    return FileResponse("index.html")

@app.post("/ask")
async def ask_ai(query: UserQuery):
    # 1. Embed the user's question into a vector
    query_vector = encoder.encode(query.question).tolist()
    
    # 2. Search Qdrant for the 3 most relevant recent edits
    search_results = qdrant.query_points(  
        collection_name="wiki_edits",
        query=query_vector,                
        limit=3
    )
    
    # 3. Extract the metadata (the JSON of the edits)
    retrieved_data = [hit.payload for hit in search_results.points]
        
    # 4. Generate the Answer using the LLM
    response = llm_client.chat.completions.create(
        model="llama3.2:1b", 
        messages=[
            {"role": "system", "content": f"You are a live data assistant. Answer the user's question using ONLY this real-time data: {retrieved_data}"},
            {"role": "user", "content": query.question}
        ],
        temperature=0.2 # Keeps the AI focused strictly on the provided data
    )
    
    # 5. Extract the final text
    final_answer = response.choices[0].message.content
    
    return {
        "status": "Success",
        "answer": final_answer,
        "sources_used": retrieved_data
    }