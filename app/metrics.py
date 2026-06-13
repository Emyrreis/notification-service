from threading import Lock

_lock = Lock()
_metrics = {
    "notifications_created_total": 0,
    "notifications_failed_total": 0,
    "notifications_by_channel": {
        "email": 0,
        "sms": 0,
    },
}


def increment_notification_created(channel: str) -> None:
    with _lock:
        _metrics["notifications_created_total"] += 1
        _metrics["notifications_by_channel"][channel] += 1


def increment_notification_failed() -> None:
    with _lock:
        _metrics["notifications_failed_total"] += 1


def get_metrics() -> dict:
    with _lock:
        return {
            "notifications_created_total": _metrics["notifications_created_total"],
            "notifications_failed_total": _metrics["notifications_failed_total"],
            "notifications_by_channel": dict(_metrics["notifications_by_channel"]),
        }


def reset_metrics() -> None:
    with _lock:
        _metrics["notifications_created_total"] = 0
        _metrics["notifications_failed_total"] = 0
        _metrics["notifications_by_channel"] = {
            "email": 0,
            "sms": 0,
        }
