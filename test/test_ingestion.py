

from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient

# 1. Initialize your client
client = CustomerMilvusClient()

# 2. Define the file you just downloaded
# Ensure this matches exactly what is in your D:/RAG Project/FinRAG/data/ folder
test_file_info = [{
    "fileName": "View Filing Data.pdf",  # Update this!
    "parentId": "1",
    "categoryName": "Financials",
    "categoryId": "101",
    "fileId": "1",
    "fileSuffix": "pdf",
    "storagePath": "D:/RAG Project/FinRAG/data/"
}]

# 3. Run the embedding and ingestion
print("Starting ingestion...")
client.embedding_to_vdb(test_file_info)
print("Ingestion complete. You can now query your data!")