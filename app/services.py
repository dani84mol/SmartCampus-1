from typing import List, Optional
from app.models import Room, RoomCreate, Booking, BookingCreate

class BookingConflictError(Exception):
    pass

class NotFoundError(Exception):
    pass

class ValidationError(Exception):
    pass

class CampusService:
    def __init__(self):
        self.rooms: dict[int, Room] = {}
        self.bookings: dict[int, Booking] = {}
        self._room_id_counter = 1
        self._booking_id_counter = 1

    # --- Gestión de Aulas ---
    def create_room(self, room_data: RoomCreate) -> Room:
        if room_data.capacidad <= 0:
            raise ValidationError("La capacidad del aula debe ser mayor que 0")
        room_id = self._room_id_counter
        room = Room(id=room_id, **room_data.model_dump())
        self.rooms[room_id] = room
        self._room_id_counter += 1
        return room

    def get_rooms(self) -> List[Room]:
        return list(self.rooms.values())

    def get_room(self, room_id: int) -> Room:
        if room_id not in self.rooms:
            raise NotFoundError(f"El aula con id {room_id} no existe")
        return self.rooms[room_id]

    def delete_room(self, room_id: int) -> None:
        if room_id not in self.rooms:
            raise NotFoundError(f"El aula con id {room_id} no existe")
        del self.rooms[room_id]
        # Si se borra un aula, se eliminan sus reservas asociadas
        self.bookings = {
            b_id: b for b_id, b in self.bookings.items() if b.aula_id != room_id
        }

    # --- Gestión de Reservas ---
    def create_booking(self, booking_data: BookingCreate) -> Booking:
        # Validación: El aula debe existir
        if booking_data.aula_id not in self.rooms:
            raise NotFoundError(f"No se puede reservar: el aula {booking_data.aula_id} no existe")

        # Validación: Hora de inicio debe ser anterior a la de fin
        if booking_data.hora_inicio >= booking_data.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de finalización")

        # Validación: Solapamiento de reservas en el mismo aula y fecha
        for existing in self.bookings.values():
            if (
                existing.aula_id == booking_data.aula_id
                and existing.fecha == booking_data.fecha
            ):
                # Hay solapamiento si:
                # nueva_inicio < existente_fin Y nueva_fin > existente_inicio
                if (
                    booking_data.hora_inicio < existing.hora_fin
                    and booking_data.hora_fin > existing.hora_inicio
                ):
                    raise BookingConflictError("Existe un solapamiento con otra reserva en esa aula")

        booking_id = self._booking_id_counter
        booking = Booking(id=booking_id, **booking_data.model_dump())
        self.bookings[booking_id] = booking
        self._booking_id_counter += 1
        return booking

    def get_bookings(self) -> List[Booking]:
        return list(self.bookings.values())

    def delete_booking(self, booking_id: int) -> None:
        if booking_id not in self.bookings:
            raise NotFoundError(f"La reserva con id {booking_id} no existe")
        del self.bookings[booking_id]

# Instancia global única para almacenar el estado
service = CampusService()