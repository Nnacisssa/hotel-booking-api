from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import Base, engine
import app.models
from app.routers import auth, hotels 


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="Hotel Booking API",
    description="REST API сервиса бронирования отелей",
    version="0.1.0",
    lifespan=lifespan
)

app.include_router(auth.router)
app.include_router(hotels.router)


@app.get("/")
async def root():
    return {"message": "Сервис бронирования успешно запущен!"}


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "booking-api"}