import os
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.grpc_server import serve

if __name__ == '__main__':
    serve() 