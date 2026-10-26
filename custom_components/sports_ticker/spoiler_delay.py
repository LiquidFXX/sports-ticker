"""Hold immutable ESPN scoreboard snapshots until their configured release time.

This module has no Home Assistant dependencies so buffer semantics can be tested
independently of entity lifecycle and scheduling.
"""

from __future__ import annotations

from collections import deque
from copy import deepcopy
from datetime import datetime, timedelta
from typing import Any


class DelayedScoreboardBuffer:
    """FIFO snapshot buffer; never expose a newer snapshot before its due time."""

    def __init__(self, delay_seconds: int) -> None:
        if delay_seconds <= 0:
            raise ValueError("Spoiler delay must be positive")
        self.delay_seconds = delay_seconds
        self._delay = timedelta(seconds=delay_seconds)
        self._pending: deque[tuple[datetime, dict[str, Any]]] = deque()

    def enqueue(self, snapshot: dict[str, Any], observed_at: datetime) -> None:
        """Copy data immediately so later live mutations cannot leak through."""
        self._pending.append((observed_at + self._delay, deepcopy(snapshot)))

    @property
    def next_due(self) -> datetime | None:
        """Return the next due time, or None if nothing is queued."""
        return self._pending[0][0] if self._pending else None

    def take_ready(self, now: datetime) -> dict[str, Any] | None:
        """Return the most recent due snapshot without releasing future data."""
        latest = None
        while self._pending and self._pending[0][0] <= now:
            _, latest = self._pending.popleft()
        return latest
