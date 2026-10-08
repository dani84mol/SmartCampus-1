from app.models import Booking, BookingCreate, Room, RoomCreate


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

    def create_room(self, room_data: RoomCreate) -> Room:
        room = Room(id=self._room_id_counter, **room_data.model_dump())
        self.rooms[self._room_id_counter] = room
        self._room_id_counter += 1
        return room

    def get_room(self, room_id: int) -> Room:
        if room_id not in self.rooms:
            raise NotFoundError(f"Aula con ID {room_id} no encontrada")
        return self.rooms[room_id]

    def get_rooms(self) -> list[Room]:
        return list(self.rooms.values())

    def delete_room(self, room_id: int) -> None:
        if room_id not in self.rooms:
            raise NotFoundError(f"Aula con ID {room_id} no encontrada")
        del self.rooms[room_id]

    def create_booking(self, booking_data: BookingCreate) -> Booking:
        # Validación: Aula existente
        if booking_data.aula_id not in self.rooms:
            raise NotFoundError(f"El aula {booking_data.aula_id} no existe")

        # Validación: Coherencia de horas
        if booking_data.hora_inicio >= booking_data.hora_fin:
            raise ValidationError("La hora de inicio debe ser anterior a la hora de fin")

        # Validación: Solapamiento de reservas en el mismo aula y fecha
        for existing in self.bookings.values():
            if (
                existing.aula_id == booking_data.aula_id
                and existing.fecha == booking_data.fecha
                and booking_data.hora_inicio < existing.hora_fin
                and booking_data.hora_fin > existing.hora_inicio
            ):
                raise BookingConflictError("Existe un solapamiento con otra reserva en esa aula")

        booking = Booking(id=self._booking_id_counter, **booking_data.model_dump())
        self.bookings[self._booking_id_counter] = booking
        self._booking_id_counter += 1
        return booking

    def get_bookings(self) -> list[Booking]:
        return list(self.bookings.values())

    def delete_booking(self, booking_id: int) -> None:
        if booking_id not in self.bookings:
            raise NotFoundError(f"Reserva con ID {booking_id} no encontrada")
        del self.bookings[booking_id]


service = CampusService()