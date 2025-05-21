#!/bin/bash

# Script to generate Python gRPC code from .proto files

# Define the directory where your .proto files are and where generated files will go.
# IMPORTANT: Adjust this if you chose a different name than 'app/protos_generated'.
PROTO_DIR="app/protos_generated"

# Define the main .proto file.
# IMPORTANT: Adjust this path if your .proto file is not directly inside PROTO_DIR
# or has a different name.
PROTO_FILE="$PROTO_DIR/db_service.proto"

echo "--- Starting Proto Generation ---"

# 1. Create the target directory if it doesn't exist
echo "Ensuring directory $PROTO_DIR exists..."
mkdir -p "$PROTO_DIR"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create directory $PROTO_DIR."
    exit 1
fi

# 2. Check if the .proto file exists
if [ ! -f "$PROTO_FILE" ]; then
    echo "ERROR: Proto file not found at $PROTO_FILE"
    echo "Please ensure your .proto file is correctly placed and named."
    exit 1
fi
echo "Found .proto file: $PROTO_FILE"

# 3. Generate Python code from proto file
echo "Generating Python code..."
python -m grpc_tools.protoc \
    -I"$PROTO_DIR" \
    --python_out="$PROTO_DIR" \
    --grpc_python_out="$PROTO_DIR" \
    "$PROTO_FILE"

# Check if protoc command was successful
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to generate Python code from $PROTO_FILE."
    echo "Check the output from grpc_tools.protoc for more details."
    exit 1
fi

# 4. Create (or touch) __init__.py to make the directory a Python package
echo "Creating/touching $PROTO_DIR/__init__.py to make it a package..."
touch "$PROTO_DIR/__init__.py"
if [ $? -ne 0 ]; then
    echo "ERROR: Failed to touch $PROTO_DIR/__init__.py."
    exit 1
fi

echo "--- Proto files generated successfully into $PROTO_DIR! ---"
