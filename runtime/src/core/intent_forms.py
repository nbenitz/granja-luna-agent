from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

from core.parsing import parse_purchase_adjustments


PURCHASE_SCHEMA: dict[str, Any] = {
    "schema_id": "purchase.v2",
    "intent": "registrar_compra",
    "title": "Compra",
    "fields": [
        {
            "name": "fecha_compra",
            "label": "Fecha de compra",
            "type": "date",
            "required": True,
        },
        {
            "name": "proveedor",
            "label": "Proveedor",
            "type": "text",
            "required": True,
        },
        {
            "name": "moneda",
            "label": "Moneda",
            "type": "select",
            "required": True,
            "options": [
                {"value": "PYG", "label": "Guaranies (PYG)"},
            ],
        },
        {
            "name": "comprobante",
            "label": "Comprobante o referencia",
            "type": "text",
            "required": False,
        },
        {
            "name": "descuento",
            "label": "Descuento",
            "type": "adjustment",
            "required": False,
        },
        {
            "name": "total_declarado",
            "label": "Total declarado",
            "type": "number",
            "required": False,
        },
    ],
    "collections": [
        {
            "name": "items",
            "label": "Items",
            "required": True,
            "item_fields": [
                {"name": "producto", "label": "Producto", "type": "text", "required": True},
                {"name": "cantidad", "label": "Cantidad", "type": "number", "required": True},
                {"name": "unidad", "label": "Unidad", "type": "text", "required": True},
                {
                    "name": "precio_unitario",
                    "label": "Precio unitario",
                    "type": "number",
                    "required": False,
                },
            ],
        }
    ],
}

INTENT_SCHEMAS: dict[str, dict[str, Any]] = {
    "registrar_compra": PURCHASE_SCHEMA,
}


def get_intent_schema(intent: str) -> dict[str, Any] | None:
    return INTENT_SCHEMAS.get(intent)


def build_structured_data(dry_run: dict[str, Any]) -> dict[str, Any] | None:
    intent = dry_run["classification"]["intent"]
    schema = get_intent_schema(intent)
    if not schema:
        return None
    if intent == "registrar_compra":
        return build_purchase_data(dry_run, schema)
    return None


