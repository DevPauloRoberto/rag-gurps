from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.rag.services.qa_service import perguntar_gurps
from app.rag.services.eval_service import avaliar_qualidade_rag

router = APIRouter(prefix="/rag", tags=["RAG & Avaliação"])


class PerguntaRequest(BaseModel):
    pergunta: str
    k: int = Field(default=4, ge=1, le=20, description="Quantidade de chunks recuperados")
    usar_hyde: bool = False


class AvaliarQualidadeRequest(BaseModel):
    limite_chunks: int = Field(default=5, ge=1, le=50)
    k: int = Field(default=4, ge=1, le=20)
    usar_hyde: bool = False
    regerar_gabarito: bool = False


@router.post("/perguntar")
def rota_perguntar(dados: PerguntaRequest):
    return perguntar_gurps(
        pergunta=dados.pergunta,
        k=dados.k,
        usar_hyde=dados.usar_hyde,
    )


@router.post("/avaliar-qualidade")
def rota_avaliar_qualidade(dados: AvaliarQualidadeRequest):
    return avaliar_qualidade_rag(
        limite_chunks=dados.limite_chunks,
        k=dados.k,
        usar_hyde=dados.usar_hyde,
        regerar_gabarito=dados.regerar_gabarito,
    )
