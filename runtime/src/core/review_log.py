from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


ReviewEvent = dict[str, Any]


def build_review_event(
    event_type: str,
    entry_id: str,
    *,
    before: Any = None,
    after: Any = None,
    section: str | None = None,
    reason: str | None = None,
    note: str | None = None,
    review_status_before: str | None = None,
    review_status_after: str | None = None,
    occurred_at: str | None = None,
) -> ReviewEvent:
    return {
        "schema_version": 1,
        "id": f"review-{uuid4().hex[:12]}",
        "occurred_at": occurred_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_type": event_type,
        "entry_id": entry_id,
        "actor": "local_user",
        "section": section,
        "reason": reason,
        "note": note,
        "review_status_before": review_status_before,
        "review_status_after": review_status_after,
        "changes": build_changes(before, after),
        "runtime": {
            "extractor": "rules_v1",
            "intent_schema": "purchase.v2" if section and section.startswith("purchase_") else None,
        },
    }


def build_curation_event(
    source_event: ReviewEvent,
    *,
    primary_reason: str,
    labels: list[str],
    training_eligibility: str,
    explanation: str,
    note_usage: str,
    supersedes_curation_event_id: str | None = None,
    occurred_at: str | None = None,
) -> ReviewEvent:
    event = {
        "schema_version": 1,
        "id": f"curation-{uuid4().hex[:12]}",
        "occurred_at": occurred_at or datetime.now().astimezone().isoformat(timespec="seconds"),
        "event_type": "feedback_curation_revised" if supersedes_curation_event_id else "feedback_curated",
        "entry_id": source_event["entry_id"],
        "actor": "codex_assisted_curator",
        "source_review_event_id": source_event["id"],
        "curation": {
            "original_reason": source_event.get("reason"),
            "primary_reason": primary_reason,
            "labels": labels,
            "training_eligibility": training_eligibility,
            "explanation": explanation,
            "note_usage": note_usage,
        },
    }
    if supersedes_curation_event_id:
        event["supersedes_curation_event_id"] = supersedes_curation_event_id
    return event


def build_changes(before: Any, after: Any, path: str = "") -> list[dict[str, Any]]:
    if isinstance(before, dict) and isinstance(after, dict):
        changes: list[dict[str, Any]] = []
        for key in sorted(set(before) | set(after)):
            child_path = f"{path}.{key}" if path else key
            changes.extend(build_changes(before.get(key), after.get(key), child_path))
        return changes
    if isinstance(before, list) and isinstance(after, list):
        changes = []
        for index in range(max(len(before), len(after))):
            child_path = f"{path}.{index}" if path else str(index)
            old_value = before[index] if index < len(before) else None
            new_value = after[index] if index < len(after) else None
            changes.extend(build_changes(old_value, new_value, child_path))
        return changes
    if before == after:
        return []
    if before is None and after is not None:
        change_type = "added"
    elif before is not None and after is None:
        change_type = "removed"
    else:
        change_type = "changed"
    return [{"path": path, "before": before, "after": after, "change_type": change_type}]


def append_review_event(path: Path, event: ReviewEvent) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")


def load_review_events(path: Path) -> list[ReviewEvent]:
    if not path.exists():
        return []
    events: list[ReviewEvent] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return events
