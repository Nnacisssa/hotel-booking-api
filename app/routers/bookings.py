from datetime import date
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Booking, BookingStatus, Room, User
from app.schemas import BookingCreate, BookingResponse

router = APIRouter(prefix="/bookings", tags=["Bookings (Бронирования)"])


def send_booking_confirmation_email(user_email: str, booking_id: int):
    """Фоновая задача: симуляция отправки e-mail пользователю."""
    print(f"[EMAIL SERVICE] 📧 Подтверждение бронирования #{booking_id} успешно отправлено на {user_email}")


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    background_tasks: BackgroundTasks, 
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Бронирование номера на указанные даты."""
    if booking_data.check_in >= booking_data.check_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Дата выезда (check_out) должна быть позже даты заезда (check_in)"
        )
    if booking_data.check_in < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя забронировать номер на прошедшую дату"
        )

    room_query = select(Room).where(Room.id == booking_data.room_id)
    room_result = await db.execute(room_query)
    if not room_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Указанный номер отеля не найден"
        )

    overlap_query = select(Booking).where(
        Booking.room_id == booking_data.room_id,
        Booking.status == BookingStatus.CONFIRMED,
        Booking.check_in < booking_data.check_out,
        Booking.check_out > booking_data.check_in
    )
    overlap_result = await db.execute(overlap_query)
    if overlap_result.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Номер уже забронирован на выбранный диапазон дат"
        )

    new_booking = Booking(
        user_id=current_user.id,
        room_id=booking_data.room_id,
        check_in=booking_data.check_in,
        check_out=booking_data.check_out
    )
    db.add(new_booking)
    await db.commit()
    await db.refresh(new_booking)

    background_tasks.add_task(
        send_booking_confirmation_email,
        user_email=current_user.email,
        booking_id=new_booking.id
    )

    return new_booking


@router.get("/me", response_model=list[BookingResponse])
async def get_my_bookings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Booking).where(Booking.user_id == current_user.id)
    result = await db.execute(query)
    return result.scalars().all()


@router.delete("/{booking_id}", response_model=BookingResponse)
async def cancel_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Booking).where(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    )
    result = await db.execute(query)
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бронирование не найдено или принадлежит другому пользователю"
        )

    booking.status = BookingStatus.CANCELLED
    await db.commit()
    await db.refresh(booking)
    return booking