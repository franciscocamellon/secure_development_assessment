# Clinic Secure API — Assessment FastAPI / DevSecOps

Projeto de referência que resolve os Exercícios 1–13 de forma incremental e integrada.

## 1. Ambiente virtual e instalação

### Windows PowerShell
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
Copy-Item .env.example .env
```

### Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
cp .env.example .env
```

Edite o `.env` e troque os valores de demonstração. **Nunca entregue o `.env`.**

## 2. Subir a aplicação
```bash
uvicorn app.main:app --reload
```

- Swagger: `http://127.0.0.1:8000/docs`
- OpenAPI: `http://127.0.0.1:8000/openapi.json`
- Health: `http://127.0.0.1:8000/health`

## 3. Testes
```bash
pytest -q --cov=app --cov-report=term-missing
```

## 4. Credenciais de demonstração
Somente quando `SEED_DEMO_DATA=true`, os usuários são criados a partir das variáveis do `.env`. O administrador exige `X-MFA-Code`, obtido pelo TOTP baseado em `DEMO_ADMIN_MFA_SECRET`.

Exemplo para gerar o código MFA localmente:
```bash
python -c "import pyotp, os; print(pyotp.TOTP(os.environ['DEMO_ADMIN_MFA_SECRET']).now())"
```

## 5. Testar autenticação
```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=doctor.demo&password=ChangeMe-Doctor-123!"
```

## 6. M2M do laboratório
Foi escolhido **OAuth 2.0 Client Credentials**, pois não há usuário humano no fluxo. O token recebe `token_type=m2m`, `role=partner_lab` e somente o scope `appointments:read_availability`.

```bash
curl -X POST http://127.0.0.1:8000/auth/m2m-token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=client_credentials&client_id=lab-demo&client_secret=ChangeMe-Lab-123!&scope=appointments%3Aread_availability"
```

## 7. OWASP ZAP baseline (passivo)
Com a API em execução:
```bash
docker run --rm --network host -v "$(pwd):/zap/wrk/:rw" ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://127.0.0.1:8000 -r zap-report.html -J zap-report.json -a -j
```

No Windows Docker Desktop, pode ser necessário usar `host.docker.internal:8000` em vez de `127.0.0.1:8000`.

## 8. Estrutura
```text
app/
  main.py
  config.py
  database.py
  routes/
  models/
  security/
  templates/
tests/
scripts/
.zap/
.github/workflows/
evidence/
RELATORIO_TECNICO.md
```

## 9. Observação importante sobre evidências
O pacote inclui código, roteiro e arquivos de configuração. Evidências que dependem de execução (prints, saída real de ZAP/GitHub Actions) precisam ser geradas na máquina/conta do aluno; o projeto não falsifica essas saídas.
