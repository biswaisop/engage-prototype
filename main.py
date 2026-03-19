import logging
from logging.handlers import RotatingFileHandler
from utils.redis_memory import RedisClient 



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
from routes.chat_service import router as chat_service_router
from routes.chat_history import router as chat_history_router
from routes.docs import router as docs_router
from contextlib import asynccontextmanager
from db.connection import MongoDb

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    MongoDb.connect()
    RedisClient.connect()
    await MongoDb.setup_indexes()
    yield
    MongoDb.disconnect()
    RedisClient.disconnect()

app = FastAPI(lifespan=lifespan)



@app.get("/health")
async def health():
    mongo_ok = await MongoDb.ping()
    redis_ok = await RedisClient.ping()
    
    status = "ok" if mongo_ok and redis_ok else "degraded"
    return {
        "status": status,
        "services": {
            "mongodb": "ok" if mongo_ok else "unreachable",
            "redis": "ok" if redis_ok else "unreachable",
        }
    }

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

#include docs router
app.include_router(
    docs_router,
    prefix="/api/docs",
    tags=["docs"]
)



