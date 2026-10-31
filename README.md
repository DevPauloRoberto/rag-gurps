# GURPS RAG API

## Como executar o projeto

### 1. Subir o banco PostgreSQL (pgvector)
```powershell
docker compose up -d
```

### 2. Baixar os modelos no Ollama
```powershell
ollama pull bge-m3:latest
ollama pull qwen2.5:7b
```

### 3. Configurar o ambiente Python
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 4. Configurar variáveis de ambiente
```powershell
Copy-Item .env.example .env
```

### 5. Rodar a API
```powershell
uvicorn app.main:app --reload
```

Acesse o Swagger em: `http://localhost:8000/docs`
