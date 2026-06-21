from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient
from app.core.bce.embedding_client import EmbeddingClient
from conf.config import EMBEDDING_MODEL

# 1. Initialize services
client = CustomerMilvusClient()
embedder = EmbeddingClient(EMBEDDING_MODEL)

# 2. Define your test question
question = "Who is the entity registrant, and what is their address?"

# 3. Get the vector representation of the question
query_embedding = embedder.get_embedding([question])

# 4. Perform retrieval and generation
# Note: Ensure the category_ids matches the one you used in test_ingestion
print("Querying the database...")
rag_result, retrieved_chunks = client.retrieval_and_generate(
    query_emb=query_embedding, 
    topK=5, 
    score=0.5, 
    category_ids=["101"], 
    messages=[{"role": "user", "content": question}]
)

print("\n--- AI Response ---")
print(rag_result)