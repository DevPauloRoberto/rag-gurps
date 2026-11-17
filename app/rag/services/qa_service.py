from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.database import SessionLocal, AvaliacaoRAG, get_vector_store
from app.rag.utils.prompts import HYDE_PROMPT, RAG_PROMPT

llm = OllamaLLM(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
)
vector_store = get_vector_store()


def perguntar_gurps(pergunta: str, k: int = 4, usar_hyde: bool = False):
    # 1. Define o texto de busca (pergunta direta ou expandida com HyDE)
    texto_busca = pergunta
    if usar_hyde:
        hyde_chain = HYDE_PROMPT | llm | StrOutputParser()
        texto_busca = hyde_chain.invoke({"query": pergunta})

    # 2. Busca os K chunks mais similares no PostgreSQL (pgvector)
    docs_recuperados = vector_store.similarity_search(texto_busca, k=k)
    contexto_texto = "\n\n---\n\n".join(doc.page_content for doc in docs_recuperados)

    # 3. Gera a resposta final usando o contexto
    rag_chain = RAG_PROMPT | llm | StrOutputParser()
    resposta = rag_chain.invoke({
        "contexto": contexto_texto,
        "query": pergunta,
    })

    # 4. Salva no banco para você poder auditar o contexto e dar nota!
    db = SessionLocal()
    try:
        registro = AvaliacaoRAG(
            pergunta=pergunta,
            contexto_recuperado=contexto_texto,
            resposta_gerada=resposta,
        )
        db.add(registro)
        db.commit()
        db.refresh(registro)
        avaliacao_id = registro.id
    finally:
        db.close()

    fontes = [
        {
            "fonte": doc.metadata.get("source", "desconhecida"),
            "pagina": doc.metadata.get("page", None),
            "trecho": doc.page_content,
        }
        for doc in docs_recuperados
    ]

    return {
        "avaliacao_id": avaliacao_id,
        "pergunta": pergunta,
        "usou_hyde": usar_hyde,
        "texto_busca_usado": texto_busca,
        "resposta": resposta,
        "chunks_recuperados": fontes,
    }
