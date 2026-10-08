from datetime import date, time

import pytest
from pydantic import ValidationError as PydanticValidationError

from app.models import BookingCreate, RoomCreate
from app.services import (
    BookingConflictError,
    CampusService,
    NotFoundError,
    ValidationError,
)


@pytest.fixture
def service():
    """Proporciona una instancia limpia del servicio para cada test."""
    return CampusService()


# --- Tests de Aulas ---


def test_create_room_success(service):
    room_data = RoomCreate(
        nombre="Laboratorio A",
        edificio="Edificio Central",
        capacidad=25,
        equipamiento=["proyector", "PCs"],
    )
    room = service.create_room(room_data)
    assert room.id == 1
    assert room.nombre == "Laboratorio A"
    assert len(service.get_rooms()) == 1


def test_create_room_invalid_capacity(service):
    with pytest.raises(PydanticValidationError):
        # La capacidad debe ser mayor que 0
        RoomCreate(nombre="Aula Invalida", edificio="Edificio B", capacidad=0)


def test_get_room_not_found(service):
    with pytest.raises(NotFoundError):
        service.get_room(999)


def test_delete_room_success(service):
    room = service.create_room(RoomCreate(nombre="Aula 1", edificio="A", capacidad=10))
    service.delete_room(room.id)
    assert len(service.get_rooms()) == 0


def test_delete_room_not_found(service):
    with pytest.raises(NotFoundError):
        service.delete_room(999)


# --- Tests de Reservas y Reglas de Negocio ---


def test_create_booking_success(service):
    room = service.create_room(RoomCreate(nombre="Aula 1", edificio="A", capacidad=10))
    booking_data = BookingCreate(
        aula_id=room.id,
        usuario="Profesor Juan",
        fecha=date(2026, 10, 10),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
    )
    booking = service.create_booking(booking_data)
    assert booking.id == 1
    assert len(service.get_bookings()) == 1


def test_create_booking_room_not_found(service):
    booking_data = BookingCreate(
        aula_id=999,
        usuario="Usuario",
        fecha=date(2026, 10, 10),
        hora_inicio=time(10, 0),
        hora_fin=time(12, 0),
    )
    with pytest.raises(NotFoundError):
        service.create_booking(booking_data)


def test_create_booking_invalid_time_range(service):
    room = service.create_room(RoomCreate(nombre="Aula 1", edificio="A", capacidad=10))
    booking_data = BookingCreate(
        aula_id=room.id,
        usuario="Usuario",
        fecha=date(2026, 10, 10),
        hora_inicio=time(14, 0),
        hora_fin=time(12, 0),
    )
    with pytest.raises(ValidationError):
        service.create_booking(booking_data)


def test_create_booking_overlap_conflict(service):
    room = service.create_room(
        RoomCreate(nombre="Laboratorio A", edificio="Edificio A", capacidad=30)
    )

    # Primera reserva: 10:00 a 12:00
    service.create_booking(
        BookingCreate(
            aula_id=room.id,
            usuario="Julian",
            fecha=date(2026, 10, 10),
            hora_inicio=time(10, 0),
            hora_fin=time(12, 0),
        )
    )

    # Segunda reserva solapada: 11:00 a 13:00 (debe dar conflicto)
    conflicting_booking = BookingCreate(
        aula_id=room.id,
        usuario="Marta",
        fecha=date(2026, 10, 10),
        hora_inicio=time(11, 0),
        hora_fin=time(13, 0),
    )
    with pytest.raises(BookingConflictError):
        service.create_booking(conflicting_booking)


def test_delete_booking_not_found(service):
    with pytest.raises(NotFoundError):
        service.delete_booking(999)