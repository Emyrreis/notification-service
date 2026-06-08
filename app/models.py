from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key = True, index = True)
    recipient_email = Column(String, nullable = False)
    channel = Column(String, nullable = False)
    subject = Column(String, nullable = False)
    message = Column(String, nullable = False)
    status = Column(String, default = "pending", nullable = False)
    created_at = Column(DateTime, default = datetime.now, nullable = False)