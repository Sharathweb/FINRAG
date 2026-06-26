import os
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY: str = Field(validation_alias="google_api_key")
    EMBEDDING_MODEL: str = "maidalun1020/bce-embedding-base_v1"
    
    model_config = SettingsConfigDict(env_file=".env")

# 2. Create the instance
settings = Settings()

BASE_DIR = Path("D:/RAG Project/FinRAG")
VECTOR_DB_PATH = os.getenv("MILVUS_URI", str(BASE_DIR / "milvus_local.db"))

# Milvus & Model Configuration
COLLECTION_NAME = "FIN_RAG"
CHUNK_SIZE = 1000  # Increased to keep related sentences together
DEVICE = "cpu"
EMBEDDING_MODEL = settings.EMBEDDING_MODEL
RERANK_MODEL = "maidalun1020/bce-reranker-base_v1"
GEMINI_API_KEY = settings.GEMINI_API_KEY

# Notification & Storage
NOTIFY_URL = "http://39.96.174.204/api/medical-assistant/knowledge/file/vector/complete"
CACHE_DIR = ".cache"
STORAGE_TYPE = "local"
STORAGE_DIR = "storage"

if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Core RAG Prompt - Updated to be more helpful and less restrictive
RAG_PROMPT = """You are a helpful assistant. Use the following Reference Information to answer the question.
If the reference information is not sufficient, please provide an answer based on your general knowledge but mention if you are doing so.
Do not refuse to answer unless the question is completely unrelated to financial or business topics.

Reference Information:
{context}
---
My Question:
{question}
---
Your Response:"""

if __name__ == "__main__":
    print("Config Loaded Successfully.")