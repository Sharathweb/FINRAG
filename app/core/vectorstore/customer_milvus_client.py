import time

from pathlib import Path
from pymilvus import MilvusClient
from app.core.bce.embedding_client import EmbeddingClient
from app.core.bce.rerank_client import RerankClient
from app.core.chat.open_chat import OpenChat
from app.core.preprocessor.file_processor import FileProcesser
from conf.config import (COLLECTION_NAME, EMBEDDING_MODEL, 
                         VECTOR_DB_PATH, RAG_PROMPT, RERANK_MODEL)
from utils.utils import logger

# Initialize Core Services
embedding_client = EmbeddingClient(EMBEDDING_MODEL)
rerank_client = RerankClient(RERANK_MODEL)
file_processor = FileProcesser()
open_chat = OpenChat()
_dim = 768

class CustomerMilvusClient:
    def __init__(self):
        db_path = "milvus_local.db"
        self.client = MilvusClient(db_path)
        self.collection_name = COLLECTION_NAME
        self.init()

    def init(self):
        if not self.client.has_collection(collection_name=self.collection_name):
            logger.info(f"Creating collection '{self.collection_name}'")
            self.client.create_collection(
                collection_name=self.collection_name,
                dimension=_dim,
                metric_type="L2"
            )
        else:
            logger.info(f"Collection '{self.collection_name}' already exists.")

        self.client.load_collection(collection_name=self.collection_name)
        logger.info(f"Collection '{self.collection_name}' loaded into memory.")

    def embedding_to_vdb(self, file_details, batch_size=1000):
        local_data_dir = Path("D:/RAG Project/FinRAG/data")
        for file_info in file_details:
            file_name = file_info.get("fileName")
            local_file = local_data_dir / file_name
            if not local_file.exists(): 
                continue
            
            docs = file_processor.split_file_to_docs(str(local_file))
            docs_content = [doc.page_content for doc in docs]
            embeddings = embedding_client.get_embedding(docs_content)
            
            entities = []
            file_id = str(file_info.get("fileId"))
            
            for idx, (cont, emb) in enumerate(zip(docs_content, embeddings)):
                unique_id_string = f"{file_id}_{idx}"
                chunk_id = abs(hash(unique_id_string)) % 10000000000
                
                entities.append({
                    "id": chunk_id,
                    "parentId": file_info.get("parentId"),
                    "categoryName": file_info.get("categoryName"),
                    "categoryId": int(file_info.get("categoryId")),
                    "fileId": file_id,
                    "fileName": file_name,
                    "fileSuffix": file_info.get("fileSuffix"),
                    "storagePath": file_info.get("storagePath"),
                    "chunkId": idx,
                    "chunkContent": cont,
                    "vector": emb,
                })
            
            self.client.insert(collection_name=self.collection_name, data=entities)
            logger.info(f"Successfully indexed {file_name} with {len(entities)} chunks")

    def retrieval_and_generate(self, query_emb, topK, score, category_ids, messages):

        load_state = self.client.get_load_state(collection_name=self.collection_name)
        if load_state.get('state') != 'Loaded':
            logger.info(f"Loading collection '{self.collection_name}' into memory...")
            self.client.load_collection(collection_name=self.collection_name)

        # 1. Search Logic
        # Corrected: Using the passed topK parameter
        search_params = {
            "collection_name": self.collection_name,
            "data": query_emb,
            "limit": topK, 
            "output_fields": ['fileName', 'chunkContent']
        }
        
        # Corrected: Only add filter if category_ids is provided
        if category_ids:
            search_params["filter"] = f"categoryId in {category_ids}"

        results = self.client.search(**search_params)
        print(f"DEBUG: Search result type: {type(results)}")
        if results:
            for i, hits in enumerate(results):
                print(f"DEBUG: Hit set {i} count: {len(hits)}")
                if len(hits) > 0:
                    print(f"DEBUG: First hit distance: {hits[0].get('distance')}")
        else:
            print("DEBUG: results object is empty/None")

        if not results or len(results[0]) == 0:
            print("DEBUG: Search found NOTHING. Are your vectors in the collection?")
        
        relevant_content = []
        
        if results:
            for hits in results:
                for hit in hits:
                    dist = hit.get('distance', 0.0)
                    content = hit.get('entity', {}).get('chunkContent', '')
                    
                    # Corrected: Compare against the passed 'score' threshold.
                    # Note: Depending on your distance metric, this might need to be 
                    # '<= score' instead of '> score'.
                    if dist <= score: 
                        relevant_content.append(content)
        
        retrieval_text = "\n\n".join(relevant_content) if relevant_content else "No relevant information found."
        
        # 2. Strict Payload Construction
        strict_payload = []
        for msg in messages:
            if not isinstance(msg, dict): continue
            role = msg.get("role", "user")
            content = msg.get("content")
            clean_role = "assistant" if role == "assistant" else "user"
            
            if content and isinstance(content, str) and content.strip():
                strict_payload.append({"role": clean_role, "content": content})
        
        # 3. Inject Context safely
        if strict_payload:
            last_msg = strict_payload[-1]
            last_msg["content"] = RAG_PROMPT.format(
                context=retrieval_text,
                question=last_msg.get("content", "")
            )
        else:
            return None, []

        print(f"DEBUG: First chunk content: {relevant_content[0][:100] if relevant_content else 'No Content'}")
        print(f"DEBUG: Retrieval text length: {len(retrieval_text)}")

        # 4. Final call with retry logic
        try:
            for attempt in range(5):
                try:
                    final_response = open_chat.chat(strict_payload)
                    if not final_response:
                        logger.error("AI returned empty/null response.")
                        return "I couldn't find an answer based on the provided documents.", relevant_content
                    return final_response, relevant_content
                except Exception as e:
                    if "429" in str(e):
                        sleep_time = 2 ** (attempt + 1)
                        logger.warning(f"Rate limited (429). Retrying in {sleep_time}s...")
                        time.sleep(sleep_time) 
                        continue
                    raise e
        except Exception as e:
            logger.error(f"Error after retries: {e}")
            return None, relevant_content