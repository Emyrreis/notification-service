import pytest

class TestIntegracaoNotifications:
    @pytest.mark.integration
    def test_criar_notificacao_persiste_no_banco(self, client):
        payload = {
            "recipient_email": "persistencia@exemplo.com",
            "channel": "email",
            "subject": "Teste de persistência",
            "message": "Este dado deve estar no banco",
        }

        client.post("/notifications", json = payload)
        response = client.get("/notifications")

        assert response.status_code == 200
        notificacoes = response.json()
        assert len(notificacoes) == 1
        assert notificacoes[0]["recipient_email"] == "persistencia@exemplo.com"

    @pytest.mark.integration
    def test_criar_multiplas_notificacoes_e_listar(self, client):
        payloads = [
            {
                "recipient_email": f"usuario{i}@exemplo.com",
                "channel": "email",
                "subject": f"Notificação {i}",
                "message": f"Mensagem {i}",
            }
            for i in range(3)
        ]

        for payload in payloads:
            client.post("/notifications", json = payload)

        response = client.get("/notifications")
        assert len(response.json()) == 3

    @pytest.mark.integration
    def test_buscar_notificacao_por_id_retorna_dados_corretos(self, client):
        payload = {
            "recipient_email": "busca@exemplo.com",
            "channel": "sms",
            "subject": "Busca por ID",
            "message": "Mensagem de busca",
        }

        criada = client.post("/notifications", json = payload).json()
        response = client.get(f"/notifications/{criada['id']}")
        body = response.json()

        assert response.status_code == 200
        assert body["id"] == criada["id"]
        assert body["recipient_email"] == "busca@exemplo.com"
        assert body["channel"] == "sms"
        assert body["status"] == "pending"

    @pytest.mark.integration
    def test_notificacao_criada_tem_status_pending(self, client):
        payload = {
            "recipient_email": "status@exemplo.com",
            "channel": "email",
            "subject": "Verificar status",
            "message": "Status deve ser pending",
        }

        response = client.post("/notifications", json = payload)
        assert response.json()["status"] == "pending"

    @pytest.mark.integration
    def test_banco_isolado_entre_testes(self, client):
        response = client.get("/notifications")
        assert response.json() == []

    @pytest.mark.integration
    def test_buscar_id_inexistente_retorna_404(self, client):
        response = client.get("/notifications/99999")

        assert response.status_code == 404
        assert response.json()["detail"] == "Notificação não encontrada"

    @pytest.mark.integration
    def test_criar_com_email_invalido_nao_persiste(self, client):
        payload = {
            "recipient_email": "isso-nao-e-email",
            "channel": "email",
            "subject": "Assunto",
            "message": "Mensagem",
        }

        response = client.post("/notifications", json = payload)
        assert response.status_code == 422

        listagem = client.get("/notifications")
        assert listagem.json() == []

    @pytest.mark.integration
    def test_criar_com_canal_invalido_nao_persiste(self, client):
        payload = {
            "recipient_email": "valido@exemplo.com",
            "channel": "telegram",
            "subject": "Assunto",
            "message": "Mensagem",
        }

        response = client.post("/notifications", json = payload)
        assert response.status_code == 422

        listagem = client.get("/notifications")
        assert listagem.json() == []