# app/tests/conftest.py
import pytest
from app.loader_retriever import MenuEmbeddingLoader, MenuRetriever
from app.llm_model import LLMModel

@pytest.fixture(scope="session")
def setup_test_collection():
    loader = MenuEmbeddingLoader(
        menu_dir="app/tests/menus",
        restaurant_id="restaurant_a"
    )
    loader.load_and_embed()

@pytest.fixture
def retriever(setup_test_collection):
    return MenuRetriever(restaurant_id="restaurant_a")

@pytest.fixture
def llm_model(retriever):
    return LLMModel(retriever=retriever)
