#!/usr/bin/env python3
"""Dry-run CLI for the first Granja Luna operational MVP.

The script intentionally uses local rules only. It does not call an LLM, does
not use an agent framework, and does not modify files.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any


DOMAIN_SIGNALS: dict[str, tuple[str, ...]] = {
    "sanidad": (
        "medicamento",
        "enfermedad",
        "sintoma",
        "sintomas",
        "vacuna",
        "aislamiento",
        "tratamiento",
    ),
    "stock-insumos": (
        "bolsa",
        "bolsas",
        "alimento",
        "deposito",
        "stock",
        "insumo",
        "insumos",
        "material",
        "maiz",
        "balanceado",
        "viruta",
        "cascarilla",
    ),
    "compras": (
        "compre",
        "compra",
        "comprar",
        "factura",
        "proveedor",
        "precio",
    ),
    "ventas": (
        "vendi",
        "venta",
        "cliente",
        "cobre",
        "entrega",
    ),
    "incubacion": (
        "incubadora",
        "huevos fertiles",
        "nacimiento",
        "incubar",
    ),
    "infraestructura": (
        "galpon",
        "corral",
        "cerco",
        "construccion",
    ),
    "alimentacion": (
        "racion",
        "consumo",
        "balanceado",
        "maiz",
        "alimento",
    ),
    "reproductores": (
        "gallo",
        "gallina",
        "raza",
        "cruce",
        "reproductor",
    ),
    "tareas-mantenimiento": (
        "hacer",
        "reparar",
        "limpiar",
        "pendiente",
        "revisar",
        "manana",
    ),
    "reportes": (
        "resumen",
        "informe",
        "cuanto",
        "comparar",
    ),
}

NUMBER_WORDS: dict[str, Decimal] = {
    "un": Decimal("1"),
    "una": Decimal("1"),
    "uno": Decimal("1"),
    "dos": Decimal("2"),
    "tres": Decimal("3"),
    "cuatro": Decimal("4"),
    "cinco": Decimal("5"),
    "seis": Decimal("6"),
    "siete": Decimal("7"),
    "ocho": Decimal("8"),
    "nueve": Decimal("9"),
    "diez": Decimal("10"),
}

UNIT_ALIASES: dict[str, str] = {
    "bolsa": "bolsa",
    "bolsas": "bolsa",
    "kg": "kg",
    "kilo": "kg",
    "kilos": "kg",
    "litro": "litro",
    "litros": "litro",
    "lts": "litro",
    "unidad": "unidad",
    "unidades": "unidad",
}


@dataclass(frozen=True)
class ParsedItem:
    product: str
    quantity: Decimal
    unit: str
    unit_price: Decimal | None

    @property
    def subtotal(self) -> Decimal | None:
        if self.unit_price is None:
            return None
        return self.quantity * self.unit_price

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "producto": self.product,
            "cantidad": number_to_json(self.quantity),
            "unidad": self.unit,
        }
        if self.unit_price is not None:
            data["precio_unitario"] = number_to_json(self.unit_price)
            data["subtotal_inferido"] = number_to_json(self.subtotal)
        return data


def strip_accents(value: str) -> str:
    normalized = unicodedata.normalize("NFD", value)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def normalize(value: str) -> str:
    value = strip_accents(value.lower())
    return re.sub(r"\s+", " ", value).strip()


def parse_decimal(raw_value: str) -> Decimal | None:
    value = raw_value.strip().lower()
    if value in NUMBER_WORDS:
        return NUMBER_WORDS[value]
    value = value.replace("gs", "").replace("pyg", "").strip()
    value = value.replace(".", "").replace(",", ".")
    try:
        return Decimal(value)
    except InvalidOperation:
        return None


def number_to_json(value: Decimal | None) -> int | float | None:
    if value is None:
        return None
    if value == value.to_integral():
        return int(value)
    return float(value)


def score_domains(normalized_text: str) -> list[str]:
    scores: list[tuple[int, str]] = []
    for domain, signals in DOMAIN_SIGNALS.items():
        score = sum(1 for signal in signals if signal in normalized_text)
        if score:
            scores.append((score, domain))
    scores.sort(key=lambda item: (-item[0], item[1]))
    return [domain for _, domain in scores]


def detect_intent(normalized_text: str, domains: list[str]) -> str:
    if "compras" in domains:
        return "registrar_compra"
    if "ventas" in domains:
        return "registrar_venta_borrador"
    if "sanidad" in domains:
        return "registrar_evento_sanitario_borrador"
    if "stock-insumos" in domains:
        return "registrar_movimiento_stock_borrador"
    if "tareas-mantenimiento" in domains:
        return "crear_tarea_borrador"
    if "reportes" in domains:
        return "preparar_reporte"
    return "registrar_bitacora_borrador"


def classify(text: str) -> dict[str, Any]:
    normalized_text = normalize(text)
    domains = score_domains(normalized_text)
    primary_domain = domains[0] if domains else "otro"
    secondary_domains = domains[1:]
    intent = detect_intent(normalized_text, domains)
    if intent == "registrar_compra":
        primary_domain = "compras"
        secondary_domains = [domain for domain in domains if domain != "compras"]
    risk_level = evaluate_risk(intent, domains, normalized_text)
    return {
        "intent": intent,
        "primary_domain": primary_domain,
        "secondary_domains": secondary_domains,
        "risk_level": risk_level,
        "information_status": "draft",
        "requires_confirmation": risk_level in {"medio", "alto", "critico"},
    }


def evaluate_risk(intent: str, domains: list[str], normalized_text: str) -> str:
    if any(word in normalized_text for word in ("borrar", "eliminar", "medicar", "dosis")):
        return "critico" if "borrar" in normalized_text or "eliminar" in normalized_text else "alto"
    if "sanidad" in domains:
        return "alto"
    if intent in {"registrar_compra", "registrar_venta_borrador"}:
        return "medio"
    if "stock-insumos" in domains:
        return "medio"
    return "bajo"


def parse_items(text: str) -> list[ParsedItem]:
    normalized_text = normalize(text)
    quantity_pattern = r"(?P<qty>\d+(?:[.,]\d+)?|un|una|uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez)"
    unit_pattern = r"(?P<unit>bolsas?|kg|kilos?|litros?|lts|unidades?|unidad)"
    product_pattern = r"(?P<product>[a-z0-9\s]+?)"
    price_pattern = r"(?:\s+a\s+(?P<price>\d[\d.,]*)(?:\s+cada\s+(?:una|uno|bolsa|unidad))?)?"
    boundary = r"(?=\s+y\s+|\s*,|\s+\.|$)"
    pattern = re.compile(
        rf"{quantity_pattern}\s+{unit_pattern}\s+de\s+{product_pattern}{price_pattern}{boundary}"
    )

    items: list[ParsedItem] = []
    for match in pattern.finditer(normalized_text):
        quantity = parse_decimal(match.group("qty"))
        unit = UNIT_ALIASES.get(match.group("unit"), match.group("unit"))
        product = clean_product(match.group("product"))
        unit_price = parse_decimal(match.group("price")) if match.group("price") else None
        if quantity is None or not product:
            continue
        items.append(
            ParsedItem(
                product=product,
                quantity=quantity,
                unit=unit,
                unit_price=unit_price,
            )
        )
    return items


def clean_product(product: str) -> str:
    product = re.sub(r"\b(cada|una|uno|unidad|bolsa)\b.*$", "", product).strip()
    product = re.sub(r"\s+", " ", product)
    return product.strip(" .,:;")


def purchase_missing_data(items: list[ParsedItem]) -> list[str]:
    missing = [
        "fecha real de compra",
        "proveedor",
        "comprobante o evidencia",
        "confirmacion de impacto en stock",
    ]
    if any(item.unit_price is None for item in items):
        missing.append("precio unitario de cada item")
    if not items:
        missing.extend(["producto/insumo", "cantidad", "unidad"])
    return missing


def build_purchase_draft(items: list[ParsedItem], today: str) -> dict[str, Any] | None:
    if not items:
        return None
    total = sum((item.subtotal for item in items if item.subtotal is not None), Decimal("0"))
    has_full_total = all(item.subtotal is not None for item in items)
    return {
        "estado": "draft",
        "fecha_inferida": today,
        "fecha_real": None,
        "proveedor": None,
        "moneda": "PYG",
        "items": [item.to_dict() for item in items],
        "total_inferido": number_to_json(total) if has_full_total else None,
        "fuente": "conversacion",
        "requiere_confirmacion": True,
    }


def build_stock_movements(items: list[ParsedItem], primary_domain: str) -> list[dict[str, Any]]:
    if not items or primary_domain != "compras":
        return []
    movements: list[dict[str, Any]] = []
    for item in items:
        movements.append(
            {
                "estado": "draft",
                "tipo_movimiento": "entrada",
                "motivo": "compra",
                "producto": item.product,
                "cantidad": number_to_json(item.quantity),
                "unidad": item.unit,
                "origen": "proveedor pendiente",
                "destino": "deposito pendiente",
                "requiere_confirmacion": True,
            }
        )
    return movements


def build_log_entry(text: str, classification: dict[str, Any], today: str) -> dict[str, Any]:
    return {
        "estado": "draft",
        "fecha_inferida": today,
        "dominio_primario": classification["primary_domain"],
        "dominios_secundarios": classification["secondary_domains"],
        "riesgo": classification["risk_level"],
        "fuente": "conversacion",
        "relato": text,
    }


def build_suggested_tasks(text: str, classification: dict[str, Any]) -> list[dict[str, Any]]:
    normalized_text = normalize(text)
    task_signals = ("revisar", "limpiar", "reparar", "pendiente", "hacer", "manana")
    if not any(signal in normalized_text for signal in task_signals):
        return []
    title = text.strip().rstrip(".")
    return [
        {
            "estado": "draft",
            "titulo": title[:90],
            "dominio": classification["primary_domain"],
            "riesgo": classification["risk_level"],
            "proximo_paso": "confirmar si debe pasar a tasks/inbox.md",
            "requiere_confirmacion": classification["requires_confirmation"],
        }
    ]


def build_confirmation(classification: dict[str, Any], items: list[ParsedItem]) -> dict[str, Any]:
    if not classification["requires_confirmation"]:
        return {
            "required": False,
            "question": "No se requiere confirmacion para este dry-run de bajo riesgo.",
        }
    if classification["intent"] == "registrar_compra" and items:
        products = ", ".join(item.product for item in items)
        return {
            "required": True,
            "question": (
                "Confirmas que prepare este borrador de compra y el movimiento de "
                f"stock propuesto para: {products}? No se registrara como hecho real "
                "hasta que lo confirmes explicitamente."
            ),
        }
    return {
        "required": True,
        "question": (
            "Confirmas que esta propuesta debe avanzar como borrador? "
            "No se registrara como hecho real sin confirmacion explicita."
        ),
    }


def build_next_actions(classification: dict[str, Any], missing_data: list[str]) -> list[str]:
    actions = ["revisar datos detectados"]
    if missing_data:
        actions.append("responder datos faltantes")
    if classification["requires_confirmation"]:
        actions.append("confirmar explicitamente antes de registrar hechos operativos")
    return actions


def build_ui_response(
    classification: dict[str, Any],
    detected_data: dict[str, Any],
    missing_data: list[str],
    purchase: dict[str, Any] | None,
    stock_movements: list[dict[str, Any]],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    components: list[dict[str, Any]] = [
        {
            "component": "summary_card",
            "props": {
                "title": "Revision de operacion",
                "body": "Se preparo una propuesta en modo dry-run. No se modificaron datos reales.",
            },
        }
    ]
    if detected_data.get("items"):
        components.append(
            {
                "component": "data_table",
                "props": {
                    "title": "Items detectados",
                    "rows": detected_data["items"],
                },
            }
        )
    if missing_data:
        components.append(
            {
                "component": "checklist",
                "props": {
                    "title": "Datos faltantes",
                    "items": missing_data,
                },
            }
        )
    if purchase:
        components.append(
            {
                "component": "summary_card",
                "props": {
                    "title": "Borrador de compra",
                    "body": "Compra propuesta en estado draft.",
                    "data": purchase,
                },
            }
        )
    if stock_movements:
        components.append(
            {
                "component": "data_table",
                "props": {
                    "title": "Movimientos de stock propuestos",
                    "rows": stock_movements,
                },
            }
        )
    components.append(
        {
            "component": "action_group",
            "props": {
                "actions": [
                    {
                        "id": "confirm",
                        "label": "Confirmar borrador",
                        "requires_confirmation": confirmation["required"],
                    },
                    {
                        "id": "edit",
                        "label": "Corregir datos",
                        "requires_confirmation": False,
                    },
                    {
                        "id": "cancel",
                        "label": "Cancelar",
                        "requires_confirmation": False,
                    },
                ]
            },
        }
    )
    return {
        "schema_version": "0.1",
        "response_type": "review",
        "title": "Revision de Granja Luna",
        "summary": confirmation["question"],
        "risk_level": classification["risk_level"],
        "requires_confirmation": classification["requires_confirmation"],
        "rendering_mode": "host_native",
        "components": components,
        "information_status": {
            "classification": "borrador",
            "detected_data": "inferido",
            "missing_data": "pendiente_validar",
            "drafts": "borrador",
        },
    }


def build_dry_run(text: str, today: str | None = None) -> dict[str, Any]:
    today = today or date.today().isoformat()
    classification = classify(text)
    items = parse_items(text) if classification["intent"] == "registrar_compra" else []
    missing_data = purchase_missing_data(items) if classification["intent"] == "registrar_compra" else []
    purchase = build_purchase_draft(items, today)
    stock_movements = build_stock_movements(items, classification["primary_domain"])
    log_entry = build_log_entry(text, classification, today)
    suggested_tasks = build_suggested_tasks(text, classification)

    detected_data: dict[str, Any] = {
        "texto_original": text,
        "items": [item.to_dict() for item in items],
    }
    if purchase and purchase.get("total_inferido") is not None:
        detected_data["total_inferido"] = purchase["total_inferido"]
        detected_data["moneda"] = "PYG"

    confirmation = build_confirmation(classification, items)
    return {
        "schema_version": "0.1",
        "mode": "dry_run",
        "side_effects": [],
        "input": {
            "text": text,
            "source": "cli",
        },
        "classification": classification,
        "detected_data": detected_data,
        "missing_data": missing_data,
        "drafts": {
            "purchase": purchase,
            "stock_movements": stock_movements,
            "log_entry": log_entry,
        },
        "suggested_tasks": suggested_tasks,
        "confirmation": confirmation,
        "ui_response": build_ui_response(
            classification,
            detected_data,
            missing_data,
            purchase,
            stock_movements,
            confirmation,
        ),
        "next_actions": build_next_actions(classification, missing_data),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Granja Luna dry-run CLI")
    parser.add_argument("message", help="Mensaje natural a analizar")
    parser.add_argument(
        "--today",
        help="Fecha ISO para pruebas o reproduccion. Por defecto usa la fecha local.",
    )
    args = parser.parse_args()
    result = build_dry_run(args.message, today=args.today)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
