from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.database import Base, engine
import app.models
from app.routers import auth, bookings, hotels


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


app.mount("/static", StaticFiles(directory="app/static"), name="static")


app.include_router(auth.router)
app.include_router(hotels.router)
app.include_router(bookings.router)



@app.get("/", include_in_schema=False)
async def read_index():
    return FileResponse("app/static/index.html")


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "booking-api"}