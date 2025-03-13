from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn

from src.api import main_router
from src.database import setup_database

@asynccontextmanager
async def lifespan(app: FastAPI):
    await setup_database()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(main_router)




