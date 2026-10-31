from fastapi import APIRouter
from app.config import settings
from app.database import init_db

router = APIRouter(tags=["Healthcheck"])

@router.get("/")
def root():
    return {"mensagem": "API RAG para regras de GURPS funcionando!"}

@router.get("/health")
def health_check():
    status = {
        "api": "online",
        "database": "offline",
        "ollama_modelo": settings.LLM_MODEL,
        "embeddings_modelo": settings.EMBEDDINGS_MODEL,
    }
    try:
        init_db()
        status["database"] = "online"
    except Exception as erro:
        status["database"] = f"offline ({str(erro)})"
    return status