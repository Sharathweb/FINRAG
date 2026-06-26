from pymilvus import MilvusClient
import os

# 1. Use an environment variable to define where your DB is.
# If on Render, set MILVUS_URI to '/mnt/data/milvus_local.db'
# For local testing, it defaults to './milvus_local.db'
db_path = os.getenv("MILVUS_URI", "./milvus_local.db")

try:
    # 2. Initialize the client (This acts as your connection)
    client = MilvusClient(uri=db_path)
    
    print(f"Successfully connected to Milvus: {db_path}")
    
    # Example: Verify it works by listing collections
    print("Collections:", client.list_collections())

except Exception as e:
    print(f"Failed to connect: {e}")