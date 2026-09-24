import json
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.dependencies import get_current_admin
from app.models import Hotel, Room, User
from app.redis import redis_client
from app.schemas import HotelCreate, HotelResponse, RoomCreate, RoomResponse

router = APIRouter(prefix="/hotels", tags=["Hotels & Rooms (Отели и Номера)"])


@router.get("", response_model=list[HotelResponse])
async def get_hotels(
    city: str | None = Query(None, description="Фильтр по городу"),
    db: AsyncSession = Depends(get_db)
):
    """Получение списка отелей с кэшированием в Redis на 60 секунд."""
    cache_key = f"hotels:city:{city or 'all'}"

    cached_hotels = await redis_client.get(cache_key)
    if cached_hotels:
        return json.loads(cached_hotels)

    query = select(Hotel).options(selectinload(Hotel.rooms))
    if city:
        query = query.where(Hotel.city.ilike(f"%{city}%"))

    result = await db.execute(query)
    hotels = result.scalars().all()

    hotels_data = [HotelResponse.model_validate(h).model_dump(mode="json") for h in hotels]

    await redis_client.set(cache_key, json.dumps(hotels_data), ex=60)

    return hotels_data


@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Получение информации о конкретном отеле по ID."""
    query = select(Hotel).options(selectinload(Hotel.rooms)).where(Hotel.id == hotel_id)
    result = await db.execute(query)
    hotel = result.scalar_one_or_none()

    if not hotel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отель не найден"
        )
    return hotel


@router.post("", response_model=HotelResponse, status_code=status.HTTP_201_CREATED)
async def create_hotel(
    hotel_data: HotelCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Создание нового отеля (Доступно только для ADMIN) + Инвалидация кэша."""
    new_hotel = Hotel(**hotel_data.model_dump())
    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)

    await redis_client.flushdb()

    return new_hotel


@router.post("/{hotel_id}/rooms", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
async def create_room(
    hotel_id: int,
    room_data: RoomCreate,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Добавление номера в отель (Доступно только для ADMIN)."""
    hotel_query = select(Hotel).where(Hotel.id == hotel_id)
    hotel_result = await db.execute(hotel_query)
    if not hotel_result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Отель не найден")

    new_room = Room(**room_data.model_dump(), hotel_id=hotel_id)
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)

    await redis_client.flushdb()

    return new_room