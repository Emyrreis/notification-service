import logging
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from sqlalchemy.orm import Session

from app import models
from app.database import engine, get_db
from app.logging_config import log_event, mask_email
from app.metrics import get_metrics, increment_notification_created, increment_notification_failed
from app.schemas import NotificationCreate, NotificationResponse
from app.services.notification_sender import (
    ExternalProviderError,
    NotificationSender,
    get_notification_sender,
)

SERVICE_NAME = "notification-service"
SERVICE_VERSION = "1.0.0"

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Notification Service",
    description="API para envio de notificacoes por e-mail e SMS",
    version=SERVICE_VERSION,
)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/metrics")
def metrics():
    return get_metrics()


@app.post("/notifications", response_model=NotificationResponse, status_code=201)
def create_notification(
    payload: NotificationCreate,
    request: Request,
    db: Session = Depends(get_db),
    sender: NotificationSender = Depends(get_notification_sender),
):
    request_id = getattr(request.state, "request_id", None)
    try:
        sender.send(payload)
    except ExternalProviderError as exc:
        db.rollback()
        increment_notification_failed()
        log_event(
            logging.ERROR,
            "notification_send_failed",
            request_id=request_id,
            channel=payload.channel,
            recipient_email=mask_email(str(payload.recipient_email)),
            error=str(exc),
        )
        raise HTTPException(
            status_code=503,
            detail="Servico externo de envio indisponivel",
        ) from exc

    notification = models.Notification(
        recipient_email=payload.recipient_email,
        channel=payload.channel,
        subject=payload.subject,
        message=payload.message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    increment_notification_created(payload.channel)
    log_event(
        logging.INFO,
        "notification_created",
        request_id=request_id,
        notification_id=notification.id,
        channel=payload.channel,
        recipient_email=mask_email(str(payload.recipient_email)),
    )
    return notification


@app.get("/notifications", response_model=list[NotificationResponse])
def list_notifications(db: Session = Depends(get_db)):
    return db.query(models.Notification).all()


@app.get("/notifications/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
    ).first()
    if not notification:
        raise HTTPException(status_code=404, detail="Notificacao nao encontrada")
    return notification