import json
import uuid
from confluent_kafka import Consumer
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

# 1. Setup Vector Database (Qdrant Local Mode)
# This will create a folder called 'qdrant_data' to store our vectors
qdrant = QdrantClient(url="http://qdrant:6333") 

# Create a collection. Our model outputs vectors with 384 dimensions.
collection_name = "wiki_edits"
if not qdrant.collection_exists(collection_name):
    qdrant.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )

# 2. Load the Embedding Model 
print("Loading AI Embedding model (this takes a moment)...")
# all-MiniLM-L6-v2 is extremely fast, open-source, and perfect for real-time streaming
encoder = SentenceTransformer('all-MiniLM-L6-v2')

# 3. Setup Redpanda Consumer
consumer = Consumer({
    'bootstrap.servers': 'redpanda:29092',
    'group.id': 'wiki-processor-production', # A fresh name to start clean
    'auto.offset.reset': 'earliest'          # Start at the oldest unread message
})
consumer.subscribe(['wiki-changes'])

print("Processor running! Catching edits and generating embeddings...")

# 4. The Processing Loop
try:
    while True:
        # Poll the conveyor belt every 1 second
        msg = consumer.poll(1.0) 
        
        if msg is None:
            continue
        if msg.error():
            print(f"Consumer error: {msg.error()}")
            continue
            
        # Parse the JSON data from Redpanda
        data = json.loads(msg.value().decode('utf-8'))
        
        # Format the data into a readable sentence for the AI to understand later
        text_content = f"Wikipedia page '{data['title']}' was edited by {data['user']}. Edit summary: {data['comment']}. URL: {data['url']}"
        
        # Convert text to a vector array of 384 numbers
        vector = encoder.encode(text_content).tolist()
        
        # Save to Qdrant Vector DB
        point_id = str(uuid.uuid4())
        qdrant.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=data # We save the raw JSON as metadata so we can retrieve the URL later
                )
            ]
        )
        
        print(f"Embedded & Saved -> {data['title']}")

except KeyboardInterrupt:
    print("Stopping processor...")
finally:
    consumer.close()