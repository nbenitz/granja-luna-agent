from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

from core.intent_forms import build_structured_data


InboxEntry = dict[str, Any]

DEFAULT_STATUS = "pending"
REVIEW_STATUSES = {"pending", "validated", "needs_information", "needs_correction", "rejected"}
OPERATION_STATUSES = {"draft", "awaiting_confirmation", "applied", "cancelled"}
STATUSES = REVIEW_STATUSES
LEGACY_STATUS_MAP = {
    "pending_review": "pending",
    "needs_edit": "needs_correction",
    "ready_to_apply": "validated",
    "cancelled": "rejected",
    "archived": "rejected",
}


def build_inbox_entry(
    dry_run: dict[str, Any],
    created_at: str | None = None,
    status: str = DEFAULT_STATUS,
) -> InboxEntry:
    status = LEGACY_STATUS_MAP.get(status, status)
    if status not in REVIEW_STATUSES:
        raise ValueError(f"Invalid inbox status: {status}")
    created_at = created_at or datetime.now().astimezone().isoformat(timespec="seconds")
    classification = dry_run["classification"]
    text = dry_run["input"]["text"]
    return {
        "schema_version": 2,
        "id": build_entry_id(created_at, text),
        "created_at": created_at,
        "updated_at": created_at,
        "review_status": status,
        "operation_status": "draft",
        "source": dry_run["input"].get("source", "cli"),
        "message": text,
        "context": dry_run["input"].get("context"),
        "classification": {
            "intent": classification["intent"],
            "primary_domain": classification["primary_domain"],
            "secondary_domains": classification.get("secondary_domains", []),
            "risk_level": classification["risk_level"],
            "requires_confirmation": classification["requires_confirmation"],
            "confidence": classification.get("confidence"),
        },
        "classification_provenance": {
            "intent": "predicted",
            "primary_domain": "predicted",
            "risk_level": "predicted",
        },
        "missing_data": dry_run.get("missing_data", []),
        "next_actions": dry_run.get("next_actions", []),
        "review": {
            "outcome": None,
            "reason": None,
            "note": None,
            "reviewed_at": None,
            "correction_count": 0,
            "last_correction_at": None,
        },
        "structured_data": build_structured_data(dry_run),
        "side_effects": [],
        "dry_run": dry_run,
    }


def build_entry_id(created_at: str, text: str) -> str:
    digest = hashlib.sha256(f"{created_at}\n{text}".encode("utf-8")).hexdigest()[:10]
    timestamp_source = strip_timezone(created_at)
    timestamp = re.sub(r"[^0-9T]", "", timestamp_source.replace(":", ""))
    return f"inbox-{timestamp}-{digest}"


def strip_timezone(timestamp: str) -> str:
    if "T" not in timestamp:
        return timestamp
    date_part, time_part = timestamp.split("T", maxsplit=1)
    time_part = time_part.split("+", maxsplit=1)[0]
    if "-" in time_part:
        time_part = time_part.rsplit("-", maxsplit=1)[0]
    return f"{date_part}T{time_part}"


