from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader

EXTENSOES_ACEITAS = [".pdf", ".md", ".txt"]

def carregar_arquivo(caminho: Path):
    extensao = caminho.suffix.lower()
    if extensao == ".pdf":
        docs = PyPDFLoader(str(caminho)).load()
    elif extensao in [".md", ".txt"]:
        docs = TextLoader(str(caminho), encoding="utf-8").load()
    else:
        return []

    for doc in docs:
        doc.page_content = doc.page_content.replace("\x00", "")
    return [doc for doc in docs if doc.page_content.strip()]
