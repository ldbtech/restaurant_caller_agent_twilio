from fastapi import APIRouter, HTTPException
from app.services.grpc_client import get_grpc_client
import socket
import psutil
import time
from typing import Dict, Any
import grpc
from datetime import datetime
from app.protos_generated import db_service_pb2

router = APIRouter()

def check_grpc_connection() -> Dict[str, Any]:
    """Check gRPC connection to db-service"""
    try:
        client = get_grpc_client()
        # Try to establish a connection with a timeout
        grpc.channel_ready_future(client.channel).result(timeout=2.0)
        
        # Try a simple GetUserProfile request with a test ID
        try:
            request = db_service_pb2.GetRequest(id="test_health_check")
            response = client.db_stub.GetUserProfile(request, timeout=2.0)
            return {
                "status": "healthy",
                "message": "Successfully connected to db-service",
                "details": "gRPC connection established"
            }
        except grpc.RpcError as e:
            # If we get a NOT_FOUND error, that's actually good - it means the service is up
            # but the test user doesn't exist
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return {
                    "status": "healthy",
                    "message": "Successfully connected to db-service",
                    "details": "Service is up but test user not found (expected)"
                }
            return {
                "status": "unhealthy",
                "message": f"gRPC request failed: {str(e)}"
            }
            
    except grpc.RpcError as e:
        return {
            "status": "unhealthy",
            "message": f"gRPC connection error: {str(e)}"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Unexpected error in gRPC connection: {str(e)}"
        }

def check_system_resources() -> Dict[str, Any]:
    """Check system resources"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            "status": "healthy",
            "resources": {
                "cpu_usage_percent": cpu_percent,
                "memory_usage_percent": memory.percent,
                "disk_usage_percent": disk.percent,
                "memory_available_gb": round(memory.available / (1024**3), 2),
                "disk_free_gb": round(disk.free / (1024**3), 2)
            }
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Error checking system resources: {str(e)}"
        }

def check_network() -> Dict[str, Any]:
    """Check network connectivity"""
    try:
        # Check if we can resolve DNS
        socket.gethostbyname('google.com')
        return {
            "status": "healthy",
            "message": "Network connectivity is good"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Network connectivity issue: {str(e)}"
        }

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Comprehensive health check endpoint that verifies:
    - gRPC connection to db-service
    - System resources (CPU, Memory, Disk)
    - Network connectivity
    - Application uptime
    """
    start_time = time.time()
    
    # Run all health checks
    grpc_status = check_grpc_connection()
    system_status = check_system_resources()
    network_status = check_network()
    
    # Calculate total response time
    response_time = time.time() - start_time
    
    # Determine overall health status
    is_healthy = all(
        check["status"] == "healthy" 
        for check in [grpc_status, system_status, network_status]
    )
    
    # Prepare response
    response = {
        "status": "healthy" if is_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": round(response_time * 1000, 2),
        "checks": {
            "grpc_connection": grpc_status,
            "system_resources": system_status,
            "network": network_status
        }
    }
    
    # If any check failed, include error details
    if not is_healthy:
        response["errors"] = [
            check["message"] 
            for check in [grpc_status, system_status, network_status]
            if check["status"] == "unhealthy"
        ]
    
    # Return appropriate status code
    if not is_healthy:
        raise HTTPException(
            status_code=503,
            detail=response
        )
    
    return response