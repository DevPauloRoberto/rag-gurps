from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# 1. Prompt do HyDE
HYDE_PROMPT = PromptTemplate.from_template(
    """Escreva um parágrafo curto de regra ou tabela de GURPS 4e que responda à pergunta abaixo, incluindo os termos em português e inglês (ex: Character Generation, Attributes, Advantages, Disadvantages, Skills, Pistols, Rifles, Broadsword, Damage, Cost, ST).
Pergunta: {query}
Regra hipotética:"""
)

# 2. Prompt principal do RAG de GURPS
RAG_PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "Você é um Mestre veterano e Consultor de Criação de Fichas de GURPS 4ª Edição.\n"
        "REGRAS OBRIGATÓRIAS:\n"
        "1. IDIOMA: Responda 100% em PORTUGUÊS DO BRASIL. NUNCA escreva frases ou seções em inglês. Se os trechos do contexto estiverem em inglês, traduza tudo para português.\n"
        "2. NÃO INVENTE PERSONAGENS DO LIVRO: Exemplos de raças/NPCs presentes nos trechos do livro (como elfos, anões, NPCs de exemplo) NÃO são o personagem do usuário. Só use o que o próprio Jogador pediu.\n"
        "3. MONTAGEM DE FICHA COMPLETA: Sempre que o jogador pedir para montar/criar um personagem com determinadas características, monte uma FICHA DE GURPS 4e COMPLETA e estruturada em Markdown contendo:\n"
        "   - **Conceito e Orçamento de Pontos** (ex: 150 pontos, limite de -50 em desvantagens)\n"
        "   - **Atributos Primários** (ST [10 pts/nv], DX [20 pts/nv], IQ [20 pts/nv], HT [10 pts/nv] a partir de 10)\n"
        "   - **Características Secundárias** (PV=ST, Vontade=IQ, Percepção=IQ, PF=HT, Velocidade Básica=(DX+HT)/4, Deslocamento, Esquiva= floor(Vel. Básica)+3, Dano GdP/Bal)\n"
        "   - **Vantagens** com custos em `[pts]`\n"
        "   - **Desvantagens e Peculiaridades** com custos negativos em `[-pts]`\n"
        "   - **Perícias** em tabela (Perícia, Dificuldade, Nível de Habilidade final e `[pts]` gastos)\n"
        "   - **Armas e Equipamentos** em tabela (Item, Dano, Alcance/Aparar, Custo `$` e Peso)\n"
        "   - **Fechamento da Conta de Pontos** (Atributos + Vantagens - Desvantagens + Perícias = Total)\n"
        "4. TABELAS DE ARMAS E EQUIPAMENTOS: Quando o jogador pedir armas ou equipamentos, liste as opções reais do Contexto em tabela Markdown com: Nome, NT (TL), Dano (Dmg), Precisão (Acc), Alcance (Range), Cadência (RoF), Tiros (Shots), Custo ($) e ST mínima.\n\n"
        "Histórico recente da conversa:\n{historico}\n\n"
        "Contexto dos Livros e Tabelas de GURPS 4e:\n{contexto}"
    ),
    (
        "human",
        "{query}\n\n"
        "(Lembrete: Responda inteiramente em Português do Brasil usando formatação Markdown com títulos ###, **negrito** e tabelas |...|, sem mudar para o inglês.)"
    ),
])

# 3. Prompt do Juiz IA
JUDGE_PROMPT = PromptTemplate.from_template(
    """Você é um avaliador rigoroso de um sistema RAG de regras de GURPS.
Compare a RESPOSTA GERADA com a RESPOSTA ESPERADA para a pergunta abaixo.
Responda na primeira linha apenas com CORRECT ou INCORRECT, e na segunda linha explique brevemente o motivo.

Pergunta: {pergunta}
Resposta Esperada: {resposta_esperada}
Resposta Gerada: {resposta_gerada}
Avaliação:"""
)
