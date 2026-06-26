import time
import json
import asyncio
import requests
import shutil
import os
import uuid
import traceback
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, UploadFile, File, Form, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pymilvus import MilvusClient

# Internal imports
from app.core.chat.open_chat import OpenChat
from app.core.vectorstore.customer_milvus_client import CustomerMilvusClient
from app.models.status import ResponseFactory
from app.core.bce.embedding_client import EmbeddingClient
from conf.config import EMBEDDING_MODEL, GEMINI_API_KEY
from conf import config
from utils.utils import logger

app = FastAPI()
cmc = CustomerMilvusClient()
open_chat = OpenChat()
embedding_client = EmbeddingClient(EMBEDDING_MODEL)

class Query(BaseModel):
    chatId: Any
    ownerId: Any
    chatName: Any
    initInputs: Optional[Dict[str, Any]] = {}
    initOpening: Any
    chatMessages: List[dict]

class Notify(BaseModel):
    syncId: Any
    status: int

def send_to_gemini(messages: List[Dict[str, str]], model: str = "gemini-2.5-flash") -> str:
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    
    cleaned_messages = [
        {"role": m.get("role") if m.get("role") in ["system", "user", "assistant"] else "user", 
         "content": str(m.get("content", ""))}
        for m in messages
    ]

    try:
        response = requests.post(url, headers=headers, json={"model": model, "messages": cleaned_messages}, timeout=30)
        return response.json()['choices'][0]['message']['content'] if response.status_code == 200 else None
    except Exception as e:
        logger.error(f"Gemini API Error: {e}")
        return None

@app.post("/chat")
async def chat(query: Query):
    logger.info(f"Received request: {query}")
    messages = []
    for x in query.chatMessages:
        content = x.get("content") or x.get("rawContent")
        if content and isinstance(content, str) and content.strip():
            messages.append({"role": x.get("role", "user").lower(), "content": content})

    if not messages:
        return JSONResponse(content=ResponseFactory.error(message="No valid content found.").to_dict())
    
    user_input = messages[-1].get('content', '')
    category_ids = query.initInputs.get("categoryIds") if query.initInputs else None

    try:
        response = None
        chunks = []
        
        query_emb = None

        if not category_ids:
            response = send_to_gemini(messages)
            if response is None:
                logger.error("DEBUG: send_to_gemini failed.")
        else:
            query_emb = embedding_client.get_embedding([user_input])
            #logger.info(f"DEBUG: Embedding generated: {len(query_emb) if query_emb else 'None'}")
            if query_emb is None or (hasattr(query_emb, 'size') and query_emb.size == 0):
                logger.error("FAILURE: Embedding generation returned empty/None.")
                return JSONResponse(status_code=500, content={"success": False, "message": "Embedding generation failed."})
            else:
                logger.info("DEBUG: Embedding generated: None")
            rag_result = cmc.retrieval_and_generate(
                query_emb=query_emb, topK=15, score=999999.0, 
                category_ids=category_ids, messages=messages
            )

            if rag_result and isinstance(rag_result, (list, tuple)) and len(rag_result) >= 2:
                response, chunks = rag_result
        
        if rag_result:
                response, chunks = rag_result
        else:
            logger.error("FAILURE: cmc.retrieval_and_generate returned None or empty.")

        messages.append({"role": "assistant", "content": response})
        suggested = send_to_gemini(messages + [{"role": "user", "content": "Suggest 3 follow-up questions."}])
        suggested_questions = [q.strip() for q in suggested.split('?') if q.strip()][:3] if suggested else []

        # Return explicit JSONResponse
        return JSONResponse(content=ResponseFactory.success(data={
            "chatId": query.chatId, "chatName": query.chatName,
            "answer": response, "suggestedQuestions": suggested_questions, "chunks": chunks
        }).to_dict())

    except Exception as e:
        logger.error(f"RAG Chat CRITICAL ERROR: {traceback.format_exc()}")
        
        return JSONResponse(status_code=500, content={"success": False, "message": str(e), "data": {}})

@app.post("/update_vector")
async def update_vector(categoryId: int = Form(...), file: UploadFile = File(...)):
    try:
        file_path = os.path.join("D:/RAG Project/FinRAG/data", file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        file_details = [{
            "id": int(time.time() * 1000),
            "fileName": file.filename,
            "parentId": "1",
            "categoryName": "Financials",
            "categoryId": categoryId, 
            "fileId": str(uuid.uuid4()),
            "fileSuffix": "pdf",
            "storagePath": "D:/RAG Project/FinRAG/data/"
        }]
        
        cmc.embedding_to_vdb(file_details)
        return {"status": "success", "filename": file.filename}
    except Exception as e:
        logger.error(f"Vector Update Error: {traceback.format_exc()}")
        return JSONResponse(status_code=500, content={"success": False, "message": "An internal error occurred", "data": {}})