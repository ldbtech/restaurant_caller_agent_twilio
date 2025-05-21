class FirestoreError(Exception):
    """Base exception for Firestore operations."""
    pass

class FirestoreValidationError(FirestoreError):
    """Raised when a Pydantic validation error occurs during Firestore operations."""
    pass

class FirestoreConnectionError(FirestoreError):
    """Raised when Firestore client fails to connect."""
    pass 