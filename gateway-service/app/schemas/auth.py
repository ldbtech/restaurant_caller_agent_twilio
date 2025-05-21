from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    display_name: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_id: str
    email: str
    display_name: str
    role: str

class TokenValidation(BaseModel):
    is_valid: bool
    user_id: str | None = None
    claims: dict | None = None
    error_message: str | None = None 