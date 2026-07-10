from __future__ import annotations

from datetime import date
from typing import Any

from core.builders import (
    build_confirmation,
    build_log_entry,
    build_next_actions,
    build_purchase_draft,
    build_stock_movements,
    build_suggested_tasks,
    build_ui_response,
    egg_collection_missing_data,
    incubation_log_missing_data,
    operational_decision_missing_data,
    purchase_missing_data,
    report_missing_data,
    sanitary_missing_data,
    stock_movement_missing_data,
    stock_analysis_missing_data,
    task_missing_data,
    workflow_candidate_missing_data,
)
from core.classifier import classify
from core.context import build_analysis_text, normalize_context
from core.parsing import (
    parse_egg_collection,
    parse_items,
    parse_purchase_adjustments,
    parse_purchase_date,
    parse_stock_observations,
)


def build_dry_run(
    text: str,
    today: str | None = None,
    context: str | dict[str, Any] | None = None,
) -> dict[str, Any]:
    today = today or date.today().isoformat()
    context_payload = normalize_context(context)
    analysis_text = build_analysis_text(text, context_payload)
    classification = classify(analysis_text)
    items = parse_items(text) if classification["intent"] == "registrar_compra" else []
    purchase_date = parse_purchase_date(text, today) if classification["intent"] == "registrar_compra" else None
    purchase_adjustments = (
        parse_purchase_adjustments(text) if classification["intent"] == "registrar_compra" else {}
    )
    stock_observations = (
        parse_stock_observations(text)
        if classification["intent"] in {"analizar_existencias_reposicion", "registrar_movimiento_stock_borrador"}
        else []
    )
    egg_collection = (
        parse_egg_collection(text, today)
        if classification["intent"] == "registrar_recoleccion_huevos"
        else None
    )
    if classification["intent"] == "registrar_compra":
        missing_data = purchase_missing_data(items)
    elif classification["intent"] == "preparar_reporte":
        missing_data = report_missing_data()
    elif classification["intent"] == "analizar_existencias_reposicion":
        missing_data = stock_analysis_missing_data()
    elif classification["intent"] == "registrar_recoleccion_huevos":
        missing_data = egg_collection_missing_data(egg_collection or {})
    elif classification["primary_domain"] == "sanidad":
        missing_data = sanitary_missing_data(classification["intent"])
    elif classification["intent"] == "registrar_bitacora_borrador" and classification["primary_domain"] == "incubacion":
        missing_data = incubation_log_missing_data()
    elif classification["intent"] == "detectar_workflow_candidato":
        missing_data = workflow_candidate_missing_data(classification["primary_domain"])
    elif classification["intent"] == "analizar_decision_operativa":
        missing_data = operational_decision_missing_data(
            classification["primary_domain"],
            classification["risk_level"],
        )
    elif classification["intent"] == "registrar_movimiento_stock_borrador":
        missing_data = stock_movement_missing_data(
            classification["primary_domain"],
            classification["secondary_domains"],
        )
    elif classification["intent"] == "crear_tarea_borrador":
        missing_data = task_missing_data(classification["primary_domain"])
    else:
        missing_data = []
    purchase = build_purchase_draft(items, today, purchase_date, purchase_adjustments)
    stock_movements = build_stock_movements(items, classification["primary_domain"])
    log_entry = build_log_entry(text, classification, today)
    suggested_tasks = build_suggested_tasks(text, classification)

    detected_data: dict[str, Any] = {
        "texto_original": text,
        "context_used": context_payload is not None,
        "items": [item.to_dict() for item in items],
        "stock_observations": stock_observations,
    }
    if egg_collection:
        detected_data["egg_collection"] = egg_collection
    if purchase and purchase.get("total_inferido") is not None:
        detected_data["total_inferido"] = purchase["total_inferido"]
        detected_data["moneda"] = "PYG"
    if purchase and purchase.get("descuento"):
        detected_data["descuento"] = purchase["descuento"]
    if purchase and purchase.get("total_declarado") is not None:
        detected_data["total_declarado"] = purchase["total_declarado"]

    confirmation = build_confirmation(classification, items, egg_collection)
    input_payload: dict[str, Any] = {
        "text": text,
        "source": "cli",
    }
    if context_payload:
        input_payload["context"] = context_payload
    return {
        "schema_version": "0.1",
        "mode": "dry_run",
        "side_effects": [],
        "input": input_payload,
        "classification": classification,
        "detected_data": detected_data,
        "missing_data": missing_data,
        "drafts": {
            "purchase": purchase,
            "stock_movements": stock_movements,
            "inventory_observations": stock_observations,
            "egg_collection": egg_collection,
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
            egg_collection,
        ),
        "next_actions": build_next_actions(classification, missing_data),
    }
