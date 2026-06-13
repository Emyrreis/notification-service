# Resumo da entrega - Aulas 2, 3 e 4

Este documento resume tudo que foi alterado e adicionado no projeto
`notification-service` para ajudar no estudo e na explicacao para o professor.

## 1. Objetivo da mudanca

O projeto ja tinha uma API FastAPI com validacao, persistencia SQLite e testes
basicos. A evolucao feita nesta entrega adiciona:

- testes de integracao com banco isolado;
- mock de um servico externo de envio de email/SMS;
- tratamento de falha do provedor externo;
- teste E2E do fluxo critico;
- configuracao e relatorio de teste de mutacao;
- observabilidade com health check, metricas e logs estruturados;
- quality gates no Pytest, Ruff e GitHub Actions.

Nada do contrato principal foi removido: o endpoint `POST /notifications`
continua criando notificacoes com HTTP `201` e status `pending` quando tudo da
certo.

## 2. Etapa A - Integracao e mocks

### O que foi implementado

Foi criada uma camada propria para representar o provedor externo de envio:

- `app/services/notification_sender.py`

Essa camada contem:

- `NotificationSender`: contrato do sender;
- `SafeMockNotificationSender`: implementacao padrao segura, que nao envia email
  nem SMS real;
- `ExternalProviderError`: excecao usada quando o provedor externo falha;
- `get_notification_sender`: dependencia usada pelo FastAPI.

Nos testes, essa dependencia e substituida via `app.dependency_overrides`. Assim,
nenhum teste dispara envio real e o mock pode ser reutilizado.

### Fluxo de sucesso

1. Cliente envia `POST /notifications`.
2. FastAPI valida o payload com Pydantic.
3. A API chama o sender mockado.
4. Se o sender nao falhar, a notificacao e salva no banco.
5. A API retorna HTTP `201` com os dados persistidos.
6. A metrica de sucesso e incrementada.
7. Um log estruturado de criacao e emitido.

### Fluxo de falha externa

1. Cliente envia `POST /notifications`.
2. FastAPI valida o payload.
3. O sender levanta `ExternalProviderError`.
4. A API executa rollback no banco.
5. A notificacao nao e persistida.
6. A API retorna HTTP `503`.
7. A metrica de falha e incrementada.
8. Um log estruturado de falha e emitido.

Esse comportamento evita registrar como aceita uma notificacao que nao foi
recebida pelo provedor externo.

## 3. Etapa B - E2E e mutacao

### Teste E2E

Foi criado:

- `tests/test_e2e.py`

O teste cobre o fluxo completo:

1. cria uma notificacao via API;
2. usa `X-Request-ID`;
3. confirma resposta HTTP `201`;
4. confirma que o sender mockado recebeu o payload;
5. confirma que a notificacao foi persistida;
6. confirma que `/metrics` refletiu a criacao.

### Mutacao

Foi adicionada a dependencia:

- `mutmut==3.6.0`

E a configuracao em:

- `pyproject.toml`

O relatorio curto esta em:

- `docs/relatorio_mutacao.md`

O cenario de mutacao documentado e a falha do provedor externo. A mutacao
simularia um bug em que a API ignora a falha ou persiste a notificacao mesmo sem
envio. O teste `test_falha_do_provedor_retorna_503_e_nao_persiste` mataria essa
mutacao porque exige HTTP `503`, banco vazio e contador de falha incrementado.

Observacao importante: o `mutmut` 3 nao roda em Windows nativo; ele pede WSL/Linux
por depender de `fork`. Por isso ele ficou configurado e documentado como etapa
manual, sem bloquear o CI.

## 4. Etapa C - Observabilidade e quality gates

### Health check

O endpoint `GET /health` foi enriquecido. Agora retorna:

```json
{
  "status": "ok",
  "service": "notification-service",
  "version": "1.0.0",
  "timestamp_utc": "2026-06-13T16:00:00+00:00"
}
```

Esse endpoint e leve e nao aciona envio externo.

### Metricas

Foi criado:

- `app/metrics.py`

E o endpoint:

- `GET /metrics`

Ele retorna contadores em memoria:

- total de notificacoes criadas;
- total de falhas;
- total por canal (`email` e `sms`).

Exemplo:

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

### Logs estruturados

Foi criado:

- `app/logging_config.py`

