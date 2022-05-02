from fastapi.testclient import TestClient

from .main import app

client = TestClient(app)


# ------------------------------------------------
#                Generic Routes
# ------------------------------------------------


def test_presence():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"msg": "Users microservice is present and ready for action."}


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"msg": "Healthy"}
