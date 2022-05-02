import pytest

from .sqlmodels import User, UserRole
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
# Because of their size, the test User data dictionaries are placed here for use below.
# User Roles only require a name and are therefore entered directly in each test.


test_user_data = {
    "role_id": 1,
    "given_name": "test",
    "family_name": "test",
    "username": "test.test",
    "password": "test",
    "email": "test.test@test.com",
    "phone": "555-123-4567"
}

test_user_data_2 = {
    "role_id": 2,
    "given_name": "tester",
    "family_name": "tester",
    "username": "tester.tester",
    "email": "tester.tester@test.com",
    "phone": "555-765-4321"
}


# ######################################################################################################################
# ########################################                               ###############################################
# ########################################             Tests             ###############################################
# ########################################                               ###############################################
# ######################################################################################################################


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


def test_empty_database_user(client: TestClient):
    response = client.get("/api/v2/users/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


def test_empty_database_users(client: TestClient):
    response = client.get("/api/v2/users/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No users found."}


def test_empty_database_role(client: TestClient):
    response = client.get("/api/v2/user_roles/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User role not found."}


def test_empty_database_roles(client: TestClient):
    response = client.get("/api/v2/user_roles/")
    assert response.status_code == 404
    assert response.json() == {"detail": "No user roles found."}


# ------------------------------------------------
#                      Users
# ------------------------------------------------


# --------------------  Create  ------------------


def test_user_create(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})

    response = client.post(
        "/api/v2/users/",
        json=test_user_data
    )
    assert response.status_code == 200

    data = response.json()
    assert data["role_id"] == 1
    assert data["given_name"] == "test"
    assert data["family_name"] == "test"
    assert data["username"] == "test.test"
    assert data["email"] == "test.test@test.com"
    assert data["phone"] == "555-123-4567"
    assert data["id"] is not None


def test_create_existing_user(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    client.post(
        "/api/v2/users/",
        json=test_user_data
    )

    response = client.post(
        "/api/v2/users/",
        json=test_user_data
    )
    assert response.status_code == 400
    assert response.json() == {"detail": "That email is already in use."}


# --------------------   Read   ------------------


def test_read_user_by_id(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/1")
    assert response.status_code == 200

    data = response.json()
    assert data["role_id"] == 1
    assert data["given_name"] == "test"
    assert data["family_name"] == "test"
    assert data["username"] == "test.test"
    assert data["email"] == "test.test@test.com"
    assert data["phone"] == "555-123-4567"
    assert data["id"] is not None


def test_read_user_by_email(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/email/test.test@test.com")
    assert response.status_code == 200

    data = response.json()
    assert data["role_id"] == 1
    assert data["given_name"] == "test"
    assert data["family_name"] == "test"
    assert data["username"] == "test.test"
    assert data["email"] == "test.test@test.com"
    assert data["phone"] == "555-123-4567"
    assert data["id"] is not None


def test_read_user_by_username(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/username/test.test")
    assert response.status_code == 200

    data = response.json()
    assert data["role_id"] == 1
    assert data["given_name"] == "test"
    assert data["family_name"] == "test"
    assert data["username"] == "test.test"
    assert data["email"] == "test.test@test.com"
    assert data["phone"] == "555-123-4567"
    assert data["id"] is not None


def test_read_users(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["role_id"] == 1
    assert data[0]["given_name"] == "test"
    assert data[0]["family_name"] == "test"
    assert data[0]["username"] == "test.test"
    assert data[0]["email"] == "test.test@test.com"
    assert data[0]["phone"] == "555-123-4567"
    assert data[0]["id"] is not None


def test_read_users_by_role(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/role_id/1")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["role_id"] == 1
    assert data[0]["given_name"] == "test"
    assert data[0]["family_name"] == "test"
    assert data[0]["username"] == "test.test"
    assert data[0]["email"] == "test.test@test.com"
    assert data[0]["phone"] == "555-123-4567"
    assert data[0]["id"] is not None


def test_read_user_id_list(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.get("/api/v2/users/ids/")
    assert response.status_code == 200
    assert response.json() == [1]


# --------------------  Update  ------------------


def test_update_user(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/user_roles/", json={"name": "guest"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.patch(
        "/api/v2/users/1",
        json=test_user_data_2
    )
    assert response.status_code == 200

    data = response.json()
    assert data["role_id"] == 2
    assert data["given_name"] == "tester"
    assert data["family_name"] == "tester"
    assert data["username"] == "tester.tester"
    assert data["email"] == "tester.tester@test.com"
    assert data["phone"] == "555-765-4321"
    assert data["id"] is not None


# --------------------  Delete  ------------------


def test_delete_user(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/users/", json=test_user_data)

    response = client.delete("/api/v2/users/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_nonextant_user(client: TestClient):
    response = client.delete("/api/v2/users/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User not found."}


# ------------------------------------------------
#                      User Roles
# ------------------------------------------------

# --------------------  Create  ------------------


def test_role_create(client: TestClient):
    response = client.post(
        "/api/v2/user_roles/",
        json={"name": "admin"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "admin"


def test_create_existing_role(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})

    response = client.post(
        "/api/v2/user_roles/",
        json={"name": "admin"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "User role with that name already exists."}


# --------------------   Read   ------------------


def test_read_roles(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})
    client.post("/api/v2/user_roles/", json={"name": "guest"})

    response = client.get("/api/v2/user_roles")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["name"] == "admin"
    assert data[0]["id"] is not None
    assert data[1]["name"] == "guest"
    assert data[1]["id"] is not None


def test_read_role_by_id(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})

    response = client.get("/api/v2/user_roles/1")
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "admin"
    assert data["id"] is not None


# --------------------  Update  ------------------


def test_update_role(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})

    response = client.patch(
        "/api/v2/user_roles/1",
        json={"name": "uber-admin"}
    )
    assert response.status_code == 200

    data = response.json()
    assert data["name"] == "uber-admin"


# --------------------  Delete  ------------------


def test_delete_role(client: TestClient):
    client.post("/api/v2/user_roles/", json={"name": "admin"})

    response = client.delete("/api/v2/user_roles/1")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_delete_nonextant_role(client: TestClient):
    response = client.delete("/api/v2/user_roles/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "User role not found."}
