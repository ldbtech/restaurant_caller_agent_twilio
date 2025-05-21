import sys
import os
# Add both the app and proto directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/proto")))

import grpc
import pytest
from app.proto import twilio_service_pb2, twilio_service_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timezone

@pytest.fixture
def grpc_stub():
    channel = grpc.insecure_channel("localhost:8080")
    stub = twilio_service_pb2_grpc.TwilioServiceStub(channel)
    yield stub

def test_send_customer_text(grpc_stub):
    now = datetime.now(timezone.utc)
    timestamp = Timestamp()
    timestamp.FromDatetime(now)

    request = twilio_service_pb2.RAGRequest(
        session_id="test_session",
        customer_text="What are the meal options?",
        history=[
            twilio_service_pb2.ConversationTurn(
                role="customer",
                text="Hi there!",
                timestamp=timestamp
            )
        ]
    )
    response = grpc_stub.SendCustomerText(request)
    assert response.session_id == "test_session"
    assert isinstance(response.ai_text, str)
    assert response.ai_text.strip() != ""
