from datetime import datetime

import pytest

from .sqlmodels import (
    Booking, BookingGuest, BookingPayment, Passenger
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


# ------------------------------------------------
#                Generic Routes
# ------------------------------------------------


def test_presence(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Users microservice is present and ready for action."}


def test_health_check(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"msg": "Healthy"}


# ------------------------------------------------
#                     Empty DB
# ------------------------------------------------





# ------------------------------------------------
#                    Bookings
# ------------------------------------------------

# --------------------  Create  ------------------





# --------------------   Read   ------------------





# --------------------  Update  ------------------





# --------------------  Delete  ------------------





# ------------------------------------------------
#                 Booking Guests
# ------------------------------------------------

# --------------------  Create  ------------------





# --------------------   Read   ------------------





# --------------------  Update  ------------------





# --------------------  Delete  ------------------





# ------------------------------------------------
#                 Booking Payments
# ------------------------------------------------

# --------------------  Create  ------------------





# --------------------   Read   ------------------





# --------------------  Update  ------------------





# --------------------  Delete  ------------------





# ------------------------------------------------
#                     Passenger
# ------------------------------------------------

# --------------------  Create  ------------------





# --------------------   Read   ------------------





# --------------------  Update  ------------------





# --------------------  Delete  ------------------


