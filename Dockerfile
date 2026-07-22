FROM python:3.11-slim

# Patch the underlying Linux OS immediately to clear CVEs
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy our scripts into the container
COPY . .