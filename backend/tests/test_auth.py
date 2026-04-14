import pytest


def test_login_valido(client):
    res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "CambiaMeEnProduccion2024!",
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert len(data["access_token"]) > 20


def test_login_password_incorrecta(client):
    res = client.post("/api/auth/login", json={
        "username": "admin",
        "password": "password_incorrecta",
    })
    assert res.status_code == 401
    assert "detail" in res.json()


def test_login_usuario_incorrecto(client):
    res = client.post("/api/auth/login", json={
        "username": "hacker",
        "password": "CambiaMeEnProduccion2024!",
    })
    assert res.status_code == 401


def test_login_payload_vacio(client):
    res = client.post("/api/auth/login", json={})
    assert res.status_code == 422


def test_acceso_privado_sin_token(client):
    res = client.get("/api/leads")
    assert res.status_code == 401


def test_acceso_privado_token_invalido(client):
    res = client.get("/api/leads", headers={"Authorization": "Bearer token_falso"})
    assert res.status_code == 401


def test_acceso_privado_token_malformado(client):
    res = client.get("/api/leads", headers={"Authorization": "Basic admin:pass"})
    assert res.status_code == 401
