
from fastapi import FastAPI, HTTPException, status

from app.models import Booking, BookingCreate, Room, RoomCreate
from app.services import (
    BookingConflictError,
    NotFoundError,
    ValidationError,
    service,
)

app = FastAPI(
    title="SmartCampus API",
    description="Microservicio REST para la gestión de aulas y reservas universitarias",
    version="1.0.0",
)

@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check():
    return {"status": "ok", "service": "smartcampus-api"}

# --- Endpoints de Aulas ---

@app.post("/rooms", response_model=Room, status_code=status.HTTP_201_CREATED, tags=["Rooms"])
def create_room(room_data: RoomCreate):
    try:
        return service.create_room(room_data)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.get("/rooms", response_model=list[Room], tags=["Rooms"])
def get_rooms():
    return service.get_rooms()

@app.get("/rooms/{id}", response_model=Room, tags=["Rooms"])
def get_room(id: int):
    try:
        return service.get_room(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

@app.delete("/rooms/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Rooms"])
def delete_room(id: int):
    try:
        service.delete_room(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))

# --- Endpoints de Reservas ---

@app.post("/bookings", response_model=Booking, status_code=status.HTTP_201_CREATED, tags=["Bookings"])
def create_booking(booking_data: BookingCreate):
    try:
        return service.create_booking(booking_data)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except BookingConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

@app.get("/bookings", response_model=list[Booking], tags=["Bookings"])
def get_bookings():
    return service.get_bookings()

@app.delete("/bookings/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Bookings"])
def delete_booking(id: int):
    try:
        service.delete_booking(id)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))