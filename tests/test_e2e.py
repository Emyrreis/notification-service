import pytest


@pytest.mark.e2e
def test_fluxo_completo_cria_envia_persiste_e_expoe_metricas(client, sent_notifications):
    payload = {
        "recipient_email": "e2e@exemplo.com",
        "channel": "sms",
        "subject": "Fluxo completo",
        "message": "Mensagem do fluxo completo",
    }

    response = client.post(
        "/notifications",
        json=payload,
        headers={"X-Request-ID": "req-e2e-001"},
    )
    body = response.json()

    assert response.status_code == 201
    assert response.headers["X-Request-ID"] == "req-e2e-001"
    assert body["recipient_email"] == "e2e@exemplo.com"
    assert body["channel"] == "sms"
    assert body["status"] == "pending"
    assert sent_notifications == [payload]

    listagem = client.get("/notifications").json()
    assert len(listagem) == 1
    assert listagem[0]["id"] == body["id"]

    metrics = client.get("/metrics").json()
    assert metrics["notifications_created_total"] == 1
    assert metrics["notifications_failed_total"] == 0
    assert metrics["notifications_by_channel"] == {
        "email": 0,
        "sms": 1,
    }
