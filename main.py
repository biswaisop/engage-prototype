from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.responses import Response
from routes import chat_service
from routes import chat_history

app = FastAPI()


@app.get("/api/health")
def health():
    return {"status": "ok"}

#include the chat service
app.include_router(
    chat_service.router,
    prefix="/api/chat",
    tags=["chat"]
)

#include the history service
app.include_router(
    chat_history.router,
    prefix="/api/chat_history",
    tags = ["chat-history"]
)