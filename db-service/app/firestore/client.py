import os
import json
from typing import Optional, Type, TypeVar, Dict, Any
from google.cloud import firestore
from pydantic import BaseModel, ValidationError
from dotenv import load_dotenv

# Load environment variables from .env.local
load_dotenv('.env.local')

T = TypeVar('T', bound=BaseModel)

class FirestoreClient:
    """
    A generic Firestore client for CRUD operations with Pydantic models.
    Usage:
        client = FirestoreClient()
        client.add('users', user_model_instance)
    """
    def __init__(self, project_id: Optional[str] = None, credential_path: Optional[str] = None):
        try:
            if credential_path:
                if not os.path.exists(credential_path):
                    raise FileNotFoundError(f"Credentials file {credential_path} does not exist")
                self.db = firestore.Client.from_service_account_json(credential_path)
            else:
                # Create credentials dict from environment variables
                credentials = {
                    "type": "service_account",
                    "project_id": os.getenv('FIREBASE_PROJECT_ID'),
                    "private_key_id": os.getenv('FIREBASE_PRIVATE_KEY_ID'),
                    "private_key": os.getenv('FIREBASE_PRIVATE_KEY').replace('\\n', '\n'),
                    "client_email": os.getenv('FIREBASE_CLIENT_EMAIL'),
                    "client_id": os.getenv('FIREBASE_CLIENT_ID'),
                    "auth_uri": os.getenv('FIREBASE_AUTH_URI'),
                    "token_uri": os.getenv('FIREBASE_TOKEN_URI'),
                    "auth_provider_x509_cert_url": os.getenv('FIREBASE_AUTH_PROVIDER_X509_CERT_URL'),
                    "client_x509_cert_url": os.getenv('FIREBASE_CLIENT_X509_CERT_URL'),
                    "universe_domain": os.getenv('FIREBASE_UNIVERSE_DOMAIN')
                }

                # Write credentials to a temporary file
                temp_cred_path = 'temp_credentials.json'
                with open(temp_cred_path, 'w') as f:
                    json.dump(credentials, f)

                try:
                    self.db = firestore.Client.from_service_account_json(temp_cred_path)
                finally:
                    # Clean up the temporary file
                    if os.path.exists(temp_cred_path):
                        os.remove(temp_cred_path)

            print(f"Firestore Client initialized for project {self.db.project}")
        except Exception as e:
            print(f"Error initializing Firestore client: {e}")
            raise ConnectionError(f"Failed to initialize Firestore client: {e}") from e

    def _serialized_model(self, data: BaseModel) -> Dict[str, Any]:
        if hasattr(data, 'model_dump'):
            return data.model_dump(mode='json', exclude_unset=True)
        else:
            return data.model_dump(exclude_unset=True)

    def _deserialize_doc(self, doc_snapshot: firestore.DocumentSnapshot, model: Type[T]) -> Optional[T]:
        if not doc_snapshot.exists:
            return None
        try:
            data = doc_snapshot.to_dict()
            if data is None:
                return None
            if 'id' not in data:
                data['id'] = doc_snapshot.id
            return model(**data)
        except ValidationError as e:
            print(f"Pydantic Validation Error Deserialization doc: {doc_snapshot.id}: {e}")
            return None
        except Exception as e:
            print(f"Error deserialization doc: {doc_snapshot.id} : {e}")
            return None

    def add(self, collection_name: str, data: BaseModel, document_id: Optional[str] = None) -> str:
        collection_ref = self.db.collection(collection_name)
        serialized = self._serialized_model(data)
        if document_id:
            doc_ref = collection_ref.document(document_id)
            doc_ref.set(serialized)
            return doc_ref.id
        else:
            doc_ref = collection_ref.add(serialized)[1]
            return doc_ref.id

    def get(self, collection_name: str, document_id: str, model: Type[T]) -> Optional[T]:
        doc_ref = self.db.collection(collection_name).document(document_id)
        doc_snapshot = doc_ref.get()
        return self._deserialize_doc(doc_snapshot, model)

    def update(self, collection_name: str, document_id: str, data: BaseModel) -> bool:
        doc_ref = self.db.collection(collection_name).document(document_id)
        try:
            doc_ref.update(self._serialized_model(data))
            return True
        except Exception as e:
            print(f"Error updating document {document_id} in {collection_name}: {e}")
            return False

    def delete(self, collection_name: str, document_id: str) -> bool:
        doc_ref = self.db.collection(collection_name).document(document_id)
        try:
            doc_ref.delete()
            return True
        except Exception as e:
            print(f"Error deleting document {document_id} in {collection_name}: {e}")
            return False

    def list_all(self, collection_name: str, model: Type[T]) -> Dict[str, T]:
        collection_ref = self.db.collection(collection_name)
        docs = collection_ref.stream()
        result = {}
        for doc in docs:
            obj = self._deserialize_doc(doc, model)
            if obj:
                result[doc.id] = obj
        return result 