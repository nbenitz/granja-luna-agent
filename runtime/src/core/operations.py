from __future__ import annotations

import json
import os
import secrets
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any
from uuid import uuid4

MOVEMENT_TYPES = {"egg_collection", "purchase", "expense", "sale"}
MOVEMENT_STATUSES = {"awaiting_confirmation", "applied", "cancelled"}


class OperationInputError(ValueError):
    def __init__(self, field: str, label: str, message: str | None = None) -> None:
        self.field = field
        self.label = label
        self.message = message or f"Falta un dato indispensable: {label}."
        super().__init__(self.message)

    def as_detail(self) -> dict[str, object]:
        return {
            "code": "invalid_or_missing_required_data",
            "message": self.message,
            "missing_field": {"path": self.field, "label": self.label},
        }


def _create_structured_draft(
    movement_type: str,
    payload: dict[str, Any],
    *,
    source: str,
    actor: str,
    request_id: str | None = None,
    request_text: str | None = None,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    if movement_type not in MOVEMENT_TYPES:
        raise OperationInputError(
            "movement_type",
            "tipo de movimiento",
            f"Tipo de movimiento no soportado: {movement_type}.",
        )
    timestamp = occurred_at or now_iso()
    interpreted = normalize_movement(movement_type, payload)
    movement_id = f"mov-{uuid4()}"
    if movement_type == "egg_collection":
        interpreted["lot_id"] = f"egg-lot-{movement_id.removeprefix('mov-')}"
    confirmation_code = secrets.token_hex(4)
    requested_payload = deepcopy(payload)
    if request_text:
        requested_payload["request_text"] = request_text
    return {
        "schema_version": 1,
        "id": movement_id,
        "movement_type": movement_type,
        "operation_status": "awaiting_confirmation",
        "record_status": "draft",
        "effective_date": interpreted["effective_date"],
        "created_at": timestamp,
        "updated_at": timestamp,
        "data": interpreted,
        "inventory_effects": build_inventory_effects(movement_type, interpreted),
        "confirmation": {
            "required": True,
            "code": confirmation_code,
            "summary": confirmation_summary(movement_type, interpreted),
            "confirmed_at": None,
        },
        "trace": {
            "requested": {
                "at": timestamp,
                "source": clean_text(source) or "unknown",
                "actor": clean_text(actor) or "unknown",
                "request_id": clean_text(request_id),
                "payload": requested_payload,
            },
            "interpreted": {
                "at": timestamp,
                "method": "deterministic_structured_input_v1",
                "payload": deepcopy(interpreted),
            },
            "confirmed": None,
            "registered": None,
        },
    }


def normalize_movement(movement_type: str, payload: dict[str, Any]) -> dict[str, Any]:
    if movement_type == "egg_collection":
        return normalize_egg_collection(payload)
    if movement_type == "purchase":
        return normalize_purchase(payload)
    if movement_type == "expense":
        return normalize_expense(payload)
    return normalize_sale(payload)


def normalize_egg_collection(payload: dict[str, Any]) -> dict[str, Any]:
    effective_date = required_date(payload, "date", "fecha de recolección")
    flock = required_text(payload, "flock", "plantel o lote de origen")
    eggs_total = required_integer(payload, "eggs_total", "cantidad total de huevos", minimum=0)
    result = {
        "effective_date": effective_date,
        "flock": flock,
        "flock_id": clean_text(payload.get("flock_id")),
        "barn_id": clean_text(payload.get("barn_id")),
        "eggs_total": eggs_total,
        "eggs_healthy": optional_integer(payload, "eggs_healthy", minimum=0),
        "eggs_broken": optional_integer(payload, "eggs_broken", minimum=0),
        "eggs_dirty": optional_integer(payload, "eggs_dirty", minimum=0),
        "destination": clean_text(payload.get("destination")),
        "storage_area_id": clean_text(payload.get("storage_area_id")),
        "purpose": clean_text(payload.get("purpose")),
        "physical_separation": optional_boolean(
            payload, "physical_separation", default=False
        ),
        "identification_stage": optional_choice(
            payload,
            "identification_stage",
            {"collection", "storage", "incubation", "hatch", "unspecified"},
            default="unspecified",
        ),
        "classifications": normalize_egg_classifications(
            payload.get("classifications"), eggs_total
        ),
        "notes": clean_text(payload.get("notes")),
    }
    classified = [
        value
        for value in (result["eggs_healthy"], result["eggs_broken"], result["eggs_dirty"])
        if value is not None
    ]
    if sum(classified) > eggs_total:
        raise OperationInputError(
            "eggs_total",
            "cantidad total de huevos",
            "La suma de huevos clasificados no puede superar la cantidad total.",
        )
    return result


def normalize_egg_classifications(value: Any, eggs_total: int) -> list[dict[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise OperationInputError(
            "classifications",
            "clasificaciones de los huevos",
            "Las clasificaciones deben ser una lista.",
        )
    normalized: list[dict[str, Any]] = []
    totals_by_axis: dict[str, int] = defaultdict(int)
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise OperationInputError(
                f"classifications.{index}",
                f"clasificación {index + 1}",
            )
        axis = required_text(item, "axis", f"eje de la clasificación {index + 1}")
        label = required_text(item, "value", f"valor de la clasificación {index + 1}")
        quantity = required_integer(
            item,
            "quantity",
            f"cantidad de la clasificación {index + 1}",
            minimum=1,
        )
        certainty = optional_choice(
            item,
            "certainty",
            {"observed", "probable", "confirmed_at_hatch"},
            default="observed",
        )
        information_status = optional_choice(
            item,
            "information_status",
            {"confirmed", "inferred", "pending_review"},
            default="confirmed",
        )
        method = optional_choice(
            item,
            "method",
            {"manual", "automatic"},
            default="manual",
        )
        confidence = optional_number(item, "confidence", minimum=0)
        if confidence is not None and confidence > 1:
            raise OperationInputError(
                f"classifications.{index}.confidence",
                "confianza de clasificación entre 0 y 1",
            )
        totals_by_axis[axis.casefold()] += quantity
        normalized.append(
            {
                "axis": axis,
                "value": label,
                "quantity": quantity,
                "certainty": certainty,
                "information_status": information_status,
                "method": method,
                "station_id": clean_text(item.get("station_id")),
                "confidence": confidence,
                "notes": clean_text(item.get("notes")),
            }
        )
    if any(total > eggs_total for total in totals_by_axis.values()):
        raise OperationInputError(
            "classifications",
            "clasificaciones de los huevos",
            "La suma dentro de un mismo eje no puede superar los huevos recolectados.",
        )
    return normalized


def normalize_purchase(payload: dict[str, Any]) -> dict[str, Any]:
    effective_date = required_date(payload, "date", "fecha real de compra")
    supplier = required_text(payload, "supplier", "proveedor")
    items = normalize_items(payload.get("items"))
    price_status = required_choice(
        payload,
        "price_status",
        "estado del precio (confirmed o pending)",
        {"confirmed", "pending"},
    )
    inventory_effect = required_choice(
        payload,
        "inventory_effect",
        "decisión de inventario (add o none)",
        {"add", "none"},
    )
    declared_total = optional_number(payload, "total_amount", minimum=0)
    currency = clean_text(payload.get("currency"))
    calculated_total = calculate_items_total(items)
    if price_status == "confirmed" and declared_total is None and calculated_total is None:
        raise OperationInputError(
            "total_amount",
            "precio total o precio unitario de cada item",
        )
    if (
        declared_total is not None
        and calculated_total is not None
        and Decimal(str(declared_total)) != Decimal(str(calculated_total))
    ):
        raise OperationInputError(
            "total_amount",
            "total correcto de la compra",
            "El total declarado no coincide con la suma de cantidades y precios unitarios.",
        )
    if (declared_total is not None or calculated_total is not None) and not currency:
        raise OperationInputError("currency", "moneda")
    return {
        "effective_date": effective_date,
        "supplier": supplier,
        "items": items,
        "price_status": price_status,
        "currency": currency,
        "total_amount": declared_total if declared_total is not None else calculated_total,
        "total_provenance": (
            "declared"
            if declared_total is not None
            else "calculated"
            if calculated_total is not None
            else None
        ),
        "inventory_effect": inventory_effect,
        "category": clean_text(payload.get("category")),
        "receipt_reference": clean_text(payload.get("receipt_reference")),
        "notes": clean_text(payload.get("notes")),
    }


def normalize_expense(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "effective_date": required_date(payload, "date", "fecha real del gasto"),
        "description": required_text(payload, "description", "concepto del gasto"),
        "category": required_text(payload, "category", "categoría del gasto"),
        "amount": required_number(payload, "amount", "monto", minimum=0),
        "currency": required_text(payload, "currency", "moneda"),
        "payee": clean_text(payload.get("payee")),
        "receipt_reference": clean_text(payload.get("receipt_reference")),
        "notes": clean_text(payload.get("notes")),
    }


def normalize_sale(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "effective_date": required_date(payload, "date", "fecha real de venta"),
        "customer": clean_text(payload.get("customer")),
        "items": normalize_items(payload.get("items")),
        "total_amount": required_number(payload, "total_amount", "monto total de venta", minimum=0),
        "currency": required_text(payload, "currency", "moneda"),
        "inventory_effect": required_choice(
            payload,
            "inventory_effect",
            "decisión de inventario (subtract o none)",
            {"subtract", "none"},
        ),
        "payment_status": clean_text(payload.get("payment_status")),
        "notes": clean_text(payload.get("notes")),
    }


def normalize_items(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise OperationInputError("items", "al menos un item")
    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, dict):
            raise OperationInputError(f"items.{index}", f"item {index + 1}")
        normalized.append(
            {
                "product": required_text(item, "product", f"producto del item {index + 1}"),
                "quantity": required_number(
                    item,
                    "quantity",
                    f"cantidad del item {index + 1}",
                    minimum=0,
                    exclusive_minimum=True,
                ),
                "unit": required_text(item, "unit", f"unidad del item {index + 1}"),
                "unit_price": optional_number(item, "unit_price", minimum=0),
                "category": clean_text(item.get("category")),
            }
        )
    return normalized


def build_inventory_effects(movement_type: str, data: dict[str, Any]) -> list[dict[str, Any]]:
    direction = None
    if movement_type == "purchase" and data.get("inventory_effect") == "add":
        direction = Decimal("1")
    elif movement_type == "sale" and data.get("inventory_effect") == "subtract":
        direction = Decimal("-1")
    if direction is None:
        return []
    return [
        {
            "product": item["product"],
            "unit": item["unit"],
            "category": item.get("category") or data.get("category"),
            "quantity_delta": number_to_json(Decimal(str(item["quantity"])) * direction),
        }
        for item in data["items"]
    ]


def build_event(
    event_type: str,
    movement: dict[str, Any],
    *,
    source: str,
    actor: str,
    occurred_at: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "event_id": f"evt-{uuid4()}",
        "movement_id": movement["id"],
        "event_type": event_type,
        "occurred_at": occurred_at or now_iso(),
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "movement": deepcopy(movement),
    }


def append_event(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        file.flush()
        os.fsync(file.fileno())


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid operational JSONL at {path}:{line_number}: {exc}") from exc
        events.append(event)
    return events


def load_movements(path: Path) -> list[dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for event in load_events(path):
        movement_id = event.get("movement_id")
        movement = event.get("movement")
        if not movement_id or not isinstance(movement, dict):
            continue
        if movement_id not in latest:
            order.append(movement_id)
        latest[movement_id] = movement
    return [latest[movement_id] for movement_id in order]


def _find_movement_in_store(path: Path, movement_id: str) -> dict[str, Any]:
    for movement in load_movements(path):
        if movement.get("id") == movement_id:
            return movement
    raise KeyError(f"Movement not found: {movement_id}")


def get_inventory(path: Path, *, product: str | None = None) -> dict[str, Any]:
    balances: dict[tuple[str, str], Decimal] = defaultdict(Decimal)
    display: dict[tuple[str, str], dict[str, Any]] = {}
    for movement in load_movements(path):
        if movement.get("operation_status") != "applied":
            continue
        for effect in movement.get("inventory_effects", []):
            product_name = str(effect.get("product", "")).strip()
            unit = str(effect.get("unit", "")).strip()
            if not product_name or not unit:
                continue
            key = (product_name.casefold(), unit.casefold())
            balances[key] += Decimal(str(effect.get("quantity_delta", 0)))
            display.setdefault(
                key,
                {
                    "product": product_name,
                    "unit": unit,
                    "category": effect.get("category"),
                },
            )
    query = clean_text(product)
    items: list[dict[str, Any]] = []
    for key, quantity in balances.items():
        item = {
            **display[key],
            "quantity": number_to_json(quantity),
            "needs_reconciliation": quantity < 0,
        }
        if query and query.casefold() not in item["product"].casefold():
            continue
        items.append(item)
    items.sort(key=lambda item: (item["product"].casefold(), item["unit"].casefold()))
    return {
        "as_of": now_iso(),
        "scope": "confirmed_bridge_movements_only",
        "items": items,
        "warnings": [
            "El inventario incluye solo movimientos confirmados registrados por este puente.",
            "Un saldo negativo indica que falta conciliar un stock inicial o un movimiento previo.",
        ],
    }


def egg_storage_lots(
    path: Path,
    *,
    structure_records: list[dict[str, Any]] | None = None,
    incubation_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    storage_names = {
        record["id"]: record.get("data", {}).get("name")
        for record in structure_records or []
        if record.get("record_type") == "egg_storage_area"
        and record.get("status") == "applied"
    }
    allocations: dict[str, int] = defaultdict(int)
    allocation_details: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in incubation_records or []:
        if record.get("record_type") != "batch" or record.get("status") != "applied":
            continue
        for source in record.get("data", {}).get("source_egg_lots", []):
            lot_id = str(source.get("lot_id", ""))
            quantity = int(source.get("quantity", 0))
            if not lot_id or quantity <= 0:
                continue
            allocations[lot_id] += quantity
            allocation_details[lot_id].append(
                {
                    "destination_type": "incubation_batch",
                    "destination_id": record["id"],
                    "quantity": quantity,
                }
            )
    lots: list[dict[str, Any]] = []
    for movement in load_movements(path):
        data = movement.get("data", {})
        if (
            movement.get("movement_type") != "egg_collection"
            or movement.get("operation_status") != "applied"
            or not data.get("storage_area_id")
            or not data.get("lot_id")
        ):
            continue
        total = int(data.get("eggs_total", 0))
        allocated = allocations[data["lot_id"]]
        lots.append(
            {
                "schema_version": 1,
                "id": data["lot_id"],
                "collection_movement_id": movement["id"],
                "effective_date": data["effective_date"],
                "flock": data["flock"],
                "flock_id": data.get("flock_id"),
                "barn_id": data.get("barn_id"),
                "purpose": data.get("purpose"),
                "storage_area_id": data["storage_area_id"],
                "storage_area_name": storage_names.get(data["storage_area_id"]),
                "quantity_collected": total,
                "quantity_allocated": allocated,
                "quantity_available": total - allocated,
                "needs_reconciliation": allocated > total,
                "physical_separation": data.get("physical_separation", False),
                "identification_stage": data.get("identification_stage", "unspecified"),
                "classifications": deepcopy(data.get("classifications", [])),
                "allocations": allocation_details[data["lot_id"]],
                "notes": data.get("notes"),
            }
        )
    lots.sort(key=lambda item: (item["effective_date"], item["id"]), reverse=True)
    return lots


def get_daily_summary(path: Path, effective_date: str) -> dict[str, Any]:
    parsed_date = parse_iso_date(effective_date, "date", "fecha del resumen")
    movements = [
        item
        for item in load_movements(path)
        if item.get("operation_status") == "applied" and item.get("effective_date") == parsed_date
    ]
    counts = Counter(item.get("movement_type", "unknown") for item in movements)
    money: dict[str, dict[str, Decimal]] = defaultdict(lambda: defaultdict(Decimal))
    eggs_total = 0
    for movement in movements:
        movement_type = movement.get("movement_type")
        data = movement.get("data", {})
        if movement_type == "egg_collection":
            eggs_total += int(data.get("eggs_total", 0))
        amount_field = "amount" if movement_type == "expense" else "total_amount"
        amount = data.get(amount_field)
        currency = data.get("currency")
        if movement_type in {"purchase", "expense", "sale"} and amount is not None and currency:
            money[str(currency)][str(movement_type)] += Decimal(str(amount))
    monetary_totals = {
        currency: {kind: number_to_json(amount) for kind, amount in totals.items()}
        for currency, totals in sorted(money.items())
    }
    pending = sum(
        1
        for item in load_movements(path)
        if item.get("operation_status") == "awaiting_confirmation"
    )
    return {
        "date": parsed_date,
        "scope": "confirmed_bridge_movements_only",
        "confirmed_movements": len(movements),
        "by_type": dict(counts),
        "egg_collection": {"eggs_total": eggs_total},
        "monetary_totals": monetary_totals,
        "pending_movements": pending,
        "movements": movements,
    }


def get_operations_status(path: Path) -> dict[str, Any]:
    movements = load_movements(path)
    return {
        "status": "ok",
        "mode": "draft_then_explicit_confirmation",
        "source_of_truth": "granja_luna_operational_events",
        "movement_types": sorted(MOVEMENT_TYPES),
        "movements": {
            "total": len(movements),
            "awaiting_confirmation": sum(
                1 for item in movements if item.get("operation_status") == "awaiting_confirmation"
            ),
            "applied": sum(1 for item in movements if item.get("operation_status") == "applied"),
            "cancelled": sum(
                1 for item in movements if item.get("operation_status") == "cancelled"
            ),
        },
        "destructive_actions_enabled": False,
    }


def confirmation_summary(movement_type: str, data: dict[str, Any]) -> str:
    if movement_type == "egg_collection":
        destination = (
            f" y almacenarlos en {data['storage_area_id']}"
            if data.get("storage_area_id")
            else ""
        )
        return (
            f"Registrar {data['eggs_total']} huevos del plantel {data['flock']} "
            f"con fecha {data['effective_date']}{destination}."
        )
    if movement_type == "purchase":
        return (
            f"Registrar compra a {data['supplier']} con {len(data['items'])} item(s), "
            f"fecha {data['effective_date']} e inventario {data['inventory_effect']}."
        )
    if movement_type == "expense":
        return (
            f"Registrar gasto de {data['amount']} {data['currency']} en "
            f"{data['category']} con fecha {data['effective_date']}."
        )
    return (
        f"Registrar venta de {len(data['items'])} item(s) por "
        f"{data['total_amount']} {data['currency']} con fecha {data['effective_date']}."
    )


def calculate_items_total(items: list[dict[str, Any]]) -> int | float | None:
    if not items or any(item.get("unit_price") is None for item in items):
        return None
    total = sum(
        (Decimal(str(item["quantity"])) * Decimal(str(item["unit_price"])) for item in items),
        Decimal("0"),
    )
    return number_to_json(total)


def required_text(payload: dict[str, Any], field: str, label: str) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        raise OperationInputError(field, label)
    return value


def required_date(payload: dict[str, Any], field: str, label: str) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        raise OperationInputError(field, label)
    return parse_iso_date(value, field, label)


def parse_iso_date(value: str, field: str, label: str) -> str:
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise OperationInputError(
            field, label, f"{label.capitalize()} debe usar YYYY-MM-DD."
        ) from exc


def required_integer(
    payload: dict[str, Any],
    field: str,
    label: str,
    *,
    minimum: int,
) -> int:
    value = payload.get(field)
    if value is None or value == "":
        raise OperationInputError(field, label)
    if isinstance(value, bool):
        raise OperationInputError(field, label, f"{label.capitalize()} debe ser un número entero.")
    try:
        number = Decimal(str(value))
    except InvalidOperation as exc:
        raise OperationInputError(
            field, label, f"{label.capitalize()} debe ser un número entero."
        ) from exc
    if number != number.to_integral() or number < minimum:
        raise OperationInputError(
            field, label, f"{label.capitalize()} debe ser un entero mayor o igual a {minimum}."
        )
    return int(number)


def optional_integer(
    payload: dict[str, Any],
    field: str,
    *,
    minimum: int,
) -> int | None:
    if payload.get(field) is None or payload.get(field) == "":
        return None
    return required_integer(payload, field, field.replace("_", " "), minimum=minimum)


def required_number(
    payload: dict[str, Any],
    field: str,
    label: str,
    *,
    minimum: int,
    exclusive_minimum: bool = False,
) -> int | float:
    if payload.get(field) is None or payload.get(field) == "":
        raise OperationInputError(field, label)
    value = parse_number(payload.get(field), field, label)
    invalid = value <= minimum if exclusive_minimum else value < minimum
    if invalid:
        comparator = "mayor que" if exclusive_minimum else "mayor o igual a"
        raise OperationInputError(
            field, label, f"{label.capitalize()} debe ser {comparator} {minimum}."
        )
    return number_to_json(value)


def optional_number(
    payload: dict[str, Any],
    field: str,
    *,
    minimum: int,
) -> int | float | None:
    if payload.get(field) is None or payload.get(field) == "":
        return None
    return required_number(payload, field, field.replace("_", " "), minimum=minimum)


def parse_number(value: Any, field: str, label: str) -> Decimal:
    if isinstance(value, bool):
        raise OperationInputError(field, label, f"{label.capitalize()} debe ser numérico.")
    try:
        number = Decimal(str(value).replace(",", "."))
    except InvalidOperation as exc:
        raise OperationInputError(field, label, f"{label.capitalize()} debe ser numérico.") from exc
    if not number.is_finite():
        raise OperationInputError(field, label, f"{label.capitalize()} debe ser finito.")
    return number


def required_choice(
    payload: dict[str, Any],
    field: str,
    label: str,
    choices: set[str],
) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        raise OperationInputError(field, label)
    if value not in choices:
        raise OperationInputError(
            field,
            label,
            f"{label.capitalize()} debe ser uno de: {', '.join(sorted(choices))}.",
        )
    return value


def optional_choice(
    payload: dict[str, Any],
    field: str,
    choices: set[str],
    *,
    default: str,
) -> str:
    value = clean_text(payload.get(field))
    if value is None:
        return default
    if value not in choices:
        raise OperationInputError(
            field,
            field.replace("_", " "),
            f"{field.replace('_', ' ').capitalize()} debe ser uno de: "
            f"{', '.join(sorted(choices))}.",
        )
    return value


def optional_boolean(payload: dict[str, Any], field: str, *, default: bool) -> bool:
    value = payload.get(field)
    if value is None or value == "":
        return default
    if not isinstance(value, bool):
        raise OperationInputError(
            field,
            field.replace("_", " "),
            f"{field.replace('_', ' ').capitalize()} debe ser true o false.",
        )
    return value


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def number_to_json(value: Decimal) -> int | float:
    if value == value.to_integral():
        return int(value)
    return float(value)


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


class OperationValidationError(ValueError):
    def __init__(self, code: str, missing_field: str, question: str) -> None:
        self.code = code
        self.missing_field = missing_field
        self.question = question
        super().__init__(question)

    def detail(self) -> dict[str, str]:
        return {
            "code": self.code,
            "missing_field": self.missing_field,
            "question": self.question,
        }


def create_movement_draft(
    movement_type: str,
    payload: dict[str, Any],
    *,
    source: str,
    actor: str,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    original_payload = deepcopy(payload)
    normalized_input = deepcopy(payload)
    normalized_input["date"] = payload.get("effective_date")
    if movement_type in {"purchase", "sale"}:
        update_inventory = payload.get("update_inventory")
        normalized_input["inventory_effect"] = (
            "add"
            if movement_type == "purchase" and update_inventory is True
            else "subtract"
            if movement_type == "sale" and update_inventory is True
            else "none"
            if update_inventory is False
            else None
        )
    try:
        movement = _create_structured_draft(
            movement_type,
            normalized_input,
            source=source,
            actor=actor,
            request_id=request_id,
        )
    except OperationInputError as exc:
        field = {
            "date": "effective_date",
            "inventory_effect": "update_inventory",
        }.get(exc.field, exc.field)
        raise OperationValidationError(
            "missing_required_data"
            if exc.message.startswith("Falta un dato indispensable")
            else "invalid_data",
            field,
            operation_question(movement_type, field, exc.message),
        ) from exc
    movement["type"] = movement["movement_type"]
    movement["status"] = movement["operation_status"]
    movement["trace"]["requested"]["payload"] = original_payload
    event = build_event(
        "movement_drafted",
        movement,
        source=source,
        actor=actor,
        occurred_at=movement["created_at"],
    )
    return movement, event


def confirm_movement(
    path: Path,
    movement_id: str,
    confirmation_code: str,
    *,
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        movement = deepcopy(_find_movement_in_store(path, movement_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found",
            "movement_id",
            "El movimiento no existe.",
        ) from exc
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente el resumen exacto de este movimiento?",
        )
    expected_code = str(movement.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected_code, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador. Revisa el movimiento antes de confirmar.",
        )
    status = movement.get("status", movement.get("operation_status"))
    if status == "applied":
        movement["idempotent_replay"] = True
        return movement, None
    if status != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status",
            "movement_id",
            "El movimiento no está pendiente de confirmación.",
        )
    timestamp = now_iso()
    event_id = f"evt-{uuid4()}"
    movement["status"] = "applied"
    movement["operation_status"] = "applied"
    movement["record_status"] = "confirmed"
    movement["updated_at"] = timestamp
    movement["confirmation"]["confirmed_at"] = timestamp
    movement["trace"]["confirmed"] = {
        "at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "request_id": clean_text(request_id),
        "explicit": True,
    }
    movement["trace"]["registered"] = {
        "at": timestamp,
        "event_id": event_id,
        "store": "granja_luna_operational_events",
        "operation_status": "applied",
    }
    event = {
        "schema_version": 1,
        "event_id": event_id,
        "movement_id": movement_id,
        "event_type": "movement_applied",
        "occurred_at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "movement": deepcopy(movement),
    }
    return movement, event


def cancel_movement_draft(
    path: Path,
    movement_id: str,
    confirmation_code: str,
    reason: str,
    *,
    source: str,
    actor: str,
    explicit_confirmation: bool,
    request_id: str | None = None,
) -> tuple[dict[str, Any], dict[str, Any] | None]:
    try:
        movement = deepcopy(_find_movement_in_store(path, movement_id))
    except KeyError as exc:
        raise OperationValidationError(
            "not_found", "movement_id", "El movimiento no existe."
        ) from exc
    if not explicit_confirmation:
        raise OperationValidationError(
            "explicit_confirmation_required",
            "explicit_confirmation",
            "¿Confirmas explícitamente la cancelación de este borrador?",
        )
    expected_code = str(movement.get("confirmation", {}).get("code", ""))
    if not secrets.compare_digest(expected_code, str(confirmation_code)):
        raise OperationValidationError(
            "confirmation_code_mismatch",
            "confirmation_code",
            "El código no corresponde a este borrador.",
        )
    status = movement.get("status", movement.get("operation_status"))
    if status == "cancelled":
        movement["idempotent_replay"] = True
        return movement, None
    if status != "awaiting_confirmation":
        raise OperationValidationError(
            "invalid_status", "movement_id", "Solo se puede cancelar un borrador pendiente."
        )
    cancellation_reason = clean_text(reason)
    if cancellation_reason is None:
        raise OperationValidationError(
            "missing_required_data", "reason", "¿Por qué se cancela este borrador?"
        )
    timestamp = now_iso()
    event_id = f"evt-{uuid4()}"
    movement["status"] = "cancelled"
    movement["operation_status"] = "cancelled"
    movement["record_status"] = "cancelled"
    movement["updated_at"] = timestamp
    movement["trace"]["cancelled"] = {
        "at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "request_id": clean_text(request_id),
        "explicit": True,
        "reason": cancellation_reason,
    }
    event = {
        "schema_version": 1,
        "event_id": event_id,
        "movement_id": movement_id,
        "event_type": "movement_cancelled",
        "occurred_at": timestamp,
        "source": clean_text(source) or "unknown",
        "actor": clean_text(actor) or "unknown",
        "movement": deepcopy(movement),
    }
    return movement, event


def append_operation_event(path: Path, event: dict[str, Any]) -> None:
    append_event(path, event)


def load_operation_events(path: Path) -> list[dict[str, Any]]:
    return load_events(path)


def find_movement(movements: list[dict[str, Any]], movement_id: str) -> dict[str, Any]:
    for movement in movements:
        if movement.get("id") == movement_id:
            return movement
    raise KeyError(f"Movement not found: {movement_id}")


def list_pending_movements(path: Path, *, limit: int = 100) -> list[dict[str, Any]]:
    pending = [
        movement
        for movement in load_movements(path)
        if movement.get("status", movement.get("operation_status")) == "awaiting_confirmation"
    ]
    pending.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
    return pending[:limit]


def inventory_summary(path: Path, *, product: str | None = None) -> dict[str, Any]:
    return get_inventory(path, product=product)


def daily_summary(path: Path, effective_date: str) -> dict[str, Any]:
    try:
        summary = get_daily_summary(path, effective_date)
    except OperationInputError as exc:
        raise OperationValidationError(
            "invalid_data",
            "date",
            operation_question("summary", "date", exc.message),
        ) from exc
    return {
        **summary,
        "eggs_collected": summary["egg_collection"]["eggs_total"],
        "money": summary["monetary_totals"],
    }


def operations_status(path: Path) -> dict[str, Any]:
    return get_operations_status(path)


def operation_question(movement_type: str, field: str, fallback: str) -> str:
    questions = {
        ("egg_collection", "effective_date"): "¿Cuál fue la fecha de recolección?",
        ("egg_collection", "flock"): "¿De qué plantel o lote provienen los huevos?",
        ("egg_collection", "eggs_total"): "¿Cuántos huevos se recolectaron en total?",
        ("purchase", "effective_date"): "¿Cuál fue la fecha de compra?",
        ("purchase", "supplier"): "¿Quién fue el proveedor?",
        ("purchase", "items"): "¿Cuál fue el primer producto comprado?",
        ("purchase", "price_status"): "¿El precio está confirmado o queda pendiente?",
        ("purchase", "currency"): "¿En qué moneda se registró la compra?",
        ("purchase", "total_amount"): "¿Cuál es el total correcto de la compra?",
        ("purchase", "update_inventory"): "¿La compra debe aumentar el inventario?",
        ("expense", "effective_date"): "¿Cuál fue la fecha del gasto?",
        ("expense", "description"): "¿Cuál fue el concepto del gasto?",
        ("expense", "category"): "¿Cuál es la categoría del gasto?",
        ("expense", "amount"): "¿Cuál fue el monto del gasto?",
        ("expense", "currency"): "¿En qué moneda fue el gasto?",
        ("sale", "effective_date"): "¿Cuál fue la fecha de venta?",
        ("sale", "items"): "¿Cuál fue el primer producto vendido?",
        ("sale", "total_amount"): "¿Cuál fue el monto total de la venta?",
        ("sale", "currency"): "¿En qué moneda fue la venta?",
        ("sale", "update_inventory"): "¿La venta debe descontarse del inventario?",
        ("summary", "date"): "¿Qué fecha quieres resumir en formato YYYY-MM-DD?",
    }
    return questions.get((movement_type, field), fallback)
