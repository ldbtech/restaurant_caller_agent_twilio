# app/main.py
import sys
import os

# Add the 'proto' directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'proto')))
from datetime import datetime, timezone
import grpc
from concurrent import futures
from app.proto import twilio_service_pb2
from app.proto import twilio_service_pb2_grpc
from google.protobuf.timestamp_pb2 import Timestamp  # <--- Correct import
from app.llm_model import LLMModel
from app.loader_retriever import MenuRetriever, MenuEmbeddingLoader
from dotenv import load_dotenv
import logging

env_file = ".env.k8s" if os.getenv("K8S_ENV") else ".env.local"
load_dotenv(dotenv_path=env_file)

logging.basicConfig(level=logging.INFO)

#redis_client = redis.Redis(host='localhost', port=6379, db=0)  # Adjust host/port as needed
class TwilioServiceServicer(twilio_service_pb2_grpc.TwilioServiceServicer):
    def __init__(self):
        restaurant_id = os.getenv("RESTAURANT_ID", "restaurant_a")
        collection_name = os.getenv("CHROMA_COLLECTION_NAME", "menu_collection")
        menu_dir = os.getenv("MENU_DIR", os.path.join(os.path.dirname(__file__), "tests", "menus"))

        try:
            # Ensure the Chroma collection exists by loading and embedding
            loader = MenuEmbeddingLoader(
                menu_dir=menu_dir,
                restaurant_id=restaurant_id,
                collection_name=collection_name
            )
            loader.load_and_embed()

            # Now initialize the retriever with the same info
            retriever = MenuRetriever(
                restaurant_id=restaurant_id,
                collection_name=collection_name
            )
        except Exception as e:
            print(f"❌ Failed to set up retriever for {restaurant_id}: {e}")
            retriever = None

        self.llm_model = LLMModel(retriever=retriever)

    def SendCustomerText(self, request, context):
        print(f"Received RAGRequest: Session ID={request.session_id}, Customer Text='{request.customer_text}'")

        # Get ai response from the dummy ai

        ai_response_text = self.llm_model.generate_response(request.customer_text, request.history)

        # Create the RagResponse
        response = twilio_service_pb2.RAGResponse(
            session_id=request.session_id,
            ai_text = ai_response_text,
            timestamp=Timestamp()
        )

        response.timestamp.FromDatetime(datetime.now(timezone.utc))

        logging.info(
            f"Sending RAGResponse: Session ID={response.session_id}, AI Text='{response.ai_text}', Timestamp='{response.timestamp.ToDatetime()}'")
        return response

import signal
import logging
logging.basicConfig(level=logging.INFO)
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    twilio_service_pb2_grpc.add_TwilioServiceServicer_to_server(TwilioServiceServicer(), server)

    host = os.environ.get("LLM_GRPC_HOST", "0.0.0.0")
    port = os.environ.get("LLM_GRPC_PORT", "8080")
    server_address = f"{host}:{port}"

    server.add_insecure_port(server_address)

    def handle_sigterm(*_):
        logging.info("Shutting down gRPC server...")
        server.stop(0)

    signal.signal(signal.SIGTERM, handle_sigterm)
    signal.signal(signal.SIGINT, handle_sigterm)

    server.start()
    print(f"Starting LLM gRPC server on {server_address}")
    server.wait_for_termination() # until the customer hangup.

if __name__ == '__main__':
    serve()