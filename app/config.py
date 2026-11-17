import os
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # secrets ligados a config do BD
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = quote_plus(os.getenv("DB_PASSWORD", "postgres"))
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DB_NAME: str = os.getenv("DB_NAME", "gurps_rag")
    COLLECTION_NAME: str = os.environ["COLLECTION_NAME"]

    # url do BD montada
    DATABASE_URL: str = (
        f"postgresql+psycopg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    #secrets ligados aos modelos de IA
    OLLAMA_BASE_URL: str = os.environ["OLLAMA_BASE_URL"]
    EMBEDDINGS_MODEL: str = os.environ["EMBEDDINGS_MODEL"]
    TOKENIZER_MODEL: str = os.environ["TOKENIZER_MODEL"]
    LLM_MODEL: str = os.environ["LLM_MODEL"]

    #secrets para os chunks
    DOCS_DIR: str = os.environ["DOCS_DIR"]
    REPOS_DIR: str = os.environ["REPOS_DIR"]
    CHUNK_SIZE: int = int(os.environ["CHUNK_SIZE"])
    CHUNK_OVERLAP_RATIO: float = float(os.environ["CHUNK_OVERLAP_RATIO"])

settings = Settings()
