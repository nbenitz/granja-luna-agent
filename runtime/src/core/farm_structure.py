from __future__ import annotations

import secrets
from copy import deepcopy
from pathlib import Path
from typing import Any
from uuid import uuid4

from core.operations import (
    OperationValidationError,
    append_event,
    clean_text,
    load_events,
    now_iso,
)

STRUCTURE_TYPES = {"barn", "flock", "egg_storage_area"}
EGG_STORAGE_PURPOSES = {"incubation_candidate", "commercial", "classification", "mixed"}
EGG_CLASSIFICATION_MODES = {
    "mixed_batch_with_observations",
    "separated_at_collection",
    "automatic_classification",
}


def create_structure_draft(
    path: Path,
    record_type: str,
    payload: dict[str, Any],
    *,
    source: str,
    actor: str,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if record_type not in STRUCTURE_TYPES:
        raise OperationValidationError(
            "invalid_data",
            "record_type",
            f"Tipo de registro no soportado: {record_type}.",
        )
    records = load_structure_records(path)
    data = _normalize_record(record_type, payload, records)
    _ensure_unique_name(records, record_type, data["name"])
    timestamp = now_iso()
    record_id = f"{record_type}-{uuid4()}"
    record = {
        "schema_version": 1,
        "id": record_id,
        "record_type": record_type,
        "operation_status": "awaiting_confirmation",
        "record_status": "draft",
        "created_at": timestamp,
        "updated_at": timestamp,
        "data": data,
        "confirmation": {
            "required": True,
            "code": secrets.token_hex(4),
            "summary": _confirmation_summary(record_type, data),
            "confirmed_at": None,
        },
        "trace": {
            "requested": {
                "at": timestamp,
                "source": clean_text(source) or "unknown",
                "actor": clean_text(actor) or "unknown",
                "request_id": clean_text(request_id),
                "payload": deepcopy(payload),
            },
            "interpreted": {
                "at": timestamp,
                "method": "deterministic_structured_input_v1",
                "payload": deepcopy(data),
            },
            "confirmed": None,
            "registered": None,
        },
        "type": record_type,
        "status": "awaiting_confirmation",
    }
    return record, _build_event("structure_record_drafted", record, source, actor)


def confirm_structure_record(
    path: Path,
    record_id: str,
    confirmation_code: str,
    *,
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        record = deepcopy(find_structure_record(load_structure_records(path), record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found",
            "record_id",
            "El registro de estructura no existe.",
        ) from exc
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente el resumen exacto de este registro?",
        )
    expected_code = str(record.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected_code, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador. Revisa el registro antes de confirmar.",
        )
    if record.get("status") == "applied":
        record["idempotent_replay"] = True
        return record, None
    if record.get("status") != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status",
            "record_id",
            "El registro no está pendiente de confirmación.",
        )
    if record["record_type"] == "flock":
        _validate_barn_reference(record["data"].get("barn_id"), load_structure_records(path))
    _ensure_unique_name(
        load_structure_records(path),
        record["record_type"],
        record["data"]["name"],
        exclude_id=record_id,
    )
    timestamp = now_iso()
    event_id = f"evt-{uuid4()}"
    record["status"] = "applied"
    record["operation_status"] = "applied"
    record["record_status"] = "confirmed"
    record["updated_at"] = timestamp
    record["confirmation"]["confirmed_at"] = timestamp
    record["trace"]["confirmed"] = {
        "at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "request_id": clean_text(request_id),
        "explicit": True,
    }
    record["trace"]["registered"] = {
        "at": timestamp,
        "event_id": event_id,
        "store": "granja_luna_structure_events",
        "operation_status": "applied",
    }
    event = _build_event(
        "structure_record_applied",
        record,
        source,
        actor,
        event_id=event_id,
    )
    return record, event


def cancel_structure_draft(
    path: Path,
    record_id: str,
    confirmation_code: str,
    reason: str,
    *,
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        record = deepcopy(find_structure_record(load_structure_records(path), record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "record_id", "El registro de estructura no existe."
        ) from exc
    _validate_cancellation(record, confirmation_code, explicit_confirmation)
    if record.get("status") == "cancelled":
        record["idempotent_replay"] = True
        return record, None
    if record.get("status") != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status", "record_id", "Solo se puede cancelar un borrador pendiente."
        )
    cancellation_reason = clean_text(reason)
    if cancellation_reason is None:
        raise OperationValidationError(
            "missing_required_data", "reason", "¿Por qué se cancela este borrador?"
        )
    timestamp = now_iso()
    event_id = f"evt-{uuid4()}"
    record["status"] = "cancelled"
    record["operation_status"] = "cancelled"
    record["record_status"] = "cancelled"
    record["updated_at"] = timestamp
    record["trace"]["cancelled"] = {
        "at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "request_id": clean_text(request_id),
        "explicit": True,
        "reason": cancellation_reason,
    }
    return record, _build_event(
        "structure_record_cancelled", record, source, actor, event_id=event_id
    )


def _validate_cancellation(
    record: dict[str, Any], confirmation_code: str, explicit_confirmation: bool
) -> None:
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente la cancelación de este borrador?",
        )
    expected_code = str(record.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected_code, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador.",
        )


def append_structure_event(path: Path, event: dict[str, Any]) -> None:
    append_event(path, event)


def load_structure_records(path: Path) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for event in load_events(path):
        record_id = event.get("record_id")
        record = event.get("record")
        if not record_id or not isinstance(record, dict):
            continue
        if record_id not in latest:
            order.append(record_id)
        latest[record_id] = record
    return [latest[record_id] for record_id in order]


def list_structure_records(
    path: Path,
    *,
    record_type: str | None = None,
    status: str = "applied",
    limit: int = 100,
) -> list[dict[str, Any]]:
    records = load_structure_records(path)
    if record_type is not None:
        records = [record for record in records if record.get("record_type") == record_type]
    records = [record for record in records if record.get("status") == status]
    records.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return records[:limit]


def find_structure_record(
    records: list[dict[str, Any]],
    record_id: str,
) -> dict[str, Any]:
    for record in records:
        if record.get("id") == record_id:
            return record
    raise KeyError(f"Structure record not found: {record_id}")


def _normalize_record(
    record_type: str,
    payload: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    name = _required_text(payload, "name", "¿Cómo se llama este registro?")
    notes = clean_text(payload.get("notes"))
    if record_type == "barn":
        capacity = _optional_positive_integer(
            payload.get("capacity"),
            "capacity",
            "La capacidad",
        )
        return {"name": name, "capacity": capacity, "notes": notes}
    if record_type == "egg_storage_area":
        purpose = clean_text(payload.get("purpose"))
        if purpose not in EGG_STORAGE_PURPOSES:
            raise OperationValidationError(
                "invalid_data",
                "purpose",
                "El propósito debe ser incubation_candidate, commercial, classification o mixed.",
            )
        classification_mode = (
            clean_text(payload.get("classification_mode"))
            or "mixed_batch_with_observations"
        )
        if classification_mode not in EGG_CLASSIFICATION_MODES:
            raise OperationValidationError(
                "invalid_data",
                "classification_mode",
                "El modo de clasificación indicado no está soportado.",
            )
        return {
            "name": name,
            "purpose": purpose,
            "capacity_eggs": _optional_positive_integer(
                payload.get("capacity"),
                "capacity",
                "La capacidad en huevos",
            ),
            "classification_mode": classification_mode,
            "active": _optional_boolean(payload.get("active"), default=True),
            "notes": notes,
        }
    hen_breeds = _required_text_list(
        payload.get("hen_breeds"),
        "hen_breeds",
        "¿Qué raza o razas de gallinas componen el plantel?",
    )
    rooster_breeds = _optional_text_list(payload.get("rooster_breeds"), "rooster_breeds")
    barn_id = clean_text(payload.get("barn_id"))
    _validate_barn_reference(barn_id, records)
    return {
        "name": name,
        "purpose": clean_text(payload.get("purpose")),
        "bird_count": _optional_positive_integer(
            payload.get("bird_count"),
            "bird_count",
            "La cantidad de aves",
        ),
        "hen_breeds": hen_breeds,
        "rooster_breeds": rooster_breeds,
        "bird_groups": _optional_bird_groups(payload.get("bird_groups")),
        "egg_label": clean_text(payload.get("egg_label")),
        "barn_id": barn_id,
        "notes": notes,
    }


def _required_text(payload: dict[str, Any], field: str, question: str) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        raise OperationValidationError("missing_required_data", field, question)
    return value


def _required_text_list(value: Any, field: str, question: str) -> list[str]:
    items = _optional_text_list(value, field)
    if not items:
        raise OperationValidationError("missing_required_data", field, question)
    return items


def _optional_text_list(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise OperationValidationError(
            "invalid_data",
            field,
            f"{field} debe ser una lista de textos.",
        )
    result: list[str] = []
    seen: set[str] = set()
    for item in value:
        text = clean_text(item)
        if text is None:
            raise OperationValidationError(
                "invalid_data",
                field,
                f"{field} no puede contener valores vacíos.",
            )
        key = text.casefold()
        if key not in seen:
            result.append(text)
            seen.add(key)
    return result


def _optional_bird_groups(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise OperationValidationError(
            "invalid_data", "bird_groups", "Los grupos de aves deben ser una lista."
        )
    groups: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise OperationValidationError(
                "invalid_data", "bird_groups", f"El grupo {index + 1} debe ser un objeto."
            )
        breed = _required_text(
            item,
            "breed",
            f"¿Qué raza o cruce corresponde al grupo {index + 1}?",
        )
        sex = clean_text(item.get("sex")) or "unknown"
        if sex not in {"hen", "rooster", "mixed", "unknown"}:
            raise OperationValidationError(
                "invalid_data", "bird_groups", "El sexo debe ser hen, rooster, mixed o unknown."
            )
        groups.append(
            {
                "breed": breed,
                "sex": sex,
                "count": _optional_positive_integer(
                    item.get("count"),
                    "bird_groups.count",
                    "La cantidad del grupo",
                ),
                "notes": clean_text(item.get("notes")),
            }
        )
    return groups


def _optional_boolean(value: Any, *, default: bool) -> bool:
    if value is None or value == "":
        return default
    if not isinstance(value, bool):
        raise OperationValidationError(
            "invalid_data", "active", "El estado activo debe ser true o false."
        )
    return value


def _optional_positive_integer(value: Any, field: str, label: str) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        raise OperationValidationError(
            "invalid_data",
            field,
            f"{label} debe ser un número entero positivo.",
        )
    try:
        capacity = int(value)
    except (TypeError, ValueError) as exc:
        raise OperationValidationError(
            "invalid_data",
            field,
            f"{label} debe ser un número entero positivo.",
        ) from exc
    if capacity <= 0 or str(capacity) != str(value).strip():
        raise OperationValidationError(
            "invalid_data",
            field,
            f"{label} debe ser un número entero positivo.",
        )
    return capacity


def _validate_barn_reference(barn_id: str | None, records: list[dict[str, Any]]) -> None:
    if barn_id is None:
        return
    try:
        barn = find_structure_record(records, barn_id)
    except KeyError as exc:
        raise OperationValidationError(
            "not_found",
            "barn_id",
            "El galpón indicado no existe.",
        ) from exc
    if barn.get("record_type") != "barn" or barn.get("status") != "applied":
        raise OperationValidationError(
            "invalid_data",
            "barn_id",
            "El galpón debe estar confirmado antes de asignarle un plantel.",
        )


def _ensure_unique_name(
    records: list[dict[str, Any]],
    record_type: str,
    name: str,
    *,
    exclude_id: str | None = None,
) -> None:
    duplicate = next(
        (
            record
            for record in records
            if record.get("id") != exclude_id
            if record.get("record_type") == record_type
            and record.get("status") == "applied"
            and str(record.get("data", {}).get("name", "")).casefold() == name.casefold()
        ),
        None,
    )
    if duplicate is not None:
        label = {
            "barn": "galpón",
            "flock": "plantel",
            "egg_storage_area": "almacén de huevos",
        }.get(record_type, "registro")
        raise OperationValidationError(
            "conflict",
            "name",
            f"Ya existe un {label} confirmado con ese nombre.",
        )


def _confirmation_summary(record_type: str, data: dict[str, Any]) -> str:
    if record_type == "barn":
        capacity = data.get("capacity")
        suffix = f" con capacidad para {capacity} aves" if capacity is not None else ""
        return f"Registrar el galpón {data['name']}{suffix}."
    if record_type == "egg_storage_area":
        capacity = data.get("capacity_eggs")
        suffix = f" con capacidad para {capacity} huevos" if capacity is not None else ""
        return f"Registrar el almacén de huevos {data['name']}{suffix}."
    location = f" en {data['barn_id']}" if data.get("barn_id") else " sin galpón asignado"
    count = f" con {data['bird_count']} aves" if data.get("bird_count") is not None else ""
    return f"Registrar el plantel {data['name']}{count}{location}."


def _build_event(
    event_type: str,
    record: dict[str, Any],
    source: str,
    actor: str,
    *,
    event_id: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "event_id": event_id or f"evt-{uuid4()}",
        "record_id": record["id"],
        "event_type": event_type,
        "occurred_at": now_iso(),
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "record": deepcopy(record),
    }
