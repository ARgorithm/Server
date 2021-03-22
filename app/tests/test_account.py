import json
from fastapi.testclient import TestClient
from app.main import app

def test_auth():
    client = TestClient(app)
    response = client.get("/auth")
    assert response.status_code == 404

def test_programmer(monkeypatch):
    monkeypatch.setenv("AUTH", "ENABLED")
    client = TestClient(app)
    account = {"username" : "programmer@email.com", "password" : "test"}
    response = client.post("/programmers/register", data = account)
    assert response.status_code == 200
    response = client.post("/programmers/register", data = account)
    assert response.status_code == 409

    notexisting = {"username" : "programmer@gmail.com", "password" : "test"}
    wrongpassword = {"username" : "programmer@email.com", "password" : "test1"}
    response = client.post("/programmers/login", data = notexisting)
    assert response.status_code == 404
    response = client.post("/programmers/login", data = wrongpassword)
    assert response.status_code == 401
    response = client.post("/programmers/login", data = account)
    assert response.status_code == 200
    content = json.loads(response.content)
    assert content["token_type"] == "bearer"

    token = content["access_token"]
    dummy = "faultyjwt"
    headers = {"authorization" : "Bearer " + dummy}
    response =client.post("/programmers/verify", headers = headers)
    assert response.status_code == 401
    headers = {"authorization" : "Bearer " + token}
    response =client.post("/programmers/verify", headers = headers)
    assert response.status_code == 200
    