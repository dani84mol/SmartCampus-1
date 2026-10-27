const API_URL = "http://localhost:8000";

async function loadData() {
    try {
        // Cargar Aulas
        const resRooms = await fetch(`${API_URL}/rooms`);
        const rooms = await resRooms.json();
        const roomsList = document.getElementById("rooms-list");
        const roomSelect = document.getElementById("booking-room-select");
                 
        roomsList.innerHTML = "";
        roomSelect.innerHTML = '<option value="">-- Seleccione un aula --</option>';
                 
        rooms.forEach(room => {
            roomsList.innerHTML += `<li>${room.nombre} (${room.edificio}) - Capacidad: ${room.capacidad} 
                 <button onclick="deleteRoom(${room.id})" style="background:#dc3545; padding: 5px;">Eliminar</button></li>`;
            roomSelect.innerHTML += `<option value="${room.id}">${room.nombre} (${room.edificio})</option>`;
        });

        // Cargar Reservas
        const resBookings = await fetch(`${API_URL}/bookings`);
        const bookings = await resBookings.json();
        const bookingsList = document.getElementById("bookings-list");
                 
        bookingsList.innerHTML = "";
        bookings.forEach(b => {
            bookingsList.innerHTML += `<li>Aula ID: ${b.aula_id} | ${b.usuario} (${b.fecha} de ${b.hora_inicio} a ${b.hora_fin}) 
                <button onclick="deleteBooking(${b.id})" style="background:#dc3545; padding: 5px;">Cancelar</button></li>`;
        });
    } catch (error) {
        console.error("Error al conectar con la API:", error);
    }
}

// Crear Aula
document.getElementById("room-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const response = await fetch(`${API_URL}/rooms`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            nombre: document.getElementById("room-name").value,
            edificio: document.getElementById("room-building").value,
            capacidad: parseInt(document.getElementById("room-capacity").value),
            equipamiento: []
        })
    });
    if (response.ok) {
        document.getElementById("msg-room").innerHTML = '<p class="success">Aula creada con éxito</p>';
        document.getElementById("room-form").reset();
        loadData();
    } else {
        document.getElementById("msg-room").innerHTML = '<p class="error">Error al crear el aula</p>';
    }
});

// Crear Reserva
document.getElementById("booking-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const response = await fetch(`${API_URL}/bookings`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            aula_id: parseInt(document.getElementById("booking-room-select").value),
            usuario: document.getElementById("booking-user").value,
            fecha: document.getElementById("booking-date").value,
            hora_inicio: document.getElementById("booking-start").value + ":00",
            hora_fin: document.getElementById("booking-end").value + ":00"
        })
    });
    const msgDiv = document.getElementById("msg-booking");
    if (response.status === 201) {
        msgDiv.innerHTML = '<p class="success">Reserva creada correctamente</p>';
        document.getElementById("booking-form").reset();
        loadData();
    } else if (response.status === 409) {
        msgDiv.innerHTML = '<p class="error">Conflicto: Ya existe una reserva en ese horario para esta aula.</p>';
    } else if (response.status === 400) {
        msgDiv.innerHTML = '<p class="error">Error: La hora de inicio debe ser anterior a la de fin.</p>';
    } else {
        msgDiv.innerHTML = '<p class="error">Error al procesar la reserva.</p>';
    }
});

async function deleteRoom(id) {
    await fetch(`${API_URL}/rooms/${id}`, { method: "DELETE" });
    loadData();
}

async function deleteBooking(id) {
    await fetch(`${API_URL}/bookings/${id}`, { method: "DELETE" });
    loadData();
}

loadData();