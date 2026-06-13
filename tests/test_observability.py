import json
import logging
from datetime import datetime

import pytest

from app.logging_config import LOGGER_NAME, logger


class TestObservability:
    @pytest.mark.integration
    def test_metrics_iniciam_zeradas(self, client):
        response = client.get("/metrics")

        assert response.status_code == 200
        assert response.json() == {
            "notifications_created_total": 0,
            "notifications_failed_total": 0,
            "notifications_by_channel": {
                "email": 0,
                "sms": 0,
            },
        }

    @pytest.mark.integration
    def test_metrics_incrementam_por_canal(self, client):
        client.post(
            "/notifications",
            json={
                "recipient_email": "email@exemplo.com",
                "channel": "email",
                "subject": "Email",
                "message": "Mensagem por email",
            },
        )
        client.post(
            "/notifications",
            json={
                "recipient_email": "sms@exemplo.com",
                "channel": "sms",
                "subject": "SMS",
                "message": "Mensagem por sms",
            },
        )

        metrics = client.get("/metrics").json()

        assert metrics["notifications_created_total"] == 2
        assert metrics["notifications_failed_total"] == 0
        assert metrics["notifications_by_channel"] == {
            "email": 1,
            "sms": 1,
        }

    @pytest.mark.integration
    def test_health_retorna_metadados_e_timestamp_utc(self, client):
        body = client.get("/health").json()

        assert body["status"] == "ok"
        assert body["service"] == "notification-service"
        assert body["version"] == "1.0.0"
        assert datetime.fromisoformat(body["timestamp_utc"])

    @pytest.mark.integration
    def test_log_de_criacao_e_json_e_nao_expoe_mensagem(self, client, caplog):
        caplog.set_level(logging.INFO, logger=LOGGER_NAME)
        payload = {
            "recipient_email": "logs@exemplo.com",
            "channel": "email",
            "subject": "Logs",
            "message": "conteudo sensivel da mensagem",
        }

        client.post(
            "/notifications",
            json=payload,
            headers={"X-Request-ID": "req-logs-001"},
        )

        record = next(
            item for item in caplog.records if getattr(item, "action", "") == "notification_created"
        )
        formatted = logger.handlers[0].formatter.format(record)
        parsed = json.loads(formatted)

        assert parsed["action"] == "notification_created"
        assert parsed["request_id"] == "req-logs-001"
        assert parsed["recipient_email"] == "l***@exemplo.com"
        assert "conteudo sensivel da mensagem" not in formatted
        assert "logs@exemplo.com" not in formatted
