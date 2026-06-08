from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from app.schemas import NotificationCreate, NotificationResponse
from app.database import engine, get_db
from app import models

models.Base.metadata.create_all(bind = engine)

app = FastAPI(
    title = "Notification Service",
    description = "API para envio de notificações por e-mail e SMS",
    version = "1.0.0",
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/notifications", response_model = NotificationResponse, status_code = 201)
def create_notification(payload: NotificationCreate, db: Session = Depends(get_db)):
    notification = models.Notification(
        recipient_email = payload.recipient_email,
        channel = payload.channel,
        subject = payload.subject,
        message = payload.message,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification

@app.get("/notifications", response_model = list[NotificationResponse])
def list_notifications(db: Session = Depends(get_db)):
    return db.query(models.Notification).all()

@app.get("/notifications/{notification_id}", response_model = NotificationResponse)
def get_notification(notification_id: int, db: Session = Depends(get_db)):
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id
    ).first()
    if not notification:
        raise HTTPException(status_code = 404, detail = "Notificação não encontrada")
    return notification