from fastapi import FastAPI
from app.api.health_controller import router as health_router
from app.api.ingestion_controller import router as ingestion_router
from app.api.rag_controller import router as rag_router

app = FastAPI(
    title="GURPS RAG API",
    description="Backend RAG para regras de GURPS com FastAPI, Ollama e pgvector",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(ingestion_router)
app.include_router(rag_router)