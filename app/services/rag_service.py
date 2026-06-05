
import asyncio
from fastapi import HTTPException
from langchain_google_genai import GoogleGenerativeAI
from langchain_chroma.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate

from app.services.embeddings import embeddings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class rag_service:
    @staticmethod
    async def rag_response(question: str):
        
        prompt_template = """
        Você é um assistente de IA especializado em responder perguntas com base em documentos fornecidos.
        Use os seguintes documentos para responder à pergunta:
        {context}
        pergunta: {question_user}
        Responda de forma clara e concisa, utilizando as informações dos documentos. 
        Se a resposta não estiver presente nos documentos, diga que não sabe.
        """
        try:

            emb = embeddings.get_embeddings()

            db = Chroma(persist_directory="data/chroma", embedding_function=emb)

            results = db.similarity_search_with_relevance_scores(question, k=3)

            # o results retorna uma tupla (tupla = (documento, score)) ele esta falando que se o score for menor que 0.4 e para encerrar 
            if not results or results[0][1] < 0.4:
                logger.error("Desculpe, não tenho informações suficientes para responder a essa pergunta.")
                raise HTTPException(status_code=404, detail="Desculpe, não tenho informações suficientes para responder a essa pergunta.")  

            context = []
            for result in results:
                context.append(result[0].page_content)

            # .join junta todos os textos e separa pelo que eu quiser, nesse caso \n\n---\n\n, ele desfaz a lsita e junta tudo em uma string.
            context = "\n\n---\n\n".join(context)

            prompt_model = ChatPromptTemplate.from_template(prompt_template)
            prompt = prompt_model.invoke({"context": context, "question_user": question})

            model = GoogleGenerativeAI(model="gemini-2.0-flash")
            response = model.invoke(prompt)

            if asyncio.iscoroutine(response):
                response = await response

            logger.info(f"✓ Pergunta: {question} - Resposta: {response}")

        except Exception as e:
            logger.error(f"✗ Erro no envio do prompt: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar a pergunta.")
        
        return response