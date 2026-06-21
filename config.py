import os
from pathlib import Path

# Base directory for the project
BASE_DIR = Path("D:/RAG_Project/FinRAG")

# Local storage paths
DATA_DIR = BASE_DIR / "data"
VECTOR_DB_PATH = BASE_DIR / "milvus_local.db"

# Model settings
EMBEDDING_MODEL = "BAAI/bge-base-en-v1.5" # Excellent local model
LOCAL_LLM = "llama3" # Use Ollama to run this