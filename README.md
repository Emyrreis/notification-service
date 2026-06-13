# Notification Service

Projeto academico da disciplina de Teste e Qualidade de Software.

A API REST recebe eventos de notificacao por e-mail ou SMS, valida os dados com
Pydantic, aciona um provedor externo mockado, persiste a notificacao em SQLite e
expoe health check, metricas simples, logs estruturados e quality gates no CI.

## Tecnologias

| Tecnologia | Versao | Funcao |
|---|---:|---|
| Python | 3.12 | Linguagem principal |
| FastAPI | 0.115.6 | API REST |
| Pydantic | 2.10.4 | Validacao de dados |
| SQLAlchemy | 2.0.36 | Persistencia SQLite |
| Uvicorn | 0.34.0 | Servidor ASGI |
| Pytest | 8.3.4 | Testes automatizados |
| pytest-cov | 6.0.0 | Cobertura com gate minimo |
| httpx | 0.28.1 | Cliente HTTP usado pelo TestClient |
| Ruff | 0.15.17 | Lint no CI |
| mutmut | 3.6.0 | Testes de mutacao manuais |

## Como executar

```powershell
python -m venv .venv
.\.venv\Scripts\activate
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

A API fica disponivel em `http://localhost:8000`.

Swagger: `http://localhost:8000/docs`

## Endpoints

| Metodo | Rota | Descricao |
|---|---|---|
| `GET` | `/health` | Retorna status, nome do servico, versao e timestamp UTC |
| `GET` | `/metrics` | Retorna contadores em memoria |
| `POST` | `/notifications` | Cria uma notificacao e aciona o sender mockado |
| `GET` | `/notifications` | Lista notificacoes persistidas |
| `GET` | `/notifications/{id}` | Busca notificacao por ID |

Exemplo de `/health`:

```json
{
  "status": "ok",
  "service": "notification-service",
  "version": "1.0.0",
  "timestamp_utc": "2026-06-13T16:00:00+00:00"
}
```

Exemplo de `/metrics`:

```json
{
  "notifications_created_total": 1,
  "notifications_failed_total": 0,
  "notifications_by_channel": {
    "email": 1,
    "sms": 0
  }
}
```

## Servico externo mockado

A chamada externa esta isolada em `app/services/notification_sender.py`.
O provedor padrao (`SafeMockNotificationSender`) nao envia email ou SMS real; ele existe
para demonstrar a integracao sem efeitos externos. Nos testes, essa dependencia e
substituida por mocks via `app.dependency_overrides`.

Em caso de `ExternalProviderError`, o endpoint `POST /notifications`:

- retorna HTTP `503`;
- nao persiste a notificacao;
- incrementa `notifications_failed_total`;
- registra log estruturado sem expor o conteudo da mensagem.

## Testes

Comandos locais:

```powershell
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m unit --no-cov
.\.venv\Scripts\python.exe -m pytest -m integration --no-cov
.\.venv\Scripts\python.exe -m pytest -m e2e --no-cov
```

Categorias:

- `unit`: validacao de schemas e contratos basicos dos endpoints.
- `integration`: TestClient + SQLite em memoria + sender mockado.
- `e2e`: fluxo critico completo, de requisicao ate persistencia e metricas.

Cenarios cobertos:

- criacao valida por e-mail e SMS;
- rejeicao de e-mail invalido, canal invalido, assunto vazio e mensagem vazia;
- persistencia e listagem em banco isolado por teste;
- falha do provedor externo com HTTP `503` e sem persistencia;
- `/health` com metadados e timestamp UTC;
- `/metrics` com contadores de sucesso, canal e falha;
- logs JSON com request ID e dados sensiveis mascarados.

## Observabilidade

Cada requisicao recebe um `request_id`. Se o header `X-Request-ID` vier na entrada,
ele e reutilizado; caso contrario, a API gera um UUID. O valor tambem volta no header
`X-Request-ID` da resposta.

Os logs usam o modulo `logging` padrao com formato JSON e campos:

- `timestamp`;
- `level`;
- `action`;
- `request_id`;
- `notification_id`, quando houver;
- `channel`;
- `recipient_email` mascarado;
- `error`, quando houver falha externa.

O conteudo de `message` nao e registrado em log.

## Quality Gates

O CI falha se qualquer criterio abaixo nao for atendido:

- `ruff check app tests` sem erros;
- testes unitarios passando;
- testes de integracao passando;
- testes E2E passando;
- suite completa com cobertura minima de `70%`.

O gate de cobertura esta configurado em `pytest.ini`:

```ini
--cov-fail-under=70
```

## Mutacao

O projeto inclui `mutmut==3.6.0` e configuracao em `pyproject.toml`.

No Windows nativo, o `mutmut` 3 deve ser executado via WSL/Linux porque depende de
suporte a `fork`. A mutacao nesta entrega e manual/informativa e nao bloqueia o CI.

Comandos em WSL/Linux:

```bash
python -m mutmut run
python -m mutmut browse
```

O relatorio curto esta em `docs/relatorio_mutacao.md`.

## CI/CD

O GitHub Actions executa, em etapas separadas:

1. checkout;
2. configuracao do Python 3.12;
3. instalacao de dependencias;
4. lint com Ruff;
5. testes unitarios;
6. testes de integracao;
7. testes E2E;
8. suite completa com cobertura e gate minimo;
9. publicacao de `coverage.xml` como artefato.

## Alunos

- Emyr Reis - [@Emyrreis](https://github.com/Emyrreis)
- Jose Avello - [@JoseAvello00](https://github.com/JoseAvello00)
