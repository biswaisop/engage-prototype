import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),              # console
        logging.FileHandler("app.log")        # file
    ]
)

from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.responses import Response
from routes.chat_service import router as chat_service_router
from routes.chat_history import router as chat_history_router
from contextlib import asynccontextmanager
from db.connection import MongoDb



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




#include the leads service
# app.include_router(
#     lead_capture.router,
#     prefix="/api/leads",
#     tags=["leads"]
# )