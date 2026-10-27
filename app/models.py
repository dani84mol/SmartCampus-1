from datetime import date, time

from pydantic import BaseModel, Field


class RoomCreate(BaseModel):
    nombre: str
    edificio: str
    capacidad: int = Field(gt=0, description="La capacidad debe ser mayor que 0")
    equipamiento: list[str] = []

class Room(RoomCreate):
    id: int

class BookingCreate(BaseModel):
    aula_id: int
    usuario: str
    fecha: date
    hora_inicio: time
    hora_fin: time

class Booking(BookingCreate):
    id: int