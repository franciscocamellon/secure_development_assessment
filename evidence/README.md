# Evidências a capturar antes da entrega

Este diretório documenta os prints/saídas que o aluno deve gerar localmente. Não contém evidência fabricada.

1. `01-venv-uvicorn.png`: terminal com `.venv` ativo e `uvicorn app.main:app --reload`, mais `GET /health` e Swagger.
2. `02-response-model.png`: resposta de `/appointments/{id}` sem `audit_note` e schema OpenAPI de `AppointmentPublic`.
3. `02-xss-autoescape.png`: comentário com `<script>` persistido em ambiente de teste e HTML mostrando `&lt;script&gt;`.
4. `06-auth-jwt-mfa.png`: login de profissional e tentativa de admin sem/with `X-MFA-Code`.
5. `06-bola-403.png`: profissional A tentando consultar consulta do profissional B e recebendo 403.
6. `07-m2m.png`: token M2M com claim `token_type=m2m`/scope limitado e acesso à disponibilidade.
7. `08-09-antes-depois.png`: compare `docs/EXEMPLOS_ANTES_DA_CORRECAO.md` com os testes/rotas finais (BOLA, XSS e mass assignment).
8. `09-validacao.png`: payload com campo extra e payload `<script>` retornando 422.
9. `10-headers-cors-rate-limit.png`: headers HTTP, preflight CORS permitido/negado e 429 após limite do login.
10. `11-sqlmodel-env.png`: `.env.example`, query SQLModel e aplicação iniciando sem segredo no repositório.
11. `12-pytest.txt`: `pytest -q --cov=app`.
12. `12-bandit.json`: relatório Bandit.
13. `12-pip-audit.txt`: saída pip-audit.
14. `12-github-actions.png`: execução do workflow com gate.
15. `13-zap-report.html` e/ou `.json`: relatório real do ZAP baseline.
16. `13-openapi-audit.txt`: `pytest tests/test_openapi.py -q` e observações do relatório.

> Importante: o scan ZAP deve ser executado no seu ambiente. Não declare findings como “encontrados pelo ZAP” sem anexar a saída real.
