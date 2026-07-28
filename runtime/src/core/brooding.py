from __future__ import annotations

import secrets
from copy import deepcopy
from datetime import date
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

BROODING_RECORD_TYPES = {"area", "batch", "event"}
BROODING_EVENT_TYPES = {"mortality", "transfer_out", "observation", "closure"}


def create_brooding_draft(
    path: Path,
    record_type: str,
    payload: dict[str, Any],
    *,
    incubation_records: list[dict[str, Any]],
    source: str,
    actor: str,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if record_type not in BROODING_RECORD_TYPES:
        raise OperationValidationError(
            "invalid_data",
            "record_type",
            f"Tipo de registro de cría no soportado: {record_type}.",
        )
    records = load_brooding_records(path)
    data = _normalize_record(record_type, payload, records, incubation_records)
    if record_type == "area":
        _ensure_unique_area_name(records, data["name"])
    timestamp = now_iso()
    record_id = f"brood-{record_type}-{uuid4()}"
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
            "summary": _confirmation_summary(record_type, data, records),
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
            "cancelled": None,
            "registered": None,
        },
        "type": record_type,
        "status": "awaiting_confirmation",
    }
    return record, _build_event("brooding_record_drafted", record, source, actor)


def confirm_brooding_record(
    path: Path,
    record_id: str,
    confirmation_code: str,
    *,
    incubation_records: list[dict[str, Any]],
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    records = load_brooding_records(path)
    try:
        record = deepcopy(find_brooding_record(records, record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "record_id", "El registro de cría no existe."
        ) from exc
    _require_confirmation(record, confirmation_code, explicit_confirmation)
    if record.get("status") == "applied":
        record["idempotent_replay"] = True
        return record, None
    if record.get("status") != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status", "record_id", "El registro de cría no está pendiente."
        )
    _validate_dependencies_for_confirmation(record, records, incubation_records)
    if record["record_type"] == "area":
        _ensure_unique_area_name(records, record["data"]["name"], exclude_id=record_id)
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
        "store": "granja_luna_brooding_events",
        "operation_status": "applied",
    }
    return record, _build_event("brooding_record_applied", record, source, actor, event_id=event_id)


def cancel_brooding_draft(
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
    records = load_brooding_records(path)
    try:
        record = deepcopy(find_brooding_record(records, record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "record_id", "El registro de cría no existe."
        ) from exc
    _require_confirmation(record, confirmation_code, explicit_confirmation)
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
        "brooding_record_cancelled", record, source, actor, event_id=event_id
    )


def append_brooding_event(path: Path, event: dict[str, Any]) -> None:
    append_event(path, event)


def load_brooding_records(path: Path) -> list[dict[str, Any]]:
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


def list_brooding_records(
    path: Path,
    *,
    record_type: str | None = None,
    status: str = "applied",
    limit: int = 100,
) -> list[dict[str, Any]]:
    records = load_brooding_records(path)
    if record_type is not None:
        records = [record for record in records if record.get("record_type") == record_type]
    records = [record for record in records if record.get("status") == status]
    records.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return records[:limit]


def brooding_batch_detail(path: Path, batch_id: str) -> dict[str, Any]:
    records = load_brooding_records(path)
    try:
        batch = find_brooding_record(records, batch_id)
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "batch_id", "El lote de cría no existe."
        ) from exc
    if batch.get("record_type") != "batch" or batch.get("status") != "applied":
        raise OperationValidationError(
            "not_found", "batch_id", "El lote de cría confirmado no existe."
        )
    events = _applied_batch_events(records, batch_id)
    summary = _brooding_summary(batch, events)
    return {**deepcopy(batch), "events": deepcopy(events), "summary": summary}


def find_brooding_record(records: list[dict[str, Any]], record_id: str) -> dict[str, Any]:
    for record in records:
        if record.get("id") == record_id:
            return record
    raise KeyError(f"Brooding record not found: {record_id}")


