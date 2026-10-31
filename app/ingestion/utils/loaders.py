from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader

EXTENSOES_ACEITAS = [".pdf", ".md", ".txt"]

def carregar_arquivo(caminho: Path):
    extensao = caminho.suffix.lower()
    if extensao == ".pdf":
        return PyPDFLoader(str(caminho)).load()
    elif extensao in [".md", ".txt"]:
        return TextLoader(str(caminho), encoding="utf-8").load()
    return []