# Real-Time Streaming RAG Architecture

An end-to-end event-driven Machine Learning pipeline that captures live data streams, generates embeddings on the fly, and serves them via a semantic search API for Retrieval-Augmented Generation (RAG).

## 🏗️ Architecture

1. **Ingestion (Producer):** Listens to the live Wikipedia Server-Sent Events (SSE) stream.
2. **Message Broker (Redpanda/Kafka):** Buffers the high-throughput stream to ensure zero data loss and decouple ingestion from processing.
3. **Stream Processor:** Consumes messages continuously, chunks the text, and generates 384-dimensional embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`).
4. **Vector Database (Qdrant):** Stores the dense vectors and metadata for sub-millisecond similarity search.
5. **Retrieval API (FastAPI):** Exposes an endpoint that embeds user queries, retrieves the most relevant real-time edits, and constructs a context-aware LLM prompt.

## 🚀 Tech Stack
* **Python 3.11**
* **Apache Kafka (Redpanda)** - Event Streaming
* **Qdrant** - Vector Database
* **FastAPI** - REST API
* **Docker & Docker Compose** - Containerization & Orchestration

## ⚙️ Quick Start

**1. Clone the repository**
```bash
git clone [https://github.com/YOUR-USERNAME/realtime-streaming-rag.git](https://github.com/YOUR-USERNAME/realtime-streaming-rag.git)
cd realtime-streaming-rag