def _normalize_record(
    record_type: str,
    payload: dict[str, Any],
    records: list[dict[str, Any]],
    incubation_records: list[dict[str, Any]],
) -> dict[str, Any]:
    if record_type == "area":
        return {
            "name": _required_text(payload, "name", "¿Cómo se llama la zona de cría?"),
            "capacity": _optional_positive_integer(payload.get("capacity"), "capacity"),
            "notes": clean_text(payload.get("notes")),
        }
    if record_type == "batch":
        area_id = _required_text(payload, "area_id", "¿En qué zona estarán los pollitos?")
        _validate_reference(records, area_id, "area", allow_pending=True)
        age_min_days = _optional_nonnegative_integer(payload.get("age_min_days"), "age_min_days")
        age_max_days = _optional_nonnegative_integer(payload.get("age_max_days"), "age_max_days")
        if (age_min_days is None) != (age_max_days is None):
            raise OperationValidationError(
                "missing_required_data",
                "age_max_days",
                "Para registrar un rango de edad se necesitan el mínimo y el máximo.",
            )
        if age_min_days is not None and age_max_days is not None and age_min_days > age_max_days:
            raise OperationValidationError(
                "invalid_data", "age_max_days", "La edad máxima no puede ser menor a la mínima."
            )
        source_batch_id = clean_text(payload.get("source_incubation_batch_id"))
        if source_batch_id is not None:
            _validate_incubation_source(source_batch_id, incubation_records)
        return {
            "area_id": area_id,
            "start_date": _required_date(payload, "start_date", "¿Cuándo ingresaron a cría?"),
            "chicks_received": _required_positive_integer(
                payload.get("chicks_received"), "chicks_received"
            ),
            "source_incubation_batch_id": source_batch_id,
            "source_description": _required_text(
                payload, "source_description", "¿Cuál es el origen de los pollitos?"
            ),
            "age_min_days": age_min_days,
            "age_max_days": age_max_days,
            "notes": clean_text(payload.get("notes")),
        }
    batch_id = _required_text(payload, "batch_id", "¿A qué lote de cría corresponde?")
    batch = _validate_reference(records, batch_id, "batch", allow_pending=True)
    event_date = _required_date(payload, "event_date", "¿Cuál fue la fecha del evento?")
    if event_date < batch["data"]["start_date"]:
        raise OperationValidationError(
            "invalid_data", "event_date", "El evento no puede ser anterior al ingreso a cría."
        )
    event_type = _required_choice(payload, "event_type", BROODING_EVENT_TYPES)
    quantity = _optional_positive_integer(payload.get("quantity"), "quantity")
    final_count = _optional_nonnegative_integer(payload.get("final_count"), "final_count")
    if event_type in {"mortality", "transfer_out"} and quantity is None:
        raise OperationValidationError(
            "missing_required_data", "quantity", "¿Cuántos pollitos corresponden al evento?"
        )
    if event_type not in {"mortality", "transfer_out"} and quantity is not None:
        raise OperationValidationError(
            "invalid_data", "quantity", "Este tipo de evento no admite una cantidad."
        )
    if event_type == "transfer_out" and clean_text(payload.get("destination")) is None:
        raise OperationValidationError(
            "missing_required_data", "destination", "¿A dónde se trasladaron los pollitos?"
        )
    if event_type == "closure" and final_count is None:
        raise OperationValidationError(
            "missing_required_data", "final_count", "¿Cuántos pollitos quedan al cerrar el lote?"
        )
    if event_type != "closure" and final_count is not None:
        raise OperationValidationError(
            "invalid_data", "final_count", "El conteo final solo corresponde al cierre."
        )
    return {
        "batch_id": batch_id,
        "event_date": event_date,
        "event_type": event_type,
        "quantity": quantity,
        "final_count": final_count,
        "destination": clean_text(payload.get("destination")),
        "reason": clean_text(payload.get("reason")),
        "notes": clean_text(payload.get("notes")),
    }


