import logging
from logging.handlers import RotatingFileHandler

# ── Logging setup ─────────────────────────────────────────────────
LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

handlers = [
    logging.StreamHandler(),
    RotatingFileHandler("app.log", maxBytes=5_000_000, backupCount=3)  # 5MB per file, keep 3
]

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=handlers
)

# ── Pull uvicorn loggers into your config ─────────────────────────
for uvicorn_logger in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
    logger = logging.getLogger(uvicorn_logger)
    logger.handlers = handlers
    logger.propagate = False
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.responses import Response
from routes.chat_service import router as chat_service_router
from routes.chat_history import router as chat_history_router
from contextlib import asynccontextmanager
from db.connection import MongoDb

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    MongoDb.connect()
    await MongoDb.setup_indexes()
    yield
    MongoDb.disconnect()

app = FastAPI(lifespan=lifespan)



@app.get("/")
def health():
    return {"status": "ok"} 

#include the chat service
app.include_router(
    chat_service_router,
    prefix="/api/chat",
    tags=["chat"]
)

#include the history service
app.include_router(
    chat_history_router,
    prefix="/api/chat_history",
    tags = ["chat-history"]
)



