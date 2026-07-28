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

INCUBATION_RECORD_TYPES = {"incubator", "batch", "event"}
INCUBATION_EVENT_TYPES = {"candling", "hatching_started", "discard", "observation", "closure"}


def create_incubation_draft(
    path: Path,
    record_type: str,
    payload: dict[str, Any],
    *,
    source: str,
    actor: str,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if record_type not in INCUBATION_RECORD_TYPES:
        raise OperationValidationError(
            "invalid_data",
            "record_type",
            f"Tipo de registro de incubación no soportado: {record_type}.",
        )
    records = load_incubation_records(path)
    data = _normalize_record(record_type, payload, records)
    if record_type == "incubator":
        _ensure_unique_incubator_name(records, data["name"])
    timestamp = now_iso()
    record_id = f"inc-{record_type}-{uuid4()}"
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
            "registered": None,
        },
        "type": record_type,
        "status": "awaiting_confirmation",
    }
    return record, _build_event("incubation_record_drafted", record, source, actor)


def confirm_incubation_record(
    path: Path,
    record_id: str,
    confirmation_code: str,
    *,
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    records = load_incubation_records(path)
    try:
        record = deepcopy(find_incubation_record(records, record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found",
            "record_id",
            "El registro de incubación no existe.",
        ) from exc
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente el resumen exacto de este registro de incubación?",
        )
    expected_code = str(record.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected_code, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador de incubación.",
        )
    if record.get("status") == "applied":
        record["idempotent_replay"] = True
        return record, None
    if record.get("status") != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status",
            "record_id",
            "El registro de incubación no está pendiente.",
        )
    _validate_dependencies_for_confirmation(record, records)
    if record["record_type"] == "incubator":
        _ensure_unique_incubator_name(records, record["data"]["name"], exclude_id=record_id)
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
        "store": "granja_luna_incubation_events",
        "operation_status": "applied",
    }
    return record, _build_event(
        "incubation_record_applied",
        record,
        source,
        actor,
        event_id=event_id,
    )


def cancel_incubation_draft(
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
    records = load_incubation_records(path)
    try:
        record = deepcopy(find_incubation_record(records, record_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "record_id", "El registro de incubación no existe."
        ) from exc
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
            "El código no corresponde a este borrador de incubación.",
        )
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
        "incubation_record_cancelled", record, source, actor, event_id=event_id
    )


def append_incubation_event(path: Path, event: dict[str, Any]) -> None:
    append_event(path, event)


def load_incubation_records(path: Path) -> list[dict[str, Any]]:
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


def list_incubation_records(
    path: Path,
    *,
    record_type: str | None = None,
    status: str = "applied",
    limit: int = 100,
) -> list[dict[str, Any]]:
    records = load_incubation_records(path)
    if record_type is not None:
        records = [record for record in records if record.get("record_type") == record_type]
    records = [record for record in records if record.get("status") == status]
    records.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return records[:limit]


def batch_detail(path: Path, batch_id: str) -> dict[str, Any]:
    records = load_incubation_records(path)
    try:
        batch = find_incubation_record(records, batch_id)
    except KeyError as exc:
        raise OperationValidationError("not_found", "batch_id", "El lote no existe.") from exc
    if batch.get("record_type") != "batch" or batch.get("status") != "applied":
        raise OperationValidationError("not_found", "batch_id", "El lote confirmado no existe.")
    events = [
        record
        for record in records
        if record.get("record_type") == "event"
        and record.get("status") == "applied"
        and record.get("data", {}).get("batch_id") == batch_id
    ]
    events.sort(key=lambda item: (item["data"]["event_date"], item["created_at"]))
    discarded = sum(int(event["data"].get("units_discarded") or 0) for event in events)
    closure = next((event for event in events if event["data"]["event_type"] == "closure"), None)
    results = None
    if closure is not None:
        results = {
            field: closure["data"][field]
            for field in ("hatched_alive", "eggs_unhatched", "chicks_dead", "chicks_malformed")
        }
    return {
        **deepcopy(batch),
        "events": deepcopy(events),
        "summary": {
            "eggs_set": batch["data"]["eggs_set"],
            "units_discarded": discarded,
            "unresolved_units": 0 if closure is not None else batch["data"]["eggs_set"] - discarded,
            "closed": closure is not None,
            "results": results,
        },
    }


