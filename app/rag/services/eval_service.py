from langchain_core.output_parsers import StrOutputParser
from app.database import SessionLocal, AvaliacaoRAG
from app.rag.services.qa_service import llm
from app.rag.utils.prompts import JUDGE_PROMPT


def dar_nota_manual(avaliacao_id: int, nota: float, comentario: str | None = None):
    db = SessionLocal()
    try:
        item = db.query(AvaliacaoRAG).filter(AvaliacaoRAG.id == avaliacao_id).first()
        if not item:
            return None

        item.nota_usuario = nota
        if comentario is not None:
            item.comentario = comentario

        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


def avaliar_com_juiz_ia(avaliacao_id: int, resposta_esperada: str):
    db = SessionLocal()
    try:
        item = db.query(AvaliacaoRAG).filter(AvaliacaoRAG.id == avaliacao_id).first()
        if not item:
            return None

        judge_chain = JUDGE_PROMPT | llm | StrOutputParser()
        parecer = judge_chain.invoke({
            "pergunta": item.pergunta,
            "resposta_esperada": resposta_esperada,
            "resposta_gerada": item.resposta_gerada,
        })

        primeira_linha = parecer.strip().split("\n")[0].upper()
        veredito = "CORRECT" if "CORRECT" in primeira_linha and "INCORRECT" not in primeira_linha else "INCORRECT"

        item.resposta_esperada = resposta_esperada
        item.nota_juiz_ia = veredito
        item.comentario = parecer.strip()

        db.commit()
        db.refresh(item)
        return item
    finally:
        db.close()


def listar_avaliacoes_e_metricas():
    db = SessionLocal()
    try:
        todas = db.query(AvaliacaoRAG).order_by(AvaliacaoRAG.id.desc()).all()
    finally:
        db.close()

    notas_manuais = [a.nota_usuario for a in todas if a.nota_usuario is not None]
    notas_ia = [a.nota_juiz_ia for a in todas if a.nota_juiz_ia is not None]

    media_usuario = round(sum(notas_manuais) / len(notas_manuais), 2) if notas_manuais else None
    taxa_acerto_ia = (
        round((notas_ia.count("CORRECT") / len(notas_ia)) * 100, 1)
        if notas_ia else None
    )

    return {
        "total_perguntas_testadas": len(todas),
        "media_nota_usuario": media_usuario,
        "taxa_acerto_juiz_ia_percent": taxa_acerto_ia,
        "historico": todas,
    }