from datetime import datetime

import pytest

from .sqlmodels import (
    Airport, Airplane, AirplaneType, Flight, Route
)
from .main import app, get_session

from fastapi.testclient import TestClient

from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


# ------------------------------------------------
#          Pytest Fixture: Test Session
# ------------------------------------------------

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    SQLModel.metadata.create_all(bind=engine)
    with Session(engine) as session:
        yield session


# ------------------------------------------------
#          Pytest Fixture: Test Client
# ------------------------------------------------


@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


# ------------------------------------------------
#                    Test Data
# ------------------------------------------------

airport_1 = {
    "iata_id": "JFK",
    "city": "New York, NY",
    "name": "John F. Kennedy International",
    "longitude": 40.639801,
    "latitude": -73.7789,
    "elevation": 13
}

airport_2 = {
    "iata_id": "LAX",
    "city": "Los Angeles, CA",
    "name": "Los Angeles International Airport",
    "longitude": 33.942501,
    "latitude": -118.407997,
    "elevation": 125
}

route_1 = {
    "origin_id": "JFK",
    "destination_id": "LAX"
}

route_2 = {
    "origin_id": "LAX",
    "destination_id": "JFK"
}

flight_1 = {
    "route_id": 1,
    "airplane_id": 1,
    "departure_time": str(datetime.utcnow()),
    "reserved_seats": 28,
    "seat_price": 121.47
}

flight_2 = {
    "route_id": 1,
    "airplane_id": 2,
    "departure_time": str(datetime.utcnow()),
    "reserved_seats": 112,
    "seat_price": 289.34
}


# ------------------------------------------------
#                Generic Routes
# ------------------------------------------------


def test_presence(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Flights microservice is present and ready for action."}


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"msg": "Healthy"}


# ------------------------------------------------
#                     Empty DB
# ------------------------------------------------


def test_empty_database_airplane(client: TestClient):
    response = client.get("/api/v2/airplanes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane not found"}


def test_empty_database_airplane_type(client: TestClient):
    response = client.get("/api/v2/airplane_types/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane type not found"}


def test_empty_database_airport(client: TestClient):
    response = client.get("/api/v2/airports/JFK")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airport not found"}


def test_empty_database_flight(client: TestClient):
    response = client.get("/api/v2/flights/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Flight not found"}


def test_empty_database_route(client: TestClient):
    response = client.get("/api/v2/routes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Route not found"}


# ------------------------------------------------
#                    Airplanes
# ------------------------------------------------

# --------------------  Create  ------------------


def test_airplane_create(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})

    response = client.post("/api/v2/airplanes/", json={"type_id": 1})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["type_id"] == 1


# --------------------   Read   ------------------


def test_airplane_read(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})

    response = client.get("/api/v2/airplanes/1")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["type_id"] == 1


def test_nonextant_airplane_read(client: TestClient):
    response = client.get("/api/v2/airplanes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane not found"}


def test_airplanes_read(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplane_types/", json={"max_capacity": 222})
    client.post("/api/v2/airplanes/", json={"type_id": 1})
    client.post("/api/v2/airplanes/", json={"type_id": 2})

    response = client.get("/api/v2/airplanes/")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["id"] is not None
    assert data[0]["type_id"] == 1
    assert data[1]["id"] is not None
    assert data[1]["type_id"] == 2


def test_airplane_read_by_type(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplane_types/", json={"max_capacity": 222})
    client.post("/api/v2/airplanes/", json={"type_id": 1})
    client.post("/api/v2/airplanes/", json={"type_id": 2})
    client.post("/api/v2/airplanes/", json={"type_id": 1})

    response = client.get("/api/v2/airplanes/type/1")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["id"] is not None
    assert data[0]["type_id"] == 1
    assert data[1]["id"] is not None
    assert data[1]["type_id"] == 1


# --------------------  Update  ------------------


def test_airplane_update(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplane_types/", json={"max_capacity": 222})
    client.post("/api/v2/airplanes/", json={"type_id": 1})

    response = client.patch("/api/v2/airplanes/1", json={"type_id": 2})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["type_id"] == 2


def test_nonextant_airplane_update(client: TestClient):
    response = client.patch("/api/v2/airplanes/1", json={"type_id": 2})
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane not found"}


# --------------------  Delete  ------------------


def test_airplane_delete(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})

    response = client.delete("/api/v2/airplanes/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_nonextant_airplane_delete(client: TestClient):
    response = client.delete("/api/v2/airplanes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane not found"}


# ------------------------------------------------
#                  Airplane Types
# ------------------------------------------------

# --------------------  Create  ------------------


def test_airplane_type_create(client: TestClient):
    response = client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["max_capacity"] == 150


def test_airplane_type_exists_create(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})

    response = client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    assert response.status_code == 400
    assert response.json() == {"detail": "An airplane type with that capacity already exists"}


# --------------------   Read   ------------------


def test_airplane_type_read(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})

    response = client.get("/api/v2/airplane_types/1")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["max_capacity"] == 150


# --------------------  Update  ------------------


def test_airplane_type_update(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})

    response = client.patch("/api/v2/airplane_types/1", json={"max_capacity": 200})
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["max_capacity"] == 200


