import asyncio
from fastapi import APIRouter, UploadFile
from fastapi.responses import StreamingResponse

from app.vectorstore.chroma_db import chroma_db
from app.services.rag_service import rag_service
from app.services.embeddings import embeddings

upload_doc = APIRouter(prefix="/upload", tags=["Upload"])
chat_router = APIRouter(prefix="/chat", tags=["Chat"])
models_usualy = APIRouter(prefix="/models", tags=["Models"])
health_router = APIRouter(prefix="/health", tags=["Health"])

@upload_doc.post("/")
async def upload(docs: UploadFile):
    return await chroma_db.create_db(docs)
    
@chat_router.post("/")
async def chat(question: str):
    response = await rag_service.rag_response(question)
    return {"answer": response}

@chat_router.post("/stream")
async def chat_stream(question: str):

    async def generate():
        async for chunk in rag_service.rag_response_stream(question):
            yield chunk
            await asyncio.sleep(0.3)

    return StreamingResponse(generate(), media_type="text/event-stream")

@models_usualy.get("/")
async def models():
    embeddings.get_models_usualy()
    return {"message": "Modelos listados no console."}

@health_router.get("/")
async def health():
    return {"status": "ok"}