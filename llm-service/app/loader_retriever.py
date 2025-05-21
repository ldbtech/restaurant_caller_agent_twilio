import chromadb
import os
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

# Load environment variables
env_file = ".env.k8s" if os.getenv("K8S_ENV") else ".env.local"
load_dotenv(dotenv_path=env_file)

# Load values from .env
CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "menu_collection")
RESTAURANT_ID = os.getenv("RESTAURANT_ID", "default")
MENU_DIR = os.getenv("MENU_DIR", "./menus")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")  # Optional

def get_chroma_client(persist=True, path=CHROMA_DB_PATH):
    return chromadb.PersistentClient(path) if persist else chromadb.EphemeralClient()


class MenuEmbeddingLoader:
    def __init__(self, menu_dir=MENU_DIR, collection_name=CHROMA_COLLECTION_NAME, restaurant_id=RESTAURANT_ID, client=None):
        self.menu_dir = menu_dir
        self.restaurant_id = restaurant_id
        self.collection_name = f"{collection_name}_{restaurant_id}"

        self.client = client or get_chroma_client()

        model_name = "all-MiniLM-L6-v2"
        self.embedding_func = embedding_functions.SentenceTransformerEmbeddingFunction(model_name)

        self.collection = self._setup_collection()

    def _setup_collection(self):
        if self.collection_name in [c.name for c in self.client.list_collections()]:
            self.client.delete_collection(name=self.collection_name)

        return self.client.create_collection(name=self.collection_name, embedding_function=self.embedding_func)

    def load_and_embed(self):
        docs, metadatas, ids = [], [], []

        for file_name in os.listdir(self.menu_dir):
            if file_name.endswith(".txt"):
                path = os.path.join(self.menu_dir, file_name)
                with open(path, "r", encoding="utf-8") as f:
                    text = f.read()
                    chunks = [p.strip() for p in text.split("\n\n") if p.strip()]
                    for i, chunk in enumerate(chunks):
                        doc_id = f"{self.restaurant_id}_{file_name}_{i}"
                        docs.append(chunk)
                        metadatas.append({"restaurant_id": self.restaurant_id})
                        ids.append(doc_id)

        self.collection.add(documents=docs, metadatas=metadatas, ids=ids)
        print(f"✅ Loaded {len(docs)} chunks for restaurant '{self.restaurant_id}' into collection '{self.collection_name}'")

class MenuRetriever:
    def __init__(self, collection_name=CHROMA_COLLECTION_NAME, restaurant_id=RESTAURANT_ID, client=None):
        self.collection_name = f"{collection_name}_{restaurant_id}"
        self.client = client or get_chroma_client()
        model_name = "all-MiniLM-L6-v2"
        self.embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name)

        self.collection = self.client.get_collection(name=self.collection_name, embedding_function=self.embedding_fn)

    def get_relevant_chunks(self, query, top_k=2):
        results = self.collection.query(query_texts=[query], n_results=top_k)
        return "\n\n".join(results["documents"][0])
