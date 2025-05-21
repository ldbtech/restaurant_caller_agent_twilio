import os
from datetime import datetime, timedelta
from typing import Dict, Optional
import firebase_admin
from firebase_admin import auth, credentials
from google.protobuf import timestamp_pb2
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class AuthService:
    def __init__(self):
        """Initialize Firebase Admin SDK."""
        try:
            # Check if required environment variables are set
            required_vars = [
                'FIREBASE_PROJECT_ID',
                'FIREBASE_PRIVATE_KEY_ID',
                'FIREBASE_PRIVATE_KEY',
                'FIREBASE_CLIENT_EMAIL',
                'FIREBASE_CLIENT_ID',
                'FIREBASE_AUTH_URI',
                'FIREBASE_TOKEN_URI',
                'FIREBASE_AUTH_PROVIDER_X509_CERT_URL',
                'FIREBASE_CLIENT_X509_CERT_URL',
                'FIREBASE_UNIVERSE_DOMAIN'
            ]
            
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

            # Initialize Firebase Admin SDK with credentials from environment
            cred = credentials.Certificate({
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
            })
            
            firebase_admin.initialize_app(cred)
            print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Error initializing Firebase Admin SDK: {e}")
            raise

    def register_user(self, email: str, password: str, display_name: str, role: str = "student") -> Dict:
        """Register a new user."""
        try:
            # Create user in Firebase Auth
            user = auth.create_user(
                email=email,
                password=password,
                display_name=display_name
            )

            # Set custom claims
            auth.set_custom_user_claims(user.uid, {"role": role})

            # Create custom tokens
            access_token = auth.create_custom_token(user.uid)
            refresh_token = auth.create_custom_token(user.uid, {"refresh": True})

            return {
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": role,
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except Exception as e:
            raise Exception(f"Error registering user: {str(e)}")

    def login_user(self, email: str, password: str) -> Dict:
        """Login a user."""
        try:
            # Get user by email
            user = auth.get_user_by_email(email)
            
            # Create custom tokens
            access_token = auth.create_custom_token(user.uid)
            refresh_token = auth.create_custom_token(user.uid, {"refresh": True})

            return {
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.custom_claims.get("role", "student"),
                "access_token": access_token,
                "refresh_token": refresh_token
            }
        except Exception as e:
            raise Exception(f"Error logging in user: {str(e)}")

    def validate_token(self, token: str) -> Dict:
        """Validate a Firebase ID token."""
        try:
            decoded_token = auth.verify_id_token(token)
            return {
                "is_valid": True,
                "user_id": decoded_token["uid"],
                "claims": decoded_token
            }
        except Exception as e:
            return {
                "is_valid": False,
                "error_message": str(e)
            }

    def get_user_profile(self, user_id: str) -> Dict:
        """Get user profile information."""
        try:
            user = auth.get_user(user_id)
            return {
                "user_id": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "role": user.custom_claims.get("role", "student"),
                "custom_claims": user.custom_claims,
                "created_at": user.user_metadata.creation_timestamp,
                "updated_at": user.user_metadata.last_sign_in_timestamp
            }
        except Exception as e:
            raise Exception(f"Error getting user profile: {str(e)}")

    def update_user_profile(self, user_id: str, display_name: Optional[str] = None,
                          email: Optional[str] = None, role: Optional[str] = None,
                          custom_claims: Optional[Dict] = None) -> Dict:
        """Update user profile information."""
        try:
            update_data = {}
            if display_name:
                update_data["display_name"] = display_name
            if email:
                update_data["email"] = email

            # Update user profile
            user = auth.update_user(user_id, **update_data)

            # Update custom claims if provided
            if role or custom_claims:
                current_claims = user.custom_claims or {}
                if role:
                    current_claims["role"] = role
                if custom_claims:
                    current_claims.update(custom_claims)
                auth.set_custom_user_claims(user_id, current_claims)

            return self.get_user_profile(user_id)
        except Exception as e:
            raise Exception(f"Error updating user profile: {str(e)}")

    def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        try:
            auth.delete_user(user_id)
            return True
        except Exception as e:
            raise Exception(f"Error deleting user: {str(e)}")

    def revoke_token(self, token: str) -> bool:
        """Revoke a refresh token."""
        try:
            auth.revoke_refresh_tokens(token)
            return True
        except Exception as e:
            raise Exception(f"Error revoking token: {str(e)}")

    @staticmethod
    def datetime_to_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
        """Convert datetime to protobuf timestamp."""
        ts = timestamp_pb2.Timestamp()
        ts.FromDatetime(dt)
        return ts 