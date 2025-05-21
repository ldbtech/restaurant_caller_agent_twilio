# auth-service/pp/models/auth_models.py
from typing import Optional, Literal
from pydantic import BaseModel, EmailStr, Field

class SignUpRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., min_length=6, description="Password of the user")
    display_name: Optional[str] = Field(default=None, min_length=3, description="Display name of the user")
    university_name: Optional[str] = Field(default="University at Buffalo", description="Name of the university the student attends.")
    invitation_code: Optional[str] = Field(default=None, description="Invitation code of the user")

class SignInRequest(BaseModel):
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")

class VerifyTokenRequest(BaseModel):
    """ Model for a verification token sent from the client."""
    idToken: str = Field(..., description="Firebase ID token obtained after client-side sign-in.")

class UserInfoResponse(BaseModel):
    """ Model for returning user information after authentication/verification  """
    uid: str = Field(..., description="Firebase unique user ID")
    email: EmailStr = Field(..., description="Email address of the user")
    displayName: Optional[str] = Field(default=None, min_length=3, description="Display name of the user")
    major: Optional[Literal["Student"]] = Field(default=None, description="ser's profession, defaulting to Student for this service's focus.")
    emailVerified: Optional[bool] = Field(default=None)
    photoUrl: Optional[str] = Field(default=None)

class SignUpResponse(BaseModel):
    uid: str = Field(..., description="Firebase unique user ID")
    email: EmailStr = Field(default=None, description="Email address of the user")
    message: str = Field(default="User Created Successfully", description="Confirmation message")