import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.loader_retriever import MenuEmbeddingLoader

if __name__ == "__main__":
    loader = MenuEmbeddingLoader(
        menu_dir="app/tests/menus",
        restaurant_id="yemma"
    )
    loader.load_and_embed()
