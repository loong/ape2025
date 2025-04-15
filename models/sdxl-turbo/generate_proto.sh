#!/bin/bash

# Create proto directory if it doesn't exist
mkdir -p proto

# Generate Python gRPC files
python -m grpc_tools.protoc \
    -I. \
    --python_out=. \
    --grpc_python_out=. \
    proto/sdxl_turbo.proto

echo "Generated gRPC Python files in proto directory" 