def find_incubation_record(
    records: list[dict[str, Any]],
    record_id: str,
) -> dict[str, Any]:
    for record in records:
        if record.get("id") == record_id:
            return record
    raise KeyError(f"Incubation record not found: {record_id}")


def _normalize_record(
    record_type: str,
    payload: dict[str, Any],
    records: list[dict[str, Any]],
) -> dict[str, Any]:
    if record_type == "incubator":
        return {
            "name": _required_text(payload, "name", "¿Cómo se llama la incubadora?"),
            "capacity": _required_positive_integer(
                payload.get("capacity"),
                "capacity",
                "¿Cuál es la capacidad de la incubadora en huevos?",
            ),
            "notes": clean_text(payload.get("notes")),
        }
    if record_type == "batch":
        incubator_id = _required_text(
            payload,
            "incubator_id",
            "¿En qué incubadora se ingresó el lote?",
        )
        _validate_reference(records, incubator_id, "incubator", allow_pending=True)
        eggs_set = _required_positive_integer(
            payload.get("eggs_set"),
            "eggs_set",
            "¿Cuántos huevos ingresaron a incubación?",
        )
        source_egg_lots = _optional_source_egg_lots(payload.get("source_egg_lots"))
        if source_egg_lots and sum(item["quantity"] for item in source_egg_lots) != eggs_set:
            raise OperationValidationError(
                "result_mismatch",
                "source_egg_lots",
                "Las cantidades tomadas de lotes almacenados deben sumar los huevos ingresados.",
            )
        return {
            "incubator_id": incubator_id,
            "start_date": _required_date(payload, "start_date", "¿Qué día ingresaron los huevos?"),
            "eggs_set": eggs_set,
            "source_description": _required_text(
                payload,
                "source_description",
                "¿Cuál es el origen de los huevos?",
            ),
            "source_flock": clean_text(payload.get("source_flock")),
            "collection_dates": _optional_date_list(payload.get("collection_dates")),
            "purchase_movement_id": clean_text(payload.get("purchase_movement_id")),
            "source_egg_lots": source_egg_lots,
            "notes": clean_text(payload.get("notes")),
        }
    batch_id = _required_text(payload, "batch_id", "¿A qué lote corresponde el evento?")
    batch = _validate_reference(records, batch_id, "batch", allow_pending=True)
    event_date = _required_date(payload, "event_date", "¿Cuál fue la fecha del evento?")
    if event_date < batch["data"]["start_date"]:
        raise OperationValidationError(
            "invalid_data",
            "event_date",
            "La fecha del evento no puede ser anterior al ingreso del lote.",
        )
    event_type = _required_choice(
        payload,
        "event_type",
        INCUBATION_EVENT_TYPES,
        "¿Qué tipo de evento de incubación ocurrió?",
    )
    units_discarded = _optional_nonnegative_integer(
        payload.get("units_discarded"),
        "units_discarded",
        "La cantidad descartada debe ser un entero mayor o igual a cero.",
    )
    if event_type == "discard" and not units_discarded:
        raise OperationValidationError(
            "missing_required_data",
            "units_discarded",
            "¿Cuántas unidades se descartaron?",
        )
    results = {
        field: _optional_nonnegative_integer(
            payload.get(field),
            field,
            f"{label} debe ser un entero mayor o igual a cero.",
        )
        for field, label in (
            ("hatched_alive", "La cantidad de nacidos vivos"),
            ("eggs_unhatched", "La cantidad de huevos no eclosionados"),
            ("chicks_dead", "La cantidad de pollitos muertos"),
            ("chicks_malformed", "La cantidad de pollitos con malformación"),
        )
    }
    if event_type == "closure":
        for field, value in results.items():
            if value is None:
                raise OperationValidationError(
                    "missing_required_data",
                    field,
                    "El cierre requiere todos los resultados finales, incluyendo ceros.",
                )
    elif any(value is not None for value in results.values()):
        raise OperationValidationError(
            "invalid_data",
            "event_type",
            "Los resultados finales solo pueden informarse en un evento closure.",
        )
    return {
        "batch_id": batch_id,
        "event_date": event_date,
        "event_type": event_type,
        "units_discarded": units_discarded,
        "reason": clean_text(payload.get("reason")),
        "notes": clean_text(payload.get("notes")),
        **results,
    }


