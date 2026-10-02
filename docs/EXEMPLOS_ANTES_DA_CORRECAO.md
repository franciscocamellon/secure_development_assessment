# Exemplos históricos — estado vulnerável antes das correções

> Estes trechos são documentação didática e **não são importados nem executados pela aplicação final**.

## V-01 — BOLA
```python
@app.get("/appointments/{appointment_id}")
def get_appointment(appointment_id: int, session: Session = Depends(get_session)):
    return session.get(Appointment, appointment_id)  # sem ownership
```

**Depois:** `owned_appointment` + `authorize_appointment_access`, com testes 403.

## V-02 — Stored XSS
```html
<td>{{ appointment.patient_comment | safe }}</td>
```

**Depois:** Jinja2 com auto-escape e sem `safe`, além do teste com `<script>` persistido.

## V-03 — Mass assignment
```python
appointment = Appointment(**payload_from_client)
```

**Depois:** schemas explícitos com `extra='forbid'` e atualização apenas de campos declarados.

## V-04 — SQL injection
```python
statement = text(f"SELECT * FROM appointment WHERE status = '{status}'")
```

**Depois:** SQLModel `select(...).where(Appointment.status == status)`, parametrizado pelo driver.

## V-05 — Security misconfiguration
```python
CORSMiddleware(app, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
```

**Depois:** allowlist explícita, métodos/headers limitados e security headers.

## V-06 — Brute force
Endpoint de login sem controle de frequência.

**Depois:** rate limit específico do login, mais restritivo que o limite geral da API.