# --------------------  Delete  ------------------


def test_airplane_type_delete(client: TestClient):
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})

    response = client.delete("/api/v2/airplane_types/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_airplane_type_nonextant_delete(client: TestClient):
    response = client.delete("/api/v2/airplane_types/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airplane type not found"}


# ------------------------------------------------
#                     Airports
# ------------------------------------------------

# --------------------  Create  ------------------


def test_airport_create(client: TestClient):
    response = client.post("/api/v2/airports/", json=airport_1)
    data = response.json()

    assert response.status_code == 200
    assert data["iata_id"] == airport_1["iata_id"]
    assert data["city"] == airport_1["city"]
    assert data["name"] == airport_1["name"]
    assert data["longitude"] == airport_1["longitude"]
    assert data["latitude"] == airport_1["latitude"]
    assert data["elevation"] == airport_1["elevation"]


# --------------------   Read   ------------------


def test_airport_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)

    response = client.get("/api/v2/airports/JFK")
    data = response.json()

    assert response.status_code == 200
    assert data["iata_id"] == airport_1["iata_id"]
    assert data["city"] == airport_1["city"]
    assert data["name"] == airport_1["name"]
    assert data["longitude"] == airport_1["longitude"]
    assert data["latitude"] == airport_1["latitude"]
    assert data["elevation"] == airport_1["elevation"]


# def test_airport_read_by_city(client: TestClient):
#     client.post("/api/v2/airports/", json=airport_1)
#
#     city = airport_1["city"]
#     response = client.get(f"/api/v2/airports/city/{city}")
#     data = response.json()
#
#     assert response.status_code == 200
#     assert data[0]["iata_id"] == airport_1["iata_id"]
#     assert data[0]["city"] == airport_1["city"]
#     assert data[0]["name"] == airport_1["name"]
#     assert data[0]["longitude"] == airport_1["longitude"]
#     assert data[0]["latitude"] == airport_1["latitude"]
#     assert data[0]["elevation"] == airport_1["elevation"]


def test_airports_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)

    response = client.get("/api/v2/airports/")
    data = response.json()

    assert response.status_code == 200
    assert data[0]["iata_id"] == airport_1["iata_id"]
    assert data[0]["city"] == airport_1["city"]
    assert data[0]["name"] == airport_1["name"]
    assert data[0]["longitude"] == airport_1["longitude"]
    assert data[0]["latitude"] == airport_1["latitude"]
    assert data[0]["elevation"] == airport_1["elevation"]
    assert data[1]["iata_id"] == airport_2["iata_id"]
    assert data[1]["city"] == airport_2["city"]
    assert data[1]["name"] == airport_2["name"]
    assert data[1]["longitude"] == airport_2["longitude"]
    assert data[1]["latitude"] == airport_2["latitude"]
    assert data[1]["elevation"] == airport_2["elevation"]


# --------------------  Update  ------------------


def test_airport_update(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)

    response = client.patch("/api/v2/airports/JFK", json=airport_2)
    assert response.status_code == 200

    data = response.json()
    assert data["iata_id"] == airport_2["iata_id"]
    assert data["city"] == airport_2["city"]
    assert data["name"] == airport_2["name"]
    assert data["longitude"] == airport_2["longitude"]
    assert data["latitude"] == airport_2["latitude"]
    assert data["elevation"] == airport_2["elevation"]


# --------------------  Delete  ------------------


def test_airport_delete(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)

    response = client.delete("/api/v2/airports/JFK")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_airport_nonextant_delete(client: TestClient):
    response = client.delete("/api/v2/airports/JFK")
    assert response.status_code == 404
    assert response.json() == {"detail": "Airport not found"}


# ------------------------------------------------
#                      Flights
# ------------------------------------------------

# --------------------  Create  ------------------


def test_flight_create(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})

    response = client.post("/api/v2/flights/", json=flight_1)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["route_id"] == flight_1["route_id"]
    assert data["airplane_id"] == flight_1["airplane_id"]
    assert data["departure_time"] == flight_1["departure_time"]
    assert data["reserved_seats"] == flight_1["reserved_seats"]


# --------------------   Read   ------------------