def _validate_dependencies_for_confirmation(
    record: dict[str, Any],
    records: list[dict[str, Any]],
    incubation_records: list[dict[str, Any]],
) -> None:
    if record["record_type"] == "batch":
        area = _validate_reference(records, record["data"]["area_id"], "area", allow_pending=False)
        source_batch_id = record["data"].get("source_incubation_batch_id")
        if source_batch_id is not None:
            hatched_alive = _validate_incubation_source(source_batch_id, incubation_records)
            allocated = sum(
                int(item["data"]["chicks_received"])
                for item in records
                if item.get("record_type") == "batch"
                and item.get("status") == "applied"
                and item.get("data", {}).get("source_incubation_batch_id") == source_batch_id
            )
            if allocated + record["data"]["chicks_received"] > hatched_alive:
                raise OperationValidationError(
                    "source_quantity_exceeded",
                    "chicks_received",
                    "Los lotes de cría superarían los nacidos vivos del lote de incubación.",
                )
        capacity = area["data"].get("capacity")
        if capacity is not None:
            occupied = sum(
                _brooding_summary(item, _applied_batch_events(records, item["id"]))["current_count"]
                for item in records
                if item.get("record_type") == "batch"
                and item.get("status") == "applied"
                and item.get("data", {}).get("area_id") == area["id"]
                and not _brooding_summary(item, _applied_batch_events(records, item["id"]))[
                    "closed"
                ]
            )
            if occupied + record["data"]["chicks_received"] > capacity:
                raise OperationValidationError(
                    "capacity_exceeded",
                    "chicks_received",
                    "Los lotes abiertos superarían la capacidad de la zona de cría.",
                )
    if record["record_type"] == "event":
        batch = _validate_reference(
            records, record["data"]["batch_id"], "batch", allow_pending=False
        )
        events = _applied_batch_events(records, batch["id"])
        summary = _brooding_summary(batch, events)
        if summary["closed"]:
            raise OperationValidationError(
                "conflict", "batch_id", "El lote de cría ya está cerrado."
            )
        quantity = int(record["data"].get("quantity") or 0)
        if quantity > summary["current_count"]:
            raise OperationValidationError(
                "invalid_data", "quantity", "La cantidad supera los pollitos actuales del lote."
            )
        if record["data"]["event_type"] == "closure":
            if record["data"]["final_count"] != summary["current_count"]:
                raise OperationValidationError(
                    "result_mismatch",
                    "final_count",
                    "El conteo final debe coincidir con los pollitos actuales del lote.",
                )


def _validate_incubation_source(batch_id: str, incubation_records: list[dict[str, Any]]) -> int:
    batch = next(
        (
            item
            for item in incubation_records
            if item.get("id") == batch_id
            and item.get("record_type") == "batch"
            and item.get("status") == "applied"
        ),
        None,
    )
    if batch is None:
        raise OperationValidationError(
            "invalid_dependency",
            "source_incubation_batch_id",
            "El lote de incubación de origen debe estar confirmado.",
        )
    closure = next(
        (
            item
            for item in incubation_records
            if item.get("record_type") == "event"
            and item.get("status") == "applied"
            and item.get("data", {}).get("batch_id") == batch_id
            and item.get("data", {}).get("event_type") == "closure"
        ),
        None,
    )
    if closure is None:
        raise OperationValidationError(
            "invalid_dependency",
            "source_incubation_batch_id",
            "El lote de incubación debe estar cerrado antes de trasladar sus pollitos a cría.",
        )
    return int(closure["data"]["hatched_alive"])


def _applied_batch_events(records: list[dict[str, Any]], batch_id: str) -> list[dict[str, Any]]:
    events = [
        item
        for item in records
        if item.get("record_type") == "event"
        and item.get("status") == "applied"
        and item.get("data", {}).get("batch_id") == batch_id
    ]
    events.sort(key=lambda item: (item["data"]["event_date"], item["created_at"]))
    return events


def _brooding_summary(batch: dict[str, Any], events: list[dict[str, Any]]) -> dict[str, Any]:
    mortality = sum(
        int(item["data"].get("quantity") or 0)
        for item in events
        if item["data"]["event_type"] == "mortality"
    )
    transferred = sum(
        int(item["data"].get("quantity") or 0)
        for item in events
        if item["data"]["event_type"] == "transfer_out"
    )
    closure = next((item for item in events if item["data"]["event_type"] == "closure"), None)
    current = int(batch["data"]["chicks_received"]) - mortality - transferred
    return {
        "chicks_received": batch["data"]["chicks_received"],
        "mortality": mortality,
        "transferred_out": transferred,
        "current_count": current,
        "closed": closure is not None,
        "final_count": closure["data"]["final_count"] if closure is not None else None,
    }


