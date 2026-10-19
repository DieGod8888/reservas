def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_room(client):
    response = client.post("/rooms", json={"name": "Sala A", "capacity": 8})
    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Sala A", "capacity": 8}


def test_create_room_with_duplicate_name(client):
    client.post("/rooms", json={"name": "Sala A", "capacity": 8})
    response = client.post("/rooms", json={"name": "Sala A", "capacity": 4})
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una sala con ese nombre"


def test_create_room_with_invalid_data(client):
    response = client.post("/rooms", json={"name": "Sala A", "capacity": "ocho"})
    assert response.status_code == 422


def test_list_rooms(client):
    client.post("/rooms", json={"name": "Sala A", "capacity": 8})
    client.post("/rooms", json={"name": "Sala B", "capacity": 4})
    response = client.get("/rooms")
    assert response.status_code == 200
    assert [room["name"] for room in response.json()] == ["Sala A", "Sala B"]


def test_get_room(client, room):
    response = client.get(f"/rooms/{room['id']}")
    assert response.status_code == 200
    assert response.json() == room


def test_get_room_not_found(client):
    response = client.get("/rooms/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sala no encontrada"


def test_update_room(client, room):
    response = client.put(
        f"/rooms/{room['id']}", json={"name": "Sala B", "capacity": 20}
    )
    assert response.status_code == 200
    assert response.json() == {"id": room["id"], "name": "Sala B", "capacity": 20}


def test_update_room_not_found(client):
    response = client.put("/rooms/999", json={"name": "Sala A", "capacity": 8})
    assert response.status_code == 404
    assert response.json()["detail"] == "Sala no encontrada"


def test_update_room_with_duplicate_name(client, room):
    client.post("/rooms", json={"name": "Sala B", "capacity": 4})
    response = client.put(
        f"/rooms/{room['id']}", json={"name": "Sala B", "capacity": 8}
    )
    assert response.status_code == 409
    assert response.json()["detail"] == "Ya existe una sala con ese nombre"


def test_delete_room(client, room):
    response = client.delete(f"/rooms/{room['id']}")
    assert response.status_code == 204
    assert client.get(f"/rooms/{room['id']}").status_code == 404


def test_delete_room_not_found(client):
    response = client.delete("/rooms/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Sala no encontrada"


def test_delete_room_with_reservations(client, room):
    client.post(
        "/reservations",
        json={
            "room_id": room["id"],
            "customer_name": "Ana",
            "start_time": "2026-10-20T10:00:00",
            "end_time": "2026-10-20T11:00:00",
        },
    )
    response = client.delete(f"/rooms/{room['id']}")
    assert response.status_code == 409
    assert response.json()["detail"] == "La sala tiene reservas"
