from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# 1. Prompt do HyDE (cria uma resposta hipotética para melhorar a busca vetorial)
HYDE_PROMPT = PromptTemplate.from_template(
    """Escreva um parágrafo curto de regra de GURPS que possa responder à pergunta abaixo. Não adicione comentários extras.
Pergunta: {query}
Regra hipotética:"""
)

# 2. Prompt principal do RAG de GURPS
RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Você é um Mestre especialista nas regras de GURPS. "
        "Responda à pergunta usando EXCLUSIVAMENTE o contexto fornecido abaixo. "
        "Se a regra não estiver no contexto, diga claramente que não encontrou no material indexado.\n\n"
        "Contexto:\n{contexto}"
    ),
    ("human", "{query}"),
])

# 3. Prompt do Juiz IA (inspirado no QAEvalChain da sua aula, mas rodando no seu Ollama local!)
JUDGE_PROMPT = PromptTemplate.from_template(
    """Você é um avaliador rigoroso de um sistema RAG de regras de GURPS.
Compare a RESPOSTA GERADA com a RESPOSTA ESPERADA para a pergunta abaixo.
Responda na primeira linha apenas com CORRECT ou INCORRECT, e na segunda linha explique brevemente o motivo.

Pergunta: {pergunta}
Resposta Esperada: {resposta_esperada}
Resposta Gerada: {resposta_gerada}
Avaliação:"""
)