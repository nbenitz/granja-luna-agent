"""Append-only intake for the Content Studio.

This module deliberately captures intent and evidence without pretending that a model
already produced a brief or a publishable artifact. Later agent runs can reference the
request id and append versioned artifacts without turning chat history into source of truth.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


SUPPORTED_CHANNELS = {"facebook", "instagram", "whatsapp", "otro"}
SUPPORTED_CONTENT_TYPES = {
    "reel",
    "historia",
    "publicacion",
    "carrusel",
    "respuesta",
    "campana",
    "por_definir",
}
SUPPORTED_SOURCE_STAGES = {"actual", "prueba", "aspiracion", "futuro", "desconocido"}


class ContentRequestError(ValueError):
    pass


def create_content_request(path: Path, payload: dict[str, Any]) -> dict[str, Any]:
    instruction = str(payload.get("instruction") or "").strip()
    if not instruction:
        raise ContentRequestError("Contame qué contenido querés preparar.")
    channels = _unique_tokens(payload.get("channels"), SUPPORTED_CHANNELS)
    content_type = str(payload.get("content_type") or "por_definir")
    if content_type not in SUPPORTED_CONTENT_TYPES:
        raise ContentRequestError("El tipo de contenido no está soportado.")
    source_stage = str(payload.get("source_stage") or "desconocido")
    if source_stage not in SUPPORTED_SOURCE_STAGES:
        raise ContentRequestError("El estado de la información no es válido.")
    media_batch_ids = [
        item[:100]
        for item in _unique_strings(payload.get("media_batch_ids"))
        if item.startswith("upload-")
    ][:20]
    created_at = datetime.now().astimezone().isoformat(timespec="seconds")
    questions = _next_questions(
        objective=_optional(payload.get("objective"), 1000),
        audience=_optional(payload.get("audience"), 1000),
        channels=channels,
        source_stage=source_stage,
        media_batch_ids=media_batch_ids,
    )
    request = {
        "schema_version": "content-request.v1",
        "id": f"content-{uuid4().hex[:16]}",
        "created_at": created_at,
        "updated_at": created_at,
        "status": "idea",
        "instruction": instruction[:12000],
        "objective": _optional(payload.get("objective"), 1000),
        "audience": _optional(payload.get("audience"), 1000),
        "channels": channels,
        "content_type": content_type,
        "source_stage": source_stage,
        "call_to_action": _optional(payload.get("call_to_action"), 1000),
        "notes": _optional(payload.get("notes"), 4000),
        "media_batch_ids": media_batch_ids,
        "questions_to_resolve": questions,
        "risk_level": "bajo",
        "publication_requires_approval": True,
        "workflow": [
            {"stage": "idea", "status": "complete"},
            {"stage": "brief", "status": "pending"},
            {"stage": "draft", "status": "pending"},
            {"stage": "review", "status": "pending"},
            {"stage": "approval", "status": "pending"},
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(request, ensure_ascii=False, sort_keys=True) + "\n")
    return request


def load_content_requests(path: Path, *, limit: int = 20) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    requests_by_id: dict[str, dict[str, Any]] = {}
    request_order: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict) and item.get("id"):
            request_id = str(item["id"])
            if request_id not in requests_by_id:
                request_order.append(request_id)
            requests_by_id[request_id] = item
    requests = [requests_by_id[request_id] for request_id in request_order]
    return list(reversed(requests[-max(1, min(limit, 100)) :]))


def find_content_request(path: Path, request_id: str) -> dict[str, Any]:
    for item in load_content_requests(path, limit=100):
        if item.get("id") == request_id:
            return item
    raise KeyError(request_id)


def supersede_content_request(
    path: Path,
    *,
    request_id: str,
    replacement_id: str,
    reason: str,
) -> dict[str, Any]:
    if request_id == replacement_id:
        raise ContentRequestError("La solicitud no puede reemplazarse a sí misma.")
    current = find_content_request(path, request_id)
    replacement = find_content_request(path, replacement_id)
    if current.get("status") == "superseded":
        if current.get("superseded_by") == replacement_id:
            return current
        raise ContentRequestError("La solicitud ya fue reemplazada por otra.")
    updated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    revision = {
        **current,
        "updated_at": updated_at,
        "status": "superseded",
        "superseded_by": replacement["id"],
        "supersession_reason": str(reason or "").strip()[:1000],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(revision, ensure_ascii=False, sort_keys=True) + "\n")
    return revision


def _next_questions(
    *,
    objective: str | None,
    audience: str | None,
    channels: list[str],
    source_stage: str,
    media_batch_ids: list[str],
) -> list[dict[str, str]]:
    questions: list[dict[str, str]] = []
    if not objective:
        questions.append({"field": "objective", "question": "¿Qué debería lograr esta pieza?"})
    if not audience:
        questions.append({"field": "audience", "question": "¿A quién queremos llegar?"})
    if not channels:
        questions.append({"field": "channels", "question": "¿En qué canal se publicaría?"})
    if source_stage == "desconocido":
        questions.append(
            {"field": "source_stage", "question": "¿Es algo actual, una prueba o una idea futura?"}
        )
    if not media_batch_ids:
        questions.append(
            {"field": "media", "question": "¿Qué fotos o videos reales respaldan la idea?"}
        )
    return questions


def _unique_tokens(value: object, allowed: set[str]) -> list[str]:
    return [item for item in _unique_strings(value) if item in allowed]


def _unique_strings(value: object) -> list[str]:
    if not isinstance(value, list):
        return []
    result: list[str] = []
    for raw in value:
        item = str(raw or "").strip()
        if item and item not in result:
            result.append(item)
    return result


def _optional(value: object, limit: int) -> str | None:
    cleaned = str(value or "").strip()
    return cleaned[:limit] or None
