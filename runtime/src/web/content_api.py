"""HTTP boundary for local media uploads and the first Content Studio intake."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from pathlib import Path
from threading import Lock
from typing import Literal

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from core.content_requests import (
    ContentRequestError,
    create_content_request,
    find_content_request,
    load_content_requests,
)
from core.media_library import connect_media_library
from core.media_uploads import (
    MediaUploadError,
    begin_upload_item,
    complete_upload_batch,
    create_upload_batch,
    fail_upload_item,
    finish_upload_item,
    get_upload_batch,
    list_upload_batches,
    temporary_upload_path,
    validate_uploaded_file,
)


class UploadFileDescriptor(BaseModel):
    name: str = Field(min_length=1, max_length=500)
    size: int = Field(ge=1)
    type: str = Field(default="application/octet-stream", max_length=200)
    last_modified: int | None = Field(default=None, ge=0)


class UploadBatchRequest(BaseModel):
    files: list[UploadFileDescriptor] = Field(min_length=1, max_length=100)
    context: str | None = Field(default=None, max_length=4000)
    source: str = Field(default="content_web", min_length=1, max_length=100)


class ContentRequestPayload(BaseModel):
    instruction: str = Field(min_length=1, max_length=12000)
    objective: str | None = Field(default=None, max_length=1000)
    audience: str | None = Field(default=None, max_length=1000)
    channels: list[Literal["facebook", "instagram", "whatsapp", "otro"]] = Field(
        default_factory=list, max_length=4
    )
    content_type: Literal[
        "reel",
        "historia",
        "publicacion",
        "carrusel",
        "respuesta",
        "campana",
        "por_definir",
    ] = "por_definir"
    source_stage: Literal["actual", "prueba", "aspiracion", "futuro", "desconocido"] = (
        "desconocido"
    )
    call_to_action: str | None = Field(default=None, max_length=1000)
    notes: str | None = Field(default=None, max_length=4000)
    media_batch_ids: list[str] = Field(default_factory=list, max_length=20)


def build_content_router(
    *,
    media_database_path: Path,
    media_root: Path,
    content_requests_path: Path,
    state_lock: Lock,
    log_event: Callable[..., None],
    max_files: int = 100,
    max_file_bytes: int = 1024 * 1024 * 1024,
    max_batch_bytes: int = 4 * 1024 * 1024 * 1024,
    reserve_bytes: int = 512 * 1024 * 1024,
) -> APIRouter:
    router = APIRouter()

    @router.post("/api/media/upload-batches", status_code=201)
    def create_media_upload(payload: UploadBatchRequest) -> dict[str, object]:
        try:
            with state_lock, connect_media_library(media_database_path) as connection:
                batch = create_upload_batch(
                    connection,
                    files=[item.model_dump() for item in payload.files],
                    context=payload.context,
                    source=payload.source,
                    media_root=media_root,
                    max_files=max_files,
                    max_file_bytes=max_file_bytes,
                    max_batch_bytes=max_batch_bytes,
                    reserve_bytes=reserve_bytes,
                )
        except MediaUploadError as exc:
            raise _upload_http_error(exc) from exc
        log_event(
            "media_upload_batch_created",
            related_entry_id=str(batch["id"]),
            details={
                "file_count": int(batch["expected_count"]),
                "expected_bytes": int(batch["expected_bytes"]),
                "has_context": bool(batch.get("context")),
            },
        )
        return batch

    @router.get("/api/media/upload-batches")
    def recent_media_uploads(
        limit: int = Query(default=10, ge=1, le=50),
    ) -> list[dict[str, object]]:
        with state_lock, connect_media_library(media_database_path) as connection:
            return list_upload_batches(connection, limit=limit)

    @router.get("/api/media/upload-batches/{batch_id}")
    def media_upload(batch_id: str) -> dict[str, object]:
        try:
            with state_lock, connect_media_library(media_database_path) as connection:
                return get_upload_batch(connection, batch_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Tanda de carga no encontrada.") from exc

    @router.put("/api/media/upload-batches/{batch_id}/items/{item_id}")
    async def upload_media_item(
        batch_id: str, item_id: str, request: Request
    ) -> dict[str, object]:
        try:
            with state_lock, connect_media_library(media_database_path) as connection:
                item = begin_upload_item(connection, batch_id, item_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Archivo de la tanda no encontrado.") from exc
        except MediaUploadError as exc:
            raise _upload_http_error(exc) from exc
        if item["status"] in {"uploaded", "duplicate"}:
            return item

        temp_path = temporary_upload_path(media_root, batch_id, item_id)
        digest = hashlib.sha256()
        written = 0
        expected_size = int(item["expected_size"])
        try:
            with temp_path.open("wb") as target:
                async for chunk in request.stream():
                    if not chunk:
                        continue
                    written += len(chunk)
                    if written > max_file_bytes or written > expected_size:
                        raise MediaUploadError(
                            "El archivo recibido supera el tamaño declarado o permitido.",
                            code="file_too_large",
                        )
                    target.write(chunk)
                    digest.update(chunk)
            if written != expected_size:
                raise MediaUploadError(
                    "La carga quedó incompleta; podés volver a intentarla.",
                    code="incomplete_upload",
                )
            detected_mime = validate_uploaded_file(temp_path, str(item["original_name"]))
            with state_lock, connect_media_library(media_database_path) as connection:
                saved = finish_upload_item(
                    connection,
                    batch_id=batch_id,
                    item_id=item_id,
                    temp_path=temp_path,
                    media_root=media_root,
                    actual_size=written,
                    sha256=digest.hexdigest(),
                    detected_mime=detected_mime,
                )
            log_event(
                "media_upload_item_saved",
                related_entry_id=batch_id,
                details={"status": saved["status"], "size_bytes": written},
            )
            return saved
        except MediaUploadError as exc:
            temp_path.unlink(missing_ok=True)
            with state_lock, connect_media_library(media_database_path) as connection:
                fail_upload_item(
                    connection,
                    batch_id=batch_id,
                    item_id=item_id,
                    message=str(exc),
                )
            raise _upload_http_error(exc) from exc
        except Exception as exc:
            temp_path.unlink(missing_ok=True)
            with state_lock, connect_media_library(media_database_path) as connection:
                fail_upload_item(
                    connection,
                    batch_id=batch_id,
                    item_id=item_id,
                    message="No se pudo guardar el archivo.",
                )
            raise HTTPException(
                status_code=500, detail="No se pudo guardar el archivo. Podés reintentar."
            ) from exc

    @router.post("/api/media/upload-batches/{batch_id}/complete")
    def complete_media_upload(batch_id: str) -> dict[str, object]:
        try:
            with state_lock:
                batch = complete_upload_batch(
                    batch_id=batch_id,
                    media_root=media_root,
                    media_database_path=media_database_path,
                )
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Tanda de carga no encontrada.") from exc
        except MediaUploadError as exc:
            raise _upload_http_error(exc) from exc
        except (FileNotFoundError, RuntimeError) as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        log_event(
            "media_upload_batch_completed",
            related_entry_id=batch_id,
            details={
                "uploaded_count": int(batch["uploaded_count"]),
                "duplicate_count": int(batch["duplicate_count"]),
                "error_count": int(batch["error_count"]),
            },
        )
        return batch

    @router.post("/api/content/requests", status_code=201)
    def submit_content_request(payload: ContentRequestPayload) -> dict[str, object]:
        if payload.media_batch_ids:
            with state_lock, connect_media_library(media_database_path) as connection:
                known = {
                    row["id"]
                    for row in connection.execute(
                        "SELECT id FROM media_upload_batches WHERE id IN ({})".format(
                            ",".join("?" for _ in payload.media_batch_ids)
                        ),
                        tuple(payload.media_batch_ids),
                    ).fetchall()
                }
            if known != set(payload.media_batch_ids):
                raise HTTPException(
                    status_code=422,
                    detail="Una de las tandas vinculadas no existe en la biblioteca.",
                )
        try:
            with state_lock:
                request_item = create_content_request(
                    content_requests_path, payload.model_dump()
                )
        except ContentRequestError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        log_event(
            "content_request_created",
            related_entry_id=str(request_item["id"]),
            details={
                "channel_count": len(request_item["channels"]),
                "media_batch_count": len(request_item["media_batch_ids"]),
                "content_type": request_item["content_type"],
            },
        )
        return request_item

    @router.get("/api/content/requests")
    def content_requests(
        limit: int = Query(default=20, ge=1, le=100),
    ) -> list[dict[str, object]]:
        with state_lock:
            return load_content_requests(content_requests_path, limit=limit)

    @router.get("/api/content/requests/{request_id}")
    def content_request(request_id: str) -> dict[str, object]:
        try:
            with state_lock:
                return find_content_request(content_requests_path, request_id)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="Solicitud de contenido no encontrada.") from exc

    return router


def _upload_http_error(error: MediaUploadError) -> HTTPException:
    status = 413 if error.code in {"file_too_large", "batch_too_large"} else 507 if error.code == "insufficient_storage" else 409 if error.code in {"batch_closed", "batch_incomplete", "destination_conflict"} else 422
    return HTTPException(status_code=status, detail={"code": error.code, "message": str(error)})
