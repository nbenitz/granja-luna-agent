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
    operational_decision_missing_data,
    purchase_missing_data,
    sanitary_missing_data,
    stock_movement_missing_data,
    stock_analysis_missing_data,
    workflow_candidate_missing_data,
)
from core.classifier import classify
from core.parsing import parse_items, parse_stock_observations


def build_dry_run(text: str, today: str | None = None) -> dict[str, Any]:
    today = today or date.today().isoformat()
    classification = classify(text)
    items = parse_items(text) if classification["intent"] == "registrar_compra" else []
    stock_observations = (
        parse_stock_observations(text)
        if classification["intent"] in {"analizar_existencias_reposicion", "registrar_movimiento_stock_borrador"}
        else []
    )
    if classification["intent"] == "registrar_compra":
        missing_data = purchase_missing_data(items)
    elif classification["intent"] == "analizar_existencias_reposicion":
        missing_data = stock_analysis_missing_data()
    elif classification["primary_domain"] == "sanidad":
        missing_data = sanitary_missing_data(classification["intent"])
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
    else:
        missing_data = []
    purchase = build_purchase_draft(items, today)
    stock_movements = build_stock_movements(items, classification["primary_domain"])
    log_entry = build_log_entry(text, classification, today)
    suggested_tasks = build_suggested_tasks(text, classification)

    detected_data: dict[str, Any] = {
        "texto_original": text,
        "items": [item.to_dict() for item in items],
        "stock_observations": stock_observations,
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
            "inventory_observations": stock_observations,
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