def test_flight_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})
    client.post("/api/v2/flights/", json=flight_1)

    response = client.get("/api/v2/flights/1")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["route_id"] == flight_1["route_id"]
    assert data["airplane_id"] == flight_1["airplane_id"]
    assert data["departure_time"] == flight_1["departure_time"]
    assert data["reserved_seats"] == flight_1["reserved_seats"]


def test_flights_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})      # plane 1
    client.post("/api/v2/airplanes/", json={"type_id": 1})      # plane 2
    client.post("/api/v2/flights/", json=flight_1)
    client.post("/api/v2/flights/", json=flight_2)

    response = client.get("/api/v2/flights/")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] is not None
    assert data[0]["route_id"] == flight_1["route_id"]
    assert data[0]["airplane_id"] == flight_1["airplane_id"]
    assert data[0]["departure_time"] == flight_1["departure_time"]
    assert data[0]["reserved_seats"] == flight_1["reserved_seats"]
    assert data[1]["id"] is not None
    assert data[1]["route_id"] == flight_2["route_id"]
    assert data[1]["airplane_id"] == flight_2["airplane_id"]
    assert data[1]["departure_time"] == flight_2["departure_time"]
    assert data[1]["reserved_seats"] == flight_2["reserved_seats"]


def test_flights_read_by_route(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})      # plane 1
    client.post("/api/v2/airplanes/", json={"type_id": 1})      # plane 2
    client.post("/api/v2/flights/", json=flight_1)
    client.post("/api/v2/flights/", json=flight_2)

    response = client.get("/api/v2/flights/route/1")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] is not None
    assert data[0]["route_id"] == flight_1["route_id"]
    assert data[1]["id"] is not None
    assert data[1]["route_id"] == flight_2["route_id"]


# --------------------  Update  ------------------


def test_flight_update(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})
    client.post("/api/v2/flights/", json=flight_1)

    response = client.patch("/api/v2/flights/1", json=flight_2)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["route_id"] == flight_2["route_id"]
    assert data["airplane_id"] == flight_2["airplane_id"]
    assert data["departure_time"] == flight_2["departure_time"]
    assert data["reserved_seats"] == flight_2["reserved_seats"]


# --------------------  Delete  ------------------


def test_flight_delete(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/airplane_types/", json={"max_capacity": 150})
    client.post("/api/v2/airplanes/", json={"type_id": 1})
    client.post("/api/v2/flights/", json=flight_1)

    response = client.delete("/api/v2/flights/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_flight_nonextant_delete(client: TestClient):
    response = client.delete("/api/v2/flights/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Flight not found"}


# ------------------------------------------------
#                      Routes
# ------------------------------------------------

# --------------------  Create  ------------------


def test_route_create(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)

    response = client.post("/api/v2/routes/", json=route_1)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["origin_id"] == "JFK"
    assert data["destination_id"] == "LAX"
    assert data["duration"] is not None


# --------------------   Read   ------------------


def test_route_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/routes/", json=route_2)

    response = client.get("/api/v2/routes/1")
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["origin_id"] == "JFK"
    assert data["destination_id"] == "LAX"
    assert data["duration"] is not None


def test_routes_read(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/routes/", json=route_2)

    response = client.get("/api/v2/routes")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 2
    assert data[0]["id"] is not None
    assert data[0]["origin_id"] == "JFK"
    assert data[0]["destination_id"] == "LAX"
    assert data[0]["duration"] is not None
    assert data[1]["id"] is not None
    assert data[1]["origin_id"] == "LAX"
    assert data[1]["destination_id"] == "JFK"
    assert data[1]["duration"] is not None


def test_route_read_by_origin(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/routes/", json=route_2)

    response = client.get("/api/v2/routes/origin/JFK")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] is not None
    assert data[0]["origin_id"] == "JFK"


def test_route_read_by_destination(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)
    client.post("/api/v2/routes/", json=route_2)

    response = client.get("/api/v2/routes/destination/JFK")
    data = response.json()

    assert response.status_code == 200
    assert len(data) == 1
    assert data[0]["id"] is not None
    assert data[0]["destination_id"] == "JFK"


# --------------------  Update  ------------------


def test_route_update(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)

    response = client.patch("/api/v2/routes/1", json=route_2)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] is not None
    assert data["origin_id"] == "LAX"
    assert data["destination_id"] == "JFK"
    assert data["duration"] is not None


# --------------------  Delete  ------------------


def test_route_delete(client: TestClient):
    client.post("/api/v2/airports/", json=airport_1)
    client.post("/api/v2/airports/", json=airport_2)
    client.post("/api/v2/routes/", json=route_1)

    response = client.delete("/api/v2/routes/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_route_nonextant_delete(client: TestClient):
    response = client.delete("/api/v2/routes/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "Route not found"}

