# evn/cli/cli_logger.py
from datetime import datetime, timezone
import threading


class CliLogger:
    """
    Centralized logger for CliBase classes.
    Supports structured event logging and path resolution.
    """
    _logs = {}
    _lock = threading.Lock()

    @classmethod
    def log(cls, target, message: str, *, event: str = None, data: dict = None):
        path = cls._resolve_path(target)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
            "event": event or "log",
            "message": message,
            "data": data or {},
        }
        with cls._lock:
            cls._logs.setdefault(path, []).append(entry)

    @classmethod
    def get_log(cls, target) -> list[dict]:
        path = cls._resolve_path(target)
        return cls._logs.get(path, [])

    @classmethod
    def clear(cls, target):
        path = cls._resolve_path(target)
        with cls._lock:
            cls._logs[path] = []

    @classmethod
    def _resolve_path(cls, target):
        # if it's an instance with get_full_path, use that
        if hasattr(target, "get_full_path") and not isinstance(target, type):
            return target.get_full_path()
        # if it's a class, use its __name__
        if hasattr(target, "__name__"):
            return target.__name__
        return str(target)

    @classmethod
    def print_log(cls, target):
        for entry in cls.get_log(target):
            print(entry)

    @classmethod
    def log_event_context(cls, target, event: str, data: dict = None):
        """Context manager for logging entry/exit of an event."""
        class _LogCtx:
            def __enter__(self_):
                cls.log(target, f"begin {event}", event=event, data=data)
                return self_
            def __exit__(self_, *exc):
                cls.log(target, f"end {event}", event=event, data=data)
        return _LogCtx()


# Usage:
# CliLogger.log(self, "message", event="something_happened", data={...})
# CliLogger.get_log(MyCLIClass)
