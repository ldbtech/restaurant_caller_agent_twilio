import sys 

print(f"Initial sys.path: {sys.path}")

import grpc
from concurrent import futures
from google.protobuf import timestamp_pb2
from google.protobuf import struct_pb2
from datetime import datetime
import time

from .firestore.client import FirestoreClient
from .models import UserProfile, UserSettings, Event, EventResource, AiSuggestion
from .protos_generated import db_service_pb2
from .protos_generated import db_service_pb2_grpc



def datetime_to_timestamp(dt: datetime) -> timestamp_pb2.Timestamp:
    ts = timestamp_pb2.Timestamp()
    ts.FromDatetime(dt)
    return ts

def timestamp_to_datetime(ts: timestamp_pb2.Timestamp) -> datetime:
    return ts.ToDatetime()

class DatabaseServiceServicer(db_service_pb2_grpc.DatabaseServiceServicer):
    def __init__(self):
        self.client = FirestoreClient()

    # User Profile Methods
    def CreateUserProfile(self, request, context):
        try:
            profile = UserProfile(
                id=request.id,
                displayName=request.display_name,
                email=request.email,
                role=request.role,
                school=request.school,
                preferences=dict(request.preferences),
                bio=request.bio,
                avatarUrl=request.avatar_url,
                createdAt=timestamp_to_datetime(request.created_at),
                updatedAt=timestamp_to_datetime(request.updated_at)
            )
            doc_id = self.client.add("users", profile)
            return db_service_pb2.UserProfileResponse(
                profile=request,
                message=f"User profile created with ID: {doc_id}"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return db_service_pb2.UserProfileResponse()

    def GetUserProfile(self, request, context):
        try:
            profile = self.client.get("users", request.id, UserProfile)
            if not profile:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"User profile not found with ID: {request.id}")
                return db_service_pb2.UserProfileResponse()

            response = db_service_pb2.UserProfileRequest(
                id=profile.id,
                display_name=profile.displayName,
                email=profile.email,
                role=profile.role,
                school=profile.school,
                preferences=struct_pb2.Struct(fields=profile.preferences),
                bio=profile.bio,
                avatar_url=profile.avatarUrl,
                created_at=datetime_to_timestamp(profile.createdAt),
                updated_at=datetime_to_timestamp(profile.updatedAt)
            )
            return db_service_pb2.UserProfileResponse(
                profile=response,
                message="User profile retrieved successfully"
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return db_service_pb2.UserProfileResponse()

    # Similar implementations for other methods...

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    db_service_pb2_grpc.add_DatabaseServiceServicer_to_server(
        DatabaseServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC Server started on port 50051")
    try:
        while True:
            time.sleep(86400)  # One day in seconds
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve() 