Os logs usam o modulo `logging` padrao e formato JSON. Campos principais:

- `timestamp`;
- `level`;
- `action`;
- `request_id`;
- `notification_id`, quando existir;
- `channel`;
- `recipient_email` mascarado;
- `error`, em caso de falha.

O conteudo da mensagem nao e logado para evitar vazamento de dado sensivel.

### Request ID

Foi adicionado middleware no FastAPI:

- se a requisicao vier com `X-Request-ID`, a API reutiliza esse valor;
- se nao vier, a API gera um UUID;
- a resposta sempre devolve o header `X-Request-ID`.

Isso ajuda a rastrear uma requisicao nos logs.

## 5. Arquivos modificados

### Aplicacao

- `app/main.py`: adiciona middleware de request ID, `/health`, `/metrics`,
  chamada ao sender, tratamento de `ExternalProviderError`, metricas e logs.
- `app/database.py`: passa a aceitar `DATABASE_URL` por variavel de ambiente,
  mantendo SQLite local como padrao.

### Configuracao

- `requirements.txt`: adiciona `ruff` e `mutmut`.
- `pytest.ini`: adiciona marcador `e2e` e mantem cobertura minima de 70%.
- `pyproject.toml`: configura Ruff e Mutmut.
- `.gitignore`: ignora `.ruff_cache/` e `mutants/`.
- `.github/workflows/ci.yml`: separa etapas de lint, testes por categoria,
  cobertura e upload do relatorio.

### Testes

- `tests/conftest.py`: cria banco SQLite em memoria, limpa metricas por teste e
  sobrescreve o sender com mock.
- `tests/test_notifications.py`: atualiza testes unitarios e de endpoints para
  usar a fixture isolada.
- `tests/test_integration.py`: cobre persistencia, isolamento, validacoes e falha
  do provedor externo.
- `tests/test_e2e.py`: adiciona fluxo completo.
- `tests/test_observability.py`: testa `/health`, `/metrics` e logs sem dados
  sensiveis.

### Documentacao

- `README.md`: documenta endpoints, sender mockado, testes, observabilidade,
  quality gates, CI e mutacao.
- `docs/relatorio_mutacao.md`: explica o cenario de mutacao escolhido.
- `docs/resumo_entrega_aulas_2_3_4.md`: este documento de estudo.

## 6. Dependencias adicionadas

- `ruff==0.15.17`: usado para lint de `app` e `tests`, garantindo padrao minimo
  de qualidade no CI.
- `mutmut==3.6.0`: usado para teste de mutacao manual/documentado, avaliando se
  os testes realmente detectam bugs introduzidos artificialmente.

## 7. Quality gates

O projeto agora tem os seguintes gates:

1. `ruff check app tests` sem erros.
2. Testes unitarios passando.
3. Testes de integracao passando.
4. Teste E2E passando.
5. Suite completa com cobertura minima de 70%.

Resultado validado localmente:

- `30 passed`;
- cobertura total: `95.35%`.

## 8. Comandos para validar localmente

No Windows:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check app tests
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m pytest -m unit --no-cov
.\.venv\Scripts\python.exe -m pytest -m integration --no-cov
.\.venv\Scripts\python.exe -m pytest -m e2e --no-cov
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Em WSL/Linux, para mutacao:

```bash
python -m mutmut run
python -m mutmut browse
```

## 9. Como explicar para o professor

Uma explicacao curta:

> Nesta entrega, evoluimos a API para cobrir integracao, E2E, observabilidade e
> quality gates. Primeiro isolamos o servico externo de envio em uma camada
> propria, permitindo mock limpo nos testes e evitando envio real. Depois
> implementamos um fluxo de falha: se o provedor externo falha, a API retorna
> 503, faz rollback e nao persiste a notificacao. Em seguida adicionamos um
> teste E2E que cobre o caminho completo da requisicao ate metricas. Por fim,
> adicionamos health check enriquecido, metricas em memoria, logs JSON com
> request ID e sem dados sensiveis, alem de lint, cobertura minima e pipeline
> separado no GitHub Actions.

Pontos que valem destacar:

- Banco de teste isolado com SQLite em memoria.
- Sender externo sempre mockado nos testes.
- Falha externa testada e tratada com rollback.
- Logs nao expõem `message` nem email completo.
- CI falha se lint, testes ou cobertura minima nao forem atendidos.
