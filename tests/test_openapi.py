def test_openapi_declares_bearer_security(client):
    schema = client.get("/openapi.json").json()
    schemes = schema["components"]["securitySchemes"]
    assert "OAuth2PasswordBearer" in schemes
    assert "/appointments/{appointment_id}" in schema["paths"]


def test_sensitive_internal_fields_not_in_public_schema(client):
    schema = client.get("/openapi.json").json()
    appointment = schema["components"]["schemas"]["AppointmentPublic"]
    props = appointment["properties"]
    assert "audit_note" not in props
    assert "hashed_password" not in props
