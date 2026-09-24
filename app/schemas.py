from datetime import datetime
from pydantic import BaseModel, EmailStr
from app.models import UserRole

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: EmailStr
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoomBase(BaseModel):
    room_number: str
    price_per_night: int
    capacity: int = 2


class RoomCreate(RoomBase):
    pass


class RoomResponse(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True



class HotelBase(BaseModel):
    title: str
    description: str | None = None
    city: str
    address: str


class HotelCreate(HotelBase):
    pass


class HotelResponse(HotelBase):
    id: int
    rooms: list[RoomResponse] = []

    class Config:
        from_attributes = True