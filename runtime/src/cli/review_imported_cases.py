#!/usr/bin/env python3
"""Interactive review CLI for imported Granja Luna learning cases.

The tool records feedback in JSONL and never confirms operational facts.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
import sys
from typing import Any


RUNTIME_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = RUNTIME_DIR / "examples" / "imported-cases-pending-review.json"
DEFAULT_FEEDBACK = RUNTIME_DIR / "examples" / "case-review-feedback.jsonl"

sys.path.insert(0, str(SRC_DIR))

from core.case_review import (  # noqa: E402
    append_feedback,
    expected_snapshot,
    find_case,
    input_digest,
    latest_feedback_by_case,
    load_feedback_entries,
    load_imported_cases,
    runtime_snapshot,
    summarize_reviews,
    truncate,
)
from core.dry_run import build_dry_run  # noqa: E402


INTENTS = (
    "registrar_compra",
    "registrar_movimiento_stock_borrador",
    "analizar_existencias_reposicion",
    "crear_tarea_borrador",
    "registrar_evento_sanitario_borrador",
    "registrar_venta_borrador",
    "preparar_reporte",
    "registrar_bitacora_borrador",
    "analizar_decision_operativa",
    "detectar_workflow_candidato",
    "preguntar_datos_faltantes",
)

DOMAINS = (
    "compras",
    "stock-insumos",
    "alimentacion",
    "sanidad",
    "ventas",
    "incubacion",
    "infraestructura",
    "tareas-mantenimiento",
    "reportes",
    "reproductores",
    "finanzas",
    "otro",
)

RISKS = ("bajo", "medio", "alto", "critico")


def main() -> int:
    parser = argparse.ArgumentParser(description="Review imported Granja Luna learning cases")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Imported cases JSON file")
    parser.add_argument("--feedback", type=Path, default=DEFAULT_FEEDBACK, help="Feedback JSONL file")
    parser.add_argument("--case-id", help="Review or inspect one specific case")
    parser.add_argument("--limit", type=int, default=1, help="Number of cases to review interactively")
    parser.add_argument("--include-reviewed", action="store_true", help="Include cases already reviewed")
    parser.add_argument("--list", action="store_true", help="List cases and review status")
    parser.add_argument("--summary", action="store_true", help="Print feedback summary")
    parser.add_argument("--today", help="ISO date used for runtime dry-run snapshots")
    args = parser.parse_args()

    cases = load_imported_cases(args.input)
    entries = load_feedback_entries(args.feedback)
    latest = latest_feedback_by_case(entries)

    if args.list:
        print_case_list(cases, latest)
        return 0

    if args.summary:
        print(json.dumps(summarize_reviews(cases, entries), ensure_ascii=False, indent=2, sort_keys=True))
        return 0

    selected = select_cases(cases, latest, args.case_id, args.limit, args.include_reviewed)
    if not selected:
        print("No hay casos pendientes con esos filtros.")
        return 0

    for index, case in enumerate(selected, start=1):
        review_case(case, args.feedback, args.today, index, len(selected), latest.get(case["id"]))

    return 0


def print_case_list(cases: list[dict[str, Any]], latest: dict[str, dict[str, Any]]) -> None:
    print("ID | estado_review | decision | fuente | dominio | riesgo | resumen")
    print("---|---|---|---|---|---|---")
    for case in cases:
        expected = expected_snapshot(case)
        feedback = latest.get(case["id"])
        status = "reviewed" if feedback else "pending"
        decision = feedback.get("review_decision", "-") if feedback else "-"
        source = case.get("source", "-")
        print(
            f"{case['id']} | {status} | {decision} | {source} | "
            f"{expected.get('primary_domain')} | {expected.get('risk_level')} | "
            f"{truncate(case.get('input_text', ''), 80)}"
        )


def select_cases(
    cases: list[dict[str, Any]],
    latest: dict[str, dict[str, Any]],
    case_id: str | None,
    limit: int,
    include_reviewed: bool,
) -> list[dict[str, Any]]:
    if case_id:
        return [find_case(cases, case_id)]
    reviewable = [case for case in cases if include_reviewed or case["id"] not in latest]
    return reviewable[: max(limit, 0)]


def review_case(
    case: dict[str, Any],
    feedback_path: Path,
    today: str | None,
    index: int,
    total: int,
    latest: dict[str, Any] | None,
) -> None:
    print("\n" + "=" * 80)
    print(f"Caso {index}/{total}: {case['id']}")
    if latest:
        print(f"Ultima revision: {latest.get('reviewed_at')} / {latest.get('review_decision')}")

    expected = expected_snapshot(case)
    result = build_dry_run(case["input_text"], today=today)
    current = runtime_snapshot(result)

    print("\nEntrada:")
    print(case["input_text"])
    print("\nEsperado importado:")
    print(json.dumps(expected, ensure_ascii=False, indent=2, sort_keys=True))
    print("\nRuntime actual:")
    print(json.dumps(current, ensure_ascii=False, indent=2, sort_keys=True))

    decision = prompt_choice(
        "\nDecision",
        {
            "p": "promote_to_learning_dataset",
            "k": "keep_pending",
            "e": "needs_edit",
            "d": "discard",
            "s": "skip",
        },
        default="k",
    )
    if decision == "skip":
        print("Saltado sin guardar feedback.")
        return

    text_judgment = prompt_choice(
        "El texto representa una entrada util?",
        {
            "s": "representative",
            "e": "needs_text_edit",
            "n": "not_representative",
            "?": "unsure",
        },
        default="s",
    )
    expected_judgment = prompt_choice(
        "La salida esperada importada esta bien?",
        {
            "s": "accepted",
            "c": "corrected",
            "?": "unsure",
        },
        default="s",
    )

    corrected_expected = {}
    if expected_judgment == "corrected":
        corrected_expected = prompt_corrections(expected)

    operational_follow_up = prompt_bool(
        "Esto necesita revisarse aparte como posible hecho operativo? "
        "(no se confirma ni registra desde este CLI)",
        default=False,
    )
    notes = input("Notas libres (enter para omitir): ").strip()

    entry = {
        "schema_version": 1,
        "reviewed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "case_id": case["id"],
        "source": case.get("source"),
        "case_kind": case.get("case_kind"),
        "input_digest": input_digest(case),
        "review_decision": decision,
        "text_judgment": text_judgment,
        "expected_judgment": expected_judgment,
        "corrected_expected": corrected_expected,
        "operational_follow_up": operational_follow_up,
        "operational_fact_status": "not_confirmed_in_feedback",
        "notes": notes,
        "expected_snapshot": expected,
        "runtime_snapshot": current,
    }
    append_feedback(feedback_path, entry)
    print(f"Feedback guardado en {feedback_path}")


def prompt_choice(prompt: str, options: dict[str, str], default: str) -> str:
    labels = ", ".join(f"{key}={value}" for key, value in options.items())
    while True:
        answer = input(f"{prompt} [{labels}] default={default}: ").strip().lower()
        if not answer:
            answer = default
        if answer in options:
            return options[answer]
        print("Opcion no valida.")


def prompt_bool(prompt: str, default: bool) -> bool:
    default_label = "s" if default else "n"
    while True:
        answer = input(f"{prompt} [s/n] default={default_label}: ").strip().lower()
        if not answer:
            return default
        if answer in {"s", "si", "y", "yes"}:
            return True
        if answer in {"n", "no"}:
            return False
        print("Responde s o n.")


def prompt_corrections(expected: dict[str, Any]) -> dict[str, Any]:
    print("\nValores validos:")
    print("intenciones:", ", ".join(INTENTS))
    print("dominios:", ", ".join(DOMAINS))
    print("riesgos:", ", ".join(RISKS))
    intent = prompt_optional_value("Intent corregida", expected.get("intent"), INTENTS)
    primary_domain = prompt_optional_value("Dominio principal corregido", expected.get("primary_domain"), DOMAINS)
    risk_level = prompt_optional_value("Riesgo corregido", expected.get("risk_level"), RISKS)
    requires_confirmation = prompt_bool(
        "Requiere confirmacion?",
        default=bool(expected.get("requires_confirmation")),
    )
    return {
        "intent": intent,
        "primary_domain": primary_domain,
        "risk_level": risk_level,
        "requires_confirmation": requires_confirmation,
    }


def prompt_optional_value(prompt: str, current: str | None, allowed: tuple[str, ...]) -> str | None:
    while True:
        answer = input(f"{prompt} default={current}: ").strip()
        if not answer:
            return current
        if answer in allowed:
            return answer
        print("Valor no valido.")


if __name__ == "__main__":
    raise SystemExit(main())
