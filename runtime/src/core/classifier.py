from __future__ import annotations

import re
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
        "medicar",
        "dosis",
        "antiparasitario",
        "ivermectina",
        "iverm",
        "iverm avicola",
        "oxyclina",
        "oximed",
        "oxitetraciclina",
        "antibiotico",
        "vitaminado",
        "debiles",
        "debil",
        "flacas",
        "engripadas",
        "parasitos",
        "suministrar",
        "indicaciones",
    ),
    "stock-insumos": (
        "bolsa",
        "bolsas",
        "alimento",
        "deposito",
        "depósito",
        "stock",
        "insumo",
        "insumos",
        "material",
        "maiz",
        "balanceado",
        "balanceados",
        "viruta",
        "cascarilla",
        "ivermectina",
        "iverm",
        "oxyclina",
        "oximed",
        "antibiotico",
        "vitaminado",
        "existencias",
        "tengo",
        "tenemos",
        "quedan",
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
        "huevo",
        "huevos",
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
        "comida",
        "comedero",
        "agua",
    ),
    "reproductores": (
        "gallo",
        "gallina",
        "gallinas",
        "aves",
        "barrados",
        "ponedoras",
        "raza",
        "cruce",
        "reproductor",
    ),
    "tareas-mantenimiento": (
        "hacer",
        "mejorar",
        "reparar",
        "limpiar",
        "pendiente",
        "revisar",
        "manana",
        "plato",
        "comedero",
    ),
    "reportes": (
        "resumen",
        "informe",
        "cuanto",
        "cuantos",
        "cuántos",
        "comparar",
        "hasta cuando",
        "hasta cuándo",
        "durar",
        "duracion",
        "duración",
    ),
}


def match_domain_signals(normalized_text: str) -> dict[str, list[str]]:
    matched: dict[str, list[str]] = {}
    for domain, signals in DOMAIN_SIGNALS.items():
        domain_matches = [signal for signal in signals if signal_matches(normalized_text, signal)]
        if domain_matches:
            matched[domain] = domain_matches
    return matched


def signal_matches(normalized_text: str, signal: str) -> bool:
    pattern = rf"(?<!\w){re.escape(signal)}(?!\w)"
    return re.search(pattern, normalized_text) is not None


def score_domains(normalized_text: str) -> list[str]:
    matched = match_domain_signals(normalized_text)
    scores: list[tuple[int, str]] = []
    for domain, signals in matched.items():
        scores.append((len(signals), domain))
    scores.sort(key=lambda item: (-item[0], item[1]))
    return [domain for _, domain in scores]


def build_domain_scores(matched_signals: dict[str, list[str]]) -> dict[str, int]:
    return {domain: len(signals) for domain, signals in matched_signals.items()}


def detect_intent(normalized_text: str, domains: list[str]) -> str:
    if is_stock_replenishment_question(normalized_text, domains):
        return "analizar_existencias_reposicion"
    if "sanidad" in domains:
        if is_sanitary_applied_event(normalized_text):
            return "registrar_evento_sanitario_borrador"
        if is_sanitary_missing_data_question(normalized_text):
            return "preguntar_datos_faltantes"
        if is_sanitary_decision_question(normalized_text):
            return "analizar_decision_operativa"
        return "registrar_evento_sanitario_borrador"
    if "compras" in domains:
        return "registrar_compra"
    if "ventas" in domains:
        return "registrar_venta_borrador"
    if "stock-insumos" in domains:
        return "registrar_movimiento_stock_borrador"
    if "tareas-mantenimiento" in domains:
        return "crear_tarea_borrador"
    if "reportes" in domains:
        return "preparar_reporte"
    return "registrar_bitacora_borrador"


def is_stock_replenishment_question(normalized_text: str, domains: list[str]) -> bool:
    if "stock-insumos" not in domains:
        return False
    review_markers = (
        "existencias",
        "cuantos",
        "cuántos",
        "tengo",
        "tenemos",
        "quedan",
        "deposito",
        "depósito",
    )
    planning_markers = (
        "hasta cuando",
        "hasta cuándo",
        "durar",
        "faltar",
        "que debo comprar",
        "qué debo comprar",
        "comprar minimamente",
        "comprar mínimamente",
    )
    return any(marker in normalized_text for marker in review_markers) and any(
        marker in normalized_text for marker in planning_markers
    )


def is_sanitary_applied_event(normalized_text: str) -> bool:
    applied_markers = (
        "le acabo de dar",
        "le di",
        "les di",
        "le puse",
        "les puse",
        "aplique",
        "aplicamos",
        "administre",
        "administramos",
        "medique",
    )
    return any(marker in normalized_text for marker in applied_markers)


def is_sanitary_missing_data_question(normalized_text: str) -> bool:
    question_markers = (
        "indicaciones",
        "como suministrar",
        "como se suministra",
        "como dar",
        "como aplicar",
        "que dosis",
        "cuanta dosis",
        "cuanto tengo que dar",
    )
    return any(marker in normalized_text for marker in question_markers)


def is_sanitary_decision_question(normalized_text: str) -> bool:
    decision_markers = (
        "que me conviene",
        "que recomiendas",
        "me recomiendas",
        "le puedo dar",
        "les puedo dar",
        "puedo dar",
        "puedo usar",
        "en que orden",
        "primero",
        "despues",
    )
    return any(marker in normalized_text for marker in decision_markers)


def classify(text: str) -> dict[str, Any]:
    normalized_text = normalize(text)
    matched_signals = match_domain_signals(normalized_text)
    domain_scores = build_domain_scores(matched_signals)
    domains = score_domains(normalized_text)
    primary_domain = domains[0] if domains else "otro"
    secondary_domains = domains[1:]
    intent = detect_intent(normalized_text, domains)
    if intent == "registrar_compra":
        primary_domain = "compras"
        secondary_domains = [domain for domain in domains if domain != "compras"]
    if intent == "analizar_existencias_reposicion":
        primary_domain = "stock-insumos"
        secondary_domains = [domain for domain in domains if domain != "stock-insumos"]
    if intent in {
        "registrar_evento_sanitario_borrador",
        "analizar_decision_operativa",
        "preguntar_datos_faltantes",
    } and "sanidad" in domains:
        primary_domain = "sanidad"
        secondary_domains = [domain for domain in domains if domain != "sanidad"]
    risk_level = evaluate_risk(intent, domains, normalized_text)
    return {
        "intent": intent,
        "primary_domain": primary_domain,
        "secondary_domains": secondary_domains,
        "risk_level": risk_level,
        "information_status": "draft",
        "requires_confirmation": risk_level in {"medio", "alto", "critico"},
        "matched_signals": matched_signals,
        "domain_scores": domain_scores,
        "confidence": estimate_confidence(intent, primary_domain, domain_scores),
    }


def estimate_confidence(intent: str, primary_domain: str, domain_scores: dict[str, int]) -> str:
    if primary_domain == "otro" or not domain_scores:
        return "low"
    if intent == "registrar_compra" and domain_scores.get("compras", 0) >= 1:
        return "medium"
    primary_score = domain_scores.get(primary_domain, 0)
    if primary_score >= 2:
        return "medium"
    return "low"
