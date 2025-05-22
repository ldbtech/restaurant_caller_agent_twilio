# auth-service/pp/models/auth_models.py
from typing import Optional, Literal, Dict
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, validator
import re

class SignUpRequest(BaseModel):
    """Model for user registration request."""
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(
        ...,
        min_length=8,
        description="Password of the user (min 8 characters, must contain uppercase, lowercase, number, and special character)"
    )
    display_name: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Display name of the user"
    )
    university_name: Optional[str] = Field(
        default="University at Buffalo",
        description="Name of the university the student attends"
    )
    invitation_code: Optional[str] = Field(
        default=None,
        description="Invitation code for registration"
    )
    role: Literal["student", "professor", "admin"] = Field(
        default="student",
        description="User role in the system"
    )

    @validator('password')
    def validate_password_strength(cls, v):
        """Validate password strength."""
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @validator('display_name')
    def validate_display_name(cls, v):
        """Validate display name format."""
        if re.search(r'[<>{}[\]\\]', v):
            raise ValueError('Display name contains invalid characters')
        return v

class SignInRequest(BaseModel):
    """Model for user login request."""
    email: EmailStr = Field(..., description="Email address of the user")
    password: str = Field(..., description="Password of the user")

class VerifyTokenRequest(BaseModel):
    """Model for token verification request."""
    idToken: str = Field(..., description="Firebase ID token obtained after client-side sign-in")

class UserInfoResponse(BaseModel):
    """Model for user information response."""
    uid: str = Field(..., description="Firebase unique user ID")
    email: EmailStr = Field(..., description="Email address of the user")
    display_name: str = Field(..., description="Display name of the user")
    role: Literal["student", "professor", "admin"] = Field(
        default="student",
        description="User role in the system"
    )
    university_name: Optional[str] = Field(
        default=None,
        description="Name of the university"
    )
    email_verified: bool = Field(
        default=False,
        description="Whether the email has been verified"
    )
    photo_url: Optional[str] = Field(
        default=None,
        description="URL of the user's profile photo"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the user was created"
    )
    last_sign_in: Optional[datetime] = Field(
        default=None,
        description="Timestamp of the last sign-in"
    )
    custom_claims: Optional[Dict] = Field(
        default=None,
        description="Custom claims associated with the user"
    )

class SignUpResponse(BaseModel):
    """Model for registration response."""
    uid: str = Field(..., description="Firebase unique user ID")
    email: EmailStr = Field(..., description="Email address of the user")
    display_name: str = Field(..., description="Display name of the user")
    role: str = Field(..., description="User role in the system")
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    message: str = Field(
        default="User created successfully",
        description="Confirmation message"
    )

class TokenResponse(BaseModel):
    """Model for token response."""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(
        default="Bearer",
        description="Type of the token"
    )
    expires_in: int = Field(
        ...,
        description="Token expiration time in seconds"
    )

class ErrorResponse(BaseModel):
    """Model for error response."""
    error: str = Field(..., description="Error message")
    error_code: str = Field(..., description="Error code")
    details: Optional[Dict] = Field(
        default=None,
        description="Additional error details"
    )