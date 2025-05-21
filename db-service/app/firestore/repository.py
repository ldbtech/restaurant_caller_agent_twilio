from typing import Type, TypeVar, Optional, Dict
from pydantic import BaseModel
from .client import FirestoreClient

T = TypeVar('T', bound=BaseModel)

class FirestoreRepository:
    """
    Base repository for Firestore operations. Extend this for each model if you want to encapsulate business logic.
    """
    def __init__(self, collection_name: str, model: Type[T], client: Optional[FirestoreClient] = None):
        self.collection_name = collection_name
        self.model = model
        self.client = client or FirestoreClient()

    def add(self, data: T, document_id: Optional[str] = None) -> str:
        return self.client.add(self.collection_name, data, document_id)

    def get(self, document_id: str) -> Optional[T]:
        return self.client.get(self.collection_name, document_id, self.model)

    def update(self, document_id: str, data: T) -> bool:
        return self.client.update(self.collection_name, document_id, data)

    def delete(self, document_id: str) -> bool:
        return self.client.delete(self.collection_name, document_id)

    def list_all(self) -> Dict[str, T]:
        return self.client.list_all(self.collection_name, self.model) 