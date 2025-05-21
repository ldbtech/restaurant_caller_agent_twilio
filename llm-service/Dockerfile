# Use Python base image
FROM python:3.12-slim

# Install system dependencies for Chroma, Ollama bindings, etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Pre-copy requirements for better caching
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the source code
COPY . .

# Expose the gRPC port (match with your ENV or Kubernetes service)
EXPOSE 8080

# Default command to run the gRPC server
CMD ["python", "app/main.py"]
