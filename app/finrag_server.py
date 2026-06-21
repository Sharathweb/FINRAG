import time
import json
import asyncio
import requests
import shutil
import os
from typing import Any, Dict, List
from fastapi import FastAPI
from pydantic import BaseModel

# Internal imports
from app.core.chat.open_chat import OpenChat
from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient
from app.models.status import ResponseFactory # Using our new Factory
from app.core.bce.embedding_client import EmbeddingClient
from conf.config import EMBEDDING_MODEL
from conf import config
from utils.utils import logger
from pymilvus import MilvusClient
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import JSONResponse

app = FastAPI()
cmc = CustomerMilvusClient()
open_chat = OpenChat()

embedding_client = EmbeddingClient(EMBEDDING_MODEL)

class Item(BaseModel):
    syncId: Any
    sysCategory: Any

class Query(BaseModel):
    chatId: Any
    ownerId: Any
    chatName: Any
    initInputs: Dict
    initOpening: Any
    chatMessages: List[dict]

class Notify(BaseModel):
    syncId: Any
    status: int

def notify_completion(notify_msg: Notify):
    logger.info(f"Notifying completion for syncId: {notify_msg.syncId}")
    payload = {"syncId": notify_msg.syncId, "status": notify_msg.status}
    try:
        response = requests.post(
            config.NOTIFY_URL, 
            headers={'content-type': 'application/json'},
            data=json.dumps(payload)
        )
        if response.status_code == 200:
            logger.info("Sync notification successful!")
        return response
    except Exception as e:
        logger.error(f"Failed to send notification: {e}")

@app.post("/chat")
async def chat(query: Query):
    logger.info(f"Chat request received for chatId: {query.chatId}")
    messages = [{"role": x.get("role").lower(), "content": x.get("rawContent")} for x in query.chatMessages]

    try:
        chunks = []
        response = None
        
        # 1. Branching Logic with safety checks
        if not query.initInputs.get("categoryIds"):
            logger.info("Executing Open Chat...")
            response = open_chat.chat(messages)
        else:
            logger.info("Executing RAG Knowledge Query...")
            user_input = messages[-1]['content']
            query_emb = embedding_client.get_embedding([user_input]) 
            
            response, retrieval_results = cmc.retrieval_and_generate(
                query_emb=query_emb, 
                topK=10, 
                score=0.5, 
                category_ids=query.initInputs.get("categoryIds"), 
                messages=messages
            )
            
            # Check if retrieval returned valid content
            if retrieval_results:
                chunks = [{"index": x[1], "chunk": x[2], "score": x[0]} for x in retrieval_results]

        # 2. Safety check for API failures
        if response is None:
            return ResponseFactory.error(message="AI service is currently unavailable (API Error).").to_dict()

        # 3. Suggest follow-up questions
        messages.append({"role": "assistant", "content": response})
        suggestion_prompt = "Based on our conversation, suggest 3 potential follow-up questions ending with '?'"
        suggestion_messages = messages + [{"role": "user", "content": suggestion_prompt}]
        
        suggested = open_chat.chat(suggestion_messages)
        
        # Handle cases where the LLM might not return a string
        suggested_questions = []
        if suggested and isinstance(suggested, str):
            suggested_questions = [q.strip() for q in suggested.split('?') if q.strip()][:3]

        return ResponseFactory.success(data={
            "chatId": query.chatId,
            "chatName": query.chatName,
            "answer": response,
            "suggestedQuestions": suggested_questions,
            "chunks": chunks
        }).to_dict()

    except Exception as e:
        logger.error(f"RAG Chat error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return ResponseFactory.error(message=f"RAG query failed: {str(e)}").to_dict()

@app.post("/update_vector")
async def update_vector(request: Request):
    try:
        form = await request.form()
        category_id = form.get("categoryId")
        file = form.get("file")
        
        # 1. Save file to disk (in the data folder)
        file_path = os.path.join("D:/RAG Project/FinRAG/data", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # 2. Prepare the metadata for your CustomerMilvusClient
        file_details = [{
            "fileName": file.filename,
            "parentId": "1", # Or derive from your form
            "categoryName": "Financials",
            "categoryId": category_id,
            "fileId": str(time.time()), # Unique ID
            "fileSuffix": "pdf",
            "storagePath": "D:/RAG Project/FinRAG/data/"
        }]
        
        # 3. Process and index
        cmc.embedding_to_vdb(file_details)
        
        return {"status": "success", "filename": file.filename}
        
    except Exception as e:
        logger.error(f"Error during ingestion: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.get("/status")
def get_status():
    client = MilvusClient(uri="http://localhost:19530") # Adjust URI to your setup
    stats = client.get_collection_stats(collection_name="YOUR_COLLECTION_NAME")
    return {"row_count": stats.get('row_count', 0)}

@app.post("/upload")
async def upload_file(
    categoryId: int = Form(...),  # Use Form(...) to extract it from multipart data
    file: UploadFile = File(...)
):
    # Saving the File
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # 2. Trigger processing in background
    # You pass the file_path and categoryId to your processing logic
    asyncio.create_task(process_file_for_indexing(file_path, categoryId))
    
    return {"status": "File received, processing in background", "filename": file.filename}

async def process_file_for_indexing(file_path: str, category_id: int):
    try:
        # Your existing cmc logic here:
        # detail = cmc.parse_file(file_path)
        # cmc.embedding_to_vdb(detail, category_id)
        logger.info(f"Successfully indexed: {file_path}")
    except Exception as e:
        logger.error(f"Indexing error: {e}")