def append_inbox_entry(path: Path, entry: InboxEntry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def write_inbox_entries(path: Path, entries: list[InboxEntry]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        for entry in entries:
            file.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")
    temp_path.replace(path)


def load_inbox_entries(path: Path) -> list[InboxEntry]:
    if not path.exists():
        return []
    entries: list[InboxEntry] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(normalize_inbox_entry(json.loads(line)))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return entries


def normalize_inbox_entry(entry: InboxEntry) -> InboxEntry:
    legacy_status = entry.pop("status", None)
    review_status = entry.get("review_status") or LEGACY_STATUS_MAP.get(legacy_status, "pending")
    if review_status not in REVIEW_STATUSES:
        review_status = "pending"
    entry["schema_version"] = 2
    entry["review_status"] = review_status
    entry["operation_status"] = entry.get("operation_status", "draft")
    entry["classification_provenance"] = entry.get("classification_provenance") or {
        "intent": "predicted",
        "primary_domain": "predicted",
        "risk_level": "predicted",
    }
    entry.pop("information_status", None)
    old_review = entry.get("review") or {}
    entry["review"] = {
        "outcome": old_review.get("outcome"),
        "reason": old_review.get("reason"),
        "note": old_review.get("note", old_review.get("notes")),
        "reviewed_at": old_review.get("reviewed_at"),
        "correction_count": old_review.get("correction_count", 0),
        "last_correction_at": old_review.get("last_correction_at"),
    }
    return entry


def find_inbox_entry(entries: list[InboxEntry], entry_id: str) -> InboxEntry:
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    raise KeyError(f"Inbox entry not found: {entry_id}")


def summarize_inbox(entries: list[InboxEntry]) -> dict[str, Any]:
    status_counts = Counter(entry.get("review_status", "unknown") for entry in entries)
    operation_counts = Counter(entry.get("operation_status", "unknown") for entry in entries)
    risk_counts = Counter(entry.get("classification", {}).get("risk_level", "unknown") for entry in entries)
    domain_counts = Counter(entry.get("classification", {}).get("primary_domain", "unknown") for entry in entries)
    confirmation_count = sum(1 for entry in entries if entry.get("classification", {}).get("requires_confirmation"))
    return {
        "total": len(entries),
        "by_review_status": dict(status_counts),
        "by_operation_status": dict(operation_counts),
        "by_status": dict(status_counts),
        "by_risk": dict(risk_counts),
        "by_primary_domain": dict(domain_counts),
        "requires_confirmation": confirmation_count,
    }


def update_inbox_entry_review(
    entries: list[InboxEntry],
    entry_id: str,
    review_status: str,
    outcome: str,
    reason: str | None = None,
    reviewed_at: str | None = None,
    note: str | None = None,
) -> InboxEntry:
    if review_status not in REVIEW_STATUSES:
        raise ValueError(f"Invalid inbox review status: {review_status}")
    reviewed_at = reviewed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    entry = find_inbox_entry(entries, entry_id)
    entry["review_status"] = review_status
    entry["updated_at"] = reviewed_at
    review = entry.get("review", {})
    review.update({"outcome": outcome, "reason": reason, "note": note, "reviewed_at": reviewed_at})
    entry["review"] = review
    return entry


def record_inbox_correction(entry: InboxEntry, corrected_at: str | None = None) -> InboxEntry:
    corrected_at = corrected_at or datetime.now().astimezone().isoformat(timespec="seconds")
    review = entry.get("review", {})
    review["correction_count"] = int(review.get("correction_count", 0)) + 1
    review["last_correction_at"] = corrected_at
    review["outcome"] = None
    review["reviewed_at"] = None
    entry["review"] = review
    entry["review_status"] = "pending"
    entry["updated_at"] = corrected_at
    return entry


def update_inbox_entry_status(
    entries: list[InboxEntry],
    entry_id: str,
    status: str,
    reviewed_at: str | None = None,
    notes: str | None = None,
) -> InboxEntry:
    mapped = LEGACY_STATUS_MAP.get(status, status)
    outcome = "accepted" if mapped == "validated" else "deferred"
    if mapped == "rejected":
        outcome = "rejected"
    return update_inbox_entry_review(entries, entry_id, mapped, outcome, reviewed_at=reviewed_at, note=notes)


def filter_inbox_entries(entries: list[InboxEntry], status: str | None = None) -> list[InboxEntry]:
    if status is None:
        return entries
    status = LEGACY_STATUS_MAP.get(status, status)
    if status not in REVIEW_STATUSES:
        raise ValueError(f"Invalid inbox status: {status}")
    return [entry for entry in entries if entry.get("review_status") == status]


def format_inbox_table(entries: list[InboxEntry]) -> str:
    if not entries:
        return "No hay entradas en el inbox con esos filtros."
    lines = ["ID | estado | riesgo | dominio | intencion | resumen", "---|---|---|---|---|---"]
    for entry in entries:
        classification = entry.get("classification", {})
        lines.append(
            " | ".join(
                [
                    entry.get("id", "-"),
                    entry.get("review_status", "-"),
                    classification.get("risk_level", "-"),
                    classification.get("primary_domain", "-"),
                    classification.get("intent", "-"),
                    truncate(entry.get("message", ""), 90),
                ]
            )
        )
    return "\n".join(lines)


def format_inbox_detail(entry: InboxEntry) -> str:
    classification = entry.get("classification", {})
    lines = [
        "Granja Luna inbox",
        "",
        f"ID: {entry.get('id')}",
        f"Revision: {entry.get('review_status')}",
        f"Operacion: {entry.get('operation_status')}",
        f"Creado: {entry.get('created_at')}",
        f"Intencion: {classification.get('intent')}",
        f"Dominio principal: {classification.get('primary_domain')}",
    ]
    secondary_domains = classification.get("secondary_domains", [])
    if secondary_domains:
        lines.append(f"Dominios secundarios: {', '.join(secondary_domains)}")
    lines.append(
        "Riesgo: "
        f"{classification.get('risk_level')} | "
        f"Confirmacion requerida: {yes_no(bool(classification.get('requires_confirmation')))} | "
        f"Confianza: {classification.get('confidence', 'n/a')}"
    )
    lines.extend(["", "Mensaje:", f"- {entry.get('message', '')}"])
    context = entry.get("context")
    if context:
        lines.extend(["", "Contexto auxiliar:", f"- {context.get('text')}"])
    missing_data = entry.get("missing_data", [])
    if missing_data:
        lines.append("")
        lines.append("Datos faltantes:")
        lines.extend(f"- {item}" for item in missing_data)
    next_actions = entry.get("next_actions", [])
    if next_actions:
        lines.append("")
        lines.append("Proximas acciones:")
        lines.extend(f"- {item}" for item in next_actions)
    lines.extend(["", "Nota: la revision no aplico cambios operativos. side_effects: []"])
    return "\n".join(lines)


def truncate(text: str, max_length: int = 110) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def yes_no(value: bool) -> str:
    return "si" if value else "no"
