from .base_service import BaseService
from app.services.grpc_client import get_grpc_client

class DbService(BaseService):
    def __init__(self):
        super().__init__("db")
        self.client = get_grpc_client()
        self.stub = self.client.get_stub("db")
    
    def get_user_profile(self, user_id: str):
        request = {"id": user_id}
        return self._make_grpc_call(self.stub.GetUserProfile, request)
    
    # Add other DB service methods here 