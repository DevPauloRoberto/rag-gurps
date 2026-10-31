from pathlib import Path
from git import Repo
from app.config import settings
from app.database import SessionLocal, FonteDocumento, get_vector_store
from app.ingestion.utils.loaders import carregar_arquivo
from app.ingestion.utils.splitter import criar_splitter

PASTA_REPOS = Path(settings.REPOS_DIR)

def ingerir_repositorio_git(repo_url: str, chunk_size: int = settings.CHUNK_SIZE):
    PASTA_REPOS.mkdir(parents=True, exist_ok=True)
    nome_repo = repo_url.rstrip("/").split("/")[-1].replace(".git", "")
    destino = PASTA_REPOS / nome_repo

    if not destino.exists():
        Repo.clone_from(repo_url, str(destino))
    else:
        Repo(str(destino)).remotes.origin.pull()

    todos_docs = []
    for ext in ["*.md", "*.txt", "*.pdf"]:
        for arquivo in destino.rglob(ext):
            try:
                todos_docs.extend(carregar_arquivo(arquivo))
            except Exception:
                continue

    splitter = criar_splitter(chunk_size=chunk_size)
    pedacos = splitter.split_documents(todos_docs)

    if pedacos:
        vector_store = get_vector_store()
        vector_store.add_documents(pedacos)

        db = SessionLocal()
        try:
            fonte = FonteDocumento(
                nome=nome_repo,
                tipo="git",
                caminho_ou_url=repo_url,
                total_chunks=len(pedacos),
            )
            db.add(fonte)
            db.commit()
        finally:
            db.close()

    return {
        "repositorio": nome_repo,
        "arquivos_lidos": len(todos_docs),
        "chunks_gerados": len(pedacos),
        "overlap_tokens": int(chunk_size * settings.CHUNK_OVERLAP_RATIO),
    }