def _validate_dependencies_for_confirmation(
    record: dict[str, Any],
    records: list[dict[str, Any]],
) -> None:
    if record["record_type"] == "batch":
        incubator = _validate_reference(
            records,
            record["data"]["incubator_id"],
            "incubator",
            allow_pending=False,
        )
        closed_batch_ids = {
            item["data"]["batch_id"]
            for item in records
            if item.get("record_type") == "event"
            and item.get("status") == "applied"
            and item.get("data", {}).get("event_type") == "closure"
        }
        occupied = sum(
            int(item["data"]["eggs_set"])
            for item in records
            if item.get("record_type") == "batch"
            and item.get("status") == "applied"
            and item.get("data", {}).get("incubator_id") == incubator["id"]
            and item.get("id") not in closed_batch_ids
        )
        if occupied + record["data"]["eggs_set"] > incubator["data"]["capacity"]:
            raise OperationValidationError(
                "capacity_exceeded",
                "eggs_set",
                "Los lotes abiertos superarían la capacidad confirmada de la incubadora.",
            )
    if record["record_type"] == "event":
        batch = _validate_reference(
            records,
            record["data"]["batch_id"],
            "batch",
            allow_pending=False,
        )
        confirmed_discarded = sum(
            int(item["data"].get("units_discarded") or 0)
            for item in records
            if item.get("record_type") == "event"
            and item.get("status") == "applied"
            and item.get("data", {}).get("batch_id") == batch["id"]
        )
        new_discarded = int(record["data"].get("units_discarded") or 0)
        if confirmed_discarded + new_discarded > batch["data"]["eggs_set"]:
            raise OperationValidationError(
                "invalid_data",
                "units_discarded",
                "Los descartes acumulados no pueden superar los huevos ingresados.",
            )
        if record["data"]["event_type"] == "closure":
            if any(
                item.get("record_type") == "event"
                and item.get("status") == "applied"
                and item.get("data", {}).get("batch_id") == batch["id"]
                and item.get("data", {}).get("event_type") == "closure"
                for item in records
            ):
                raise OperationValidationError(
                    "conflict",
                    "event_type",
                    "El lote ya tiene un cierre confirmado.",
                )
            remaining = batch["data"]["eggs_set"] - confirmed_discarded - new_discarded
            final_total = sum(
                int(record["data"][field])
                for field in (
                    "hatched_alive",
                    "eggs_unhatched",
                    "chicks_dead",
                    "chicks_malformed",
                )
            )
            if final_total != remaining:
                raise OperationValidationError(
                    "result_mismatch",
                    "hatched_alive",
                    "Los resultados finales deben sumar las unidades pendientes del lote.",
                )


def _validate_reference(
    records: list[dict[str, Any]],
    record_id: str,
    record_type: str,
    *,
    allow_pending: bool,
) -> dict[str, Any]:
    try:
        record = find_incubation_record(records, record_id)
    except KeyError as exc:
        raise OperationValidationError(
            "not_found",
            f"{record_type}_id",
            f"El registro {record_type} indicado no existe.",
        ) from exc
    allowed = {"applied", "awaiting_confirmation"} if allow_pending else {"applied"}
    if record.get("record_type") != record_type or record.get("status") not in allowed:
        raise OperationValidationError(
            "invalid_dependency",
            f"{record_type}_id",
            f"El registro {record_type} debe estar confirmado antes de continuar.",
        )
    return record


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
            "invalid_data",
            field,
            "La fecha debe tener formato YYYY-MM-DD y ser válida.",
        ) from exc


