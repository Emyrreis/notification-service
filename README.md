Notification Service
Projeto acadêmico desenvolvido para a disciplina de Teste e Qualidade de Software.
API REST construída com FastAPI que recebe eventos e registra notificações por e-mail ou SMS, demonstrando na prática os conceitos de testes automatizados, CI/CD e qualidade de software.

Tecnologias
TecnologiaVersãoFunçãoPython3.12Linguagem principalFastAPI0.115.6Framework da API RESTPydantic2.10.4Validação de dados e schemasUvicorn0.34.0Servidor ASGIPytest8.3.4Framework de testespytest-cov6.0.0Medição de cobertura de códigohttpx0.28.1Cliente HTTP para testes de endpointGitHub Actions—Pipeline de CI/CD

Como executar
Pré-requisitos
Python 3.12
pip

Instalação
#Clone o repositório
git clone https://github.com/Emyrreis/notification-service.git
cd notification-service

#Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  #Para Linux/macOS
.venv\Scripts\activate     #Para Windows

# Instale as dependências
pip install -r requirements.txt
Rodando a API
bashuvicorn app.main:app --reload
A API estará disponível em http://localhost:8000
Documentação interativa automática (Swagger): http://localhost:8000/docs

Endpoints
MétodoRotaDescriçãoStatus de sucessoGET/healthVerifica se a API está no ar200 OKPOST/notificationsCria uma nova notificação201 CreatedGET/notificationsLista todas as notificações200 OKGET/notifications/{id}Busca uma notificação por ID200 OK

Validações aplicadas

recipient_email — deve ser um endereço de e-mail válido (EmailStr)
channel — aceita somente "email" ou "sms" (Literal)
subject — não pode ser vazio ou conter apenas espaços
message — não pode ser vazia ou conter apenas espaços

Dados inválidos retornam 422 automaticamente.

Testes
Rodando os testes
bashpytest
O comando executa todos os testes, mede a cobertura do pacote app/ e exibe quais linhas não foram cobertas.

Rodando por categoria
bashpytest -m unit      #Testes unitários
pytest -m integration   #Testes de integração

Resultado esperado
16 passed — cobertura total: 100%

Quality Gate
O pytest.ini define um critério mínimo de cobertura de 70%. Se a cobertura cair abaixo desse valor, o pytest retorna erro e o CI falha automaticamente, bloqueando o commit.
ini--cov-fail-under=70

CI/CD — Pipeline GitHub Actions
A cada git push para main ou develop, o GitHub Actions executa automaticamente:
Cria uma máquina Ubuntu limpa (sem configurações locais)
Instala Python 3.12
Instala as dependências do requirements.txt com versões fixadas
Roda pytest com verificação de cobertura
Publica o coverage.xml como artefato da execução

Alunos:
Emyr Reis — @Emyrreis
José Avello — @JoseAvello00
