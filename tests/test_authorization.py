from tests.conftest import token_for


def test_non_admin_cannot_access_admin_route(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:read"])
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_bola_blocked_for_another_professional(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:read"])
    response = client.get(f"/appointments/{seeded['a2'].id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_patient_cannot_read_another_patient_appointment(client, seeded):
    token = token_for(seeded["patient1"], ["appointments:read"])
    response = client.get(f"/appointments/{seeded['a2'].id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_m2m_token_cannot_use_human_write_endpoint(client, seeded):
    from app.security.auth import create_access_token
    token, _ = create_access_token(subject="lab-demo", role="partner_lab", scopes=["appointments:read_availability"], token_type="m2m")
    response = client.get(f"/appointments/{seeded['a1'].id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code in (401, 403)


def test_admin_cannot_modify_clinical_appointment(client, seeded):
    token = token_for(seeded["admin"], ["appointments:write", "admin"])
    response = client.patch(
        f"/appointments/{seeded['a1'].id}",
        json={"status": "cancelled"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403
