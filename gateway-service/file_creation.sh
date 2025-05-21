#!/bin/bash

# Create directories
mkdir -p app/core \
         app/api/v1/endpoints \
         app/services \
         app/schemas \
         tests

# Create files
touch app/__init__.py \
      app/main.py \
      app/core/__init__.py \
      app/core/config.py \
      app/core/logging.py \
      app/api/__init__.py \
      app/api/v1/__init__.py \
      app/api/v1/endpoints/__init__.py \
      app/api/v1/endpoints/health.py \
      app/services/__init__.py \
      app/services/grpc_client.py \
      app/schemas/__init__.py \
      app/schemas/base.py \
      tests/__init__.py \
      tests/conftest.py \
      .env.example \
      .gitignore \
      Dockerfile \
      docker-compose.yml \
      requirements.txt \
      README.md

echo "FastAPI project structure created successfully!"
