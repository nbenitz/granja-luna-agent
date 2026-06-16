from __future__ import annotations


def evaluate_risk(intent: str, domains: list[str], normalized_text: str) -> str:
    if any(word in normalized_text for word in ("borrar", "eliminar")):
        return "critico"
    if "sanidad" in domains and has_critical_sanitary_marker(normalized_text):
        return "critico"
    if "sanidad" in domains:
        return "alto"
    if intent == "detectar_workflow_candidato":
        if "infraestructura" in domains and any(marker in normalized_text for marker in ("cerco", "divisoria")):
            return "medio"
        return "bajo"
    if intent == "analizar_decision_operativa":
        if has_high_risk_reproductive_plan(normalized_text):
            return "alto"
        if "reproductores" in domains or "infraestructura" in domains:
            return "medio"
    if intent in {"registrar_compra", "registrar_venta_borrador", "analizar_existencias_reposicion"}:
        return "medio"
    if "stock-insumos" in domains:
        return "medio"
    return "bajo"


def has_critical_sanitary_marker(normalized_text: str) -> bool:
    markers = (
        "le acabo de dar",
        "le puse",
        "aplique",
        "administre",
        "medique",
        "como suministrar",
        "indicaciones",
        "que dosis",
        "dosis",
        "medicar",
        "debiles",
        "debil",
        "flacas",
        "engripadas",
        "sintomas",
    )
    return any(marker in normalized_text for marker in markers)


def has_high_risk_reproductive_plan(normalized_text: str) -> bool:
    markers = (
        "plan black star",
        "500 black star",
        "retirar gallos",
        "incubar escalonado",
        "incubacion escalonada",
        "mantener la linea pura",
        "mantener línea pura",
    )
    return any(marker in normalized_text for marker in markers)
