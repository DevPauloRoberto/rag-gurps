from langchain_ollama import OllamaLLM
from langchain_core.output_parsers import StrOutputParser
from app.config import settings
from app.database import SessionLocal, AvaliacaoRAG, get_vector_store
from app.rag.utils.prompts import HYDE_PROMPT, RAG_PROMPT

llm = OllamaLLM(
    model=settings.LLM_MODEL,
    base_url=settings.OLLAMA_BASE_URL,
    num_ctx=3072,
    temperature=0.2,
)
vector_store = get_vector_store()

_ultimos_chunks = []

SAUDACOES = {"oi", "ola", "olá", "bom dia", "boa tarde", "boa noite", "boa noitw", "opa", "e ai", "eai"}


def _eh_saudacao(texto: str) -> bool:
    limpo = texto.strip().lower().rstrip("!?.")
    return limpo in SAUDACOES or len(limpo) <= 4


def perguntar_gurps(
    pergunta: str,
    k: int = 5,
    usar_hyde: bool = False,
    historico: list[dict] | None = None,
):
    global _ultimos_chunks
    historico = historico or []

    # Se for apenas "olá / boa noite", responde sem sujar o banco vetorial com chunks aleatórios
    if _eh_saudacao(pergunta):
        return {
            "avaliacao_id": None,
            "pergunta": pergunta,
            "usou_hyde": False,
            "texto_busca_usado": "(saudação direta)",
            "resposta": (
                "Olá! Sou seu Mestre e Consultor de GURPS 4ª Edição. "
                "Posso te ajudar a montar uma ficha do zero (distribuindo pontos em ST, DX, IQ, HT, Vantagens, Desvantagens e Perícias), "
                "escolher armas, armaduras e equipamentos iniciais com preços ($), ou tirar dúvidas de regras. "
                "Me conta: qual o estilo do personagem, nível tecnológico (NT/TL) e quantos pontos você tem para gastar?"
            ),
            "chunks_recuperados": [],
        }

    # Padrão 2: Junta apenas a última pergunta real do usuário (ignorando "olá boa noite")
    perguntas_uteis = [
        m["texto"]
        for m in historico
        if m.get("autor") == "usuario" and not _eh_saudacao(m.get("texto", ""))
    ]
    ultima_pergunta = perguntas_uteis[-1] if perguntas_uteis else ""
    texto_busca = f"{ultima_pergunta} | {pergunta}" if ultima_pergunta else pergunta

    if usar_hyde:
        hyde_chain = HYDE_PROMPT | llm | StrOutputParser()
        texto_busca = hyde_chain.invoke({"query": texto_busca})

    docs_novos = vector_store.similarity_search(texto_busca, k=k)

    # Padrão 3: Mescla com os 2 melhores chunks da pergunta anterior (sem duplicar)
    docs_recuperados = list(docs_novos)
    textos_ja_incluidos = {d.page_content for d in docs_recuperados}
    for doc_antigo in _ultimos_chunks[:2]:
        if doc_antigo.page_content not in textos_ja_incluidos:
            docs_recuperados.append(doc_antigo)

    _ultimos_chunks = docs_novos[:2]

    contexto_texto = "\n\n---\n\n".join(doc.page_content for doc in docs_recuperados)

    historico_texto = "\n".join(
        f"{'Jogador' if m.get('autor') == 'usuario' else 'Mestre'}: {m.get('texto', '')}"
        for m in historico[-4:]
        if not _eh_saudacao(m.get("texto", ""))
    ) or "Início da conversa."

    rag_chain = RAG_PROMPT | llm | StrOutputParser()
    resposta = rag_chain.invoke({
        "historico": historico_texto,
        "contexto": contexto_texto,
        "query": pergunta,
    })

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
