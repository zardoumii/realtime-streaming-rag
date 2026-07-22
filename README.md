Real-Time Streaming RAG Architecture

An end-to-end event-driven Machine Learning pipeline that captures live data streams, generates embeddings on the fly, and serves them via a semantic search API for Retrieval-Augmented Generation (RAG).

New: Now features a built-in web frontend and local LLM integration for entirely offline, GPU-accelerated RAG!

🏗️ Architecture

Ingestion (Producer): Listens to the live Wikipedia Server-Sent Events (SSE) stream.

Message Broker (Redpanda/Kafka): Buffers the high-throughput stream to ensure zero data loss and decouple ingestion from processing.

Stream Processor: Consumes messages continuously, chunks the text, and generates 384-dimensional embeddings using sentence-transformers (all-MiniLM-L6-v2).

Vector Database (Qdrant): Stores the dense vectors and metadata for sub-millisecond similarity search.

Retrieval API (FastAPI): Exposes an endpoint that embeds user queries and retrieves the most relevant real-time edits.

LLM Generation: Uses the openai python client connected to a local Ollama instance to synthesize answers based strictly on live data.

Web UI: A lightweight, vanilla HTML/JS frontend served directly by FastAPI for a ChatGPT-style chat experience.

🚀 Tech Stack

Python 3.11

Apache Kafka (Redpanda) - Event Streaming

Qdrant - Vector Database

FastAPI - REST API & Web Server

Docker & Docker Compose - Containerization & Orchestration

Ollama (Llama 3 / 3.2) - Local LLM Generation

HTML/CSS/JS - Frontend Interface

⚙️ Quick Start

1. Clone the repository

git clone https://github.com/YOUR-USERNAME/realtime-streaming-rag.git
cd realtime-streaming-rag


2. Start the Local LLM (Optional but recommended)
Install Ollama, then download the tiny model:

ollama run llama3.2:1b


3. Start the cluster
The entire backend microservice architecture is containerized. Start it with:

docker compose up --build -d


4. Access the Web UI
Once running, open your web browser and navigate to:
👉 http://127.0.0.1:8000

You can also access the interactive API documentation at http://127.0.0.1:8000/docs.

5. Shut down cleanly

docker compose down
