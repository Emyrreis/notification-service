from fastapi import FastAPI, HTTPException
from app.schemas import NotificationCreate, NotificationResponse
from datetime import datetime

app = FastAPI(
    title = "Notification Service",
    description = "API para envio de notificações por e-mail e SMS",
    version = "1.0.0",
)

_notifications: list[dict] = []
_next_id: int = 1

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/notifications", response_model=NotificationResponse, status_code=201)
def create_notification(payload: NotificationCreate):
    global _next_id
    notification = {
        "id": _next_id,
        "recipient_email": payload.recipient_email,
        "channel": payload.channel,
        "subject": payload.subject,
        "message": payload.message,
        "status": "pending",
        "created_at": datetime.now(),
    }
    _notifications.append(notification)
    _next_id += 1
    return notification


@app.get("/notifications", response_model=list[NotificationResponse])
def list_notifications():
    return _notifications


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int):
    for n in _notifications:
        if n["id"] == notification_id:
            return n
    raise HTTPException(status_code=404, detail="Notificação não encontrada")