from fastapi import FastAPI

from app.core.logging import setup_logging

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.conversations import router as conversations_router

from app.core.config import settings


setup_logging()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
)


app.include_router(auth_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(conversations_router)


@app.get("/")
def root():
    return {
        "message": "DocuMind API is running"
    }