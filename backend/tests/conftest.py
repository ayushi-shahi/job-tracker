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
def auth_token(client, db):
    """
    Creates a fresh user per test function to avoid cross-test state.
    Uses a counter stored on the fixture to generate unique emails.
    """
    import uuid
    unique_email = f"testuser_{uuid.uuid4().hex[:8]}@example.com"

    reg = client.post("/auth/register", json={
        "email": unique_email,
        "password": "password123"
    })
    assert reg.status_code == 201, f"Registration failed: {reg.get_json()}"
    return reg.get_json()["token"]