def _optional_date_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise OperationValidationError(
            "invalid_data",
            "collection_dates",
            "Las fechas de recolección deben ser una lista.",
        )
    return [
        _required_date({"date": item}, "date", "¿Cuál fue la fecha de recolección?")
        for item in value
    ]


def _optional_source_egg_lots(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise OperationValidationError(
            "invalid_data", "source_egg_lots", "Los lotes de origen deben ser una lista."
        )
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise OperationValidationError(
                "invalid_data",
                "source_egg_lots",
                f"El lote de origen {index + 1} debe ser un objeto.",
            )
        lot_id = _required_text(
            item,
            "lot_id",
            f"¿Cuál es el identificador del lote de origen {index + 1}?",
        )
        if lot_id in seen:
            raise OperationValidationError(
                "invalid_data", "source_egg_lots", "Un lote de origen no puede repetirse."
            )
        seen.add(lot_id)
        result.append(
            {
                "lot_id": lot_id,
                "quantity": _required_positive_integer(
                    item.get("quantity"),
                    "source_egg_lots.quantity",
                    "La cantidad tomada del lote debe ser positiva.",
                ),
            }
        )
    return result


def _required_positive_integer(value: Any, field: str, question: str) -> int:
    number = _parse_integer(value, field, question)
    if number <= 0:
        raise OperationValidationError("invalid_data", field, question)
    return number


def _optional_nonnegative_integer(value: Any, field: str, question: str) -> int | None:
    if value is None or value == "":
        return None
    number = _parse_integer(
        value,
        field,
        question,
    )
    if number < 0:
        raise OperationValidationError(
            "invalid_data",
            field,
            question,
        )
    return number


def _parse_integer(value: Any, field: str, question: str) -> int:
    if isinstance(value, bool) or value is None or value == "":
        raise OperationValidationError("missing_required_data", field, question)
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise OperationValidationError("invalid_data", field, question) from exc
    if str(number) != str(value).strip():
        raise OperationValidationError("invalid_data", field, question)
    return number


def _required_choice(
    payload: dict[str, Any],
    field: str,
    choices: set[str],
    question: str,
) -> str:
    value = _required_text(payload, field, question)
    if value not in choices:
        raise OperationValidationError(
            "invalid_data",
            field,
            f"Valor no soportado. Usa uno de: {', '.join(sorted(choices))}.",
        )
    return value


def _ensure_unique_incubator_name(
    records: list[dict[str, Any]],
    name: str,
    *,
    exclude_id: str | None = None,
) -> None:
    duplicate = next(
        (
            record
            for record in records
            if record.get("id") != exclude_id
            and record.get("record_type") == "incubator"
            and record.get("status") == "applied"
            and str(record.get("data", {}).get("name", "")).casefold() == name.casefold()
        ),
        None,
    )
    if duplicate is not None:
        raise OperationValidationError(
            "conflict",
            "name",
            "Ya existe una incubadora confirmada con ese nombre.",
        )


def _confirmation_summary(
    record_type: str,
    data: dict[str, Any],
    records: list[dict[str, Any]],
) -> str:
    if record_type == "incubator":
        return (
            f"Registrar la incubadora {data['name']} con capacidad para {data['capacity']} huevos."
        )
    if record_type == "batch":
        incubator = find_incubation_record(records, data["incubator_id"])
        return (
            f"Ingresar {data['eggs_set']} huevos a {incubator['data']['name']} "
            f"con fecha {data['start_date']}."
        )
    return (
        f"Registrar evento {data['event_type']} del lote {data['batch_id']} "
        f"con fecha {data['event_date']} y {data.get('units_discarded') or 0} descartes."
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
