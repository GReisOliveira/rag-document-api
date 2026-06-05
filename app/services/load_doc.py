import shutil

from fastapi import HTTPException, UploadFile
from langchain_core.documents import Document
from app.utils.logger import setup_logger

import csv
import os
import pymupdf
from pathlib import Path

logger = setup_logger(__name__)

class load_doc:

    async def saved_files(type_doc: str, docs: UploadFile):

        if type_doc == "pdf":
            #Cria um objeto de caminho para a pasta onde você quer guardar os pdfs, se a pasta nao existir ele cria
            uploads_dir = Path("data/uploads/pdf")

        elif type_doc == "csv":
            #Cria um objeto de caminho para a pasta onde você quer guardar os csvs
            uploads_dir = Path("data/uploads/csv")
            
        # mkdir = criar pasta, parents=True = criar pastas intermediárias se não existirem, exist_ok=True = não lançar erro se a pasta já existir
        uploads_dir.mkdir(parents=True, exist_ok=True)
        # path(docs.filename).name = pega o nome do arquivo enviado, e junta com o caminho da pasta onde vai ser salvo
        saved_path = uploads_dir / Path(docs.filename).name

        try:
            # open(saved_path, "wb") = abre o arquivo para escrita em modo binário, 
            # shutil.copyfileobj(docs.file, buffer) copia o conteúdo do arquivo(docs.file) enviado para o local(buffer(saved_path)) onde vai ser salvo
            with open(saved_path, "wb") as buffer:
                shutil.copyfileobj(docs.file, buffer)
                logger.info(f"✓ Arquivo salvo com sucesso: {saved_path}")

            if type_doc == "pdf":
                return await load_doc.load_pdf(saved_path)
            
            return await load_doc.load_csv(saved_path)
        
        except Exception as e:
            logger.error(f"Erro ao salvar upload: {e}")
            raise HTTPException(status_code=500, detail="Erro ao salvar arquivo enviado")
        
    @staticmethod
    async def type_doc(docs: UploadFile):

       # path() pega o nome do arquivo e vc pode acessar partes desse nome com o atributo .suffix(pega a extensão do arquivo)
        ext = Path(docs.filename or "").suffix.lower()

        if ext == ".pdf":
            return "pdf"
        if ext == ".csv":
            return "csv"

        # lê um sample e reposiciona o ponteiro
        sample = await docs.read(4096)
        await docs.seek(0)

        # PDF começa com %PDF
        if sample.startswith(b"%PDF"):
            return "pdf"

        # tenta detectar CSV usando csv.Sniffer
        try:
            # utf-8 decodifica acentos e outros caracteres; errors="ignore" ignora caracteres que não podem ser decodificados (pode perder dados, mas evita falhas)
            text_sample = sample.decode("utf-8", errors="ignore")
            csv.Sniffer().sniff(text_sample, delimiters=[",", ";", "\t", "|"])
            return "csv"
        
        except Exception:
            logger.error(f"Não foi possível determinar o tipo do arquivo {docs.filename}. Extensão: {ext}")
            raise HTTPException(status_code=400, detail="Tipo de arquivo não suportado. Envie um PDF ou CSV.")

    @staticmethod #estou criando uma lista desncessária de documentos, porque o chunker do pdf espera uma lista de documentos, mesmo que seja só um documento, e para manter a consistência com o csv que já retorna uma lista de documentos
    async def load_pdf(doc: Path):
        
        # uploads_dir = Path("data/uploads/pdf")
        docs = []
        
        # if not sent_docs.exists():
        #     print(f"arquivos {sent_docs} não encontrada")
        #     return docs
        
        try:     # pymupdf ja separa pagina e text como se fosse um array
            with pymupdf.open(str(doc)) as docopen:
                text = ""

                for page in docopen: # pymupdf tem essa função get_text() para pegar o texto do pdf
                    text = page.get_text()

                    docs.append(Document(page_content=text, metadata={"source": str(doc.name), "page": page.number + 1}))

                logger.info(f"✓ Processado: {doc.name}")

                # # fecha o arquivo para liberar recursos do sistema, e evitar vazamento de memória
                # doc.close()

        except Exception as e:
            logger.error(f"✗ Erro ao processar {doc.name}: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar os arquivos PDF.")
        
        for i, d in enumerate(docs):
            logger.info(f"index:{i}, Documento: {d.metadata['source']} - Total de caracteres: {len(d.page_content)} - Page: {d.metadata['page']} - Texto: {d.page_content[:100]}...\n------------------------------------------------------------------------------------------------------------------\n")

        return docs
        
    @staticmethod
    async def load_csv(doc: Path):

        docs = []

        try:
            with open(doc, "r", encoding="utf-8-sig", newline="") as file:
                sample = file.read(4096)
                file.seek(0)

                dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
                # lê linha por linha e transforma cada linha em um dicionário.
                reader = csv.DictReader(file, dialect=dialect) # DictReader le a linha(file) e dialect e o que separa as linha
                # row_number é o número da linha.
                # row é o conteúdo daquela linha em formato de dicionário.
                # start=2 é usado porque normalmente a linha 1 é o cabeçalho.
                for row_number, row in enumerate(reader, start=2):
                    # pula linha vazias 
                    # all() se todos os "values" da linha estao vazias
                    if not row or all(value is None or str(value).strip() == "" for value in row.values()): # row.values pega somente os valores
                        continue

                    text_parts = []
                    # esse for e necessario, porque o DictReader retorna um dicionário, e para fazer o chunk e necessario virar stirng 
                    for key, value in row.items(): # row.items pega chave e valor na ordem
                        if value is None or str(value).strip() == "":
                            continue

                        text_parts.append(f"{key}: {value}")

                        if not text_parts:
                            continue

                    docs.append(
                        Document(
                            page_content=" | ".join(text_parts),
                            metadata={
                                "source": str(doc.name),
                                "row_number": row_number,
                            }
                        )
                    )
                    
                logger.info(f"✓ Processado: {doc.name}")
                # # fecha para liberar recursos do sistema, e evitar vazamento de memória                    
                # file.close(
        except Exception as e:
            logger.error(f"✗ Erro ao processar {doc.name}: {e}")
            raise HTTPException(status_code=500, detail="Erro ao processar o arquivo CSV.")
    
        return docs
        
    # teste n\---------------------------------
    async def load_csv_teste(sent_docs: Path):

        docs = []

        try:
            for csv_file in sent_docs.glob("*.csv"):

                try:
                    with open(csv_file, "r", encoding="utf-8-sig", newline="") as file:
                        sample = file.read(4096)
                        file.seek(0)

                        dialect = csv.Sniffer().sniff(sample, delimiters=[",", ";", "\t", "|"])
                        # lê linha por linha e transforma cada linha em um dicionário.
                        reader = csv.DictReader(file, dialect=dialect) # DictReader le a linha(file) e dialect e o que separa as linhas

                        # row_number é o número da linha.
                        # row é o conteúdo daquela linha em formato de dicionário.
                        # start=2 é usado porque normalmente a linha 1 é o cabeçalho.
                        for row_number, row in enumerate(reader, start=2):
                            # pula linha vazias 
                            # all() se todos os "values" da linha estao vazias
                            if not row or all(value is None or str(value).strip() == "" for value in row.values()):
                                continue

                            text_parts = []
                            # esse for e necessario, porque o DictReader retorna um dicionário, e para fazer o chunk e necessario virar stirng 
                            for key, value in row.items():
                                if value is None or str(value).strip() == "":
                                    continue
                                text_parts.append(f"{key}: {value}")

                            if not text_parts:
                                continue

                            docs.append(
                                Document(
                                    page_content=" | ".join(text_parts),
                                    metadata={
                                        "source": str(csv_file),
                                        "row_number": row_number,
                                    }
                                )
                            )

                        logger.info(f"✓ Processado: {csv_file.name}")

                        # # fecha para liberar recursos do sistema, e evitar vazamento de memória                    
                        # file.close()

                except Exception as e:
                    logger.error(f"✗ Erro ao processar {csv_file.name}: {e}")
                    raise HTTPException(status_code=500, detail="Erro ao processar o arquivo CSV.")
            
            return docs
        
        except Exception as e:
            logger.error(f"✗ Erro ao acessar CSV: {e}")
            raise HTTPException(status_code=500, detail="Erro ao acessar o arquivo CSV.")
        