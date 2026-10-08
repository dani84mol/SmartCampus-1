import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.services import service


@pytest.fixture(autouse=True)
def reset_service_state():
    """Limpia el estado en memoria antes de cada prueba de integración."""
    service.rooms.clear()
    service.bookings.clear()
    service._room_id_counter = 1
    service._booking_id_counter = 1

client = TestClient(app)

# --- Pruebas de Health Check ---

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "smartcampus-api"}

# --- Pruebas de Integración de Aulas (Rooms) ---

def test_create_and_get_room():
    payload = {
        "nombre": "Aula Magna",
        "edificio": "Pabellón Norte",
        "capacidad": 150,
        "equipamiento": ["microfono", "proyector"]
    }
    # Crear aula -> 201 Created
    post_res = client.post("/rooms", json=payload)
    assert post_res.status_code == 201
    data = post_res.json()
    assert data["id"] == 1
    assert data["nombre"] == "Aula Magna"

    # Obtener aula por ID -> 200 OK
    get_res = client.get("/rooms/1")
    assert get_res.status_code == 200
    assert get_res.json()["edificio"] == "Pabellón Norte"

def test_create_room_invalid_capacity():
    payload = {
        "nombre": "Aula Pequeña",
        "edificio": "Pabellón Sur",
        "capacidad": 0
    }
    # Capacidad inválida -> 422 Unprocessable Entity (validado por Pydantic)
    response = client.post("/rooms", json=payload)
    assert response.status_code == 422

def test_get_room_not_found():
    # Consultar aula inexistente -> 404 Not Found
    response = client.get("/rooms/999")
    assert response.status_code == 404

def test_delete_room_success_and_not_found():
    # Crear aula
    res = client.post("/rooms", json={"nombre": "Taller", "edificio": "B", "capacidad": 20})
    room_id = res.json()["id"]

    # Borrar aula existente -> 204 No Content
    del_res = client.delete(f"/rooms/{room_id}")
    assert del_res.status_code == 204

    # Intentar borrar de nuevo -> 404 Not Found
    del_again = client.delete(f"/rooms/{room_id}")
    assert del_again.status_code == 404

# --- Pruebas de Integración de Reservas (Bookings) ---

def test_create_booking_success():
    # Crear aula previa
    client.post("/rooms", json={"nombre": "Seminario 1", "edificio": "Central", "capacidad": 30})

    booking_payload = {
        "aula_id": 1,
        "usuario": "Prof. Lopez",
        "fecha": "2026-11-15",
        "hora_inicio": "09:00:00",
        "hora_fin": "11:00:00"
    }
    # Crear reserva -> 201 Created
    response = client.post("/bookings", json=booking_payload)
    assert response.status_code == 201
    assert response.json()["id"] == 1

def test_create_booking_room_not_found():
    booking_payload = {
        "aula_id": 999,
        "usuario": "Prof. Lopez",
        "fecha": "2026-11-15",
        "hora_inicio": "09:00:00",
        "hora_fin": "11:00:00"
    }
    # Aula no existe -> 404 Not Found
    response = client.post("/bookings", json=booking_payload)
    assert response.status_code == 404

def test_create_booking_invalid_time_range():
    client.post("/rooms", json={"nombre": "Seminario 1", "edificio": "Central", "capacidad": 30})

    # Hora de inicio posterior a la de fin
    booking_payload = {
        "aula_id": 1,
        "usuario": "Prof. Lopez",
        "fecha": "2026-11-15",
        "hora_inicio": "12:00:00",
        "hora_fin": "10:00:00"
    }
    # Error de coherencia temporal -> 400 Bad Request
    response = client.post("/bookings", json=booking_payload)
    assert response.status_code == 400

def test_create_booking_overlap_conflict():
    client.post("/rooms", json={"nombre": "Seminario 1", "edificio": "Central", "capacidad": 30})

    # Reserva 1: 10:00 a 12:00
    client.post("/bookings", json={
        "aula_id": 1,
        "usuario": "Grupo A",
        "fecha": "2026-11-15",
        "hora_inicio": "10:00:00",
        "hora_fin": "12:00:00"
    })

    # Reserva 2 en solapamiento: 11:00 a 13:00 -> 409 Conflict
    conflict_payload = {
        "aula_id": 1,
        "usuario": "Grupo B",
        "fecha": "2026-11-15",
        "hora_inicio": "11:00:00",
        "hora_fin": "13:00:00"
    }
    response = client.post("/bookings", json=conflict_payload)
    assert response.status_code == 409

def test_delete_booking_not_found():
    response = client.delete("/bookings/999")
    assert response.status_code == 404