import os
import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin.auth import UserRecord, EmailAlreadyExistsError, UserNotFoundError
from typing import Optional

from ..models.auth_models import UserInfoResponse

class FirebaseAuthService:
    """ Handles Firebase auth Operations """

    def __init__(self, credential_path: Optional[str] = None):

        try:
            if firebase_admin._app:
                print("Firebase Admin SDK already initialized")
                self.app = firebase_admin.get_app()
            else:
                if credential_path:
                    if not os.path.exists(credential_path):
                        raise FileNotFoundError(f"Credentials file {credential_path} not found")
                    cred = credentials.Certificate(credential_path)
                    print("Firebase Admin SDK initialized")
                else:
                    print("Initializing Firebase Admin SDK using default credentials")
                    cred = credentials.ApplicationDefault()
                self.app = firebase_admin.initialize_app(cred)

                print("Firebase Admin SDK initialized successfully")
        except Exception as e:
            print(f"Failed to initialize Firebase Admin SDK: {e}")
            raise ConnectionError(f"Failed to initialize Firebase Admin SDK: {e}") from e

    def create_user(self, email: str, password: str, display_name: Optional[str] = None) -> UserRecord:
        """
         - Creates a new user in Firebase Authentic -
        :param email: Email address of the user
        :param password: User's password (must be >= 6)
        :param display_name: User's display name for the user.
        :return: The created UserRecord object.

        :raises: EmailAlreadyExistsError, ValueError, Exception
        """

        try:
            user_record = auth.create_user(email=email, password=password, display_name=display_name, app=self.app)
            print("Created new user in Firebase Authentic successfully")
            return user_record
        except EmailAlreadyExistsError as e:
            print(f"Email address already exists in Firebase Authentic: {e}")
            raise EmailAlreadyExistsError(f"Email address already exists in Firebase Authentic: {e}") from e
        except ValueError as e:
            print(f"Failed to create new user in Firebase Authentic: {e}")
            raise ValueError(f"Failed to create new user in Firebase Authentic: {e}") from e
        except Exception as e:
            print(f"An expected error occurred during user creation: {e}")
            raise ConnectionError(f"Failed to create new user in Firebase Authentic: {e}") from e

    def verify_id_token(self, id_token: str) -> UserInfoResponse:
        """
        Verifies a firebase ID token sent from the client.
        :param id_token: The firebase ID token string.
        :return: UserInfoResponse object with the decoder user details.
        :return:
        """


