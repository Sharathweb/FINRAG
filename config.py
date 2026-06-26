import os
from pathlib import Path

# --- Add these lines to define the paths ---
BASE_DIR = Path("D:/RAG_Project/FinRAG")
VECTOR_DB_PATH = os.getenv("MILVUS_URI", str(BASE_DIR / "milvus_local.db"))
# -------------------------------------------

COLLECTION_NAME = "fin_rag_collection"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RAG_PROMPT = "Your RAG prompt goes here..." # Ensure this exists
RERANK_MODEL = "maidalun1020/bce-reranker-base_v1" # Ensure this exists

# Add any other variables you are importing here as well