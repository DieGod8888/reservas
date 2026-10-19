from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Room
from app.schemas import RoomCreate, RoomOut

router = APIRouter(prefix="/rooms", tags=["salas"])


def get_room_or_404(db: Session, room_id: int) -> Room:
    room = db.get(Room, room_id)
    if room is None:
        raise HTTPException(status_code=404, detail="Sala no encontrada")
    return room


def check_unique_name(db: Session, name: str, room_id: int | None = None) -> None:
    query = select(Room).where(Room.name == name)
    if room_id is not None:
        query = query.where(Room.id != room_id)
    if db.scalar(query):
        raise HTTPException(status_code=409, detail="Ya existe una sala con ese nombre")


@router.post("", status_code=201, summary="Crea una sala")
def create_room(data: RoomCreate, db: Session = Depends(get_db)) -> RoomOut:
    check_unique_name(db, data.name)
    room = Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.get("", summary="Lista todas las salas")
def list_rooms(db: Session = Depends(get_db)) -> list[RoomOut]:
    return db.scalars(select(Room)).all()


@router.get("/{room_id}", summary="Obtiene una sala por su id")
def get_room(room_id: int, db: Session = Depends(get_db)) -> RoomOut:
    return get_room_or_404(db, room_id)


@router.put("/{room_id}", summary="Actualiza una sala")
def update_room(room_id: int, data: RoomCreate, db: Session = Depends(get_db)) -> RoomOut:
    room = get_room_or_404(db, room_id)
    check_unique_name(db, data.name, room_id)
    room.name = data.name
    room.capacity = data.capacity
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{room_id}", status_code=204, summary="Elimina una sala")
def delete_room(room_id: int, db: Session = Depends(get_db)) -> None:
    room = get_room_or_404(db, room_id)
    if room.reservations:
        raise HTTPException(status_code=409, detail="La sala tiene reservas")
    db.delete(room)
    db.commit()