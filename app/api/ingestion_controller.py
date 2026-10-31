from fastapi import APIRouter
from pydantic import BaseModel
from app.config import settings
from app.database import SessionLocal, FonteDocumento
from app.ingestion.services.local_service import ingerir_pasta_local, PASTA_DOCS
from app.ingestion.services.git_service import ingerir_repositorio_git

router = APIRouter(prefix="/ingestao", tags=["Ingestão de Dados"])

class GitIngestRequest(BaseModel):
    repo_url: str
    chunk_size: int = settings.CHUNK_SIZE

@router.get("/fontes")
def listar_fontes():
    db = SessionLocal()
    try:
        fontes_salvas = db.query(FonteDocumento).all()
    finally:
        db.close()

    PASTA_DOCS.mkdir(exist_ok=True)
    arquivos_na_pasta = [f.name for f in PASTA_DOCS.iterdir() if f.is_file()]

    return {
        "arquivos_na_pasta_documentos": arquivos_na_pasta,
        "fontes_indexadas_no_banco": fontes_salvas,
    }

@router.post("/local")
def rota_ingerir_local(chunk_size: int = settings.CHUNK_SIZE):
    resultado = ingerir_pasta_local(chunk_size=chunk_size)
    return {
        "status": "concluido",
        "chunk_size_tokens": chunk_size,
        "overlap_tokens": int(chunk_size * settings.CHUNK_OVERLAP_RATIO),
        "processados": resultado,
    }

@router.post("/git")
def rota_ingerir_git(dados: GitIngestRequest):
    return ingerir_repositorio_git(
        repo_url=dados.repo_url,
        chunk_size=dados.chunk_size,
    )