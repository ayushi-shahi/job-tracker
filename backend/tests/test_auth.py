def test_register_success(client):
    res = client.post("/auth/register", json={
        "email": "new@example.com",
        "password": "password123"
    })
    assert res.status_code == 201
    data = res.get_json()
    assert "token" in data
    assert data["user"]["email"] == "new@example.com"
    assert "password_hash" not in data["user"]


def test_register_duplicate_email(client):
    client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "password123"
    })
    res = client.post("/auth/register", json={
        "email": "dup@example.com",
        "password": "password123"
    })
    assert res.status_code == 409


def test_register_invalid_email(client):
    res = client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "password123"
    })
    assert res.status_code == 422


def test_register_short_password(client):
    res = client.post("/auth/register", json={
        "email": "short@example.com",
        "password": "123"
    })
    assert res.status_code == 422


def test_login_success(client):
    client.post("/auth/register", json={
        "email": "login@example.com",
        "password": "password123"
    })
    res = client.post("/auth/login", json={
        "email": "login@example.com",
        "password": "password123"
    })
    assert res.status_code == 200
    assert "token" in res.get_json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={
        "email": "wrong@example.com",
        "password": "password123"
    })
    res = client.post("/auth/login", json={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert res.status_code == 401