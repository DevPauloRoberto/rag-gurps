import json
from pathlib import Path
from sqlalchemy import text
from langchain_classic.evaluation.qa import QAGenerateChain, QAEvalChain

from app.database import engine
from app.rag.services.qa_service import llm, perguntar_gurps

ARQUIVO_QA_PAIRS = Path("qa_pairs.json")


def buscar_chunks_do_banco(limite: int) -> list[str]:
    with engine.connect() as conn:
        linhas = conn.execute(
            text("SELECT document FROM langchain_pg_embedding LIMIT :limite"),
            {"limite": limite},
        ).fetchall()
    return [linha[0] for linha in linhas if linha[0]]


def gerar_gabarito_qa(limite_chunks: int = 5) -> list[dict]:
    pedacos = buscar_chunks_do_banco(limite_chunks)
    if not pedacos:
        return []

    example_gen_chain = QAGenerateChain.from_llm(llm)
    new_examples = example_gen_chain.apply_and_parse(
        [{"doc": texto} for texto in pedacos]
    )

    with open(ARQUIVO_QA_PAIRS, "w", encoding="utf-8") as file:
        json.dump(new_examples, file, indent=2, ensure_ascii=False)

    return new_examples


def avaliar_qualidade_rag(
    limite_chunks: int = 5,
    k: int = 4,
    usar_hyde: bool = False,
    regerar_gabarito: bool = False,
):
    # 1. A IA lê os Chunks do banco e cria o Gabarito (qa_pairs.json)
    if regerar_gabarito or not ARQUIVO_QA_PAIRS.exists():
        new_examples = gerar_gabarito_qa(limite_chunks)
    else:
        with open(ARQUIVO_QA_PAIRS, "r", encoding="utf-8") as file:
            new_examples = json.load(file)

    if not new_examples:
        return {"erro": "Nenhum chunk encontrado no banco. Faça a ingestão primeiro."}

    eval_data = [
        {
            "query": pair["qa_pairs"]["query"],
            "answer": pair["qa_pairs"]["answer"],
        }
        for pair in new_examples[:limite_chunks]
    ]

    # 2. O seu RAG faz a prova passando pela sua função perguntar_gurps()
    predictions = []
    for item in eval_data:
        resultado_rag = perguntar_gurps(
            pergunta=item["query"],
            k=k,
            usar_hyde=usar_hyde,
        )
        predictions.append({"result": resultado_rag["resposta"]})

    # 3. O Juiz IA (QAEvalChain) corrige a prova comparando com o gabarito
    eval_chain = QAEvalChain.from_llm(llm)
    graded_outputs = eval_chain.evaluate(eval_data, predictions)

    corrects = 0
    detalhes = []
    for i, item in enumerate(eval_data):
        parecer = graded_outputs[i]["results"]
        nota = parecer.split("\n")[-1].split(":")[-1].strip()
        acertou = 1 if nota == "CORRECT" else 0
        corrects += acertou

        detalhes.append({
            "pergunta_gerada": item["query"],
            "gabarito_esperado": item["answer"],
            "resposta_do_rag": predictions[i]["result"],
            "veredito_juiz": nota,
        })

    return {
        "total_questoes": len(eval_data),
        "acertos": corrects,
        "taxa_acerto": corrects / len(eval_data),
        "provas_corrigidas": detalhes,
    }
