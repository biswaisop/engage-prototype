from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.responses import Response
from routes import chat_service

app = FastAPI()


@app.get("/api/health")
def health():
    return {"status": "ok"}

app.include_router(
    chat_service.router,
    prefix="/chat",
    tags=["chat"]
)