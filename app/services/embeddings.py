from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from google import genai


load_dotenv()


EMBEDDING_MODEL = "models/gemini-embedding-2"

class embeddings:

    @staticmethod
    def get_embeddings() -> GoogleGenerativeAIEmbeddings:

        # client = genai.Client()

        # for model in client.models.list():
        #     if "embed" in model.name:
        #         print(model.name)

        return GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    @staticmethod
    def get_models_usualy():

        client = genai.Client()

        for model in client.models.list():
            
            print(model.name)

            if "embed" in model.name:
                print(model.name)

    @staticmethod
    def embed_texts_batch(texts: list[str]) -> list[list[float]]:
        client = genai.Client()
        embeddings_list = []
        
        for text in texts:
            result = client.models.embed_content(
                model=EMBEDDING_MODEL,
                contents=text,  # um texto por vez
            )
            embeddings_list.append(result.embeddings[0].values)
        
        return embeddings_list