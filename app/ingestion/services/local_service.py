from pathlib import Path
from app.config import settings
from app.database import SessionLocal, FonteDocumento, get_vector_store
from app.ingestion.utils.loaders import EXTENSOES_ACEITAS, carregar_arquivo
from app.ingestion.utils.splitter import criar_splitter

PASTA_DOCS = Path(settings.DOCS_DIR)
TAMANHO_LOTE = 50

def ingerir_pasta_local(chunk_size: int = settings.CHUNK_SIZE):
    PASTA_DOCS.mkdir(exist_ok=True)
    splitter = criar_splitter(chunk_size=chunk_size)
    vector_store = get_vector_store()
    db = SessionLocal()
    resultados = []

    try:
        for arquivo in PASTA_DOCS.iterdir():
            if arquivo.is_file() and arquivo.suffix.lower() in EXTENSOES_ACEITAS:
                ja_existe = (
                    db.query(FonteDocumento)
                    .filter(FonteDocumento.nome == arquivo.name)
                    .first()
                )
                if ja_existe:
                    resultados.append({"arquivo": arquivo.name, "status": "ja_indexado"})
                    continue

                docs = carregar_arquivo(arquivo)
                pedacos = splitter.split_documents(docs)

                if pedacos:
                    for i in range(0, len(pedacos), TAMANHO_LOTE):
                        vector_store.add_documents(pedacos[i : i + TAMANHO_LOTE])

                    fonte = FonteDocumento(
                        nome=arquivo.name,
                        tipo=arquivo.suffix.lower().replace(".", ""),
                        caminho_ou_url=str(arquivo),
                        total_chunks=len(pedacos),
                    )
                    db.add(fonte)
                    db.commit()
                    resultados.append({"arquivo": arquivo.name, "chunks": len(pedacos)})
    finally:
        db.close()

    return resultados
