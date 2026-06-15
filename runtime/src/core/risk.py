from __future__ import annotations


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

