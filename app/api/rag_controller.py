from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.rag.services.qa_service import perguntar_gurps
from app.rag.services.eval_service import (
    dar_nota_manual,
    avaliar_com_juiz_ia,
    listar_avaliacoes_e_metricas,
)

router = APIRouter(prefix="/rag", tags=["RAG & Avaliação"])


class PerguntaRequest(BaseModel):
    pergunta: str
    k: int = Field(default=4, ge=1, le=20, description="Quantidade de chunks recuperados")
    usar_hyde: bool = False


class NotaManualRequest(BaseModel):
    nota: float = Field(..., ge=0, le=10, description="Nota de 0 a 10 para a resposta")
    comentario: str | None = None


class JuizIARequest(BaseModel):
    resposta_esperada: str


@router.post("/perguntar")
def rota_perguntar(dados: PerguntaRequest):
    return perguntar_gurps(
        pergunta=dados.pergunta,
        k=dados.k,
        usar_hyde=dados.usar_hyde,
    )


@router.get("/avaliacoes")
def rota_listar_avaliacoes():
    return listar_avaliacoes_e_metricas()


@router.patch("/avaliacoes/{avaliacao_id}/nota")
def rota_dar_nota(avaliacao_id: int, dados: NotaManualRequest):
    atualizado = dar_nota_manual(avaliacao_id, dados.nota, dados.comentario)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return atualizado


@router.post("/avaliacoes/{avaliacao_id}/juiz-ia")
def rota_juiz_ia(avaliacao_id: int, dados: JuizIARequest):
    atualizado = avaliar_com_juiz_ia(avaliacao_id, dados.resposta_esperada)
    if not atualizado:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return atualizado