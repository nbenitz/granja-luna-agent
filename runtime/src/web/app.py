from __future__ import annotations

import os
import sys
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import Callable, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

SRC_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_INBOX_PATH = Path(os.getenv("GRANJA_INBOX_PATH", RUNTIME_DIR / "state" / "inbox.jsonl"))
DEFAULT_USAGE_PATH = Path(
    os.getenv("GRANJA_USAGE_PATH", RUNTIME_DIR / "state" / "usage-events.jsonl")
)
DEFAULT_REVIEW_EVENTS_PATH = Path(
    os.getenv("GRANJA_REVIEW_EVENTS_PATH", RUNTIME_DIR / "state" / "review-events.jsonl")
)
DEFAULT_OPERATIONS_PATH = Path(
    os.getenv("GRANJA_OPERATIONS_PATH", RUNTIME_DIR / "state" / "operation-events.jsonl")
)
DEFAULT_STRUCTURE_PATH = Path(
    os.getenv("GRANJA_STRUCTURE_PATH", RUNTIME_DIR / "state" / "structure-events.jsonl")
)
DEFAULT_INCUBATION_PATH = Path(
    os.getenv("GRANJA_INCUBATION_PATH", RUNTIME_DIR / "state" / "incubation-events.jsonl")
)
DEFAULT_BROODING_PATH = Path(
    os.getenv("GRANJA_BROODING_PATH", RUNTIME_DIR / "state" / "brooding-events.jsonl")
)
DEFAULT_MEDIA_DATABASE_PATH = Path(
    os.getenv(
        "GRANJA_MEDIA_DATABASE_PATH",
        RUNTIME_DIR / "state" / "media-library" / "library.sqlite3",
    )
)
DEFAULT_MEDIA_ROOT = Path(
    os.getenv("GRANJA_MEDIA_ROOT", RUNTIME_DIR.parent / "media" / "inbox")
)
DEFAULT_MEDIA_DERIVATIVES_PATH = Path(
    os.getenv(
        "GRANJA_MEDIA_DERIVATIVES_PATH",
        RUNTIME_DIR / "state" / "media-library" / "derivatives",
    )
)
DEFAULT_ENV_FILE = RUNTIME_DIR.parent / ".env"

sys.path.insert(0, str(SRC_DIR))

from core.brooding import (  # noqa: E402
    BROODING_RECORD_TYPES,
    append_brooding_event,
    brooding_batch_detail,
    cancel_brooding_draft,
    confirm_brooding_record,
    create_brooding_draft,
    list_brooding_records,
)
from core.dry_run import build_dry_run  # noqa: E402
from core.farm_structure import (  # noqa: E402
    STRUCTURE_TYPES,
    append_structure_event,
    cancel_structure_draft,
    confirm_structure_record,
    create_structure_draft,
    find_structure_record,
    list_structure_records,
    load_structure_records,
)
from core.inbox import (  # noqa: E402
    append_inbox_entry,
    build_inbox_entry,
    filter_inbox_entries,
    find_inbox_entry,
    load_inbox_entries,
    normalize_inbox_entry,
    record_inbox_correction,
    summarize_inbox,
    update_inbox_entry_review,
    write_inbox_entries,
)
from core.incubation import (  # noqa: E402
    INCUBATION_RECORD_TYPES,
    append_incubation_event,
    batch_detail,
    cancel_incubation_draft,
    confirm_incubation_record,
    create_incubation_draft,
    find_incubation_record,
    list_incubation_records,
    load_incubation_records,
)
from core.local_env import get_local_secret  # noqa: E402
from core.media_curation import (  # noqa: E402
    CONTENT_PILLARS,
    EDITORIAL_INTENTS,
    EXTERNAL_ANALYSIS_BLOCKED_DECISIONS,
    FACEBOOK_LAUNCH_SLOTS,
    SHOT_TYPES,
    SUBJECT_TAGS,
    MediaCurationError,
    analyze_cluster_locally,
    derivative_path,
    get_cluster,
    list_curation_clusters,
    prepare_asset_derivatives,
    save_cluster_curation,
    save_gemini_analysis,
    validate_gemini_burst_result,
)
from core.media_library import connect_media_library  # noqa: E402
from core.intent_forms import (  # noqa: E402
    ensure_structured_data,
    update_structured_values,
    validate_structured_data,
)
from core.operations import (  # noqa: E402
    MOVEMENT_STATUSES,
    MOVEMENT_TYPES,
    OperationValidationError,
    append_operation_event,
    cancel_movement_draft,
    confirm_movement,
    create_movement_draft,
    daily_summary,
    egg_storage_lots,
    find_movement,
    inventory_summary,
    list_pending_movements,
    load_movements,
    operations_status,
)
from core.review_log import (  # noqa: E402
    append_review_event,
    build_review_event,
    load_review_events,
)
from core.usage_log import (  # noqa: E402
    append_usage_event,
    build_usage_event,
    load_usage_events,
    summarize_usage,
)

ReviewStatus = Literal["pending", "validated", "needs_information", "needs_correction", "rejected"]
CorrectionSection = Literal["purchase_general", "purchase_items", "classification"]
CorrectionReason = Literal["system_error", "new_information", "ambiguous_input"]
ReviewDecision = Literal["confirm", "needs_information", "needs_correction", "reject"]


class CaptureRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    context: str | None = Field(default=None, max_length=12000)


class CorrectionRequest(BaseModel):
    section: CorrectionSection
    reason: CorrectionReason
    note: str | None = Field(default=None, max_length=2000)
    data: dict[str, object]


class ReviewRequest(BaseModel):
    decision: ReviewDecision
    reason: str | None = Field(default=None, max_length=100)
    note: str | None = Field(default=None, max_length=2000)


class OperationDraftRequest(BaseModel):
    effective_date: object | None = None
    flock: object | None = None
    flock_id: object | None = None
    barn_id: object | None = None
    eggs_total: object | None = None
    eggs_healthy: object | None = None
    eggs_broken: object | None = None
    eggs_dirty: object | None = None
    destination: object | None = None
    storage_area_id: object | None = None
    purpose: object | None = None
    physical_separation: object | None = None
    identification_stage: object | None = None
    classifications: object | None = None
    supplier: object | None = None
    items: object | None = None
    price_status: object | None = None
    currency: object | None = None
    total_amount: object | None = None
    update_inventory: object | None = None
    receipt_reference: object | None = None
    description: object | None = None
    category: object | None = None
    amount: object | None = None
    payee: object | None = None
    customer: object | None = None
    payment_status: object | None = None
    notes: object | None = None
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


class OperationConfirmRequest(BaseModel):
    confirmation_code: str = Field(min_length=8, max_length=32)
    explicit_confirmation: bool
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


class StructureDraftRequest(BaseModel):
    name: object | None = None
    capacity: object | None = None
    purpose: object | None = None
    classification_mode: object | None = None
    active: object | None = None
    bird_count: object | None = None
    hen_breeds: object | None = None
    rooster_breeds: object | None = None
    bird_groups: object | None = None
    egg_label: object | None = None
    barn_id: object | None = None
    notes: object | None = None
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


class IncubationDraftRequest(BaseModel):
    name: object | None = None
    capacity: object | None = None
    incubator_id: object | None = None
    start_date: object | None = None
    eggs_set: object | None = None
    source_description: object | None = None
    source_flock: object | None = None
    collection_dates: object | None = None
    purchase_movement_id: object | None = None
    source_egg_lots: object | None = None
    batch_id: object | None = None
    event_date: object | None = None
    event_type: object | None = None
    units_discarded: object | None = None
    hatched_alive: object | None = None
    eggs_unhatched: object | None = None
    chicks_dead: object | None = None
    chicks_malformed: object | None = None
    reason: object | None = None
    notes: object | None = None
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


class BroodingDraftRequest(BaseModel):
    name: object | None = None
    capacity: object | None = None
    area_id: object | None = None
    start_date: object | None = None
    chicks_received: object | None = None
    source_incubation_batch_id: object | None = None
    source_description: object | None = None
    age_min_days: object | None = None
    age_max_days: object | None = None
    batch_id: object | None = None
    event_date: object | None = None
    event_type: object | None = None
    quantity: object | None = None
    final_count: object | None = None
    destination: object | None = None
    reason: object | None = None
    notes: object | None = None
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


class DraftCancelRequest(BaseModel):
    confirmation_code: str = Field(min_length=8, max_length=32)
    explicit_confirmation: bool
    reason: str = Field(min_length=1, max_length=1000)
    source: str = Field(default="direct_granja_api", min_length=1, max_length=100)
    actor: str = Field(default="user", min_length=1, max_length=100)
    request_id: str | None = Field(default=None, max_length=200)


EditorialIntent = Literal["panoramica", "detalle", "portada", "proceso", "archivo"]
ShotType = Literal[
    "panoramica_paisaje", "escena_general", "grupo_aves", "retrato_detalle",
    "accion_proceso",
]
ContentPillar = Literal[
    "animales_y_personalidad", "crianza_responsable", "vida_libre_y_naturaleza",
    "trabajo_y_profesionalismo", "aprendizaje_y_educacion",
    "razas_genetica_y_produccion", "productos_y_disponibilidad",
    "comunidad_y_humor", "fe_gratitud_y_proposito",
]
SubjectTag = Literal[
    "pollitos", "gallinas_caseras", "gallos", "brahma", "rhode_island_red",
    "plymouth_rock_barred", "black_star", "pastoreo", "comportamiento_natural",
    "alimentacion", "cuidado", "sanidad_con_contexto", "limpieza_e_infraestructura",
    "incubacion_y_cria", "naturaleza_y_paisaje", "trabajo_diario",
]
CurationDecision = Literal["keep", "reserve", "needs_context", "private", "no_usable"]
SelectionReason = Literal[
    "mejor_encuadre", "sujeto_mas_claro", "cuenta_mejor_la_historia", "mejor_luz",
    "mejor_gesto_o_comportamiento", "muestra_mejor_el_entorno",
    "representa_mejor_el_objetivo", "aporta_otro_angulo", "mayor_valor_emocional",
]


class MediaCurationRequest(BaseModel):
    editorial_intents: list[EditorialIntent] = Field(default_factory=list, max_length=5)
    shot_types: list[ShotType] = Field(default_factory=list, max_length=5)
    content_pillars: list[ContentPillar] = Field(default_factory=list, max_length=9)
    subject_tags: list[SubjectTag] = Field(default_factory=list, max_length=16)
    group_decision: CurationDecision = "keep"
    campaign_slots: list[Literal[
        "facebook_portada", "facebook_bienvenida", "facebook_pollitos_caseros",
        "facebook_brahma", "facebook_black_star", "facebook_vida_natural",
        "facebook_comunidad",
    ]] = Field(default_factory=list, max_length=7)
    primary_asset_id: str | None = Field(default=None, max_length=100)
    primary_intent: EditorialIntent | None = None
    primary_shot_type: ShotType | None = None
    primary_reasons: list[SelectionReason] = Field(default_factory=list, max_length=9)
    primary_campaign_slots: list[str] = Field(default_factory=list, max_length=7)
    secondary_asset_id: str | None = Field(default=None, max_length=100)
    secondary_intent: EditorialIntent | None = None
    secondary_shot_type: ShotType | None = None
    secondary_reasons: list[SelectionReason] = Field(default_factory=list, max_length=9)
    secondary_campaign_slots: list[str] = Field(default_factory=list, max_length=7)
    note: str | None = Field(default=None, max_length=2000)


class MediaGeminiRequest(BaseModel):
    editorial_intents: list[EditorialIntent] = Field(default_factory=list, max_length=5)
    shot_types: list[ShotType] = Field(default_factory=list, max_length=5)
    content_pillars: list[ContentPillar] = Field(default_factory=list, max_length=9)
    subject_tags: list[SubjectTag] = Field(default_factory=list, max_length=16)
    campaign_slots: list[str] = Field(default_factory=list, max_length=7)
    context: str | None = Field(default=None, max_length=2000)
    confirm_external_processing: bool
    confirm_privacy_review: bool
    model: str = Field(default="gemini-3.5-flash", min_length=1, max_length=100)


def validate_egg_collection_references(
    data: dict[str, object], structure_records: list[dict[str, object]]
) -> None:
    references = (
        ("flock_id", "flock", "El plantel indicado debe existir y estar confirmado."),
        ("barn_id", "barn", "El galpón indicado debe existir y estar confirmado."),
        (
            "storage_area_id",
            "egg_storage_area",
            "El almacén de huevos debe existir y estar confirmado.",
        ),
    )
    for field, record_type, question in references:
        record_id = data.get(field)
        if not record_id:
            continue
        try:
            record = find_structure_record(structure_records, str(record_id))
        except KeyError as exc:
            raise OperationValidationError("not_found", field, question) from exc
        if record.get("record_type") != record_type or record.get("status") != "applied":
            raise OperationValidationError("invalid_dependency", field, question)


def validate_source_egg_lots(
    sources: object,
    *,
    operations_path: Path,
    structure_path: Path,
    incubation_path: Path,
) -> None:
    if not sources:
        return
    if not isinstance(sources, list):
        raise OperationValidationError(
            "invalid_data", "source_egg_lots", "Los lotes de origen deben ser una lista."
        )
    available = {
        lot["id"]: int(lot["quantity_available"])
        for lot in egg_storage_lots(
            operations_path,
            structure_records=load_structure_records(structure_path),
            incubation_records=load_incubation_records(incubation_path),
        )
    }
    for source in sources:
        if not isinstance(source, dict) or source.get("lot_id") not in available:
            raise OperationValidationError(
                "not_found", "source_egg_lots", "El lote de huevos almacenados no existe."
            )
        quantity = int(source.get("quantity", 0))
        if quantity > available[str(source["lot_id"])]:
            raise OperationValidationError(
                "capacity_exceeded",
                "source_egg_lots",
                "La cantidad solicitada supera los huevos disponibles en el lote.",
            )


def create_app(
    inbox_path: Path = DEFAULT_INBOX_PATH,
    usage_path: Path = DEFAULT_USAGE_PATH,
    review_events_path: Path = DEFAULT_REVIEW_EVENTS_PATH,
    operations_path: Path = DEFAULT_OPERATIONS_PATH,
    structure_path: Path = DEFAULT_STRUCTURE_PATH,
    incubation_path: Path = DEFAULT_INCUBATION_PATH,
    brooding_path: Path = DEFAULT_BROODING_PATH,
    media_database_path: Path = DEFAULT_MEDIA_DATABASE_PATH,
    media_root: Path = DEFAULT_MEDIA_ROOT,
    media_derivatives_path: Path = DEFAULT_MEDIA_DERIVATIVES_PATH,
    env_file: Path = DEFAULT_ENV_FILE,
    gemini_image_analyzer: Callable[..., dict[str, object]] | None = None,
) -> FastAPI:
    app = FastAPI(title="Granja Luna", version="0.1.0", docs_url="/api/docs", redoc_url=None)
    state_lock = Lock()

    @app.middleware("http")
    async def add_browser_security_headers(request, call_next):
        response = await call_next(request)
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        response.headers.setdefault("Permissions-Policy", "microphone=(self)")
        if request.url.path == "/" or request.url.path.startswith("/static/"):
            response.headers["Cache-Control"] = "no-store"
        if not request.url.path.startswith("/api/docs"):
            response.headers.setdefault(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data:; connect-src 'self'; object-src 'none'; "
                "base-uri 'self'; frame-ancestors 'none'",
            )
        return response

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    def log_event(
        event_type: str,
        related_entry_id: str | None = None,
        details: dict[str, object] | None = None,
    ) -> None:
        event = build_usage_event(event_type, related_entry_id=related_entry_id, details=details)
        append_usage_event(usage_path, event)

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        log_event("app_opened")
        return FileResponse(STATIC_DIR / "index.html")

    @app.get("/api/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "mode": "local_lan"}

    @app.get("/api/media/clusters")
    def media_clusters(
        limit: int = Query(default=30, ge=1, le=100),
    ) -> list[dict[str, object]]:
        with state_lock, connect_media_library(media_database_path) as connection:
            return list_curation_clusters(connection, limit=limit)

    @app.get("/api/media/clusters/{cluster_id}")
    def media_cluster(cluster_id: str) -> dict[str, object]:
        with state_lock, connect_media_library(media_database_path) as connection:
            try:
                return get_cluster(connection, cluster_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Grupo de medios no encontrado.") from exc

    @app.post("/api/media/clusters/{cluster_id}/technical-analysis")
    def technical_media_analysis(cluster_id: str) -> dict[str, object]:
        with state_lock, connect_media_library(media_database_path) as connection:
            try:
                cluster = analyze_cluster_locally(
                    connection,
                    cluster_id,
                    media_root=media_root,
                    derivative_root=media_derivatives_path,
                )
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Grupo de medios no encontrado.") from exc
            except (FileNotFoundError, MediaCurationError, RuntimeError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            log_event(
                "media_technical_analysis_completed",
                related_entry_id=cluster_id,
                details={"asset_count": len(cluster["members"])},
            )
            return cluster

    @app.get("/api/media/assets/{asset_id}/thumbnail")
    def media_thumbnail(asset_id: str) -> FileResponse:
        with state_lock, connect_media_library(media_database_path) as connection:
            try:
                asset = next(
                    member
                    for cluster in list_curation_clusters(connection, limit=100)
                    for member in cluster["members"]
                    if member["id"] == asset_id
                )
                if not asset.get("thumbnail_path"):
                    prepare_asset_derivatives(
                        connection,
                        asset_id,
                        media_root=media_root,
                        derivative_root=media_derivatives_path,
                    )
                    connection.commit()
                    cluster_id = connection.execute(
                        "SELECT cluster_id FROM media_cluster_members WHERE asset_id = ? LIMIT 1",
                        (asset_id,),
                    ).fetchone()[0]
                    asset = next(
                        item for item in get_cluster(connection, cluster_id)["members"]
                        if item["id"] == asset_id
                    )
                path = derivative_path(media_derivatives_path, str(asset["thumbnail_path"]))
            except (KeyError, StopIteration, TypeError) as exc:
                raise HTTPException(status_code=404, detail="Medio no encontrado.") from exc
            except (FileNotFoundError, MediaCurationError, RuntimeError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        return FileResponse(
            path,
            media_type="image/jpeg",
            headers={"Cache-Control": "private, max-age=3600"},
        )

    @app.get("/api/media/assets/{asset_id}/preview")
    def media_preview(asset_id: str) -> FileResponse:
        with state_lock, connect_media_library(media_database_path) as connection:
            row = connection.execute(
                """
                SELECT x.analysis_path
                FROM media_assets a
                LEFT JOIN media_asset_analysis x ON x.asset_id = a.id
                WHERE a.id = ? AND a.is_missing = 0
                """,
                (asset_id,),
            ).fetchone()
            if row is None:
                raise HTTPException(status_code=404, detail="Medio no encontrado.")
            if not row["analysis_path"]:
                try:
                    prepare_asset_derivatives(
                        connection,
                        asset_id,
                        media_root=media_root,
                        derivative_root=media_derivatives_path,
                    )
                    connection.commit()
                except (KeyError, FileNotFoundError, MediaCurationError, RuntimeError) as exc:
                    raise HTTPException(status_code=422, detail=str(exc)) from exc
                row = connection.execute(
                    "SELECT analysis_path FROM media_asset_analysis WHERE asset_id = ?",
                    (asset_id,),
                ).fetchone()
            try:
                path = derivative_path(media_derivatives_path, str(row["analysis_path"]))
            except (TypeError, FileNotFoundError, MediaCurationError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
        return FileResponse(
            path,
            media_type="image/jpeg",
            headers={"Cache-Control": "private, max-age=3600"},
        )

    @app.patch("/api/media/clusters/{cluster_id}/curation")
    def curate_media_cluster(
        cluster_id: str, payload: MediaCurationRequest
    ) -> dict[str, object]:
        with state_lock, connect_media_library(media_database_path) as connection:
            try:
                curation = save_cluster_curation(
                    connection,
                    cluster_id,
                    editorial_intents=list(payload.editorial_intents),
                    campaign_slots=list(payload.campaign_slots),
                    shot_types=list(payload.shot_types),
                    content_pillars=list(payload.content_pillars),
                    subject_tags=list(payload.subject_tags),
                    group_decision=payload.group_decision,
                    primary_asset_id=payload.primary_asset_id,
                    primary_intent=payload.primary_shot_type or payload.primary_intent,
                    primary_reasons=list(payload.primary_reasons),
                    primary_campaign_slots=list(
                        payload.primary_campaign_slots or payload.campaign_slots
                    ),
                    secondary_asset_id=payload.secondary_asset_id,
                    secondary_intent=payload.secondary_shot_type or payload.secondary_intent,
                    secondary_reasons=list(payload.secondary_reasons),
                    secondary_campaign_slots=list(payload.secondary_campaign_slots),
                    note=payload.note,
                )
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Grupo de medios no encontrado.") from exc
            except MediaCurationError as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            log_event(
                "media_curation_saved",
                related_entry_id=cluster_id,
                details={
                    "decision": payload.group_decision,
                    "context_tag_count": len(payload.content_pillars) + len(payload.subject_tags),
                    "favorites": bool(payload.primary_asset_id) + bool(payload.secondary_asset_id),
                },
            )
            return curation

    @app.post("/api/media/clusters/{cluster_id}/gemini")
    def analyze_media_with_gemini(
        cluster_id: str, payload: MediaGeminiRequest
    ) -> dict[str, object]:
        if not payload.confirm_external_processing:
            raise HTTPException(
                status_code=422,
                detail="Confirma explícitamente el envío de derivados sin EXIF a Gemini.",
            )
        if not payload.confirm_privacy_review:
            raise HTTPException(
                status_code=422,
                detail=(
                    "Confirma que revisaste personas y datos sensibles antes del envío externo."
                ),
            )
        if set(payload.editorial_intents) - EDITORIAL_INTENTS:
            raise HTTPException(status_code=422, detail="Intención editorial no soportada.")
        if set(payload.shot_types) - SHOT_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de toma no soportado.")
        if set(payload.content_pillars) - CONTENT_PILLARS:
            raise HTTPException(status_code=422, detail="Pilar de contenido no soportado.")
        if set(payload.subject_tags) - SUBJECT_TAGS:
            raise HTTPException(status_code=422, detail="Etiqueta de tema no soportada.")
        if set(payload.campaign_slots) - FACEBOOK_LAUNCH_SLOTS:
            raise HTTPException(status_code=422, detail="Uso de campaña no soportado.")
        with state_lock, connect_media_library(media_database_path) as connection:
            try:
                existing = get_cluster(connection, cluster_id)
                decision = (existing.get("curation") or {}).get("group_decision")
                if decision in EXTERNAL_ANALYSIS_BLOCKED_DECISIONS:
                    if decision == "private":
                        raise MediaCurationError(
                            "Este grupo es privado y no puede enviarse a un proveedor externo."
                        )
                    raise MediaCurationError(
                        "Este grupo fue descartado y no se incluirá en el análisis externo."
                    )
                cluster = analyze_cluster_locally(
                    connection,
                    cluster_id,
                    media_root=media_root,
                    derivative_root=media_derivatives_path,
                )
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Grupo de medios no encontrado.") from exc
            except (FileNotFoundError, MediaCurationError, RuntimeError) as exc:
                raise HTTPException(status_code=422, detail=str(exc)) from exc
            image_members = [item for item in cluster["members"] if item["media_kind"] == "image"]
            if not image_members:
                raise HTTPException(status_code=422, detail="Este grupo no contiene fotos analizables.")
            images = [
                derivative_path(media_derivatives_path, str(item["analysis_path"]))
                for item in image_members
            ]
            names = [str(item["relative_path"]) for item in image_members]

        context_parts = []
        if payload.shot_types:
            context_parts.append("Tipos de toma que el usuario considera posibles: " + ", ".join(payload.shot_types))
        elif payload.editorial_intents:
            context_parts.append("Etiquetas heredadas de composición: " + ", ".join(payload.editorial_intents))
        if payload.subject_tags:
            context_parts.append("Temas confirmados o propuestos por el usuario: " + ", ".join(payload.subject_tags))
        if payload.content_pillars:
            context_parts.append("Pilares de marca relevantes: " + ", ".join(payload.content_pillars))
        editorial_context = ". ".join(context_parts) or "El usuario todavía no agregó contexto estructurado."
        editorial_context += "."
        if payload.campaign_slots:
            editorial_context += (
                " Objetivos concretos del lanzamiento de Facebook: "
                + ", ".join(payload.campaign_slots)
                + "."
            )
        if payload.context and payload.context.strip():
            editorial_context += f" Contexto adicional: {payload.context.strip()}"
        try:
            if gemini_image_analyzer is None:
                from runtime.src.cli.media_gemini_benchmark import analyze_images

                analyzer = analyze_images
                api_key = get_local_secret("GEMINI_API_KEY", env_file)
            else:
                analyzer = gemini_image_analyzer
                api_key = "provided-by-test-adapter"
            result = analyzer(
                api_key=api_key,
                images=images,
                prompt_type="burst",
                candidate_names=names,
                editorial_intent=editorial_context,
                model=payload.model,
                timeout=180,
            )
        except (FileNotFoundError, RuntimeError, TimeoutError) as exc:
            raise HTTPException(status_code=502, detail=str(exc)) from exc

        result["external_processing"] = {
            "explicitly_confirmed": True,
            "privacy_review_confirmed": True,
            "sanitized_derivatives_only": True,
            "originals_sent": False,
        }
        result["semantic_validation"] = validate_gemini_burst_result(result, names)
        with state_lock, connect_media_library(media_database_path) as connection:
            stored = save_gemini_analysis(
                connection, cluster_id, model=payload.model, result=result
            )
            log_event(
                "media_gemini_analysis_completed",
                related_entry_id=cluster_id,
                details={
                    "model": payload.model,
                    "asset_count": len(images),
                    "semantic_validation_valid": result["semantic_validation"]["valid"],
                },
            )
        return stored

    @app.post("/api/inbox", status_code=201)
    def capture(payload: CaptureRequest) -> dict[str, object]:
        message = payload.message.strip()
        if not message:
            raise HTTPException(status_code=422, detail="El mensaje no puede estar vacio.")
        context = payload.context.strip() if payload.context and payload.context.strip() else None
        dry_run = build_dry_run(message, context=context)
        entry = build_inbox_entry(dry_run)
        with state_lock:
            append_inbox_entry(inbox_path, entry)
            log_event(
                "inbox_created",
                related_entry_id=entry["id"],
                details={
                    "intent": entry["classification"]["intent"],
                    "primary_domain": entry["classification"]["primary_domain"],
                    "risk_level": entry["classification"]["risk_level"],
                    "message_length": len(message),
                    "context_used": context is not None,
                    "input_mode": "text_or_keyboard_dictation",
                },
            )
        return entry

    @app.get("/api/inbox")
    def list_inbox(
        status: ReviewStatus | None = None,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            entries = filter_inbox_entries(load_inbox_entries(inbox_path), status=status)
        return list(reversed(entries[-limit:]))

    @app.get("/api/inbox/summary")
    def inbox_summary() -> dict[str, object]:
        with state_lock:
            return summarize_inbox(load_inbox_entries(inbox_path))

    @app.get("/api/inbox/{entry_id}")
    def get_entry(entry_id: str) -> dict[str, object]:
        with state_lock:
            try:
                entry = find_inbox_entry(load_inbox_entries(inbox_path), entry_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Entrada no encontrada.") from exc
            ensure_structured_data(entry)
            log_event("inbox_viewed", related_entry_id=entry_id)
        return entry

    @app.patch("/api/inbox/{entry_id}/correction")
    def correct_entry(entry_id: str, payload: CorrectionRequest) -> dict[str, object]:
        note = payload.note.strip() if payload.note and payload.note.strip() else None
        with state_lock:
            entries = load_inbox_entries(inbox_path)
            try:
                entry = find_inbox_entry(entries, entry_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Entrada no encontrada.") from exc
            normalize_inbox_entry(entry)
            structured = ensure_structured_data(entry)
            before_status = entry["review_status"]
            if payload.section == "classification":
                before = deepcopy(entry["classification"])
                update_classification(entry, payload.data)
                after = deepcopy(entry["classification"])
            else:
                if not structured or structured.get("schema_id") != "purchase.v2":
                    raise HTTPException(
                        status_code=422,
                        detail="Esta entrada no tiene una compra editable.",
                    )
                before = deepcopy(structured["values"])
                values = deepcopy(structured["values"])
                if payload.section == "purchase_general":
                    for field in (
                        "fecha_compra",
                        "proveedor",
                        "moneda",
                        "comprobante",
                        "descuento",
                        "total_declarado",
                    ):
                        if field in payload.data:
                            values[field] = payload.data[field]
                else:
                    values["items"] = payload.data.get("items", [])
                provenance = {
                    "system_error": "corrected",
                    "new_information": "enriched",
                    "ambiguous_input": "clarified",
                }[payload.reason]
                update_structured_values(entry, values, provenance_source=provenance)
                after = deepcopy(entry["structured_data"]["values"])
            event = build_review_event(
                "correction_saved",
                entry_id,
                before=before,
                after=after,
                section=payload.section,
                reason=payload.reason,
                note=note,
                review_status_before=before_status,
                review_status_after="pending",
            )
            if not event["changes"]:
                raise HTTPException(
                    status_code=422,
                    detail="No se detectaron cambios para guardar.",
                )
            record_inbox_correction(entry, corrected_at=event["occurred_at"])
            write_inbox_entries(inbox_path, entries)
            append_review_event(review_events_path, event)
            log_event(
                "inbox_corrected",
                related_entry_id=entry_id,
                details={
                    "section": payload.section,
                    "reason": payload.reason,
                    "change_count": len(event["changes"]),
                },
            )
        return entry

    @app.patch("/api/inbox/{entry_id}/review")
    def review_entry(entry_id: str, payload: ReviewRequest) -> dict[str, object]:
        note = payload.note.strip() if payload.note and payload.note.strip() else None
        with state_lock:
            entries = load_inbox_entries(inbox_path)
            try:
                entry = find_inbox_entry(entries, entry_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Entrada no encontrada.") from exc
            ensure_structured_data(entry)
            before_status = entry["review_status"]
            review_status, outcome, reason = resolve_review_decision(entry, payload, note)
            event = build_review_event(
                "review_completed",
                entry_id,
                before={"review_status": before_status},
                after={"review_status": review_status},
                section="review",
                reason=reason,
                note=note,
                review_status_before=before_status,
                review_status_after=review_status,
            )
            entry = update_inbox_entry_review(
                entries,
                entry_id,
                review_status,
                outcome,
                reason=reason,
                reviewed_at=event["occurred_at"],
                note=note,
            )
            write_inbox_entries(inbox_path, entries)
            append_review_event(review_events_path, event)
            log_event(
                "inbox_reviewed",
                related_entry_id=entry_id,
                details={"review_status": review_status, "outcome": outcome, "reason": reason},
            )
        return entry

    @app.get("/api/review-events")
    def review_events(entry_id: str | None = None, limit: int = Query(default=100, ge=1, le=500)):
        with state_lock:
            events = load_review_events(review_events_path)
        if entry_id:
            events = [event for event in events if event.get("entry_id") == entry_id]
        return list(reversed(events[-limit:]))

    @app.get("/api/activity")
    def activity(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, object]]:
        with state_lock:
            events = load_usage_events(usage_path)
        return list(reversed(events[-limit:]))

    @app.get("/api/activity/summary")
    def activity_summary() -> dict[str, object]:
        with state_lock:
            return summarize_usage(load_usage_events(usage_path))

    @app.get("/api/operations/status")
    def farm_operations_status() -> dict[str, object]:
        with state_lock:
            return operations_status(operations_path)

    @app.get("/api/operations/daily-summary")
    def farm_daily_summary(date: str = Query(min_length=10, max_length=10)) -> dict[str, object]:
        with state_lock:
            try:
                return daily_summary(operations_path, date)
            except OperationValidationError as exc:
                raise HTTPException(status_code=422, detail=exc.detail()) from exc

    @app.get("/api/operations/movements")
    def farm_movements(
        status: str | None = None,
        movement_type: str | None = None,
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        if status is not None and status not in MOVEMENT_STATUSES:
            raise HTTPException(status_code=422, detail="Estado de movimiento no soportado.")
        if movement_type is not None and movement_type not in MOVEMENT_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de movimiento no soportado.")
        with state_lock:
            if status == "awaiting_confirmation" and movement_type is None:
                return list_pending_movements(operations_path, limit=limit)
            movements = load_movements(operations_path)
        if status is not None:
            movements = [movement for movement in movements if movement.get("status") == status]
        if movement_type is not None:
            movements = [
                movement for movement in movements if movement.get("type") == movement_type
            ]
        movements.sort(key=lambda item: str(item.get("created_at", "")), reverse=True)
        return movements[:limit]

    @app.get("/api/operations/movements/{movement_id}")
    def farm_movement(movement_id: str) -> dict[str, object]:
        with state_lock:
            try:
                return find_movement(load_movements(operations_path), movement_id)
            except KeyError as exc:
                raise HTTPException(status_code=404, detail="Movimiento no encontrado.") from exc

    @app.get("/api/operations/inventory")
    def farm_inventory(
        product: str | None = Query(default=None, max_length=200),
    ) -> dict[str, object]:
        with state_lock:
            return inventory_summary(operations_path, product=product)

    @app.post("/api/operations/movements/{movement_type}/drafts", status_code=201)
    def draft_farm_movement(
        movement_type: str,
        payload: OperationDraftRequest,
    ) -> dict[str, object]:
        operation_payload = payload.model_dump(exclude={"source", "actor", "request_id"})
        with state_lock:
            try:
                if movement_type == "egg_collection":
                    validate_egg_collection_references(
                        operation_payload, load_structure_records(structure_path)
                    )
                movement, event = create_movement_draft(
                    movement_type,
                    operation_payload,
                    source=payload.source,
                    actor=payload.actor,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = 404 if exc.code == "not_found" else 422
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            append_operation_event(operations_path, event)
            log_event(
                "operation_drafted",
                related_entry_id=movement["id"],
                details={"movement_type": movement_type, "source": payload.source},
            )
        return movement

    @app.post("/api/operations/movements/{movement_id}/confirm")
    def confirm_farm_movement(
        movement_id: str,
        payload: OperationConfirmRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                pending_movement = find_movement(load_movements(operations_path), movement_id)
                if pending_movement.get("type") == "egg_collection":
                    validate_egg_collection_references(
                        pending_movement.get("data", {}),
                        load_structure_records(structure_path),
                    )
                movement, event = confirm_movement(
                    operations_path,
                    movement_id,
                    payload.confirmation_code,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_operation_event(operations_path, event)
                log_event(
                    "operation_applied",
                    related_entry_id=movement_id,
                    details={"movement_type": movement["type"], "source": payload.source},
                )
        return movement

    @app.post("/api/operations/movements/{movement_id}/cancel")
    def cancel_farm_movement(
        movement_id: str,
        payload: DraftCancelRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                movement, event = cancel_movement_draft(
                    operations_path,
                    movement_id,
                    payload.confirmation_code,
                    payload.reason,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = 404 if exc.code == "not_found" else 422
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_operation_event(operations_path, event)
                log_event(
                    "operation_cancelled",
                    related_entry_id=movement_id,
                    details={"movement_type": movement["type"], "source": payload.source},
                )
        return movement

    @app.get("/api/operations/barns")
    def farm_barns(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, object]]:
        with state_lock:
            return list_structure_records(
                structure_path,
                record_type="barn",
                limit=limit,
            )

    @app.get("/api/operations/flocks")
    def farm_flocks(limit: int = Query(default=100, ge=1, le=500)) -> list[dict[str, object]]:
        with state_lock:
            return list_structure_records(
                structure_path,
                record_type="flock",
                limit=limit,
            )

    @app.get("/api/operations/egg-storage/areas")
    def egg_storage_areas(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_structure_records(
                structure_path,
                record_type="egg_storage_area",
                limit=limit,
            )

    @app.get("/api/operations/egg-storage/lots")
    def stored_egg_lots(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return egg_storage_lots(
                operations_path,
                structure_records=load_structure_records(structure_path),
                incubation_records=load_incubation_records(incubation_path),
            )[:limit]

    @app.get("/api/operations/egg-storage/lots/{lot_id}")
    def stored_egg_lot(lot_id: str) -> dict[str, object]:
        with state_lock:
            lots = egg_storage_lots(
                operations_path,
                structure_records=load_structure_records(structure_path),
                incubation_records=load_incubation_records(incubation_path),
            )
        try:
            return next(lot for lot in lots if lot["id"] == lot_id)
        except StopIteration as exc:
            raise HTTPException(status_code=404, detail="Lote de huevos no encontrado.") from exc

    @app.get("/api/operations/structure/pending")
    def pending_structure_records(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_structure_records(
                structure_path,
                status="awaiting_confirmation",
                limit=limit,
            )

    @app.post("/api/operations/structure/{record_type}/drafts", status_code=201)
    def draft_structure_record(
        record_type: str,
        payload: StructureDraftRequest,
    ) -> dict[str, object]:
        if record_type not in STRUCTURE_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de estructura no soportado.")
        structure_payload = payload.model_dump(exclude={"source", "actor", "request_id"})
        with state_lock:
            try:
                record, event = create_structure_draft(
                    structure_path,
                    record_type,
                    structure_payload,
                    source=payload.source,
                    actor=payload.actor,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            append_structure_event(structure_path, event)
            log_event(
                "structure_record_drafted",
                related_entry_id=record["id"],
                details={"record_type": record_type, "source": payload.source},
            )
        return record

    @app.post("/api/operations/structure/{record_id}/confirm")
    def confirm_farm_structure_record(
        record_id: str,
        payload: OperationConfirmRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                record, event = confirm_structure_record(
                    structure_path,
                    record_id,
                    payload.confirmation_code,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_structure_event(structure_path, event)
                log_event(
                    "structure_record_applied",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    @app.post("/api/operations/structure/{record_id}/cancel")
    def cancel_farm_structure_record(
        record_id: str,
        payload: DraftCancelRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                record, event = cancel_structure_draft(
                    structure_path,
                    record_id,
                    payload.confirmation_code,
                    payload.reason,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = 404 if exc.code == "not_found" else 422
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_structure_event(structure_path, event)
                log_event(
                    "structure_record_cancelled",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    @app.get("/api/operations/incubation/incubators")
    def farm_incubators(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_incubation_records(
                incubation_path,
                record_type="incubator",
                limit=limit,
            )

    @app.get("/api/operations/incubation/batches")
    def farm_incubation_batches(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_incubation_records(
                incubation_path,
                record_type="batch",
                limit=limit,
            )

    @app.get("/api/operations/incubation/batches/{batch_id}")
    def farm_incubation_batch(batch_id: str) -> dict[str, object]:
        with state_lock:
            try:
                return batch_detail(incubation_path, batch_id)
            except OperationValidationError as exc:
                raise HTTPException(status_code=404, detail=exc.detail()) from exc

    @app.get("/api/operations/incubation/pending")
    def pending_incubation_records(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_incubation_records(
                incubation_path,
                status="awaiting_confirmation",
                limit=limit,
            )

    @app.post("/api/operations/incubation/{record_type}/drafts", status_code=201)
    def draft_incubation_record(
        record_type: str,
        payload: IncubationDraftRequest,
    ) -> dict[str, object]:
        if record_type not in INCUBATION_RECORD_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de incubación no soportado.")
        incubation_payload = payload.model_dump(exclude={"source", "actor", "request_id"})
        with state_lock:
            try:
                record, event = create_incubation_draft(
                    incubation_path,
                    record_type,
                    incubation_payload,
                    source=payload.source,
                    actor=payload.actor,
                    request_id=payload.request_id,
                )
                if record_type == "batch":
                    validate_source_egg_lots(
                        record["data"].get("source_egg_lots"),
                        operations_path=operations_path,
                        structure_path=structure_path,
                        incubation_path=incubation_path,
                    )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            append_incubation_event(incubation_path, event)
            log_event(
                "incubation_record_drafted",
                related_entry_id=record["id"],
                details={"record_type": record_type, "source": payload.source},
            )
        return record

    @app.post("/api/operations/incubation/{record_id}/confirm")
    def confirm_farm_incubation_record(
        record_id: str,
        payload: OperationConfirmRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                pending_record = find_incubation_record(
                    load_incubation_records(incubation_path), record_id
                )
                if pending_record.get("record_type") == "batch":
                    validate_source_egg_lots(
                        pending_record.get("data", {}).get("source_egg_lots"),
                        operations_path=operations_path,
                        structure_path=structure_path,
                        incubation_path=incubation_path,
                    )
                record, event = confirm_incubation_record(
                    incubation_path,
                    record_id,
                    payload.confirmation_code,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_incubation_event(incubation_path, event)
                log_event(
                    "incubation_record_applied",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    @app.post("/api/operations/incubation/{record_id}/cancel")
    def cancel_farm_incubation_record(
        record_id: str,
        payload: DraftCancelRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                record, event = cancel_incubation_draft(
                    incubation_path,
                    record_id,
                    payload.confirmation_code,
                    payload.reason,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = 404 if exc.code == "not_found" else 422
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_incubation_event(incubation_path, event)
                log_event(
                    "incubation_record_cancelled",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    @app.get("/api/operations/brooding/areas")
    def farm_brooding_areas(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_brooding_records(
                brooding_path,
                record_type="area",
                limit=limit,
            )

    @app.get("/api/operations/brooding/batches")
    def farm_brooding_batches(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_brooding_records(
                brooding_path,
                record_type="batch",
                limit=limit,
            )

    @app.get("/api/operations/brooding/batches/{batch_id}")
    def farm_brooding_batch(batch_id: str) -> dict[str, object]:
        with state_lock:
            try:
                return brooding_batch_detail(brooding_path, batch_id)
            except OperationValidationError as exc:
                raise HTTPException(status_code=404, detail=exc.detail()) from exc

    @app.get("/api/operations/brooding/pending")
    def pending_brooding_records(
        limit: int = Query(default=100, ge=1, le=500),
    ) -> list[dict[str, object]]:
        with state_lock:
            return list_brooding_records(
                brooding_path,
                status="awaiting_confirmation",
                limit=limit,
            )

    @app.post("/api/operations/brooding/{record_type}/drafts", status_code=201)
    def draft_brooding_record(
        record_type: str,
        payload: BroodingDraftRequest,
    ) -> dict[str, object]:
        if record_type not in BROODING_RECORD_TYPES:
            raise HTTPException(status_code=422, detail="Tipo de cría no soportado.")
        brooding_payload = payload.model_dump(exclude={"source", "actor", "request_id"})
        with state_lock:
            try:
                record, event = create_brooding_draft(
                    brooding_path,
                    record_type,
                    brooding_payload,
                    incubation_records=load_incubation_records(incubation_path),
                    source=payload.source,
                    actor=payload.actor,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            append_brooding_event(brooding_path, event)
            log_event(
                "brooding_record_drafted",
                related_entry_id=record["id"],
                details={"record_type": record_type, "source": payload.source},
            )
        return record

    @app.post("/api/operations/brooding/{record_id}/confirm")
    def confirm_farm_brooding_record(
        record_id: str,
        payload: OperationConfirmRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                record, event = confirm_brooding_record(
                    brooding_path,
                    record_id,
                    payload.confirmation_code,
                    incubation_records=load_incubation_records(incubation_path),
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_brooding_event(brooding_path, event)
                log_event(
                    "brooding_record_applied",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    @app.post("/api/operations/brooding/{record_id}/cancel")
    def cancel_farm_brooding_record(
        record_id: str,
        payload: DraftCancelRequest,
    ) -> dict[str, object]:
        with state_lock:
            try:
                record, event = cancel_brooding_draft(
                    brooding_path,
                    record_id,
                    payload.confirmation_code,
                    payload.reason,
                    source=payload.source,
                    actor=payload.actor,
                    explicit_confirmation=payload.explicit_confirmation,
                    request_id=payload.request_id,
                )
            except OperationValidationError as exc:
                status_code = (
                    404 if exc.code == "not_found" else 409 if exc.code == "conflict" else 422
                )
                raise HTTPException(status_code=status_code, detail=exc.detail()) from exc
            if event is not None:
                append_brooding_event(brooding_path, event)
                log_event(
                    "brooding_record_cancelled",
                    related_entry_id=record_id,
                    details={"record_type": record["record_type"], "source": payload.source},
                )
        return record

    return app


def update_classification(entry: dict[str, object], submitted: dict[str, object]) -> None:
    intent = str(submitted.get("intent", "")).strip()
    primary_domain = str(submitted.get("primary_domain", "")).strip()
    risk_level = str(submitted.get("risk_level", "")).strip()
    if not intent or not primary_domain or risk_level not in {"bajo", "medio", "alto", "critico"}:
        raise HTTPException(status_code=422, detail="La clasificacion corregida no es valida.")
    classification = entry["classification"]
    classification["intent"] = intent
    classification["primary_domain"] = primary_domain
    classification["risk_level"] = risk_level
    classification["requires_confirmation"] = risk_level in {"medio", "alto", "critico"}
    entry["classification_provenance"] = {
        "intent": "corrected",
        "primary_domain": "corrected",
        "risk_level": "corrected",
    }


def resolve_review_decision(
    entry: dict[str, object],
    payload: ReviewRequest,
    note: str | None,
) -> tuple[str, str, str]:
    if payload.decision == "confirm":
        missing_fields = validate_structured_data(entry)
        if missing_fields:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Faltan datos obligatorios para confirmar la interpretacion.",
                    "missing_fields": missing_fields,
                },
            )
        correction_count = int(entry.get("review", {}).get("correction_count", 0))
        return "validated", "corrected" if correction_count else "accepted", "human_validation"
    if payload.decision == "needs_information":
        return "needs_information", "deferred", payload.reason or "source_information_missing"
    if payload.decision == "needs_correction":
        if not note:
            raise HTTPException(status_code=422, detail="Describe brevemente que debe corregirse.")
        return "needs_correction", "deferred", payload.reason or "correction_deferred"
    return "rejected", "rejected", payload.reason or "not_relevant"


app = create_app()
