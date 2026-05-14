from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Deque, Dict, List, Optional


class EventsFeed:
    def __init__(self, maxlen: int = 200):
        self._events: Deque[Dict[str, Any]] = deque(maxlen=maxlen)
        self._lock = Lock()

    def add(self, event_type: str, summary: str, payload: Optional[Dict[str, Any]] = None) -> None:
        e: Dict[str, Any] = {
            "ts": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "type": event_type,
            "summary": summary,
        }
        if payload is not None:
            e["payload"] = payload

        with self._lock:
            self._events.append(e)

    def list(self, limit: int = 10) -> List[Dict[str, Any]]:
        limit = max(1, min(200, int(limit)))
        with self._lock:
            data = list(self._events)
        return data[-limit:]
