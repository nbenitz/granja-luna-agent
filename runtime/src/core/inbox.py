from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any


InboxEntry = dict[str, Any]

DEFAULT_STATUS = "pending_review"
STATUSES = {"pending_review", "needs_edit", "ready_to_apply", "cancelled", "archived"}


def build_inbox_entry(
    dry_run: dict[str, Any],
    created_at: str | None = None,
    status: str = DEFAULT_STATUS,
) -> InboxEntry:
    if status not in STATUSES:
        raise ValueError(f"Invalid inbox status: {status}")
    created_at = created_at or datetime.now().astimezone().isoformat(timespec="seconds")
    classification = dry_run["classification"]
    text = dry_run["input"]["text"]
    return {
        "schema_version": 1,
        "id": build_entry_id(created_at, text),
        "created_at": created_at,
        "updated_at": created_at,
        "status": status,
        "information_status": "pending_review",
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
        "missing_data": dry_run.get("missing_data", []),
        "next_actions": dry_run.get("next_actions", []),
        "review": {
            "decision": None,
            "notes": None,
            "reviewed_at": None,
        },
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
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return entries


def find_inbox_entry(entries: list[InboxEntry], entry_id: str) -> InboxEntry:
    for entry in entries:
        if entry.get("id") == entry_id:
            return entry
    raise KeyError(f"Inbox entry not found: {entry_id}")


def summarize_inbox(entries: list[InboxEntry]) -> dict[str, Any]:
    status_counts = Counter(entry.get("status", "unknown") for entry in entries)
    risk_counts = Counter(entry.get("classification", {}).get("risk_level", "unknown") for entry in entries)
    domain_counts = Counter(entry.get("classification", {}).get("primary_domain", "unknown") for entry in entries)
    confirmation_count = sum(1 for entry in entries if entry.get("classification", {}).get("requires_confirmation"))
    return {
        "total": len(entries),
        "by_status": dict(status_counts),
        "by_risk": dict(risk_counts),
        "by_primary_domain": dict(domain_counts),
        "requires_confirmation": confirmation_count,
    }


def update_inbox_entry_status(
    entries: list[InboxEntry],
    entry_id: str,
    status: str,
    reviewed_at: str | None = None,
    notes: str | None = None,
) -> InboxEntry:
    if status not in STATUSES:
        raise ValueError(f"Invalid inbox status: {status}")
    reviewed_at = reviewed_at or datetime.now().astimezone().isoformat(timespec="seconds")
    entry = find_inbox_entry(entries, entry_id)
    entry["status"] = status
    entry["updated_at"] = reviewed_at
    entry["review"] = {
        "decision": status,
        "notes": notes,
        "reviewed_at": reviewed_at,
    }
    return entry


def filter_inbox_entries(entries: list[InboxEntry], status: str | None = None) -> list[InboxEntry]:
    if status is None:
        return entries
    if status not in STATUSES:
        raise ValueError(f"Invalid inbox status: {status}")
    return [entry for entry in entries if entry.get("status") == status]


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
                    entry.get("status", "-"),
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
        f"Estado: {entry.get('status')} ({entry.get('information_status')})",
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
    lines.extend(["", "Nota: entrada pendiente. No se aplicaron cambios operativos. side_effects: []"])
    return "\n".join(lines)


def truncate(text: str, max_length: int = 110) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def yes_no(value: bool) -> str:
    return "si" if value else "no"
