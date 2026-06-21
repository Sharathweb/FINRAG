import logging
from pymilvus import Collection, CollectionSchema, DataType, FieldSchema, connections, utility

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from app.core.bce.embedding_client import EmbeddingClient

# Establish Milvus connection
connections.connect("default", host="localhost", port="19530")
embedding_client = EmbeddingClient("/data/WoLLM/bce-embedding-base_v1")

# Read text document
with open("test.txt", "r", encoding="utf-8") as f:
    text_chunks = f.read().splitlines()

# Generate embeddings
embeddings = embedding_client.get_embedding(text_chunks)

# Droping the existing collection to new schema
if utility.has_collection("FIN_RAG"):
    collection = Collection("FIN_RAG")
    collection.drop()
    print("FIN_RAG collection dropped successfully.")

# Define Collection Schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=100),
    FieldSchema(name="kb_name", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="file_name", dtype=DataType.VARCHAR, max_length=100),
    FieldSchema(name="chunk_id", dtype=DataType.INT64),
    FieldSchema(name="chunk_content", dtype=DataType.VARCHAR, max_length=1024), # Increased length for content
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=768),
]

schema = CollectionSchema(fields=fields, description="Knowledge base collection")

# Initialize/Get Collection
collection_name = "test_collection3"
collection = Collection(collection_name, schema=schema)

# Create Index
index_params = {
    "metric_type": "L2",
    "index_type": "IVF_FLAT",
    "params": {"nlist": 128},
}
collection.create_index(field_name="embedding", index_params=index_params)

# Prepare and Insert Entities
# Note: Ensure the order matches the schema fields exactly
entities = [
    ["test_kb"] * len(text_chunks),
    ["test_file.txt"] * len(text_chunks),
    list(range(len(text_chunks))),
    text_chunks,
    embeddings
]

logger.info(f"Inserting {len(text_chunks)} entities into {collection_name}...")
collection.insert(entities)

# Flush to persist data and load for searching
collection.flush()
collection.load()

logger.info(f"Collection {collection_name} successfully ingested and loaded.")