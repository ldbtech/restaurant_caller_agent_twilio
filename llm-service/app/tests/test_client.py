# test_client.py
import grpc
from app.proto import twilio_service_pb2, twilio_service_pb2_grpc

channel = grpc.insecure_channel('localhost:8080')
stub = twilio_service_pb2_grpc.TwilioServiceStub(channel)

response = stub.SendCustomerText(twilio_service_pb2.RAGRequest(
    session_id="test123",
    customer_text="What kind of pizza do you have?",
    history=[]
))

print("AI Response:", response.ai_text)