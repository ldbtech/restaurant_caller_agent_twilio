import grpc
from typing import Optional, Dict
import sys
import os
from pathlib import Path

class GrpcClient:
    def __init__(self, service_configs: Dict[str, Dict[str, str]]):
        """
        Initialize gRPC client for multiple services
        
        Args:
            service_configs: Dictionary of service configurations
            Example:
            {
                "db": {
                    "host": "localhost",
                    "port": "50051",
                    "proto_path": "path/to/db/proto"
                },
                "auth": {
                    "host": "localhost",
                    "port": "50052",
                    "proto_path": "path/to/auth/proto"
                }
            }
        """
        self.channels = {}
        self.stubs = {}
        
        # Add proto paths to Python path
        for service_name, config in service_configs.items():
            proto_path = config.get("proto_path")
            if proto_path:
                sys.path.append(str(Path(proto_path).absolute()))
        
        # Import proto stubs
        from app.protos_generated import db_service_pb2_grpc
        from auth_service_pb2_grpc import AuthServiceStub
        
        # Initialize channels and stubs for each service
        for service_name, config in service_configs.items():
            channel = grpc.insecure_channel(f"{config['host']}:{config['port']}")
            self.channels[service_name] = channel
            
            # Initialize appropriate stub based on service
            if service_name == "db":
                self.stubs[service_name] = db_service_pb2_grpc.DatabaseServiceStub(channel)
            elif service_name == "auth":
                self.stubs[service_name] = AuthServiceStub(channel)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        for channel in self.channels.values():
            channel.close()
    
    def get_stub(self, service_name: str):
        """Get the stub for a specific service"""
        return self.stubs.get(service_name)

# Singleton instance
_grpc_client: Optional[GrpcClient] = None

def get_grpc_client() -> GrpcClient:
    global _grpc_client
    if _grpc_client is None:
        from app.core.config import settings
        service_configs = {
            "db": {
                "host": settings.DB_SERVICE_HOST,
                "port": settings.DB_SERVICE_PORT,
                "proto_path": settings.DB_SERVICE_PROTO_PATH
            },
            "auth": {
                "host": settings.AUTH_SERVICE_HOST,
                "port": settings.AUTH_SERVICE_PORT,
                "proto_path": settings.AUTH_SERVICE_PROTO_PATH
            }
        }
        _grpc_client = GrpcClient(service_configs)
    return _grpc_client