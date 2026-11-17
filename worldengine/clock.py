"""In-game clock: fiction time, decoupled from wall time.

Every granularity the table needs — combat rounds (seconds), scenes (minutes),
an investigation day (hours), weeks between operations — is a timedelta away.
The clock stores a naive datetime plus a free-text label ("Day 3, afternoon")
because the label is what the fiction actually speaks in.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timedelta

_UNIT_SECONDS = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
_DURATION_RE = re.compile(r"(\d+)\s*([smhdw])")


class ClockError(ValueError):
    """Bad clock input."""


def parse_iso(text: str) -> datetime:
    """Parse an ISO-8601 timestamp or date into a naive datetime."""
    raw = text.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(raw)
    except ValueError as exc:
        raise ClockError(f"not an ISO timestamp: {text!r}") from exc
    if parsed.tzinfo is not None:
        parsed = parsed.replace(tzinfo=None)
    return parsed


def format_iso(moment: datetime) -> str:
    """Seconds precision; drop the seconds field when it is zero."""
    if moment.second or moment.microsecond:
        return moment.isoformat(timespec="seconds")
    return moment.isoformat(timespec="minutes")


def parse_duration(text: str) -> timedelta:
    """Parse '90s', '15m', '2h', '1d 4h', '3w' into a timedelta."""
    raw = text.strip().lower()
    if not raw:
        raise ClockError("empty duration")
    total = 0
    for amount, unit in _DURATION_RE.findall(raw):
        total += int(amount) * _UNIT_SECONDS[unit]
    leftover = _DURATION_RE.sub("", raw).strip(" ,+")
    if not total or leftover:
        raise ClockError(
            f"bad duration {text!r}; use e.g. 30s, 15m, 2h, 1d 4h, 3w"
        )
    return timedelta(seconds=total)


@dataclass
class Clock:
    at: datetime | None = None
    label: str = ""

    @property
    def started(self) -> bool:
        return self.at is not None

    def require(self) -> datetime:
        if self.at is None:
            raise ClockError(
                "the in-game clock has no date yet; set one with `clock set`"
            )
        return self.at

    def advance(self, delta: timedelta) -> datetime:
        self.at = self.require() + delta
        return self.at

    def describe(self) -> str:
        when = format_iso(self.at) if self.at else "unset"
        return f"{when} ({self.label})" if self.label else when
