#!/bin/bash

# Create the proto directory if it doesn't exist
mkdir -p app/proto

# Generate Python code from proto file
python -m grpc_tools.protoc \
    -I app/proto \
    --python_out=app/proto \
    --grpc_python_out=app/proto \
    app/proto/auth_service.proto

# Make the generated files importable
touch app/proto/__init__.py

echo "Proto files generated successfully!" 