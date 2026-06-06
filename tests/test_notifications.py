import pytest
from pydantic import ValidationError
from app.schemas import NotificationCreate
 
class TestNotificationCreate: 
    @pytest.mark.unit
    def test_criar_notificacao_email_valida(self):
        """Deve criar uma notificação válida pelo canal email"""
        notification = NotificationCreate(
            recipient_email = "usuario@exemplo.com",
            channel = "email",
            subject = "Bem-vindo",
            message = "Sua conta foi criada com sucesso",
        )
        assert notification.recipient_email == "usuario@exemplo.com"
        assert notification.channel == "email"
        assert notification.subject == "Bem-vindo"
 
    @pytest.mark.unit
    def test_criar_notificacao_sms_valida(self):
        """Deve criar uma notificação válida pelo canal sms"""
        notification = NotificationCreate(
            recipient_email = "outro@exemplo.com",
            channel = "sms",
            subject = "Código de verificação",
            message = "Seu código é 123456",
        )
        assert notification.channel == "sms"
 
    @pytest.mark.unit
    def test_subject_com_espacos_nas_bordas_e_aceito(self):
        """Envios com espaços nas bordas devem ser aceitos"""
        notification = NotificationCreate(
            recipient_email = "a@b.com",
            channel = "email",
            subject = "  Assunto com espaço  ",
            message = "Mensagem válida",
        )
        assert "Assunto" in notification.subject
  
    @pytest.mark.unit
    def test_email_invalido_levanta_validation_error(self):
        """Email fora do formato deve levantar erro"""
        with pytest.raises(ValidationError) as exc_info:
            NotificationCreate(
                recipient_email = "isso-nao-e-email",
                channel = "email",
                subject = "Assunto",
                message = "Mensagem",
            )
        erros = exc_info.value.errors()
        campos = [e["loc"][0] for e in erros]
        assert "recipient_email" in campos
 
    @pytest.mark.unit
    def test_canal_invalido_levanta_validation_error(self):
        """Canal fora de email e sms deve levantar erro"""
        with pytest.raises(ValidationError) as exc_info:
            NotificationCreate(
                recipient_email = "usuario@exemplo.com",
                channel = "whatsapp",
                subject = "Assunto",
                message = "Mensagem",
            )
        erros = exc_info.value.errors()
        campos = [e["loc"][0] for e in erros]
        assert "channel" in campos
 
    @pytest.mark.unit
    def test_subject_vazio_levanta_validation_error(self):
        """Envio vazio deve ser rejeitado pelo validator"""
        with pytest.raises(ValidationError) as exc_info:
            NotificationCreate(
                recipient_email = "usuario@exemplo.com",
                channel = "email",
                subject = "   ",
                message = "Mensagem válida",
            )
        erros = exc_info.value.errors()
        mensagens = [e["msg"] for e in erros]
        assert any("assunto" in m.lower() for m in mensagens)
 
    @pytest.mark.unit
    def test_message_vazia_levanta_validation_error(self):
        """Messagem vazia deve ser rejeitada pelo validator"""
        with pytest.raises(ValidationError) as exc_info:
            NotificationCreate(
                recipient_email = "usuario@exemplo.com",
                channel = "email",
                subject = "Assunto válido",
                message = "",
            )
        erros = exc_info.value.errors()
        mensagens = [e["msg"] for e in erros]
        assert any("mensagem" in m.lower() for m in mensagens)
 
    @pytest.mark.unit
    def test_campos_obrigatorios_ausentes_levantam_validation_error(self):
        """Criar notificação sem nenhum campo deve levantar erro"""
        with pytest.raises(ValidationError) as exc_info:
            NotificationCreate()
        erros = exc_info.value.errors()
        #4 erros: um por cada campo ausente
        assert len(erros) == 4
 
from fastapi.testclient import TestClient
from app.main import app
 
client = TestClient(app)
 
class TestEndpoints: 
    @pytest.mark.unit
    def test_health_check_retorna_ok(self):
        """O endpoint health deve retornar status 200 ok"""
        response = client.get("/health")
 
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
  
    @pytest.mark.unit
    def test_criar_notificacao_retorna_201(self):
        """Post notifications com dados válidos deve retornar 201 created"""
        payload = {
            "recipient_email": "teste@exemplo.com",
            "channel": "email",
            "subject": "Reserva confirmada",
            "message": "Sua reserva foi confirmada com sucesso",
        }
 
        response = client.post("/notifications", json = payload)
 
        assert response.status_code == 201
 
    @pytest.mark.unit
    def test_criar_notificacao_retorna_campos_corretos(self):
        """A resposta do post deve conter todos os campos esperados"""
        payload = {
            "recipient_email": "campos@exemplo.com",
            "channel": "sms",
            "subject": "Código",
            "message": "Seu código é 999.",
        }
 
        response = client.post("/notifications", json = payload)
        body = response.json()
 
        assert "id" in body
        assert body["recipient_email"] == "campos@exemplo.com"
        assert body["channel"] == "sms"
        assert body["status"] == "pending"
        assert "created_at" in body
 
    @pytest.mark.unit
    def test_criar_notificacao_com_email_invalido_retorna_422(self):
        """Post com email inválido deve retornar 422"""
        payload = {
            "recipient_email": "nao-e-email",
            "channel": "email",
            "subject": "Assunto",
            "message": "Mensagem",
        }
 
        response = client.post("/notifications", json = payload)
 
        assert response.status_code == 422
 
    @pytest.mark.unit
    def test_criar_notificacao_com_canal_invalido_retorna_422(self):
        """Post fora dos canais previstos deve retornar 422"""
        payload = {
            "recipient_email": "valido@exemplo.com",
            "channel": "telegram",
            "subject": "Assunto",
            "message": "Mensagem",
        }
 
        response = client.post("/notifications", json = payload)
 
        assert response.status_code == 422
  
    @pytest.mark.unit
    def test_listar_notificacoes_retorna_lista(self):
        """Get notifications deve retornar uma lista"""
        response = client.get("/notifications")
 
        assert response.status_code == 200
        assert isinstance(response.json(), list)
  
    @pytest.mark.unit
    def test_buscar_notificacao_por_id_existente(self):
        """Get notification de id, deve retornar 20"""
        payload = {
            "recipient_email": "busca@exemplo.com",
            "channel": "email",
            "subject": "Busca por ID",
            "message": "Testando busca",
        }
        criada = client.post("/notifications", json = payload).json()
        notification_id = criada["id"]
 
        response = client.get(f"/notifications/{notification_id}")
 
        assert response.status_code == 200
        assert response.json()["id"] == notification_id
 
    @pytest.mark.unit
    def test_buscar_notificacao_por_id_inexistente_retorna_404(self):
        """Id inexsistente deve retornar 404 Not Found."""
        response = client.get("/notifications/99999")
 
        assert response.status_code == 404
        assert response.json()["detail"] == "Notificação não encontrada"