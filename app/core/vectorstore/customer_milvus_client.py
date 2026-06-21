import os
from pathlib import Path
from pymilvus import (Collection, CollectionSchema, DataType, FieldSchema,
                      connections, utility)

from app.core.bce.embedding_client import EmbeddingClient
from app.core.bce.rerank_client import RerankClient
from app.core.chat.open_chat import OpenChat
from app.core.preprocessor.file_processor import FileProcesser
from conf.config import (COLLECTION_NAME, EMBEDDING_MODEL,
                         MILVUS_URI, RAG_PROMPT, RERANK_MODEL)

# Initialize Core Services
embedding_client = EmbeddingClient(EMBEDDING_MODEL)
rerank_client = RerankClient(RERANK_MODEL)
file_processor = FileProcesser()
open_chat = OpenChat()
_dim = 768

from utils.utils import logger

class CustomerMilvusClient:

    def __init__(self):
        connections.connect(uri=MILVUS_URI)
        self.collection_name = COLLECTION_NAME
        self.collection = self.init()
        self.collection.load()

    def init(self):
        collection = None  # Initialize to None at the start
        try:
            if utility.has_collection(self.collection_name):
                collection = Collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists.")
            else:
                schema = CollectionSchema(self.fields)
                logger.info(f"Creating collection '{self.collection_name}'")
                collection = Collection(self.collection_name, schema)
                index_params = {
                    "metric_type": "L2",
                    "index_type": "IVF_FLAT",
                    "params": {"nlist": 2048},
                }
                collection.create_index(field_name="embedding", index_params=index_params)
                logger.info("Initialization successful!")
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            # If it fails, we should probably stop the program 
            # because the client won't work without a collection.
            raise e 
            
        return collection
    @property
    def fields(self):
        # Define the schema fields based on your data structure
        fields = [
            FieldSchema(name="id", dtype=DataType.VARCHAR, is_primary=True, auto_id=True, max_length=100),
            FieldSchema(name="parentId", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="categoryName", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="categoryId", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="fileId", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="fileName", dtype=DataType.VARCHAR, max_length=1024),
            FieldSchema(name="fileSuffix", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="storagePath", dtype=DataType.VARCHAR, max_length=256),
            FieldSchema(name="chunkId", dtype=DataType.INT64),
            FieldSchema(name="chunkContent", dtype=DataType.VARCHAR, max_length=1024),
            # Ensure _dim is defined (you have _dim = 768 at the top of your file)
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=_dim),
        ]
        return fields
    
    def embedding_to_vdb(self, file_details, batch_size=1000):
        """Processes files from local storage and inserts into Milvus."""
        # Update this path to your local data folder
        local_data_dir = Path("D:/RAG Project/FinRAG/data")

        for file_info in file_details:
            file_name = file_info.get("fileName")
            local_file = local_data_dir / file_name
            
            if not local_file.exists():
                logger.error(f"File {local_file} not found locally. Skipping.")
                continue
            
            logger.info(f"Processing local file: {local_file}")
            
            docs = file_processor.split_file_to_docs(str(local_file))
            docs_content = [doc.page_content for doc in docs]
            embeddings = embedding_client.get_embedding(docs_content)
            
            entities = []
            try:
                for idx, (cont, emb) in enumerate(zip(docs_content, embeddings)):
                    entity = {
                        "parentId": file_info.get("parentId"),
                        "categoryName": file_info.get("categoryName"),
                        "categoryId": file_info.get("categoryId"),
                        "fileId": str(file_info.get("fileId")),
                        "fileName": file_name,
                        "fileSuffix": file_info.get("fileSuffix"),
                        "storagePath": file_info.get("storagePath"),
                        "chunkId": idx,
                        "chunkContent": cont,
                        "embedding": emb,
                    }
                    entities.append(entity)
                    if len(entities) == batch_size:
                        self.collection.insert(entities)
                        self.collection.flush()
                        entities = []
                
                self.collection.insert(entities)
                self.collection.flush()
                logger.info("Successfully indexed file into vector database.")
            except Exception as e:
                logger.error(f"Failed to write {file_name} to vector database: {e}")

    def retrieval_and_generate(self, query_emb, topK, score, category_ids, messages):
        expr = "categoryId in {}".format(category_ids)
        search_params = {"metric_type": "L2", "offset": 0, "ignore_growing": False, "params": {"nprobe": 10}}

        results = self.collection.search(
            data=query_emb,
            anns_field="embedding",
            param=search_params,
            limit=topK,
            expr=expr,
            output_fields=['fileName', 'chunkContent'],
            consistency_level="Strong")
        
        relevant_content = []
        for hits in results:
            for hit in hits:
                relevant_content.append((hit.score, hit.entity.get("fileName"), hit.entity.get('chunkContent')))
        
        logger.info(f"Retrieved {len(relevant_content)} relevant chunks.")
        
        if relevant_content:
            retrieval_results = [x for x in relevant_content if x[0] > score]
            retrieval_text = "\n\n".join([x[2] for x in retrieval_results])
        else:
            retrieval_results = []
            retrieval_text = ""

        messages[-1]['content'] = RAG_PROMPT.format(context=retrieval_text, question=messages[-1]['content'])
        rag_result = open_chat.chat(messages)

        return rag_result, retrieval_results