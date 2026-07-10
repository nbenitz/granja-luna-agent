from __future__ import annotations

import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


UsageEvent = dict[str, Any]


def build_usage_event(
    event_type: str,
    related_entry_id: str | None = None,
    details: dict[str, Any] | None = None,
    occurred_at: str | None = None,
    source: str = "web",
) -> UsageEvent:
    return {
        "schema_version": 1,
        "id": f"event-{uuid4().hex[:12]}",
        "occurred_at": occurred_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_type": event_type,
        "source": source,
        "related_entry_id": related_entry_id,
        "details": details or {},
    }


def append_usage_event(path: Path, event: UsageEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def load_usage_events(path: Path) -> list[UsageEvent]:
    if not path.exists():
        return []
    events: list[UsageEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return events


def summarize_usage(events: list[UsageEvent]) -> dict[str, Any]:
    by_type = Counter(event.get("event_type", "unknown") for event in events)
    return {
        "total": len(events),
        "by_type": dict(by_type),
        "last_event_at": events[-1].get("occurred_at") if events else None,
    }