def build_purchase_data(dry_run: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    purchase = dry_run.get("drafts", {}).get("purchase") or {}
    detected_items = dry_run.get("detected_data", {}).get("items", [])
    items = [normalize_purchase_item(item) for item in detected_items]
    return {
        "schema_id": schema["schema_id"],
        "intent": schema["intent"],
        "title": schema["title"],
        "schema": schema,
        "values": {
            "fecha_compra": purchase.get("fecha_real"),
            "proveedor": purchase.get("proveedor"),
            "moneda": purchase.get("moneda", "PYG"),
            "comprobante": None,
            "descuento": purchase.get("descuento"),
            "total_declarado": purchase.get("total_declarado"),
            "items": items,
        },
        "provenance": {
            "fields": {
                "fecha_compra": "extracted" if purchase.get("fecha_real") else "missing",
                "proveedor": "extracted" if purchase.get("proveedor") else "missing",
                "moneda": "suggested",
                "comprobante": "missing",
                "descuento": "extracted" if purchase.get("descuento") else "missing",
                "total_declarado": "extracted" if purchase.get("total_declarado") is not None else "missing",
            },
            "items": [purchase_item_provenance(item) for item in items],
        },
        "suggestions": {
            "fecha_compra": purchase.get("fecha_inferida"),
        },
        "information_status": "pending_review",
    }


def ensure_structured_data(entry: dict[str, Any]) -> dict[str, Any] | None:
    structured_data = entry.get("structured_data")
    if structured_data and structured_data.get("schema_id") == "purchase.v1":
        structured_data = migrate_purchase_v1(entry, structured_data)
        entry["structured_data"] = structured_data
        return structured_data
    if structured_data and structured_data.get("schema_id") == "purchase.v2":
        ensure_purchase_v2_shape(structured_data, entry)
        return structured_data
    if structured_data:
        return structured_data
    structured_data = build_structured_data(entry.get("dry_run", {}))
    entry["structured_data"] = structured_data
    return structured_data


def update_structured_values(
    entry: dict[str, Any],
    submitted: dict[str, Any],
    provenance_source: str = "corrected",
) -> dict[str, Any] | None:
    structured_data = ensure_structured_data(entry)
    if not structured_data:
        return None
    if structured_data["schema_id"] == "purchase.v2":
        previous = structured_data.get("values", {})
        normalized = normalize_purchase_values(submitted)
        structured_data["values"] = normalized
        update_purchase_provenance(structured_data, previous, normalized, provenance_source)
    return structured_data


def normalize_purchase_values(values: dict[str, Any]) -> dict[str, Any]:
    raw_items = values.get("items") if isinstance(values.get("items"), list) else []
    return {
        "fecha_compra": clean_text(values.get("fecha_compra")),
        "proveedor": clean_text(values.get("proveedor")),
        "moneda": clean_text(values.get("moneda")) or "PYG",
        "comprobante": clean_text(values.get("comprobante")),
        "descuento": normalize_discount(values.get("descuento")),
        "total_declarado": normalize_number(values.get("total_declarado")),
        "items": [normalize_purchase_item(item) for item in raw_items if isinstance(item, dict)],
    }


def normalize_purchase_item(item: dict[str, Any]) -> dict[str, Any]:
    quantity = normalize_number(item.get("cantidad"))
    unit_price = normalize_number(item.get("precio_unitario"))
    subtotal = None
    if quantity is not None and unit_price is not None:
        subtotal = number_to_json(Decimal(str(quantity)) * Decimal(str(unit_price)))
    return {
        "producto": clean_text(item.get("producto")),
        "cantidad": quantity,
        "unidad": clean_text(item.get("unidad")),
        "precio_unitario": unit_price,
        "subtotal_inferido": subtotal,
    }


def validate_structured_data(entry: dict[str, Any]) -> list[dict[str, str]]:
    structured_data = ensure_structured_data(entry)
    if not structured_data:
        return []
    if structured_data["schema_id"] == "purchase.v2":
        return validate_purchase_values(structured_data.get("values", {}))
    return []


def validate_purchase_values(values: dict[str, Any]) -> list[dict[str, str]]:
    missing: list[dict[str, str]] = []
    for name, label in (
        ("fecha_compra", "Fecha de compra"),
        ("proveedor", "Proveedor"),
        ("moneda", "Moneda"),
    ):
        if not clean_text(values.get(name)):
            missing.append({"path": name, "label": label})
    items = values.get("items") if isinstance(values.get("items"), list) else []
    if not items:
        missing.append({"path": "items", "label": "Al menos un item"})
    for index, item in enumerate(items):
        if not clean_text(item.get("producto")):
            missing.append({"path": f"items.{index}.producto", "label": f"Producto del item {index + 1}"})
        if normalize_number(item.get("cantidad")) is None:
            missing.append({"path": f"items.{index}.cantidad", "label": f"Cantidad del item {index + 1}"})
        if not clean_text(item.get("unidad")):
            missing.append({"path": f"items.{index}.unidad", "label": f"Unidad del item {index + 1}"})
    return missing


def migrate_purchase_v1(entry: dict[str, Any], structured_data: dict[str, Any]) -> dict[str, Any]:
    values = normalize_purchase_values(structured_data.get("values", {}))
    migrated = {
        **structured_data,
        "schema_id": "purchase.v2",
        "schema": PURCHASE_SCHEMA,
        "values": values,
        "provenance": structured_data.get("provenance") or {
            "fields": {
                "fecha_compra": "extracted" if values.get("fecha_compra") else "missing",
                "proveedor": "extracted" if values.get("proveedor") else "missing",
                "moneda": "suggested",
                "comprobante": "extracted" if values.get("comprobante") else "missing",
                "descuento": "extracted" if values.get("descuento") else "missing",
                "total_declarado": "extracted" if values.get("total_declarado") is not None else "missing",
            },
            "items": [purchase_item_provenance(item) for item in values.get("items", [])],
        },
    }
    return migrated


def ensure_purchase_v2_shape(structured_data: dict[str, Any], entry: dict[str, Any] | None = None) -> None:
    values = normalize_purchase_values(structured_data.get("values", {}))
    source_text = (entry or {}).get("message") or (entry or {}).get("dry_run", {}).get("input", {}).get("text")
    adjustments = parse_purchase_adjustments(source_text) if source_text else {}
    if values.get("descuento") is None and adjustments.get("descuento"):
        values["descuento"] = adjustments["descuento"]
    if values.get("total_declarado") is None and adjustments.get("total_declarado") is not None:
        values["total_declarado"] = adjustments["total_declarado"]
    structured_data["schema"] = PURCHASE_SCHEMA
    structured_data["values"] = values
    provenance = structured_data.setdefault("provenance", {"fields": {}, "items": []})
    fields = provenance.setdefault("fields", {})
    fields.setdefault("descuento", "extracted" if values.get("descuento") else "missing")
    fields.setdefault(
        "total_declarado",
        "extracted" if values.get("total_declarado") is not None else "missing",
    )
    if adjustments.get("descuento") and fields.get("descuento") == "missing":
        fields["descuento"] = "extracted"
    if adjustments.get("total_declarado") is not None and fields.get("total_declarado") == "missing":
        fields["total_declarado"] = "extracted"


def purchase_item_provenance(item: dict[str, Any]) -> dict[str, str]:
    return {
        "producto": "extracted" if item.get("producto") else "missing",
        "cantidad": "extracted" if item.get("cantidad") is not None else "missing",
        "unidad": "extracted" if item.get("unidad") else "missing",
        "precio_unitario": "extracted" if item.get("precio_unitario") is not None else "missing",
        "subtotal_inferido": "calculated" if item.get("subtotal_inferido") is not None else "missing",
    }


def update_purchase_provenance(
    structured_data: dict[str, Any],
    previous: dict[str, Any],
    current: dict[str, Any],
    source: str,
) -> None:
    provenance = structured_data.setdefault("provenance", {"fields": {}, "items": []})
    fields = provenance.setdefault("fields", {})
    for field in (
        "fecha_compra",
        "proveedor",
        "moneda",
        "comprobante",
        "descuento",
        "total_declarado",
    ):
        if previous.get(field) != current.get(field):
            fields[field] = source
    old_items = previous.get("items", [])
    item_provenance = provenance.setdefault("items", [])
    while len(item_provenance) < len(current.get("items", [])):
        item_provenance.append({})
    del item_provenance[len(current.get("items", [])) :]
    for index, item in enumerate(current.get("items", [])):
        old_item = old_items[index] if index < len(old_items) else {}
        for field in ("producto", "cantidad", "unidad", "precio_unitario"):
            if old_item.get(field) != item.get(field):
                item_provenance[index][field] = source
        item_provenance[index]["subtotal_inferido"] = (
            "calculated" if item.get("subtotal_inferido") is not None else "missing"
        )


def normalize_discount(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    discount_type = clean_text(value.get("tipo"))
    discount_value = normalize_number(value.get("valor"))
    if discount_type not in {"monto", "porcentaje"} or discount_value is None:
        return None
    return {"tipo": discount_type, "valor": discount_value}


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def normalize_number(value: Any) -> int | float | None:
    if value is None or value == "":
        return None
    try:
        number = Decimal(str(value).replace(",", "."))
    except InvalidOperation:
        return None
    return number_to_json(number)


def number_to_json(value: Decimal) -> int | float:
    if value == value.to_integral():
        return int(value)
    return float(value)
