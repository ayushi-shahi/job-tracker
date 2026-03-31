import pytest
from app import create_app
from app.extensions import db as _db


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret",
    })
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    with app.app_context():
        yield _db
        _db.session.rollback()


@pytest.fixture(scope="function")
def client(app):
    return app.test_client()


@pytest.fixture(scope="function")
def auth_token(client):
    client.post("/auth/register", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    response = client.post("/auth/login", json={
        "email": "testuser@example.com",
        "password": "password123"
    })
    return response.get_json()["token"]