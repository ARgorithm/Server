from fastapi.testclient import TestClient
from app.main import app,config

client = TestClient(app)

def test_read():
    response = client.get("/argorithms/list")
    assert response.status_code == 200