from __future__ import annotations

from collections.abc import Mapping
from typing import Any


DEFAULT_CONTEXT_USED_FOR = ["classification", "risk", "missing_data"]
INFORMATION_STATUSES = {
    "draft",
    "pending_review",
    "confirmed",
    "confirmed_by_user",
    "legacy_reference",
    "archived",
}
CONTEXT_USED_FOR = {"classification", "risk", "missing_data"}


def normalize_context(
    context: str | Mapping[str, Any] | None,
    default_source: str = "cli_context",
) -> dict[str, Any] | None:
    if context is None:
        return None
    if isinstance(context, str):
        text = context.strip()
        source = default_source
        information_status = "pending_review"
        used_for = list(DEFAULT_CONTEXT_USED_FOR)
    else:
        raw_text = context.get("text") or context.get("source_context") or context.get("summary")
        text = str(raw_text).strip() if raw_text is not None else ""
        source = str(context.get("source", default_source))
        information_status = str(context.get("information_status", "pending_review"))
        raw_used_for = context.get("used_for", DEFAULT_CONTEXT_USED_FOR)
        used_for = [str(item) for item in raw_used_for] if isinstance(raw_used_for, list) else list(DEFAULT_CONTEXT_USED_FOR)

    if not text:
        return None
    if information_status not in INFORMATION_STATUSES:
        information_status = "pending_review"
    used_for = [item for item in used_for if item in CONTEXT_USED_FOR]

    return {
        "text": text,
        "source": source,
        "information_status": information_status,
        "used_for": used_for or list(DEFAULT_CONTEXT_USED_FOR),
    }


def build_analysis_text(text: str, context: dict[str, Any] | None) -> str:
    if not context:
        return text
    return f"{text}\n\nContexto/memoria auxiliar:\n{context['text']}"
