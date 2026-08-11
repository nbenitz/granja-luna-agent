"""Local, review-only artifacts produced by the Content Studio."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


class ContentDraftError(ValueError):
    """Raised when a requested draft is not a safe, supported local artifact."""


def list_content_drafts(root: Path, *, limit: int = 20) -> list[dict[str, object]]:
    if not root.exists():
        return []
    candidates = sorted(
        (
            path
            for path in root.iterdir()
            if path.is_file()
            and not path.is_symlink()
            and not path.name.startswith(".")
            and path.suffix.lower() == ".mp4"
        ),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return [_serialize_draft(path) for path in candidates[:limit]]


def resolve_content_draft(root: Path, filename: str) -> Path:
    if not filename or Path(filename).name != filename or filename.startswith("."):
        raise ContentDraftError("Borrador no encontrado.")
    if Path(filename).suffix.lower() != ".mp4":
        raise ContentDraftError("Borrador no encontrado.")
    resolved_root = root.resolve()
    candidate = (resolved_root / filename).resolve()
    if candidate.parent != resolved_root or not candidate.is_file() or candidate.is_symlink():
        raise ContentDraftError("Borrador no encontrado.")
    return candidate


def _serialize_draft(path: Path) -> dict[str, object]:
    stat = path.stat()
    return {
        "id": path.name,
        "filename": path.name,
        "size_bytes": stat.st_size,
        "updated_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
        "media_url": f"/api/content/drafts/{quote(path.name, safe='')}/media",
        "status": "local_draft_not_approved",
    }
