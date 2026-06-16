from __future__ import annotations

from decimal import Decimal
from typing import Any

from core.parsing import ParsedItem, number_to_json
from core.text import normalize


def purchase_missing_data(items: list[ParsedItem]) -> list[str]:
    missing = [
        "fecha real de compra",
        "proveedor",
        "comprobante o evidencia",
        "confirmacion de impacto en stock",
    ]
    if any(item.unit_price is None for item in items):
        missing.append("precio unitario de cada item")
    if not items:
        missing.extend(["producto/insumo", "cantidad", "unidad"])
    return missing


def build_purchase_draft(items: list[ParsedItem], today: str) -> dict[str, Any] | None:
    if not items:
        return None
    total = sum((item.subtotal for item in items if item.subtotal is not None), Decimal("0"))
    has_full_total = all(item.subtotal is not None for item in items)
    return {
        "estado": "draft",
        "fecha_inferida": today,
        "fecha_real": None,
        "proveedor": None,
        "moneda": "PYG",
        "items": [item.to_dict() for item in items],
        "total_inferido": number_to_json(total) if has_full_total else None,
        "fuente": "conversacion",
        "requiere_confirmacion": True,
    }


def build_stock_movements(items: list[ParsedItem], primary_domain: str) -> list[dict[str, Any]]:
    if not items or primary_domain != "compras":
        return []
    movements: list[dict[str, Any]] = []
    for item in items:
        movements.append(
            {
                "estado": "draft",
                "tipo_movimiento": "entrada",
                "motivo": "compra",
                "producto": item.product,
                "cantidad": number_to_json(item.quantity),
                "unidad": item.unit,
                "origen": "proveedor pendiente",
                "destino": "deposito pendiente",
                "requiere_confirmacion": True,
            }
        )
    return movements


def stock_analysis_missing_data() -> list[str]:
    return [
        "consumo diario aproximado por alimento",
        "cantidad de aves o lotes que consumen cada alimento",
        "stock minimo deseado antes de reponer",
        "fecha estimada de proxima visita al proveedor",
        "precios actuales si se quiere preparar compra minima",
    ]


def sanitary_missing_data(intent: str) -> list[str]:
    if intent == "preguntar_datos_faltantes":
        return [
            "foto o etiqueta completa del producto",
            "principio activo y concentracion",
            "cantidad de aves",
            "peso o edad aproximada",
            "lote o grupo afectado",
            "sintomas observados",
            "si hay ponedoras y destino de huevos",
            "si ya recibieron otro medicamento",
            "indicacion veterinaria si existe",
        ]
    if intent == "analizar_decision_operativa":
        return [
            "cantidad exacta de aves afectadas",
            "lote, galpon o corral afectado",
            "peso promedio estimado",
            "producto exacto y etiqueta",
            "motivo de la decision sanitaria",
            "sintomas concretos y evolucion",
            "si hay ponedoras y destino de huevos",
            "indicacion veterinaria si existe",
        ]
    return [
        "fecha y hora exacta de administracion",
        "lote, galpon o corral afectado",
        "cantidad exacta de aves",
        "peso promedio estimado por ave",
        "producto exacto y concentracion",
        "motivo del tratamiento",
        "consumo real del agua o alimento medicado",
        "si hay aves ponedoras y destino de huevos",
        "indicacion veterinaria o etiqueta usada",
        "observaciones posteriores",
    ]


def workflow_candidate_missing_data(primary_domain: str) -> list[str]:
    if primary_domain == "ventas":
        return [
            "productos exactos que se pueden mencionar al cliente",
            "tratamientos reales aplicados y confirmados",
            "lotes de pollitos vendidos o a vender",
            "si la ficha es historial, recomendacion o advertencia",
            "advertencias veterinarias o legales",
            "fotos o etiquetas autorizadas para compartir",
            "formato de ficha para cliente",
        ]
    if primary_domain == "stock-insumos":
        return [
            "nombre final del modulo",
            "unidades de medida oficiales",
            "categorias definitivas de insumos",
            "si vitaminas y medicamentos van en stock general o sanitario",
            "politica de stock minimo",
            "quien confirma movimientos",
            "estructura de depositos",
        ]
    if primary_domain == "infraestructura":
        return [
            "ubicacion exacta",
            "largo total o alcance",
            "materiales disponibles",
            "tipo de animales que debe contener o separar",
            "riesgo de escape o depredadores",
            "fecha prevista",
            "responsable",
        ]
    return [
        "objetivo del workflow",
        "datos necesarios",
        "criterio de confirmacion",
    ]


