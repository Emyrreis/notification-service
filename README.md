# Notification Service

Projeto acadêmico desenvolvido para a disciplina de **Teste e Qualidade de Software**.

API REST construída com FastAPI que recebe eventos e registra notificações por e-mail ou SMS, demonstrando na prática os conceitos de testes automatizados, CI/CD e qualidade de software.

---

## Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| Python | 3.12 | Linguagem principal |
| FastAPI | 0.115.6 | Framework da API REST |
| Pydantic | 2.10.4 | Validação de dados e schemas |
| Uvicorn | 0.34.0 | Servidor ASGI |
| Pytest | 8.3.4 | Framework de testes |
| pytest-cov | 6.0.0 | Medição de cobertura de código |
| httpx | 0.28.1 | Cliente HTTP para testes de endpoint |
| GitHub Actions | — | Pipeline de CI/CD |

---


## Como executar

### Pré-requisitos

- Python 3.12
- pip

### Instalação

```
# Clone o repositório
git clone https://github.com/Emyrreis/notification-service.git
cd notification-service

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Instale as dependências
pip install -r requirements.txt
```

### Rodando a API

```
uvicorn app.main:app --reload
```

A API estará disponível em `http://localhost:8000`.

Documentação interativa automática (Swagger): `http://localhost:8000/docs`

---

## Endpoints

| Método | Rota | Descrição | Status de sucesso |
|---|---|---|---|
| `GET` | `/health` | Verifica se a API está no ar | `200 OK` |
| `POST` | `/notifications` | Cria uma nova notificação | `201 Created` |
| `GET` | `/notifications` | Lista todas as notificações | `200 OK` |
| `GET` | `/notifications/{id}` | Busca uma notificação por ID | `200 OK` |

### Validações aplicadas

- `recipient_email` — deve ser um endereço de e-mail válido (`EmailStr`)
- `channel` — aceita somente `"email"` ou `"sms"` (`Literal`)
- `subject` — não pode ser vazio ou conter apenas espaços
- `message` — não pode ser vazia ou conter apenas espaços

Dados inválidos retornam `422` automaticamente.

---

## Testes

### Rodando os testes

```
pytest
```

O comando executa todos os testes, mede a cobertura do pacote `app/` e exibe quais linhas não foram cobertas.

### Rodando por categoria

```
pytest -m unit          # somente testes unitários
pytest -m integration   # somente testes de integração
```
### Estratégia de testes

O projeto utiliza duas categorias de teste:

**Testes unitários (`TestNotificationCreate`)** — testam o schema Pydantic de forma completamente isolada, sem servidor, sem banco de dados e sem requisições HTTP. Verificam as regras de validação diretamente no modelo:

- criação de notificação com dados válidos (e-mail e SMS)
- rejeição de e-mail inválido
- rejeição de canal não permitido
- rejeição de subject vazio
- rejeição de message vazia
- rejeição quando campos obrigatórios estão ausentes

**Testes de endpoint (`TestEndpoints`)** — testam as rotas HTTP usando o `TestClient` do FastAPI, que simula requisições em memória sem subir servidor real. Cobrem todos os endpoints e seus cenários de sucesso e falha:

- `GET /health` retorna `200`
- `POST /notifications` com dados válidos retorna `201` com todos os campos
- `POST /notifications` com dados inválidos retorna `422`
- `GET /notifications` retorna lista
- `GET /notifications/{id}` retorna a notificação correta
- `GET /notifications/99999` retorna `404`

---

## Quality Gate

O `pytest.ini` define um critério mínimo de cobertura de **70%**. Se a cobertura cair abaixo desse valor, o `pytest` retorna erro e o CI falha automaticamente, bloqueando o commit.

```
--cov-fail-under=70
```

---

## CI/CD — Pipeline GitHub Actions

A cada `git push` para `main` ou `develop`, o GitHub Actions executa automaticamente:

1. Cria uma máquina Ubuntu limpa (sem configurações locais)
2. Instala Python 3.12
3. Instala as dependências do `requirements.txt` com versões fixadas
4. Roda `pytest` com verificação de cobertura
5. Publica o `coverage.xml` como artefato da execução
---

## Alunos

- Emyr Reis — [@Emyrreis](https://github.com/Emyrreis)
- José Avello — [@JoseAvello00](https://github.com/JoseAvello00)
