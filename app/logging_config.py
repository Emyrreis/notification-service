import json
import logging
from datetime import datetime, timezone

LOGGER_NAME = "notification_service"


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "action": getattr(record, "action", record.getMessage()),
        }

        for field in ("request_id", "notification_id", "channel", "recipient_email", "error"):
            value = getattr(record, field, None)
            if value is not None:
                payload[field] = value

        return json.dumps(payload)


def configure_logging() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    has_json_handler = any(
        getattr(handler, "notification_json_handler", False) for handler in logger.handlers
    )
    if not has_json_handler:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        handler.notification_json_handler = True
        logger.addHandler(handler)

    logger.propagate = True
    return logger


logger = configure_logging()


def mask_email(email: str) -> str:
    local_part, separator, domain = email.partition("@")
    if not separator:
        return "***"

    first_letter = local_part[:1] or "*"
    return f"{first_letter}***@{domain}"


def log_event(level: int, action: str, request_id: str | None = None, **fields: object) -> None:
    logger.log(
        level,
        action,
        extra={
            "action": action,
            "request_id": request_id,
            **fields,
        },
    )
