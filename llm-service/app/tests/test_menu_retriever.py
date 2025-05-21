import sys
import os
# Add both the app and proto directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../app/proto")))


from app.loader_retriever import MenuEmbeddingLoader, MenuRetriever

def test_menu_retriever_basic():
    # Use a test collection and menu file
    test_restaurant_id = "test"
    test_collection_name = "menu_collection"

    # Create loader and load the test menu
    loader = MenuEmbeddingLoader(
        menu_dir="app/tests/menus",  # test file lives here
        restaurant_id=test_restaurant_id,
        collection_name=test_collection_name
    )
    loader.load_and_embed()

    # Now retrieve using the same restaurant ID and collection base name
    retriever = MenuRetriever(
        restaurant_id=test_restaurant_id,
        collection_name=test_collection_name
    )

    # Run the actual test
    query = "What kind of burgers do you have?"
    response = retriever.get_relevant_chunks(query)
    assert isinstance(response, str)
    assert "burger" in response.lower()
