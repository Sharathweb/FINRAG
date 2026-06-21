import os

# Milvus & Model Configuration
COLLECTION_NAME = "FIN_RAG"
CHUNK_SIZE = 500  # Renamed from SENTENCE_SIZE for clarity
DEVICE = "cpu"
EMBEDDING_MODEL = "maidalun1020/bce-embedding-base_v1"
RERANK_MODEL = "maidalun1020/bce-reranker-base_v1"
MILVUS_URI = "http://localhost:19530"

# Notification & Storage
NOTIFY_URL = "http://39.96.174.204/api/medical-assistant/knowledge/file/vector/complete"
CACHE_DIR = ".cache"
STORAGE_TYPE = "local"  # Options: "local" or "oss"
STORAGE_DIR = "storage"

# Create cache directory if it doesn't exist
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# Prompt for summarizing chat titles
DIALOGUE_SUMMARY = """Summarize the following conversation into a concise title.
Context:
{context}

Please limit the summary to 20 words.
Your summary:"""

# Core RAG Prompt
RAG_PROMPT = """Reference Information:
{context}
---
My Question or Instruction:
{question}
---
Please answer the question or follow the instructions based on the provided reference information.
- Reply in the same language as the question or instruction.
- Use the provided reference information only if it is relevant.
- If the information is relevant, select the most pertinent parts to support your answer.
- If the reference information does not contain the answer, reply: "I cannot answer this question based on the provided information."
- Do not make up answers.

Your Response:"""

if __name__ == "__main__":
    print(RAG_PROMPT.format(context="Apple Inc. is headquartered in Cupertino.", question="Where is Apple based?"))