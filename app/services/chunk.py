from fastapi import HTTPException
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class chunk:
    
    @staticmethod
    def create_chunks(docs: list[Document]) -> list[Document]:
        try:
            if not docs:
                return []
                                              # verifica se tem algo no page_content e se tem algo ele remove os espaços em branco, se não tiver nada ou só tiver espaço em branco ele remove o documento da lista
            valid_docs = [doc for doc in docs if doc.page_content and doc.page_content.strip()]

            if not valid_docs:
                logger.error("Nenhum documento válido para gerar chunks.")
                return []

            splitter = RecursiveCharacterTextSplitter(
                chunk_size=2000,
                chunk_overlap=500,
                length_function=len,
                add_start_index=True,
            )

            chunks = splitter.split_documents(valid_docs)

            # chunks = [doc for doc in chunks if doc.page_content and doc.page_content.strip()]

            total_chunks = len(chunks)

            logger.info(f"Total de chunks gerados: {total_chunks}")

            return chunks
            
            # for doc in docs:
            #     doc = Document(metadata={"chunk_index": {len(chunks)}})
            #     print(f"Documento: {doc.metadata} - Total de chunks: {len(chunks)} - Texto: {chunks}/n------------------------------------------------------------------------------------------------------------------/n")

        except Exception as e:
            logger.error(f"✗ Erro ao criar chunks: {e}")
            raise HTTPException(status_code=500, detail="Erro ao criar chunks.")