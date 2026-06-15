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
    purchase_missing_data,
)
from core.classifier import classify
from core.parsing import parse_items


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

