import traceback
import uuid
import chromadb
import asyncio

from fastapi import HTTPException, UploadFile

from app.services.load_doc import load_doc
from app.services.chunk import chunk
from app.services.embeddings import embeddings
from app.utils.logger import setup_logger

logger = setup_logger(__name__)

class chroma_db:
    @staticmethod
    async def create_db(docs: UploadFile):
        try:
            # embeddings = embeddings.get_embeddings()

            file_type = await load_doc.type_doc(docs)
            docs_tratados = await load_doc.saved_files(file_type, docs)

            if not docs_tratados:
                raise HTTPException(status_code=400, detail="Nenhum conteúdo foi extraído do arquivo enviado.")

            if file_type == "pdf":
                chunks = chunk.create_chunks(docs_tratados)
                chunks = [doc for doc in chunks if doc.page_content and doc.page_content.strip()]
                if not chunks:
                    raise HTTPException(status_code=400, detail="O PDF não gerou chunks para indexação.")
                texts = [doc.page_content for doc in chunks]
                metadatas = [doc.metadata for doc in chunks]

            elif file_type == "csv":
                # texts lista de page_content
                texts = [doc.page_content for doc in docs_tratados]
                metadatas = [doc.metadata for doc in docs_tratados]

            else:
                raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado.")

            # Gera embeddings manualmente — evita o bug do langchain-chroma
            logger.info(f"Gerando embeddings para {len(texts)} textos...")
            embedding_vectors = await asyncio.to_thread(embeddings.embed_texts_batch, texts)

            # Valida se voltou o número certo de embeddings
            if len(embedding_vectors) != len(texts):
                logger.error(f"Embeddings gerados ({len(embedding_vectors)}) diferem dos textos ({len(texts)})")
                raise HTTPException(status_code=500, detail="Erro ao gerar embeddings.")

            # cria um id para cada texto dentro de texts que ja e uma lista com index e texto
            ids = [str(uuid.uuid4()) for _ in texts]

            # aponta para onde vai ser salvo o banco de dados
            client = chromadb.PersistentClient(path="data/chroma")
            collection = client.get_or_create_collection(name="documents")

            collection.add(
                documents=texts,
                embeddings=embedding_vectors,
                metadatas=metadatas,
                ids=ids,
            )

            logger.info(f"✓ {len(texts)} documentos adicionados ao Chroma.")
            return {"status": "db created"}

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"✗ Erro ao criar a base de dados: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Erro ao criar a base de dados.")
        
    # def create_db(docs: UploadFile):

    #     client = chromadb.PersistentClient(path="data/chroma")
    #     collection = client.get_or_create_collection(name="documents")
    #     texts = [doc.page_content for doc in chunks]
    #     metadatas = [doc.metadata for doc in chunks]
    #     ids = [str(uuid.uuid4()) for _ in chunks]
    #     # gera os embeddings manualmente
    #     embedding_vectors = embeddings.embed_documents(texts)
    #     collection.add(
    #         documents=texts,
    #         embeddings=embedding_vectors,
    #         metadatas=metadatas,
    #         ids=ids,
    #     )