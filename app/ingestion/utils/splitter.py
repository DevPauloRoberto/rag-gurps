from transformers import AutoTokenizer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.config import settings

tokenizer = AutoTokenizer.from_pretrained(settings.TOKENIZER_MODEL)

def criar_splitter(
    chunk_size: int = settings.CHUNK_SIZE,
    overlap_ratio: float = settings.CHUNK_OVERLAP_RATIO,
):
    overlap = int(chunk_size * overlap_ratio)
    return RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
        tokenizer=tokenizer,
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )