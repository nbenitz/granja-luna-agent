"""Local derivatives, explainable image metrics, and human media curation."""

from __future__ import annotations

import json
import re
import shutil
import sqlite3
import subprocess
from pathlib import Path
from typing import Any
from uuid import uuid4

from .media_library import now_iso


EDITORIAL_INTENTS = {"panoramica", "detalle", "portada", "proceso", "archivo"}
SHOT_TYPES = {
    "panoramica_paisaje",
    "escena_general",
    "grupo_aves",
    "retrato_detalle",
    "accion_proceso",
}
CONTENT_PILLARS = {
    "animales_y_personalidad",
    "crianza_responsable",
    "vida_libre_y_naturaleza",
    "trabajo_y_profesionalismo",
    "aprendizaje_y_educacion",
    "razas_genetica_y_produccion",
    "productos_y_disponibilidad",
    "comunidad_y_humor",
    "fe_gratitud_y_proposito",
}
SUBJECT_TAGS = {
    "pollitos",
    "gallinas_caseras",
    "gallos",
    "brahma",
    "rhode_island_red",
    "plymouth_rock_barred",
    "black_star",
    "pastoreo",
    "comportamiento_natural",
    "alimentacion",
    "cuidado",
    "sanidad_con_contexto",
    "limpieza_e_infraestructura",
    "incubacion_y_cria",
    "naturaleza_y_paisaje",
    "trabajo_diario",
}
CURATION_DECISIONS = {"keep", "reserve", "needs_context", "private", "no_usable"}
EXTERNAL_ANALYSIS_BLOCKED_DECISIONS = {"private", "no_usable"}
RESERVED_EDITORIAL_CLAIM_PATTERNS = {
    r"\bevaluar (?:la )?pureza\b": "evaluar pureza racial desde una foto",
    r"\bdeterminar (?:la )?pureza\b": "determinar pureza racial desde una foto",
    r"\bmanejo sanitario\b": "presentar manejo sanitario como hecho visual",
    r"\btransporte segur[oa]\b": "presentar un transporte como seguro",
    r"\b(?:aves|pollitos|gallinas|gallos) felices\b": "presentar felicidad animal como hecho",
    r"\bdemuestra[^.]{0,80}\bcrianza responsable\b": (
        "presentar crianza responsable como demostrada"
    ),
    r"\bdemuestra[^.]{0,80}\bvida libre\b": "presentar vida libre como demostrada",
}
SELECTION_REASONS = {
    "mejor_encuadre",
    "sujeto_mas_claro",
    "cuenta_mejor_la_historia",
    "mejor_luz",
    "mejor_gesto_o_comportamiento",
    "muestra_mejor_el_entorno",
    "representa_mejor_el_objetivo",
    "aporta_otro_angulo",
    "mayor_valor_emocional",
}
LEGACY_SHOT_TYPE_MAP = {
    "panoramica": "panoramica_paisaje",
    "detalle": "retrato_detalle",
    "proceso": "accion_proceso",
}
FACEBOOK_LAUNCH_SLOTS = {
    "facebook_portada",
    "facebook_bienvenida",
    "facebook_pollitos_caseros",
    "facebook_brahma",
    "facebook_black_star",
    "facebook_vida_natural",
    "facebook_comunidad",
}


class MediaCurationError(ValueError):
    pass


def validate_gemini_burst_result(
    result: dict[str, Any], candidate_names: list[str]
) -> dict[str, Any]:
    """Validate model output against the exact burst sent to the provider.

    JSON Schema constrains the response shape at the provider boundary. This second
    validation protects local state from syntactically valid but inconsistent output.
    """

    errors: list[str] = []
    warnings: list[str] = []
    candidates = list(dict.fromkeys(candidate_names))
    candidate_set = set(candidates)
    if len(candidates) != len(candidate_names):
        errors.append("La solicitud contiene nombres de candidatos duplicados.")
    if result.get("valid_json") is not True:
        errors.append("Gemini no devolvió JSON válido.")
    analysis = result.get("analysis")
    if not isinstance(analysis, dict):
        errors.append("Gemini no devolvió un análisis estructurado.")
        return {
            "valid": False,
            "errors": errors,
            "warnings": warnings,
            "candidate_count": len(candidates),
        }

    no_candidate = analysis.get("sin_candidata_adecuada") is True
    best = analysis.get("mejor_archivo")
    favorites = analysis.get("favoritos_por_intencion")
    ranking = analysis.get("ranking")
    claims = analysis.get("afirmaciones_que_requieren_verificacion")
    if not isinstance(favorites, list):
        errors.append("La lista de favoritas no es válida.")
        favorites = []
    if len(favorites) > 2:
        errors.append("Gemini devolvió más de dos favoritas.")

    favorite_files: list[str] = []
    priorities: list[str] = []
    for favorite in favorites:
        if not isinstance(favorite, dict):
            errors.append("Una favorita no tiene estructura válida.")
            continue
        filename = favorite.get("archivo")
        priority = favorite.get("prioridad")
        if filename not in candidate_set:
            errors.append("Gemini recomendó una favorita ajena al grupo.")
        elif isinstance(filename, str):
            favorite_files.append(filename)
        if priority not in {"principal", "secundaria"}:
            errors.append("Una favorita tiene una prioridad inválida.")
        else:
            priorities.append(str(priority))
    if len(favorite_files) != len(set(favorite_files)):
        errors.append("Gemini repitió la misma foto entre sus favoritas.")
    if len(priorities) != len(set(priorities)):
        errors.append("Gemini repitió una prioridad entre sus favoritas.")

    if no_candidate:
        if best not in {None, ""} or favorites:
            errors.append("Gemini indicó que ninguna sirve, pero también eligió favoritas.")
    else:
        if best not in candidate_set:
            errors.append("La mejor foto indicada no pertenece al grupo.")
        principal = next(
            (
                item.get("archivo")
                for item in favorites
                if isinstance(item, dict) and item.get("prioridad") == "principal"
            ),
            None,
        )
        if principal is None:
            errors.append("Gemini no identificó una favorita principal.")
        elif principal != best:
            errors.append("La mejor foto no coincide con la favorita principal.")

    if not isinstance(ranking, list):
        errors.append("El ranking de candidatos no es válido.")
        ranking = []
    ranking_files = [
        item.get("archivo") for item in ranking if isinstance(item, dict)
    ]
    if len(ranking_files) != len(set(ranking_files)):
        errors.append("El ranking repite uno o más candidatos.")
    if set(ranking_files) != candidate_set:
        errors.append("El ranking no contiene exactamente todos los candidatos enviados.")
    if not isinstance(claims, list):
        errors.append("Falta separar las afirmaciones que requieren verificación.")
    if analysis.get("requiere_eleccion_humana") is not True:
        errors.append("El resultado no conserva la elección humana obligatoria.")
    editorial_parts = [str(analysis.get("resumen_de_la_escena") or "")]
    editorial_parts.extend(
        str(item.get("motivo") or "")
        for item in favorites
        if isinstance(item, dict)
    )
    editorial_parts.extend(
        str(item.get("motivo") or "")
        for item in ranking
        if isinstance(item, dict)
    )
    uses = analysis.get("uso_editorial_sugerido")
    if isinstance(uses, list):
        editorial_parts.extend(str(item) for item in uses)
    editorial_text = " ".join(editorial_parts).lower()
    for pattern, description in RESERVED_EDITORIAL_CLAIM_PATTERNS.items():
        if re.search(pattern, editorial_text):
            errors.append(
                "El texto editorial intentó " + description + "; debe moverlo a verificación."
            )
    confidence = analysis.get("confianza_0_a_1")
    if isinstance(confidence, (int, float)) and confidence >= 0.9:
        warnings.append(
            "La confianza alta del modelo no se interpreta como probabilidad calibrada."
        )

    return {
        "valid": not errors,
        "errors": list(dict.fromkeys(errors)),
        "warnings": warnings,
        "candidate_count": len(candidates),
    }


def get_asset(connection: sqlite3.Connection, asset_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM media_assets WHERE id = ? AND is_missing = 0", (asset_id,)
    ).fetchone()
    if row is None:
        raise KeyError(asset_id)
    return dict(row)


def get_cluster(connection: sqlite3.Connection, cluster_id: str) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM media_clusters WHERE id = ?", (cluster_id,)
    ).fetchone()
    if row is None:
        raise KeyError(cluster_id)
    members = connection.execute(
        """
        SELECT a.*, m.position, x.thumbnail_path, x.analysis_path,
            x.brightness_mean, x.contrast_stddev, x.sharpness_score,
            x.perceptual_hash, x.warnings_json, x.analyzed_at
        FROM media_cluster_members m
        JOIN media_assets a ON a.id = m.asset_id
        LEFT JOIN media_asset_analysis x ON x.asset_id = a.id
        WHERE m.cluster_id = ? AND a.is_missing = 0
        ORDER BY m.position
        """,
        (cluster_id,),
    ).fetchall()
    curation = connection.execute(
        "SELECT * FROM media_cluster_curation WHERE cluster_id = ?", (cluster_id,)
    ).fetchone()
    gemini = connection.execute(
        """
        SELECT id, model, requested_at, result_json
        FROM media_gemini_analyses WHERE cluster_id = ?
        ORDER BY requested_at DESC LIMIT 1
        """,
        (cluster_id,),
    ).fetchone()
    serialized_members = [_serialize_member(member) for member in members]
    return {
        **dict(row),
        "item_count": len(serialized_members),
        "members": serialized_members,
        "curation": _serialize_curation(curation),
        "gemini_analysis": _serialize_gemini(gemini),
    }


def list_curation_clusters(
    connection: sqlite3.Connection, *, limit: int = 30
) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT c.id FROM media_clusters c
        WHERE c.cluster_type = 'temporal_burst'
        ORDER BY c.label DESC LIMIT ?
        """,
        (max(0, limit),),
    ).fetchall()
    return [get_cluster(connection, row["id"]) for row in rows]


def analyze_cluster_locally(
    connection: sqlite3.Connection,
    cluster_id: str,
    *,
    media_root: Path,
    derivative_root: Path,
) -> dict[str, Any]:
    cluster = get_cluster(connection, cluster_id)
    for member in cluster["members"]:
        prepare_asset_derivatives(
            connection,
            member["id"],
            media_root=media_root,
            derivative_root=derivative_root,
        )
    connection.commit()
    return get_cluster(connection, cluster_id)


def prepare_asset_derivatives(
    connection: sqlite3.Connection,
    asset_id: str,
    *,
    media_root: Path,
    derivative_root: Path,
) -> dict[str, Any]:
    try:
        from PIL import Image, ImageOps
    except ImportError as exc:
        raise RuntimeError("Pillow es necesario para analizar fotos y crear miniaturas.") from exc
    asset = get_asset(connection, asset_id)
    source = safe_media_path(media_root, asset["relative_path"])
    if not source.is_file():
        raise FileNotFoundError(source)

    thumbnail = derivative_root / "thumbnails" / f"{asset_id}.jpg"
    analysis = derivative_root / "analysis" / f"{asset_id}.jpg"
    thumbnail.parent.mkdir(parents=True, exist_ok=True)
    analysis.parent.mkdir(parents=True, exist_ok=True)

    if asset["media_kind"] == "video":
        frame = derivative_root / "frames" / f"{asset_id}.jpg"
        frame.parent.mkdir(parents=True, exist_ok=True)
        extract_video_frame(source, frame, float(asset.get("duration_seconds") or 0))
        image_source = frame
    else:
        image_source = source

    with Image.open(image_source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        thumb = image.copy()
        thumb.thumbnail((480, 480), Image.Resampling.LANCZOS)
        thumb.save(thumbnail, "JPEG", quality=82, optimize=True)
        cloud_copy = image.copy()
        cloud_copy.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
        cloud_copy.save(analysis, "JPEG", quality=88, optimize=True)
        metrics = technical_metrics(image)

    relative_thumbnail = thumbnail.relative_to(derivative_root).as_posix()
    relative_analysis = analysis.relative_to(derivative_root).as_posix()
    connection.execute(
        """
        INSERT INTO media_asset_analysis(
            asset_id, thumbnail_path, analysis_path, brightness_mean, contrast_stddev,
            sharpness_score, perceptual_hash, warnings_json, analyzed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(asset_id) DO UPDATE SET
            thumbnail_path = excluded.thumbnail_path,
            analysis_path = excluded.analysis_path,
            brightness_mean = excluded.brightness_mean,
            contrast_stddev = excluded.contrast_stddev,
            sharpness_score = excluded.sharpness_score,
            perceptual_hash = excluded.perceptual_hash,
            warnings_json = excluded.warnings_json,
            analyzed_at = excluded.analyzed_at
        """,
        (
            asset_id,
            relative_thumbnail,
            relative_analysis,
            metrics["brightness_mean"],
            metrics["contrast_stddev"],
            metrics["sharpness_score"],
            metrics["perceptual_hash"],
            json.dumps(metrics["warnings"], ensure_ascii=False),
            now_iso(),
        ),
    )
    return metrics


def technical_metrics(image: Any) -> dict[str, Any]:
    try:
        from PIL import Image, ImageFilter, ImageOps, ImageStat
    except ImportError as exc:
        raise RuntimeError("Pillow es necesario para calcular métricas de imagen.") from exc
    sample = image.copy()
    sample.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    gray = ImageOps.grayscale(sample)
    stats = ImageStat.Stat(gray)
    brightness = float(stats.mean[0])
    contrast = float(stats.stddev[0])
    edges = gray.filter(ImageFilter.FIND_EDGES)
    sharpness = float(ImageStat.Stat(edges).var[0])
    hash_image = gray.resize((8, 8), Image.Resampling.LANCZOS)
    pixels = list(
        hash_image.get_flattened_data()
        if hasattr(hash_image, "get_flattened_data")
        else hash_image.getdata()
    )
    average = sum(pixels) / len(pixels)
    bits = "".join("1" if value >= average else "0" for value in pixels)
    perceptual_hash = f"{int(bits, 2):016x}"
    warnings: list[str] = []
    if brightness < 55:
        warnings.append("posible_subexposicion")
    elif brightness > 210:
        warnings.append("posible_sobreexposicion")
    if contrast < 28:
        warnings.append("contraste_bajo")
    if sharpness < 110:
        warnings.append("nitidez_baja_o_escena_suave")
    return {
        "brightness_mean": round(brightness, 2),
        "contrast_stddev": round(contrast, 2),
        "sharpness_score": round(sharpness, 2),
        "perceptual_hash": perceptual_hash,
        "warnings": warnings,
    }


def save_cluster_curation(
    connection: sqlite3.Connection,
    cluster_id: str,
    *,
    editorial_intents: list[str] | None = None,
    campaign_slots: list[str] | None = None,
    primary_asset_id: str | None = None,
    primary_intent: str | None = None,
    secondary_asset_id: str | None = None,
    secondary_intent: str | None = None,
    note: str | None = None,
    shot_types: list[str] | None = None,
    content_pillars: list[str] | None = None,
    subject_tags: list[str] | None = None,
    group_decision: str = "keep",
    primary_reasons: list[str] | None = None,
    primary_campaign_slots: list[str] | None = None,
    secondary_reasons: list[str] | None = None,
    secondary_campaign_slots: list[str] | None = None,
) -> dict[str, Any]:
    cluster = get_cluster(connection, cluster_id)
    member_ids = {member["id"] for member in cluster["members"]}
    normalized_intents = list(dict.fromkeys(editorial_intents or []))
    normalized_shot_types = list(dict.fromkeys(shot_types or []))
    if not normalized_shot_types:
        normalized_shot_types = [
            LEGACY_SHOT_TYPE_MAP[value]
            for value in normalized_intents
            if value in LEGACY_SHOT_TYPE_MAP
        ]
    normalized_pillars = list(dict.fromkeys(content_pillars or []))
    normalized_subjects = list(dict.fromkeys(subject_tags or []))
    normalized_primary_reasons = list(dict.fromkeys(primary_reasons or []))
    normalized_secondary_reasons = list(dict.fromkeys(secondary_reasons or []))
    normalized_primary_slots = list(
        dict.fromkeys(primary_campaign_slots if primary_campaign_slots is not None else campaign_slots or [])
    )
    normalized_secondary_slots = list(dict.fromkeys(secondary_campaign_slots or []))
    normalized_slots = list(dict.fromkeys([*normalized_primary_slots, *normalized_secondary_slots]))
    invalid = set(normalized_intents) - EDITORIAL_INTENTS
    if invalid:
        raise MediaCurationError("Una intención editorial heredada no es válida.")
    if set(normalized_shot_types) - SHOT_TYPES:
        raise MediaCurationError("Uno de los tipos de toma no es válido.")
    if set(normalized_pillars) - CONTENT_PILLARS:
        raise MediaCurationError("Uno de los pilares de contenido no es válido.")
    if set(normalized_subjects) - SUBJECT_TAGS:
        raise MediaCurationError("Una de las etiquetas de tema no es válida.")
    if group_decision not in CURATION_DECISIONS:
        raise MediaCurationError("La decisión del grupo no es válida.")
    if set(normalized_primary_reasons + normalized_secondary_reasons) - SELECTION_REASONS:
        raise MediaCurationError("Uno de los motivos de selección no es válido.")
    if set(normalized_slots) - FACEBOOK_LAUNCH_SLOTS:
        raise MediaCurationError("Uno de los usos de lanzamiento de Facebook no es válido.")
    if group_decision == "keep" and primary_asset_id is None:
        raise MediaCurationError("Selecciona una favorita principal o cambia la decisión del grupo.")
    if primary_asset_id is not None and primary_asset_id not in member_ids:
        raise MediaCurationError("La favorita principal debe pertenecer al grupo.")
    canonical_primary_intent = LEGACY_SHOT_TYPE_MAP.get(primary_intent or "", primary_intent)
    canonical_secondary_intent = LEGACY_SHOT_TYPE_MAP.get(secondary_intent or "", secondary_intent)
    if canonical_primary_intent and canonical_primary_intent not in normalized_shot_types:
        raise MediaCurationError("El tipo de toma principal debe estar seleccionado en el grupo.")
    if secondary_asset_id:
        if primary_asset_id is None:
            raise MediaCurationError("Selecciona una principal antes de conservar una secundaria.")
        if secondary_asset_id not in member_ids or secondary_asset_id == primary_asset_id:
            raise MediaCurationError("La secundaria debe ser otra foto del mismo grupo.")
        if canonical_secondary_intent and canonical_secondary_intent not in normalized_shot_types:
            raise MediaCurationError("El tipo de toma secundaria debe estar seleccionado en el grupo.")
    elif canonical_secondary_intent or normalized_secondary_reasons or normalized_secondary_slots:
        raise MediaCurationError("Selecciona una foto secundaria o quita sus datos asociados.")
    if primary_asset_id is None and (
        canonical_primary_intent or normalized_primary_reasons or normalized_primary_slots
    ):
        raise MediaCurationError("Selecciona una foto principal o quita sus datos asociados.")
    if group_decision == "no_usable" and (primary_asset_id or secondary_asset_id):
        raise MediaCurationError("Un grupo sin material utilizable no puede conservar favoritas.")
    updated_at = now_iso()
    connection.execute(
        """
        INSERT INTO media_cluster_curation(
            cluster_id, editorial_intents_json, campaign_slots_json,
            shot_types_json, content_pillars_json, subject_tags_json, group_decision,
            primary_asset_id, primary_intent, primary_reasons_json,
            primary_campaign_slots_json, secondary_asset_id, secondary_intent,
            secondary_reasons_json, secondary_campaign_slots_json, note, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(cluster_id) DO UPDATE SET
            editorial_intents_json = excluded.editorial_intents_json,
            campaign_slots_json = excluded.campaign_slots_json,
            shot_types_json = excluded.shot_types_json,
            content_pillars_json = excluded.content_pillars_json,
            subject_tags_json = excluded.subject_tags_json,
            group_decision = excluded.group_decision,
            primary_asset_id = excluded.primary_asset_id,
            primary_intent = excluded.primary_intent,
            primary_reasons_json = excluded.primary_reasons_json,
            primary_campaign_slots_json = excluded.primary_campaign_slots_json,
            secondary_asset_id = excluded.secondary_asset_id,
            secondary_intent = excluded.secondary_intent,
            secondary_reasons_json = excluded.secondary_reasons_json,
            secondary_campaign_slots_json = excluded.secondary_campaign_slots_json,
            note = excluded.note,
            updated_at = excluded.updated_at
        """,
        (
            cluster_id,
            json.dumps(normalized_intents, ensure_ascii=False),
            json.dumps(normalized_slots, ensure_ascii=False),
            json.dumps(normalized_shot_types, ensure_ascii=False),
            json.dumps(normalized_pillars, ensure_ascii=False),
            json.dumps(normalized_subjects, ensure_ascii=False),
            group_decision,
            primary_asset_id,
            canonical_primary_intent,
            json.dumps(normalized_primary_reasons, ensure_ascii=False),
            json.dumps(normalized_primary_slots, ensure_ascii=False),
            secondary_asset_id,
            canonical_secondary_intent if secondary_asset_id else None,
            json.dumps(normalized_secondary_reasons, ensure_ascii=False),
            json.dumps(normalized_secondary_slots, ensure_ascii=False),
            note.strip() if note and note.strip() else None,
            updated_at,
        ),
    )
    connection.commit()
    return get_cluster(connection, cluster_id)["curation"]


def save_gemini_analysis(
    connection: sqlite3.Connection,
    cluster_id: str,
    *,
    model: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    analysis_id = f"gemini-{uuid4().hex[:16]}"
    requested_at = now_iso()
    connection.execute(
        """
        INSERT INTO media_gemini_analyses(id, cluster_id, model, requested_at, result_json)
        VALUES (?, ?, ?, ?, ?)
        """,
        (analysis_id, cluster_id, model, requested_at, json.dumps(result, ensure_ascii=False)),
    )
    connection.commit()
    return {"id": analysis_id, "model": model, "requested_at": requested_at, "result": result}


def safe_media_path(root: Path, relative_path: str) -> Path:
    resolved_root = root.expanduser().resolve()
    candidate = (resolved_root / relative_path).resolve()
    if candidate != resolved_root and resolved_root not in candidate.parents:
        raise MediaCurationError("Ruta de medio inválida.")
    return candidate


def derivative_path(root: Path, relative_path: str) -> Path:
    return safe_media_path(root, relative_path)


def extract_video_frame(source: Path, destination: Path, duration: float) -> None:
    if not shutil.which("ffmpeg"):
        raise RuntimeError("ffmpeg es necesario para generar miniaturas de video.")
    offset = min(3.0, max(0.0, duration / 2))
    subprocess.run(
        [
            "ffmpeg", "-y", "-ss", str(offset), "-i", str(source), "-frames:v", "1",
            "-map_metadata", "-1", "-q:v", "3", str(destination),
        ],
        check=True,
        capture_output=True,
        timeout=60,
    )


def _serialize_member(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    item["warnings"] = json.loads(item.pop("warnings_json")) if item.get("warnings_json") else []
    item["thumbnail_url"] = (
        f"/api/media/assets/{item['id']}/thumbnail" if item.get("thumbnail_path") else None
    )
    item["preview_url"] = (
        f"/api/media/assets/{item['id']}/preview" if item.get("analysis_path") else None
    )
    return item


def _serialize_curation(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    item = dict(row)
    item["editorial_intents"] = _json_list(item.pop("editorial_intents_json", None))
    item["campaign_slots"] = _json_list(item.pop("campaign_slots_json", None))
    item["shot_types"] = _json_list(item.pop("shot_types_json", None))
    if not item["shot_types"]:
        item["shot_types"] = [
            LEGACY_SHOT_TYPE_MAP[value]
            for value in item["editorial_intents"]
            if value in LEGACY_SHOT_TYPE_MAP
        ]
    item["content_pillars"] = _json_list(item.pop("content_pillars_json", None))
    item["subject_tags"] = _json_list(item.pop("subject_tags_json", None))
    item["primary_reasons"] = _json_list(item.pop("primary_reasons_json", None))
    item["primary_campaign_slots"] = _json_list(
        item.pop("primary_campaign_slots_json", None)
    )
    if not item["primary_campaign_slots"] and item.get("primary_asset_id"):
        item["primary_campaign_slots"] = list(item["campaign_slots"])
    item["secondary_reasons"] = _json_list(item.pop("secondary_reasons_json", None))
    item["secondary_campaign_slots"] = _json_list(
        item.pop("secondary_campaign_slots_json", None)
    )
    item["primary_shot_type"] = LEGACY_SHOT_TYPE_MAP.get(
        item.get("primary_intent"), item.get("primary_intent")
    )
    item["secondary_shot_type"] = LEGACY_SHOT_TYPE_MAP.get(
        item.get("secondary_intent"), item.get("secondary_intent")
    )
    return item


def _json_list(value: str | None) -> list[str]:
    if not value:
        return []
    parsed = json.loads(value)
    return parsed if isinstance(parsed, list) else []


def _serialize_gemini(row: sqlite3.Row | None) -> dict[str, Any] | None:
    if row is None:
        return None
    item = dict(row)
    item["result"] = json.loads(item.pop("result_json"))
    return item
