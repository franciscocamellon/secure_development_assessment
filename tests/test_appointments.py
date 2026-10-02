from tests.conftest import token_for


def test_get_own_appointment_success(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:read"])
    response = client.get(f"/appointments/{seeded['a1'].id}", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["reason"] == "Consulta retorno"
    assert "audit_note" not in body


def test_create_appointment_success(client, seeded):
    token = token_for(seeded["pro1"], ["appointments:write"])
    payload = {
        "patient_id": seeded["p1"].id,
        "professional_id": seeded["d1"].id,
        "scheduled_at": "2026-10-06T12:00:00+00:00",
        "reason": "Acompanhamento clinico",
        "patient_comment": "Paciente estavel",
    }
    response = client.post("/appointments/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 201
    assert "audit_note" not in response.json()
