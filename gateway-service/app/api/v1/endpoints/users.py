from fastapi import APIRouter, HTTPException
from app.services.grpc_client import get_grpc_client
from app.protos_generated import db_service_pb2
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

router = APIRouter()

class UserProfileBase(BaseModel):
    display_name: str
    email: str
    role: str
    school: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None

class UserProfileCreate(UserProfileBase):
    pass

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

@router.post("/users", response_model=UserProfileResponse)
async def create_user(user: UserProfileCreate):
    try:
        client = get_grpc_client()
        now = datetime.utcnow()
        
        user_profile = db_service_pb2.UserProfileRequest(
            id=f"user_{now.timestamp()}",  # Generate a unique ID
            display_name=user.display_name,
            email=user.email,
            role=user.role,
            school=user.school,
            bio=user.bio,
            avatar_url=user.avatar_url,
            created_at=now.timestamp(),
            updated_at=now.timestamp()
        )
        
        response = client.db_stub.CreateUserProfile(user_profile)
        return UserProfileResponse(
            id=response.profile.id,
            display_name=response.profile.display_name,
            email=response.profile.email,
            role=response.profile.role,
            school=response.profile.school,
            bio=response.profile.bio,
            avatar_url=response.profile.avatar_url,
            created_at=datetime.fromtimestamp(response.profile.created_at),
            updated_at=datetime.fromtimestamp(response.profile.updated_at)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/users/{user_id}", response_model=UserProfileResponse)
async def get_user(user_id: str):
    try:
        client = get_grpc_client()
        request = db_service_pb2.GetRequest(id=user_id)
        response = client.db_stub.GetUserProfile(request)
        
        return UserProfileResponse(
            id=response.profile.id,
            display_name=response.profile.display_name,
            email=response.profile.email,
            role=response.profile.role,
            school=response.profile.school,
            bio=response.profile.bio,
            avatar_url=response.profile.avatar_url,
            created_at=datetime.fromtimestamp(response.profile.created_at),
            updated_at=datetime.fromtimestamp(response.profile.updated_at)
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.put("/users/{user_id}", response_model=UserProfileResponse)
async def update_user(user_id: str, user: UserProfileUpdate):
    try:
        client = get_grpc_client()
        now = datetime.utcnow()
        
        user_profile = db_service_pb2.UserProfileRequest(
            id=user_id,
            display_name=user.display_name,
            email=user.email,
            role=user.role,
            school=user.school,
            bio=user.bio,
            avatar_url=user.avatar_url,
            updated_at=now.timestamp()
        )
        
        response = client.db_stub.UpdateUserProfile(user_profile)
        return UserProfileResponse(
            id=response.profile.id,
            display_name=response.profile.display_name,
            email=response.profile.email,
            role=response.profile.role,
            school=response.profile.school,
            bio=response.profile.bio,
            avatar_url=response.profile.avatar_url,
            created_at=datetime.fromtimestamp(response.profile.created_at),
            updated_at=datetime.fromtimestamp(response.profile.updated_at)
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        client = get_grpc_client()
        request = db_service_pb2.GetRequest(id=user_id)
        response = client.db_stub.DeleteUserProfile(request)
        return {"success": response.success, "message": response.message}
    except Exception as e:
        raise HTTPException(status_code=404, detail="User not found") 