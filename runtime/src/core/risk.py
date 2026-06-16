from __future__ import annotations


def evaluate_risk(intent: str, domains: list[str], normalized_text: str) -> str:
    if any(word in normalized_text for word in ("borrar", "eliminar")):
        return "critico"
    if "sanidad" in domains and has_critical_sanitary_marker(normalized_text):
        return "critico"
    if "sanidad" in domains:
        return "alto"
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
