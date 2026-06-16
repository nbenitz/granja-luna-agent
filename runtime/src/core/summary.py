from __future__ import annotations

from typing import Any


def format_summary(result: dict[str, Any]) -> str:
    classification = result["classification"]
    lines: list[str] = [
        "Granja Luna dry-run",
        "",
        f"Intencion: {classification['intent']}",
        f"Dominio principal: {classification['primary_domain']}",
    ]

    secondary_domains = classification.get("secondary_domains", [])
    if secondary_domains:
        lines.append(f"Dominios secundarios: {', '.join(secondary_domains)}")
    lines.append(
        "Riesgo: "
        f"{classification['risk_level']} | "
        f"Confirmacion requerida: {yes_no(classification['requires_confirmation'])} | "
        f"Confianza: {classification.get('confidence', 'n/a')}"
    )

    append_matched_signals(lines, classification.get("matched_signals", {}))
    append_detected_items(lines, result["detected_data"].get("items", []))
    append_inventory_observations(lines, result["detected_data"].get("stock_observations", []))
    append_purchase(lines, result["drafts"].get("purchase"))
    append_stock_movements(lines, result["drafts"].get("stock_movements", []))
    append_suggested_tasks(lines, result.get("suggested_tasks", []))
    append_missing_data(lines, result.get("missing_data", []))

    confirmation = result.get("confirmation")
    if confirmation:
        lines.extend(["", "Confirmacion:", f"- {confirmation['question']}"])

    next_actions = result.get("next_actions", [])
    if next_actions:
        lines.append("")
        lines.append("Proximas acciones:")
        lines.extend(f"- {action}" for action in next_actions)

    lines.extend(["", "Nota: no se modificaron datos reales. side_effects: []"])
    return "\n".join(lines)


def append_matched_signals(lines: list[str], matched_signals: dict[str, list[str]]) -> None:
    if not matched_signals:
        return
    lines.append("")
    lines.append("Senales detectadas:")
    for domain, signals in matched_signals.items():
        lines.append(f"- {domain}: {', '.join(signals)}")


def append_detected_items(lines: list[str], items: list[dict[str, Any]]) -> None:
    if not items:
        return
    lines.append("")
    lines.append("Items detectados:")
    for item in items:
        parts = [
            item.get("producto", "producto pendiente"),
            f"{item.get('cantidad')} {item.get('unidad')}",
        ]
        if item.get("precio_unitario") is not None:
            parts.append(f"precio unitario {item['precio_unitario']}")
        if item.get("subtotal_inferido") is not None:
            parts.append(f"subtotal inferido {item['subtotal_inferido']}")
        lines.append(f"- {' | '.join(parts)}")


def append_inventory_observations(lines: list[str], observations: list[dict[str, Any]]) -> None:
    if not observations:
        return
    lines.append("")
    lines.append("Existencias detectadas (pending_review):")
    for observation in observations:
        details = [
            f"{observation.get('producto', 'producto pendiente')}",
            f"{observation.get('bolsas_estimadas_restantes')} bolsa(s) estimada(s)",
        ]
        if observation.get("porcentaje_restante_inferido") is not None:
            details.append(f"{observation['porcentaje_restante_inferido']}% restante")
        if observation.get("kg_estimados_restantes") is not None:
            details.append(f"{observation['kg_estimados_restantes']} kg estimados")
        lines.append(f"- {' | '.join(details)}")


def append_purchase(lines: list[str], purchase: dict[str, Any] | None) -> None:
    if not purchase:
        return
    lines.append("")
    lines.append("Borrador de compra:")
    if purchase.get("total_inferido") is not None:
        lines.append(f"- Total inferido: {purchase['total_inferido']} {purchase.get('moneda', '')}".strip())
    lines.append("- Estado: draft")


def append_stock_movements(lines: list[str], movements: list[dict[str, Any]]) -> None:
    if not movements:
        return
    lines.append("")
    lines.append("Movimientos de stock propuestos:")
    for movement in movements:
        lines.append(
            "- "
            f"{movement.get('tipo_movimiento')} "
            f"{movement.get('cantidad')} {movement.get('unidad')} "
            f"de {movement.get('producto')}"
        )


def append_suggested_tasks(lines: list[str], tasks: list[dict[str, Any]]) -> None:
    if not tasks:
        return
    lines.append("")
    lines.append("Tareas sugeridas:")
    for task in tasks:
        lines.append(f"- {task.get('titulo')} ({task.get('estado')})")


def append_missing_data(lines: list[str], missing_data: list[str]) -> None:
    if not missing_data:
        return
    lines.append("")
    lines.append("Datos faltantes:")
    lines.extend(f"- {item}" for item in missing_data)


def yes_no(value: bool) -> str:
    return "si" if value else "no"
