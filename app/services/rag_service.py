from fastapi import HTTPException
from langchain_google_genai import GoogleGenerativeAI
from langchain_chroma.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
# from google import genai
# from google.genai import errors as genai_errors

from app.services.embeddings import embeddings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class rag_service:

    prompt_template = """
        Você é um assistente de IA especializado em responder perguntas com base em documentos fornecidos.
        Use os seguintes documentos para responder à pergunta:
        {context}
        pergunta: {question_user}
        Responda de forma clara e concisa, utilizando as informações dos documentos. 
        Se a resposta não estiver presente nos documentos, diga que não sabe.
        """
    model = GoogleGenerativeAI(model="gemini-2.5-flash-lite")

    @staticmethod
    async def retrieve(question: str) -> str:

        if question.strip() == "":
            raise HTTPException(status_code=400, detail="A pergunta não pode estar vazia.")

        try:
            emb = embeddings.get_embeddings()
            db = Chroma(persist_directory="data/chroma", collection_name="documents", embedding_function=emb)
            results = db.similarity_search_with_relevance_scores(question, k=3)

            if results:
                for index, (document, score) in enumerate(results, start=1):
                    logger.info(f"Resultado {index}: score={score:.4f} | source={document.metadata.get('source')}")
            # o results retorna uma tupla (tupla = (documento, score)) ele esta falando que se o score for menor que 0.4 e para encerrar
            best_score = max((score for _, score in results), default=0.0)

            if not results or best_score < 0.4:
                raise HTTPException(status_code=404, detail="Desculpe, não tenho informações suficientes.")
            # .join junta todos os textos e separa pelo que eu quiser, nesse caso \n\n---\n\n, ele desfaz a lsita e junta tudo em uma string.
            context = "\n\n---\n\n".join([r[0].page_content for r in results])
            return context
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao encontrar a informação: {e}")
    
    @staticmethod
    async def rag_response(question: str):

        try:
            context = await rag_service.retrieve(question)

            prompt_model = ChatPromptTemplate.from_template(rag_service.prompt_template)
            prompt = prompt_model.invoke({"context": context, "question_user": question})

            return rag_service.model.invoke(prompt)

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"✗ Erro: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar a pergunta.")
    
    @staticmethod
    async def rag_response_stream(question: str):
        
        try:
            context = await rag_service.retrieve(question)

            prompt_model = ChatPromptTemplate.from_template(rag_service.prompt_template)
            prompt = prompt_model.invoke({"context": context, "question_user": question})

            for chunk in rag_service.model.stream(prompt):
                yield chunk

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"✗ Erro: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar a pergunta.")