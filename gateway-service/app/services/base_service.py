from typing import Any, Dict
import grpc
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class BaseService:
    def __init__(self, service_name: str):
        self.service_name = service_name
    
    def _handle_grpc_error(self, error: grpc.RpcError) -> None:
        """Handle gRPC errors and convert them to appropriate HTTP exceptions"""
        logger.error(f"gRPC error in {self.service_name} service: {error.code()}: {error.details()}")
        
        if error.code() == grpc.StatusCode.UNAVAILABLE:
            raise HTTPException(
                status_code=503,
                detail=f"{self.service_name} service is unavailable"
            )
        elif error.code() == grpc.StatusCode.NOT_FOUND:
            raise HTTPException(
                status_code=404,
                detail=f"Resource not found in {self.service_name} service"
            )
        elif error.code() == grpc.StatusCode.INVALID_ARGUMENT:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid argument in {self.service_name} service: {error.details()}"
            )
        elif error.code() == grpc.StatusCode.UNAUTHENTICATED:
            raise HTTPException(
                status_code=401,
                detail=f"Authentication failed in {self.service_name} service"
            )
        elif error.code() == grpc.StatusCode.PERMISSION_DENIED:
            raise HTTPException(
                status_code=403,
                detail=f"Permission denied in {self.service_name} service"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail=f"Error in {self.service_name} service: {error.details()}"
            )
    
    def _make_grpc_call(self, stub_method: Any, request: Any) -> Any:
        """Make a gRPC call with proper error handling"""
        try:
            logger.info(f"Making gRPC call to {self.service_name} service with request: {request}")
            response = stub_method(request)
            logger.info(f"Received response from {self.service_name} service: {response}")
            return response
        except grpc.RpcError as e:
            self._handle_grpc_error(e)
        except Exception as e:
            logger.error(f"Unexpected error in {self.service_name} service: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Unexpected error in {self.service_name} service: {str(e)}"
            ) 