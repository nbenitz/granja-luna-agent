from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import sys
from threading import Lock
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field


SRC_DIR = Path(__file__).resolve().parents[1]
RUNTIME_DIR = Path(__file__).resolve().parents[2]
STATIC_DIR = Path(__file__).resolve().parent / "static"
DEFAULT_INBOX_PATH = RUNTIME_DIR / "state" / "inbox.jsonl"
DEFAULT_USAGE_PATH = RUNTIME_DIR / "state" / "usage-events.jsonl"
DEFAULT_REVIEW_EVENTS_PATH = RUNTIME_DIR / "state" / "review-events.jsonl"

sys.path.insert(0, str(SRC_DIR))

from core.dry_run import build_dry_run  # noqa: E402
from core.inbox import (  # noqa: E402
    append_inbox_entry,
    build_inbox_entry,
    filter_inbox_entries,
    find_inbox_entry,
    load_inbox_entries,
    summarize_inbox,
    normalize_inbox_entry,
    record_inbox_correction,
    update_inbox_entry_review,
    write_inbox_entries,
)
from core.intent_forms import (  # noqa: E402
    ensure_structured_data,
    update_structured_values,
    validate_structured_data,
)
from core.usage_log import (  # noqa: E402
    append_usage_event,
    build_usage_event,
    load_usage_events,
    summarize_usage,
)
from core.review_log import (  # noqa: E402
    append_review_event,
    build_review_event,
    load_review_events,
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


def create_app(
    inbox_path: Path = DEFAULT_INBOX_PATH,
    usage_path: Path = DEFAULT_USAGE_PATH,
    review_events_path: Path = DEFAULT_REVIEW_EVENTS_PATH,
) -> FastAPI:
    app = FastAPI(title="Granja Luna", version="0.1.0", docs_url="/api/docs", redoc_url=None)
    state_lock = Lock()

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
                    raise HTTPException(status_code=422, detail="Esta entrada no tiene una compra editable.")
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
                raise HTTPException(status_code=422, detail="No se detectaron cambios para guardar.")
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
