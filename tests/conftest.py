import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.metrics import reset_metrics  # noqa: E402
from app.services.notification_sender import get_notification_sender  # noqa: E402

TEST_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)


class MockNotificationSender:
    def __init__(self, sent_notifications: list[dict]):
        self.sent_notifications = sent_notifications

    def send(self, payload):
        self.sent_notifications.append(
            {
                "recipient_email": str(payload.recipient_email),
                "channel": payload.channel,
                "subject": payload.subject,
                "message": payload.message,
            },
        )


@pytest.fixture()
def sent_notifications():
    return []


@pytest.fixture()
def db_session():
    Base.metadata.create_all(bind=engine_test)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine_test)


@pytest.fixture()
def client(db_session, sent_notifications):
    reset_metrics()

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_notification_sender():
        return MockNotificationSender(sent_notifications)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_notification_sender] = override_notification_sender
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    reset_metrics()
