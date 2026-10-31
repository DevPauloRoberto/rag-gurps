from datetime import datetime
from langchain_postgres import PGVector
from app.config import settings
from langchain_ollama import OllamaEmbeddings
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import Settings

engine = create_engine(Settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class FonteDocumento(Base):
    __tablename__ = "fontes_documentos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(50), nullable=False)
    caminho_ou_url = Column(String(500), nullable=False)
    total_chunks = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

class AvaliacaoRAG(Base):
    __tablename__ = "avaliacoes_rag"
    id = Column(Integer, primary_key=True, index=True)
    pergunta = Column(Text, nullable=False)
    contexto_recuperado = Column(Text, nullable=True)
    resposta_gerada = Column(Text, nullable=False)
    resposta_esperada = Column(Text, nullable=True)
    nota_usuario = Column(Float, nullable=True)
    nota_juiz_ia = Column(String(50), nullable=True)
    comentario = Column(Text, nullable=True)        
    criado_em = Column(DateTime, default=datetime.utcnow)

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.create_all(bind=engine)

def get_vector_store() -> PGVector:
    embeddings = OllamaEmbeddings(
        model=settings.EMBEDDINGS_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
    return PGVector(
        embeddings=embeddings,
        collection_name=settings.COLLECTION_NAME,
        connection=settings.DATABASE_URL,
        use_jsonb=True,
    )