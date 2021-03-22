import json
from fastapi.testclient import TestClient
from app.main import app

def test_init():
    client = TestClient(app)
    response = client.get("/argorithm")
    assert response.status_code == 200
    content = json.loads(response.content)
    assert content['auth'] == "DISABLED"