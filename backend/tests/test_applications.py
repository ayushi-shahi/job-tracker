import pytest


def auth_headers(token):
    return {"Authorization": f"Bearer {token}"}


def create_app_payload(**overrides):
    base = {
        "company": "Acme",
        "role": "Engineer",
        "applied_date": "2026-03-31",
        "source": "LinkedIn"
    }
    base.update(overrides)
    return base


# --- Creation ---

def test_create_application_success(client, auth_token):
    res = client.post("/applications", json=create_app_payload(),
                      headers=auth_headers(auth_token))
    assert res.status_code == 201
    data = res.get_json()
    assert data["company"] == "Acme"
    assert data["status"] == "applied"
    assert len(data["status_history"]) == 1


def test_create_application_missing_field(client, auth_token):
    res = client.post("/applications", json={"company": "Acme"},
                      headers=auth_headers(auth_token))
    assert res.status_code == 422


def test_create_requires_auth(client):
    res = client.post("/applications", json=create_app_payload())
    assert res.status_code == 401


# --- Status transitions ---

def test_valid_transition(client, auth_token):
    res = client.post("/applications", json=create_app_payload(),
                      headers=auth_headers(auth_token))
    app_id = res.get_json()["id"]

    res = client.patch(f"/applications/{app_id}/status",
                       json={"status": "screening"},
                       headers=auth_headers(auth_token))
    assert res.status_code == 200
    assert res.get_json()["status"] == "screening"


def test_invalid_transition_blocked(client, auth_token):
    res = client.post("/applications", json=create_app_payload(),
                      headers=auth_headers(auth_token))
    app_id = res.get_json()["id"]

    # Try jumping from applied directly to accepted
    res = client.patch(f"/applications/{app_id}/status",
                       json={"status": "accepted"},
                       headers=auth_headers(auth_token))
    assert res.status_code == 422
    assert "Cannot transition" in res.get_json()["error"]


def test_rejected_is_terminal(client, auth_token):
    res = client.post("/applications", json=create_app_payload(),
                      headers=auth_headers(auth_token))
    app_id = res.get_json()["id"]

    client.patch(f"/applications/{app_id}/status",
                 json={"status": "rejected"},
                 headers=auth_headers(auth_token))

    # Try to move out of rejected
    res = client.patch(f"/applications/{app_id}/status",
                       json={"status": "screening"},
                       headers=auth_headers(auth_token))
    assert res.status_code == 422


def test_status_history_recorded(client, auth_token):
    res = client.post("/applications", json=create_app_payload(),
                      headers=auth_headers(auth_token))
    app_id = res.get_json()["id"]

    client.patch(f"/applications/{app_id}/status",
                 json={"status": "screening"},
                 headers=auth_headers(auth_token))

    res = client.get(f"/applications/{app_id}",
                     headers=auth_headers(auth_token))
    history = res.get_json()["status_history"]
    assert len(history) == 2
    assert history[0]["to_status"] == "applied"
    assert history[1]["from_status"] == "applied"
    assert history[1]["to_status"] == "screening"


# --- Stats ---

def test_stats_returns_counts(client, auth_token):
    res = client.get("/applications/stats", headers=auth_headers(auth_token))
    assert res.status_code == 200
    data = res.get_json()
    assert "total" in data
    assert "by_status" in data