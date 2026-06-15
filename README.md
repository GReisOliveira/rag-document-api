# RAG Document API

API de RAG (Retrieval-Augmented Generation) construída com FastAPI. Permite fazer upload de documentos, indexá-los num banco vetorial e fazer perguntas sobre o conteúdo com suporte a streaming.

## Tecnologias

- Python
- FastAPI
- LangChain
- ChromaDB
- Google Gemini (embeddings + geração)
- SSE (Server-Sent Events)

## Pré-requisitos

- Python 3.11+
- Chave de API do Google Gemini

## Como rodar

**1. Clone o repositório**
```bash
git clone https://github.com/seu-usuario/rag-document-api.git
cd rag-document-api
```

**2. Crie e ative o ambiente virtual**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

**3. Instale as dependências**
```bash
pip install -r requirements.txt
```

**4. Configure as variáveis de ambiente**

Crie um arquivo `.env` na raiz do projeto:
```env
GOOGLE_API_KEY=sua_chave_aqui
```

**5. Suba o servidor**
```bash
python -m uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.  
Documentação Swagger em `http://localhost:8000/docs`.

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/upload/` | Faz upload de um PDF ou CSV e indexa no banco vetorial |
| POST | `/chat/` | Faz uma pergunta e retorna a resposta completa |
| POST | `/chat/stream` | Faz uma pergunta e retorna a resposta em streaming |
| GET | `/health/` | Verifica se a API está rodando |
| GET | `/models/` | Lista os modelos disponíveis no console |

## Estrutura do projeto
rag-api/

├── app/

│   ├── api/

│   │   └── routes/

│   │       └── routes.py

│   ├── services/

│   │   ├── chunk.py

│   │   ├── embeddings.py

│   │   ├── load_doc.py

│   │   └── rag_service.py

│   ├── utils/

│   │   └── logger.py

│   ├── vectorstore/

│   │   └── chroma_db.py

│   └── main.py

├── data/

│   ├── chroma/

│   └── uploads/

├── .env

├── .gitignore

└── requirements.txt
