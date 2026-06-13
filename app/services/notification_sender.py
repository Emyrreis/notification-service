from typing import Protocol

from app.schemas import NotificationCreate


class ExternalProviderError(Exception):
    """Raised when the external notification provider cannot accept the send."""


class NotificationSender(Protocol):
    def send(self, payload: NotificationCreate) -> None:
        pass


class SafeMockNotificationSender:
    """Default provider used by the app; it never sends real email or SMS."""

    provider_name = "safe-mock-provider"

    def send(self, payload: NotificationCreate) -> None:
        return None


def get_notification_sender() -> NotificationSender:
    return SafeMockNotificationSender()
