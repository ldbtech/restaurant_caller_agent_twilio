import sys
import os
# Add both the app and proto directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/proto")))

from app.loader_retriever import MenuRetriever
from app.llm_model import LLMModel
from google.protobuf.timestamp_pb2 import Timestamp
from datetime import datetime, timezone

from app.loader_retriever import MenuEmbeddingLoader, MenuRetriever
from app.llm_model import LLMModel

def test_llm_response():
    # Make sure test data exists for "yemma"
    loader = MenuEmbeddingLoader(
        menu_dir="app/tests/menus",  # or wherever your test menu lives
        restaurant_id="yemma"
    )
    loader.load_and_embed()

    # Now you can retrieve
    retriever = MenuRetriever(restaurant_id="restaurant_a")
    llm = LLMModel(retriever=retriever)

    query = "Do you have vegan options?"
    history = []
    response = llm.generate_response(query, history)

    assert isinstance(response, str)
    assert len(response) > 0
