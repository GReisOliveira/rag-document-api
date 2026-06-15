from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()

app = FastAPI()

from app.routes.routes import chat_router, health_router, models_usualy, upload_doc

app.include_router(upload_doc)
app.include_router(chat_router)
app.include_router(health_router)
app.include_router(models_usualy)