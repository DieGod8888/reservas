def reservation_data(
    room_id, start="2026-10-20T10:00:00", end="2026-10-20T11:00:00", name="Ana"
):
    return {
        "room_id": room_id,
        "customer_name": name,
        "start_time": start,
        "end_time": end,
    }


def test_create_reservation(client, room):
    response = client.post("/reservations", json=reservation_data(room["id"]))
    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "room_id": room["id"],
        "customer_name": "Ana",
        "start_time": "2026-10-20T10:00:00",
        "end_time": "2026-10-20T11:00:00",
    }


def test_create_reservation_in_missing_room(client):
    response = client.post("/reservations", json=reservation_data(999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Sala no encontrada"


def test_create_reservation_with_overlapping_schedule(client, room):
    client.post("/reservations", json=reservation_data(room["id"]))
    response = client.post(
        "/reservations",
        json=reservation_data(
            room["id"],
            start="2026-10-20T10:30:00",
            end="2026-10-20T11:30:00",
            name="Luis",
        ),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "La sala ya está reservada en ese horario"


def test_create_reservation_with_touching_schedule(client, room):
    client.post("/reservations", json=reservation_data(room["id"]))
    response = client.post(
        "/reservations",
        json=reservation_data(
            room["id"],
            start="2026-10-20T11:00:00",
            end="2026-10-20T12:00:00",
            name="Luis",
        ),
    )
    assert response.status_code == 201


def test_create_reservation_with_invalid_times(client, room):
    response = client.post(
        "/reservations",
        json=reservation_data(
            room["id"], start="2026-10-20T11:00:00", end="2026-10-20T10:00:00"
        ),
    )
    assert response.status_code == 422


def test_list_reservations(client, room):
    client.post("/reservations", json=reservation_data(room["id"]))
    client.post(
        "/reservations",
        json=reservation_data(
            room["id"], start="2026-10-20T12:00:00", end="2026-10-20T13:00:00"
        ),
    )
    response = client.get("/reservations")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_reservations_filtered_by_room(client, room):
    other_room = client.post("/rooms", json={"name": "Sala B", "capacity": 4}).json()
    client.post("/reservations", json=reservation_data(room["id"]))
    client.post("/reservations", json=reservation_data(other_room["id"]))
    response = client.get(f"/reservations?room_id={room['id']}")
    assert response.status_code == 200
    assert [item["room_id"] for item in response.json()] == [room["id"]]


def test_get_reservation(client, room):
    created = client.post("/reservations", json=reservation_data(room["id"])).json()
    response = client.get(f"/reservations/{created['id']}")
    assert response.status_code == 200
    assert response.json() == created


def test_get_reservation_not_found(client):
    response = client.get("/reservations/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Reserva no encontrada"


def test_update_reservation(client, room):
    created = client.post("/reservations", json=reservation_data(room["id"])).json()
    response = client.put(
        f"/reservations/{created['id']}",
        json=reservation_data(room["id"], name="Ana Pérez"),
    )
    assert response.status_code == 200
    assert response.json()["customer_name"] == "Ana Pérez"


def test_update_reservation_with_overlapping_schedule(client, room):
    first = client.post("/reservations", json=reservation_data(room["id"])).json()
    client.post(
        "/reservations",
        json=reservation_data(
            room["id"],
            start="2026-10-20T12:00:00",
            end="2026-10-20T13:00:00",
            name="Luis",
        ),
    )
    response = client.put(
        f"/reservations/{first['id']}",
        json=reservation_data(
            room["id"], start="2026-10-20T12:30:00", end="2026-10-20T13:30:00"
        ),
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "La sala ya está reservada en ese horario"


def test_update_reservation_in_missing_room(client, room):
    created = client.post("/reservations", json=reservation_data(room["id"])).json()
    response = client.put(f"/reservations/{created['id']}", json=reservation_data(999))
    assert response.status_code == 404
    assert response.json()["detail"] == "Sala no encontrada"


def test_update_reservation_not_found(client, room):
    response = client.put("/reservations/999", json=reservation_data(room["id"]))
    assert response.status_code == 404
    assert response.json()["detail"] == "Reserva no encontrada"


def test_delete_reservation(client, room):
    created = client.post("/reservations", json=reservation_data(room["id"])).json()
    response = client.delete(f"/reservations/{created['id']}")
    assert response.status_code == 204
    assert client.get(f"/reservations/{created['id']}").status_code == 404


def test_delete_reservation_not_found(client):
    response = client.delete("/reservations/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Reserva no encontrada"