def operational_decision_missing_data(primary_domain: str, risk_level: str) -> list[str]:
    if primary_domain == "reproductores":
        missing = [
            "objetivo principal: huevos, carne, reproductores, venta o genetica",
            "cantidad actual de aves por raza o linea",
            "sexo y edad de reproductores disponibles",
            "espacio o corrales disponibles",
            "capacidad de separar lineas",
            "demanda de mercado o destino de produccion",
            "presupuesto y costo de alimentacion",
        ]
        if risk_level == "alto":
            missing.extend(
                [
                    "capacidad real de incubadora",
                    "calendario de incubaciones",
                    "criterios de seleccion y descarte",
                ]
            )
        return missing
    if primary_domain == "infraestructura":
        return [
            "cantidad actual por galpon",
            "galpones disponibles",
            "galpones en construccion",
            "capacidad por galpon",
            "prioridad de lotes",
            "fecha estimada de terminacion",
            "presupuesto",
        ]
    return [
        "objetivo de la decision",
        "opciones disponibles",
        "datos faltantes para comparar",
    ]


def stock_movement_missing_data(primary_domain: str, secondary_domains: list[str]) -> list[str]:
    if primary_domain == "stock-insumos" and "sanidad" in secondary_domains:
        return [
            "cantidad disponible de cada producto",
            "unidad de medida",
            "fecha de compra",
            "proveedor",
            "precio",
            "vencimiento",
            "lote del producto",
            "foto o etiqueta",
            "si se registra como stock real o solo referencia",
            "ubicacion fisica en deposito",
        ]
    return []


def build_log_entry(text: str, classification: dict[str, Any], today: str) -> dict[str, Any]:
    return {
        "estado": "draft",
        "fecha_inferida": today,
        "dominio_primario": classification["primary_domain"],
        "dominios_secundarios": classification["secondary_domains"],
        "riesgo": classification["risk_level"],
        "fuente": "conversacion",
        "relato": text,
    }


def build_suggested_tasks(text: str, classification: dict[str, Any]) -> list[dict[str, Any]]:
    normalized_text = normalize(text)
    derived_task = build_comedero_task(normalized_text, classification)
    if derived_task:
        return [derived_task]
    if classification["intent"] == "detectar_workflow_candidato":
        return []
    forage_title = build_forage_task_title(normalized_text)
    if forage_title:
        return [
            {
                "estado": "draft",
                "titulo": forage_title,
                "dominio": "alimentacion",
                "dominios_relacionados": ["infraestructura", "stock-insumos"],
                "riesgo": classification["risk_level"],
                "proximo_paso": "confirmar si debe pasar a tareas como preparacion de bandeja FVH",
                "requiere_confirmacion": classification["requires_confirmation"],
            }
        ]
    task_signals = ("revisar", "limpiar", "reparar", "pendiente", "manana", "mejorar")
    if not any(signal in normalized_text for signal in task_signals):
        return []
    title = text.strip().rstrip(".")
    return [
        {
            "estado": "draft",
            "titulo": title[:90],
            "dominio": classification["primary_domain"],
            "riesgo": classification["risk_level"],
            "proximo_paso": "confirmar si debe pasar a tasks/inbox.md",
            "requiere_confirmacion": classification["requires_confirmation"],
        }
    ]


def build_comedero_task(
    normalized_text: str,
    classification: dict[str, Any],
) -> dict[str, Any] | None:
    if "mejorar" not in normalized_text:
        return None
    if not any(marker in normalized_text for marker in ("comedero", "plato")):
        return None
    return {
        "estado": "draft",
        "titulo": "Mejorar comedero/plato para reducir contaminacion del alimento",
        "dominio": "tareas-mantenimiento",
        "dominios_relacionados": ["infraestructura", classification["primary_domain"]],
        "riesgo": "medio" if classification["risk_level"] in {"alto", "critico"} else classification["risk_level"],
        "proximo_paso": "confirmar si debe planificarse como tarea de mantenimiento",
        "requiere_confirmacion": True,
    }