def _validate_reference(
    records: list[dict[str, Any]],
    record_id: str,
    record_type: str,
    *,
    allow_pending: bool,
) -> dict[str, Any]:
    try:
        record = find_brooding_record(records, record_id)
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", f"{record_type}_id", f"El registro {record_type} no existe."
        ) from exc
    allowed = {"applied", "awaiting_confirmation"} if allow_pending else {"applied"}
    if record.get("record_type") != record_type or record.get("status") not in allowed:
        raise OperationValidationError(
            "invalid_dependency",
            f"{record_type}_id",
            f"El registro {record_type} debe estar confirmado antes de continuar.",
        )
    return record


def _require_confirmation(
    record: dict[str, Any], confirmation_code: str, explicit_confirmation: bool
) -> None:
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente esta operación de cría?",
        )
    expected = str(record.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador de cría.",
        )


def _required_text(payload: dict[str, Any], field: str, question: str) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        raise OperationValidationError("missing_required_data", field, question)
    return value


def _required_date(payload: dict[str, Any], field: str, question: str) -> str:
    value = _required_text(payload, field, question)
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise OperationValidationError(
            "invalid_data", field, "La fecha debe usar el formato YYYY-MM-DD."
        ) from exc


def _required_positive_integer(value: Any, field: str) -> int:
    number = _parse_integer(value, field)
    if number <= 0:
        raise OperationValidationError(
            "invalid_data", field, "La cantidad debe ser un entero mayor que cero."
        )
    return number


def _optional_positive_integer(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    return _required_positive_integer(value, field)


def _optional_nonnegative_integer(value: Any, field: str) -> int | None:
    if value is None or value == "":
        return None
    number = _parse_integer(value, field)
    if number < 0:
        raise OperationValidationError(
            "invalid_data", field, "La cantidad debe ser un entero mayor o igual a cero."
        )
    return number


def _parse_integer(value: Any, field: str) -> int:
    if isinstance(value, bool) or value is None or value == "":
        raise OperationValidationError("missing_required_data", field, "Falta una cantidad entera.")
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise OperationValidationError(
            "invalid_data", field, "La cantidad debe ser un número entero."
        ) from exc
    if str(number) != str(value).strip():
        raise OperationValidationError(
            "invalid_data", field, "La cantidad debe ser un número entero."
        )
    return number


def _required_choice(payload: dict[str, Any], field: str, choices: set[str]) -> str:
    value = _required_text(payload, field, "¿Qué tipo de evento ocurrió?")
    if value not in choices:
        raise OperationValidationError(
            "invalid_data", field, f"Usa uno de: {', '.join(sorted(choices))}."
        )
    return value


def _ensure_unique_area_name(
    records: list[dict[str, Any]], name: str, *, exclude_id: str | None = None
) -> None:
    if any(
        item.get("id") != exclude_id
        and item.get("record_type") == "area"
        and item.get("status") == "applied"
        and str(item.get("data", {}).get("name", "")).casefold() == name.casefold()
        for item in records
    ):
        raise OperationValidationError(
            "conflict", "name", "Ya existe una zona de cría confirmada con ese nombre."
        )


def _confirmation_summary(
    record_type: str, data: dict[str, Any], records: list[dict[str, Any]]
) -> str:
    if record_type == "area":
        capacity = f" con capacidad para {data['capacity']} pollitos" if data["capacity"] else ""
        return f"Registrar la zona de cría {data['name']}{capacity}."
    if record_type == "batch":
        area = find_brooding_record(records, data["area_id"])
        return (
            f"Ingresar {data['chicks_received']} pollitos a {area['data']['name']} "
            f"con fecha {data['start_date']}."
        )
    return (
        f"Registrar evento {data['event_type']} del lote {data['batch_id']} "
        f"con fecha {data['event_date']}."
    )


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
