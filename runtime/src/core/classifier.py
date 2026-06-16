from __future__ import annotations

import re
from typing import Any

from core.risk import evaluate_risk
from core.text import normalize


DOMAIN_SIGNALS: dict[str, tuple[str, ...]] = {
    "sanidad": (
        "medicamento",
        "medicamentos",
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
        "sanidad",
        "sanitarios",
        "desinfectar",
        "desinfectar",
        "desinfeccion",
        "desinfección",
        "gentamicina",
        "bolo",
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
        "materiales",
        "productos",
        "producto",
        "referencias",
        "fotos",
        "maiz",
        "balanceado",
        "balanceados",
        "alimentos",
        "alimenticios",
        "vitaminas",
        "vinagre",
        "ajo",
        "cebolla",
        "viruta",
        "cascarilla",
        "creolina",
        "cal",
        "inventario",
        "alta",
        "baja",
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
        "vender",
        "venta",
        "cliente",
        "clientes",
        "pollitos",
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
        "incubacion",
        "incubación",
        "incubaciones",
        "escalonado",
        "escalonada",
        "clavo",
        "olor",
    ),
    "infraestructura": (
        "galpon",
        "galpón",
        "galpones",
        "galpónes",
        "corral",
        "cerco",
        "divisoria",
        "mandioca",
        "bambu",
        "bambú",
        "travesanos",
        "travesaños",
        "construccion",
        "construcción",
        "infraestructura",
        "listos",
        "perchas",
        "leghorn",
        "triangulo",
        "triángulo",
        "isosceles",
        "isósceles",
        "drenaje",
        "inclinacion",
        "inclinación",
    ),
    "alimentacion": (
        "racion",
        "consumo",
        "forraje",
        "forrajes",
        "fvh",
        "hidroponico",
        "hidropónico",
        "riego",
        "riegos",
        "secando",
        "secan",
        "bandeja",
        "bandejas",
        "balanceado",
        "maiz",
        "alimento",
        "alimentos",
        "alimenticios",
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
        "razas",
        "cruce",
        "cruces",
        "reproductor",
        "reproductores",
        "criadero",
        "rhode",
        "brahma",
        "sussex",
        "plymouth",
        "black star",
        "doble proposito",
        "doble propósito",
        "linea",
        "línea",
        "color",
        "colores",
        "verdosos",
        "celestes",
        "azulados",
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
        "mantenimiento",
        "cama",
        "cambiamos",
        "usamos",
        "agujeros",
        "perforando",
        "perforar",
    ),
    "reportes": (
        "resumen",
        "informe",
        "mostrame",
        "mostrar",
        "reporte",
        "tratamientos",
        "mes",
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
    "finanzas": (
        "adquirir",
        "valga",
        "valor",
        "costo",
        "costos",
        "presupuesto",
        "mercado",
        "plata mia",
        "plata mía",
        "gastos",
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
    if signal == "cuanto" and re.search(r"\ben cuanto a\b", normalized_text):
        return False
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
    if is_report_request(normalized_text, domains):
        return "preparar_reporte"
    if is_stock_replenishment_question(normalized_text, domains):
        return "analizar_existencias_reposicion"
    if is_sanitary_inventory_update(normalized_text, domains):
        return "registrar_movimiento_stock_borrador"
    if is_workflow_candidate(normalized_text, domains):
        return "detectar_workflow_candidato"
    if is_maintenance_stock_usage(normalized_text, domains):
        return "registrar_movimiento_stock_borrador"
    if is_forage_decision(normalized_text, domains):
        return "analizar_decision_operativa"
    if is_forage_task(normalized_text, domains):
        return "crear_tarea_borrador"
    if is_egg_color_observation(normalized_text, domains):
        return "registrar_bitacora_borrador"
    if is_incubation_log(normalized_text, domains):
        return "registrar_bitacora_borrador"
    if is_infrastructure_task(normalized_text, domains):
        return "crear_tarea_borrador"
    if "sanidad" in domains:
        if is_sanitary_applied_event(normalized_text):
            return "registrar_evento_sanitario_borrador"
        if is_sanitary_missing_data_question(normalized_text):
            return "preguntar_datos_faltantes"
        if is_sanitary_decision_question(normalized_text):
            return "analizar_decision_operativa"
        return "registrar_evento_sanitario_borrador"
    if is_operational_decision(normalized_text, domains):
        return "analizar_decision_operativa"
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


def is_report_request(normalized_text: str, domains: list[str]) -> bool:
    report_markers = ("mostrame", "mostrar", "reporte", "informe", "resumen")
    period_markers = ("este mes", "mes", "semana", "hoy")
    if not any(marker in normalized_text for marker in report_markers):
        return False
    return "reportes" in domains or any(marker in normalized_text for marker in period_markers)


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


def is_sanitary_inventory_update(normalized_text: str, domains: list[str]) -> bool:
    if not {"sanidad", "stock-insumos"}.issubset(set(domains)):
        return False
    inventory_markers = (
        "inventario",
        "productos de sanidad",
        "producto de sanidad",
        "registrar productos",
        "registra gentamicina",
        "registra iverm",
        "producto que compre",
        "producto que compré",
    )
    return any(marker in normalized_text for marker in inventory_markers)


def is_maintenance_stock_usage(normalized_text: str, domains: list[str]) -> bool:
    if not {"stock-insumos", "tareas-mantenimiento"}.issubset(set(domains)):
        return False
    maintenance_markers = ("cambiamos la cama", "cambiar la cama", "mantenimiento de cama", "usamos una bolsa")
    stock_markers = ("cascarilla", "viruta", "cal")
    return any(marker in normalized_text for marker in maintenance_markers) and any(
        marker in normalized_text for marker in stock_markers
    )


def is_forage_decision(normalized_text: str, domains: list[str]) -> bool:
    if "alimentacion" not in domains:
        return False
    forage_markers = ("forraje verde hidroponico", "forraje verde hidropónico", "fvh", "bandejas de forraje")
    decision_markers = ("ciclos de riego", "secando", "se secan", "riego")
    return any(marker in normalized_text for marker in forage_markers) and any(
        marker in normalized_text for marker in decision_markers
    )


def is_forage_task(normalized_text: str, domains: list[str]) -> bool:
    if "alimentacion" not in domains:
        return False
    forage_markers = ("forraje", "forrajes", "bandeja", "tupper")
    task_markers = ("agujeros", "perforando", "perforar", "drenaje", "agua no se tranque")
    return any(marker in normalized_text for marker in forage_markers) and any(
        marker in normalized_text for marker in task_markers
    )


def is_egg_color_observation(normalized_text: str, domains: list[str]) -> bool:
    if "reproductores" not in domains:
        return False
    egg_markers = ("huevo", "huevos")
    color_markers = ("color", "colores", "verdoso", "verdosos", "celeste", "celestes", "azulado", "azulados")
    return any(marker in normalized_text for marker in egg_markers) and any(
        marker in normalized_text for marker in color_markers
    )


def is_incubation_log(normalized_text: str, domains: list[str]) -> bool:
    if "incubacion" not in domains:
        return False
    incubator_markers = ("incubadora", "incubar", "incubacion", "incubación")
    log_markers = ("anota", "anotá", "puse", "cargue", "cargué", "huevos")
    return any(marker in normalized_text for marker in incubator_markers) and any(
        marker in normalized_text for marker in log_markers
    )


def is_infrastructure_task(normalized_text: str, domains: list[str]) -> bool:
    if "infraestructura" not in domains:
        return False
    task_markers = ("estoy armando", "armando", "construccion", "construcción", "perchas")
    return any(marker in normalized_text for marker in task_markers)


def is_workflow_candidate(normalized_text: str, domains: list[str]) -> bool:
    workflow_markers = (
        "proyecto",
        "modulo",
        "módulo",
        "nomenclatura",
        "ecosistema",
        "se tiene que poder",
        "forma de actualizar",
        "dar de alta y baja",
        "idea para la granja",
        "gestion de fotos",
        "gestión de fotos",
        "referencias de medicamentos",
        "compartir con clientes",
    )
    if not any(marker in normalized_text for marker in workflow_markers):
        return False
    return any(domain in domains for domain in ("stock-insumos", "infraestructura", "tareas-mantenimiento", "ventas"))


def is_operational_decision(normalized_text: str, domains: list[str]) -> bool:
    decision_markers = (
        "comparativa",
        "versus",
        "conviene",
        "vale la pena",
        "quiero avanzar con el plan",
        "plan black star",
        "meta a futuro",
        "objetivo",
        "doble proposito",
        "doble propósito",
        "no me viene bien",
        "no conviene",
        "todavia estoy en fase",
        "todavía estoy en fase",
        "galpones para todos",
    )
    if not any(marker in normalized_text for marker in decision_markers):
        return False
    return any(domain in domains for domain in ("reproductores", "infraestructura", "ventas", "finanzas"))


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
    if intent == "detectar_workflow_candidato":
        primary_domain = choose_workflow_primary_domain(domains)
        secondary_domains = [domain for domain in domains if domain != primary_domain]
    if intent == "analizar_decision_operativa" and "sanidad" not in domains:
        primary_domain = choose_decision_primary_domain(domains)
        secondary_domains = [domain for domain in domains if domain != primary_domain]
    if intent in {
        "registrar_evento_sanitario_borrador",
        "analizar_decision_operativa",
        "preguntar_datos_faltantes",
    } and "sanidad" in domains:
        primary_domain = "sanidad"
        secondary_domains = [domain for domain in domains if domain != "sanidad"]
    if intent == "registrar_movimiento_stock_borrador" and "sanidad" in domains and "stock-insumos" in domains:
        primary_domain = "stock-insumos"
        secondary_domains = [domain for domain in domains if domain != "stock-insumos"]
    if intent == "registrar_movimiento_stock_borrador" and is_maintenance_stock_usage(normalized_text, domains):
        primary_domain = "tareas-mantenimiento"
        secondary_domains = [domain for domain in domains if domain != "tareas-mantenimiento"]
    if intent == "crear_tarea_borrador" and is_forage_task(normalized_text, domains):
        primary_domain = "alimentacion"
        secondary_domains = [domain for domain in domains if domain != "alimentacion"]
    if intent == "crear_tarea_borrador" and is_infrastructure_task(normalized_text, domains):
        primary_domain = "infraestructura"
        secondary_domains = [domain for domain in domains if domain != "infraestructura"]
    if intent == "registrar_bitacora_borrador" and is_egg_color_observation(normalized_text, domains):
        primary_domain = "reproductores"
        secondary_domains = [domain for domain in domains if domain != "reproductores"]
    if intent == "registrar_bitacora_borrador" and is_incubation_log(normalized_text, domains):
        primary_domain = "incubacion"
        secondary_domains = [domain for domain in domains if domain != "incubacion"]
    if intent == "preparar_reporte":
        primary_domain = "reportes"
        secondary_domains = [domain for domain in domains if domain != "reportes"]
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


def choose_workflow_primary_domain(domains: list[str]) -> str:
    for preferred in ("ventas", "stock-insumos", "infraestructura", "tareas-mantenimiento"):
        if preferred in domains:
            return preferred
    return domains[0] if domains else "otro"


def choose_decision_primary_domain(domains: list[str]) -> str:
    for preferred in ("infraestructura", "reproductores", "alimentacion", "stock-insumos"):
        if preferred in domains:
            return preferred
    return domains[0] if domains else "otro"


def estimate_confidence(intent: str, primary_domain: str, domain_scores: dict[str, int]) -> str:
    if primary_domain == "otro" or not domain_scores:
        return "low"
    if intent == "registrar_compra" and domain_scores.get("compras", 0) >= 1:
        return "medium"
    primary_score = domain_scores.get(primary_domain, 0)
    if primary_score >= 2:
        return "medium"
    return "low"
