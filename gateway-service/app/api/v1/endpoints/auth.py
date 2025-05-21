from fastapi import APIRouter, Depends
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, TokenValidation
from app.services.auth_service import AuthService

router = APIRouter()

def get_auth_service():
    return AuthService()

@router.post("/register", response_model=TokenResponse)
async def register_user(
    user_data: UserRegister,
    auth_service: AuthService = Depends(get_auth_service)
):
    print(f"Received user data: {user_data}")
    response = auth_service.register_user(
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name,
        role=user_data.role
    )
    return TokenResponse(**response)

@router.post("/login", response_model=TokenResponse)
async def login_user(
    user_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    response = auth_service.login_user(
        email=user_data.email,
        password=user_data.password
    )
    return TokenResponse(**response)

@router.post("/validate-token", response_model=TokenValidation)
async def validate_token(
    token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    response = auth_service.validate_token(token)
    return TokenValidation(**response) 