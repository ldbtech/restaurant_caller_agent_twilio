# app/main.py
import logging
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "proto"))

import grpc
import twilio_service_pb2 as pb2
import twilio_service_pb2_grpc as pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp

from fastapi import FastAPI, Request

app = FastAPI()

LLM_GRPC_HOST = os.getenv("LLM_GRPC_HOST", "llm-service")
LLM_GRPC_PORT = os.getenv("LLM_GRPC_PORT", "8080")
GRPC_TARGET = f"{LLM_GRPC_HOST}:{LLM_GRPC_PORT}"

from fastapi.concurrency import run_in_threadpool

@app.post("/rag")
async def rag_route(request: Request):
    data = await request.json()
    customer_text = data.get("message", "")
    session_id = data.get("session_id", "mock_session")

    channel = grpc.insecure_channel(GRPC_TARGET)
    stub = pb2_grpc.TwilioServiceStub(channel)

    grpc_request = pb2.RAGRequest(
        session_id=session_id,
        customer_text=customer_text,
        history=[]
    )

    print("📤 Sending request to llm-service...")

    try:
        response = await run_in_threadpool(stub.SendCustomerText, grpc_request)
        print(f"✅ Got response: {response}")
        return {"session_id": response.session_id, "ai_text": response.ai_text}
    except grpc.RpcError as e:
        print(f"❌ gRPC error: {e.code()} - {e.details()}")
        return {"error": f"{e.code()} - {e.details()}"}
