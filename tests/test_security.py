from unittest.mock import patch
from tests.conftest import token_for


def test_extra_field_is_rejected(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:write"])
    payload = {
        "patient_id": seeded["p1"].id,
        "professional_id": seeded["d1"].id,
        "scheduled_at": "2026-10-06T12:00:00+00:00",
        "reason": "Consulta segura",
        "patient_comment": "ok",
        "audit_note": "attacker tries mass assignment",
    }
    response = client.post("/appointments/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_regex_rejects_script_payload(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:write"])
    payload = {
        "patient_id": seeded["p1"].id,
        "professional_id": seeded["d1"].id,
        "scheduled_at": "2026-10-06T12:00:00+00:00",
        "reason": "<script>alert(1)</script>",
    }
    response = client.post("/appointments/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 422


def test_security_headers_present(client):
    response = client.get("/health")
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "max-age" in response.headers["strict-transport-security"]


def test_jinja_autoescape_prevents_stored_xss(client, session, seeded):
    seeded["a1"].patient_comment = "<script>alert('xss')</script>"
    session.add(seeded["a1"])
    session.commit()
    token = token_for(seeded["reception"], ["appointments:read"])
    response = client.get("/internal/agenda?day=2026-10-05", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert "<script>" not in response.text
    assert "&lt;script&gt;" in response.text


def test_authentication_service_can_be_mocked_for_unit_test(client):
    fake_user = type("FakeUser", (), {"username":"mocked", "role":"professional", "id":1, "is_active":True, "mfa_enabled":False})()
    with patch("app.routes.auth.authenticate_user", return_value=fake_user):
        response = client.post("/auth/token", data={"username":"x", "password":"y"})
    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"


def test_m2m_client_credentials_rejects_scope_escalation(client):
    with patch("app.routes.auth.verify_m2m_client", return_value=True):
        response = client.post(
            "/auth/m2m-token",
            data={
                "grant_type": "client_credentials",
                "client_id": "lab-test",
                "client_secret": "Strong-Lab-Secret-123!",
                "scope": "appointments:write",
            },
        )
    assert response.status_code == 403


def test_m2m_client_credentials_issues_limited_claims(client):
    from app.security.auth import decode_token
    with patch("app.routes.auth.verify_m2m_client", return_value=True):
        response = client.post(
            "/auth/m2m-token",
            data={
                "grant_type": "client_credentials",
                "client_id": "lab-test",
                "client_secret": "Strong-Lab-Secret-123!",
                "scope": "appointments:read_availability",
            },
        )
    assert response.status_code == 200
    claims = decode_token(response.json()["access_token"])
    assert claims["token_type"] == "m2m"
    assert claims["grant_type"] == "client_credentials"
    assert claims["scopes"] == ["appointments:read_availability"]
