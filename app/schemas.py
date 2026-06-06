from pydantic import BaseModel, EmailStr, field_validator
from typing import Literal
from datetime import datetime
 
 
class NotificationCreate(BaseModel):
    recipient_email: EmailStr
    channel: Literal["email", "sms"]
    subject: str
    message: str
 
    @field_validator("subject")
    @classmethod
    def subject_nao_pode_ser_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("O assunto não pode ser vazio ou só espaços")
        return v
 
    @field_validator("message")
    @classmethod
    def message_nao_pode_ser_vazio(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("A mensagem não pode ser vazia ou só espaços")
        return v
 
 
class NotificationResponse(BaseModel):
    id: int
    recipient_email: str
    channel: str
    subject: str
    message: str
    status: str
    created_at: datetime