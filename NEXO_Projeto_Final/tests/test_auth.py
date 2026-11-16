import re

import pytest

from app import create_app
from app.models.users import User
from iniciar_bd import iniciar_bd


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "nexo.sqlite3"
    iniciar_bd(db_path)
    app = create_app({"TESTING": True, "SECRET_KEY": "test-secret-long-enough", "SQLITE_DB": db_path})
    return app.test_client()


def token(client):
    html = client.get("/login").get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)


def test_private_page_requires_authentication(client):
    response = client.get("/bem-vindo")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_login_requires_csrf_and_valid_password(client):
    assert client.post("/login", data={"username": "demo", "password": "NexoDemo2026!"}).status_code == 400
    csrf = token(client)
    bad = client.post("/login", data={"username": "demo", "password": "errada", "csrf_token": csrf})
    assert bad.status_code == 401
    assert client.get("/bem-vindo").status_code == 302
    ok = client.post("/login", data={"username": "demo", "password": "NexoDemo2026!", "csrf_token": csrf})
    assert ok.status_code == 302
    assert ok.headers["Location"].endswith("/bem-vindo")
    assert "Usuário Demo" in client.get("/bem-vindo").get_data(as_text=True)


def test_logout_clears_session_and_requires_csrf(client):
    csrf = token(client)
    client.post("/login", data={"username": "demo", "password": "NexoDemo2026!", "csrf_token": csrf})
    assert client.get("/logout").status_code == 405
    assert client.post("/logout").status_code == 400
    welcome_html = client.get("/bem-vindo").get_data(as_text=True)
    logout_token = re.search(r'name="csrf_token" value="([^"]+)"', welcome_html).group(1)
    assert client.post("/logout", data={"csrf_token": logout_token}).status_code == 302
    assert client.get("/bem-vindo").status_code == 302


def test_removed_user_cannot_continue_using_session(client):
    csrf = token(client)
    client.post("/login", data={"username": "demo", "password": "NexoDemo2026!", "csrf_token": csrf})
    User.find_by_username("demo", client.application.config["SQLITE_DB"]).delete()
    assert client.get("/bem-vindo").status_code == 302


def test_secret_key_is_configured(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    assert create_app().secret_key
