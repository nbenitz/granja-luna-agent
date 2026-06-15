from __future__ import annotations

from typing import Any

from core.risk import evaluate_risk
from core.text import normalize


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