def build_forage_task_title(normalized_text: str) -> str | None:
    if not any(marker in normalized_text for marker in ("forraje", "forrajes")):
        return None
    if not any(marker in normalized_text for marker in ("bandeja", "tupper", "agujeros", "perforar", "perforando")):
        return None
    return "Preparar bandeja perforada para forraje germinado"


def build_confirmation(classification: dict[str, Any], items: list[ParsedItem]) -> dict[str, Any]:
    if not classification["requires_confirmation"]:
        return {
            "required": False,
            "question": "No se requiere confirmacion para este dry-run de bajo riesgo.",
        }
    if classification["intent"] == "registrar_compra" and items:
        products = ", ".join(item.product for item in items)
        return {
            "required": True,
            "question": (
                "Confirmas que prepare este borrador de compra y el movimiento de "
                f"stock propuesto para: {products}? No se registrara como hecho real "
                "hasta que lo confirmes explicitamente."
            ),
        }
    return {
        "required": True,
        "question": (
            "Confirmas que esta propuesta debe avanzar como borrador? "
            "No se registrara como hecho real sin confirmacion explicita."
        ),
    }


def build_next_actions(classification: dict[str, Any], missing_data: list[str]) -> list[str]:
    actions = ["revisar datos detectados"]
    if missing_data:
        actions.append("responder datos faltantes")
    if classification["requires_confirmation"]:
        actions.append("confirmar explicitamente antes de registrar hechos operativos")
    return actions


def build_ui_response(
    classification: dict[str, Any],
    detected_data: dict[str, Any],
    missing_data: list[str],
    purchase: dict[str, Any] | None,
    stock_movements: list[dict[str, Any]],
    confirmation: dict[str, Any],
) -> dict[str, Any]:
    components: list[dict[str, Any]] = [
        {
            "component": "summary_card",
            "props": {
                "title": "Revision de operacion",
                "body": "Se preparo una propuesta en modo dry-run. No se modificaron datos reales.",
            },
        }
    ]
    if detected_data.get("items"):
        components.append(
            {
                "component": "data_table",
                "props": {
                    "title": "Items detectados",
                    "rows": detected_data["items"],
                },
            }
        )
    if detected_data.get("stock_observations"):
        components.append(
            {
                "component": "data_table",
                "props": {
                    "title": "Existencias detectadas",
                    "rows": detected_data["stock_observations"],
                },
            }
        )
    if missing_data:
        components.append(
            {
                "component": "checklist",
                "props": {
                    "title": "Datos faltantes",
                    "items": missing_data,
                },
            }
        )
    if purchase:
        components.append(
            {
                "component": "summary_card",
                "props": {
                    "title": "Borrador de compra",
                    "body": "Compra propuesta en estado draft.",
                    "data": purchase,
                },
            }
        )
    if stock_movements:
        components.append(
            {
                "component": "data_table",
                "props": {
                    "title": "Movimientos de stock propuestos",
                    "rows": stock_movements,
                },
            }
        )
    components.append(
        {
            "component": "action_group",
            "props": {
                "actions": [
                    {
                        "id": "confirm",
                        "label": "Confirmar borrador",
                        "requires_confirmation": confirmation["required"],
                    },
                    {
                        "id": "edit",
                        "label": "Corregir datos",
                        "requires_confirmation": False,
                    },
                    {
                        "id": "cancel",
                        "label": "Cancelar",
                        "requires_confirmation": False,
                    },
                ]
            },
        }
    )
    return {
        "schema_version": "0.1",
        "response_type": "review",
        "title": "Revision de Granja Luna",
        "summary": confirmation["question"],
        "risk_level": classification["risk_level"],
        "requires_confirmation": classification["requires_confirmation"],
        "rendering_mode": "host_native",
        "components": components,
        "information_status": {
            "classification": "borrador",
            "detected_data": "inferido",
            "missing_data": "pendiente_validar",
            "drafts": "borrador",
        },
    }
