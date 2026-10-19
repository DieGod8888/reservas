from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Reservation
from app.routers.rooms import get_room_or_404
from app.schemas import ReservationCreate, ReservationOut

router = APIRouter(prefix="/reservations", tags=["reservas"])


def get_reservation_or_404(db: Session, reservation_id: int) -> Reservation:
    reservation = db.get(Reservation, reservation_id)
    if reservation is None:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    return reservation


def check_no_conflict(
    db: Session,
    room_id: int,
    start_time: datetime,
    end_time: datetime,
    reservation_id: int | None = None,
) -> None:
    # Los intervalos se tratan como [inicio, fin): se permite que se toquen.
    query = select(Reservation).where(
        Reservation.room_id == room_id,
        Reservation.start_time < end_time,
        Reservation.end_time > start_time,
    )
    if reservation_id is not None:
        query = query.where(Reservation.id != reservation_id)
    if db.scalar(query):
        raise HTTPException(
            status_code=409, detail="La sala ya está reservada en ese horario"
        )


@router.post("", status_code=201, summary="Crea una reserva")
def create_reservation(
    data: ReservationCreate, db: Annotated[Session, Depends(get_db)]
) -> ReservationOut:
    get_room_or_404(db, data.room_id)
    check_no_conflict(db, data.room_id, data.start_time, data.end_time)
    reservation = Reservation(**data.model_dump())
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


@router.get("", summary="Lista las reservas, con filtro opcional por sala")
def list_reservations(
    db: Annotated[Session, Depends(get_db)], room_id: int | None = None
) -> list[ReservationOut]:
    query = select(Reservation)
    if room_id is not None:
        query = query.where(Reservation.room_id == room_id)
    return db.scalars(query).all()


@router.get("/{reservation_id}", summary="Obtiene una reserva por su id")
def get_reservation(
    reservation_id: int, db: Annotated[Session, Depends(get_db)]
) -> ReservationOut:
    return get_reservation_or_404(db, reservation_id)


@router.put("/{reservation_id}", summary="Actualiza una reserva")
def update_reservation(
    reservation_id: int,
    data: ReservationCreate,
    db: Annotated[Session, Depends(get_db)],
) -> ReservationOut:
    reservation = get_reservation_or_404(db, reservation_id)
    get_room_or_404(db, data.room_id)
    check_no_conflict(db, data.room_id, data.start_time, data.end_time, reservation_id)
    reservation.room_id = data.room_id
    reservation.customer_name = data.customer_name
    reservation.start_time = data.start_time
    reservation.end_time = data.end_time
    db.commit()
    db.refresh(reservation)
    return reservation


@router.delete("/{reservation_id}", status_code=204, summary="Elimina una reserva")
def delete_reservation(
    reservation_id: int, db: Annotated[Session, Depends(get_db)]
) -> None:
    reservation = get_reservation_or_404(db, reservation_id)
    db.delete(reservation)
    db.commit()
