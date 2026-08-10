"""Safe, resumable-enough upload batches for the local media library.

The browser creates a batch, uploads one item at a time and completes the batch only
after every item reached a terminal state. Originals stay local and are never served
by this module.
"""

from __future__ import annotations

import hashlib
import os
import re
import shutil
import sqlite3
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Iterable
from uuid import uuid4

from .media_library import connect_media_library, now_iso, read_technical_metadata, upsert_asset


ALLOWED_EXTENSIONS = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".mp4": "video/mp4"}
TERMINAL_ITEM_STATUSES = {"uploaded", "duplicate", "failed"}
SAFE_FILENAME_PATTERN = re.compile(r"[^A-Za-z0-9._-]+")


class MediaUploadError(ValueError):
    def __init__(self, message: str, *, code: str = "invalid_upload") -> None:
        super().__init__(message)
        self.code = code


def create_upload_batch(
    connection: sqlite3.Connection,
    *,
    files: list[dict[str, Any]],
    context: str | None,
    source: str,
    media_root: Path,
    max_files: int,
    max_file_bytes: int,
    max_batch_bytes: int,
    reserve_bytes: int,
) -> dict[str, Any]:
    if not files:
        raise MediaUploadError("Elegí al menos una foto o un video.", code="empty_batch")
    if len(files) > max_files:
        raise MediaUploadError(
            f"La tanda admite hasta {max_files} archivos.", code="too_many_files"
        )

    normalized: list[dict[str, Any]] = []
    total_bytes = 0
    for position, file in enumerate(files, start=1):
        supplied_name = str(file.get("name") or "").strip()
        original_name = Path(supplied_name.replace("\\", "/")).name
        expected_size = _positive_int(file.get("size"))
        claimed_mime = str(file.get("type") or "application/octet-stream")[:200]
        if not original_name:
            raise MediaUploadError("Uno de los archivos no tiene nombre.")
        extension = Path(original_name).suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            raise MediaUploadError(
                f"{original_name}: sólo se admiten JPG, JPEG y MP4.",
                code="unsupported_type",
            )
        if expected_size < 1:
            raise MediaUploadError(f"{original_name}: el archivo está vacío.", code="empty_file")
        if expected_size > max_file_bytes:
            raise MediaUploadError(
                f"{original_name}: supera el límite de {_format_bytes(max_file_bytes)}.",
                code="file_too_large",
            )
        total_bytes += expected_size
        normalized.append(
            {
                "position": position,
                "original_name": original_name[:500],
                "expected_size": expected_size,
                "claimed_mime": claimed_mime,
                "extension": extension,
            }
        )
    if total_bytes > max_batch_bytes:
        raise MediaUploadError(
            f"La tanda supera el límite de {_format_bytes(max_batch_bytes)}.",
            code="batch_too_large",
        )

    media_root.mkdir(parents=True, exist_ok=True)
    free_bytes = shutil.disk_usage(media_root).free
    if free_bytes - total_bytes < reserve_bytes:
        raise MediaUploadError(
            "No hay espacio libre suficiente para guardar la tanda con seguridad.",
            code="insufficient_storage",
        )

    batch_id = f"upload-{uuid4().hex[:16]}"
    created_at = now_iso()
    date_path = datetime.now().astimezone().strftime("%Y/%m/%d")
    connection.execute(
        """
        INSERT INTO media_upload_batches(
            id, status, context, source, expected_count, expected_bytes, created_at
        ) VALUES (?, 'pending', ?, ?, ?, ?, ?)
        """,
        (batch_id, _clean_optional(context, 4000), source[:100], len(files), total_bytes, created_at),
    )
    for file in normalized:
        item_id = f"upload-item-{uuid4().hex[:16]}"
        safe_name = sanitize_filename(file["original_name"])
        stored_relative_path = (
            f"imports/{date_path}/{batch_id}/"
            f"{file['position']:03d}-{item_id.removeprefix('upload-item-')[:8]}-{safe_name}"
        )
        connection.execute(
            """
            INSERT INTO media_upload_items(
                id, batch_id, position, original_name, stored_relative_path, claimed_mime,
                expected_size, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'pending', ?)
            """,
            (
                item_id,
                batch_id,
                file["position"],
                file["original_name"],
                stored_relative_path,
                file["claimed_mime"],
                file["expected_size"],
                created_at,
            ),
        )
    connection.commit()
    return get_upload_batch(connection, batch_id)


def begin_upload_item(
    connection: sqlite3.Connection, batch_id: str, item_id: str
) -> dict[str, Any]:
    batch = _batch_row(connection, batch_id)
    if batch["status"] not in {"pending", "uploading", "completed_with_errors"}:
        raise MediaUploadError("La tanda ya no acepta archivos.", code="batch_closed")
    row = connection.execute(
        "SELECT * FROM media_upload_items WHERE id = ? AND batch_id = ?",
        (item_id, batch_id),
    ).fetchone()
    if row is None:
        raise KeyError(item_id)
    if row["status"] in {"uploaded", "duplicate"}:
        return dict(row)
    connection.execute(
        "UPDATE media_upload_items SET status = 'uploading', error = NULL WHERE id = ?",
        (item_id,),
    )
    connection.execute(
        "UPDATE media_upload_batches SET status = 'uploading', completed_at = NULL WHERE id = ?",
        (batch_id,),
    )
    connection.commit()
    return dict(row)


def temporary_upload_path(media_root: Path, batch_id: str, item_id: str) -> Path:
    path = media_root / ".uploads" / batch_id / f"{item_id}.part"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def write_upload_stream(
    stream: BinaryIO,
    destination: Path,
    *,
    expected_size: int,
    max_file_bytes: int,
    chunk_size: int = 1024 * 1024,
) -> tuple[int, str]:
    """Synchronous helper used by tests and non-ASGI clients."""
    digest = hashlib.sha256()
    written = 0
    try:
        with destination.open("wb") as target:
            while chunk := stream.read(chunk_size):
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
                "La carga quedó incompleta; conservamos la tanda para reintentar.",
                code="incomplete_upload",
            )
        return written, digest.hexdigest()
    except Exception:
        destination.unlink(missing_ok=True)
        raise


def validate_uploaded_file(path: Path, original_name: str) -> str:
    extension = Path(original_name).suffix.lower()
    expected_mime = ALLOWED_EXTENSIONS.get(extension)
    if expected_mime is None:
        raise MediaUploadError("Tipo de archivo no admitido.", code="unsupported_type")
    with path.open("rb") as file:
        header = file.read(32)
    if extension in {".jpg", ".jpeg"}:
        if not header.startswith(b"\xff\xd8\xff"):
            raise MediaUploadError(
                "El archivo no contiene una imagen JPEG válida.", code="invalid_signature"
            )
        try:
            from PIL import Image

            with Image.open(path) as image:
                image.verify()
        except Exception as exc:
            raise MediaUploadError(
                "La imagen está dañada o incompleta.", code="invalid_media"
            ) from exc
    else:
        if len(header) < 12 or header[4:8] != b"ftyp":
            raise MediaUploadError(
                "El archivo no contiene un video MP4 válido.", code="invalid_signature"
            )
        try:
            read_technical_metadata(path, "video")
        except Exception as exc:
            raise MediaUploadError(
                "El video está dañado, incompleto o usa un contenedor no compatible.",
                code="invalid_media",
            ) from exc
    return expected_mime


def finish_upload_item(
    connection: sqlite3.Connection,
    *,
    batch_id: str,
    item_id: str,
    temp_path: Path,
    media_root: Path,
    actual_size: int,
    sha256: str,
    detected_mime: str,
) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM media_upload_items WHERE id = ? AND batch_id = ?",
        (item_id, batch_id),
    ).fetchone()
    if row is None:
        temp_path.unlink(missing_ok=True)
        raise KeyError(item_id)

    duplicate = connection.execute(
        """
        SELECT id FROM media_assets
        WHERE sha256 = ? AND is_missing = 0
        ORDER BY first_seen_at LIMIT 1
        """,
        (sha256,),
    ).fetchone()
    batch_duplicate = connection.execute(
        """
        SELECT id FROM media_upload_items
        WHERE batch_id = ? AND id != ? AND sha256 = ? AND status = 'uploaded'
        ORDER BY position LIMIT 1
        """,
        (batch_id, item_id, sha256),
    ).fetchone()
    if duplicate is not None or batch_duplicate is not None:
        temp_path.unlink(missing_ok=True)
        connection.execute(
            """
            UPDATE media_upload_items
            SET status = 'duplicate', actual_size = ?, sha256 = ?, detected_mime = ?,
                asset_id = ?, uploaded_at = ?, error = NULL
            WHERE id = ?
            """,
            (
                actual_size,
                sha256,
                detected_mime,
                duplicate["id"] if duplicate is not None else None,
                now_iso(),
                item_id,
            ),
        )
    else:
        final_path = safe_stored_path(media_root, str(row["stored_relative_path"]))
        final_path.parent.mkdir(parents=True, exist_ok=True)
        if final_path.exists():
            temp_path.unlink(missing_ok=True)
            raise MediaUploadError(
                "Ya existe un archivo con el destino reservado.", code="destination_conflict"
            )
        os.replace(temp_path, final_path)
        connection.execute(
            """
            UPDATE media_upload_items
            SET status = 'uploaded', actual_size = ?, sha256 = ?, detected_mime = ?,
                uploaded_at = ?, error = NULL
            WHERE id = ?
            """,
            (actual_size, sha256, detected_mime, now_iso(), item_id),
        )
    _refresh_batch_totals(connection, batch_id)
    connection.commit()
    return get_upload_item(connection, batch_id, item_id)


def fail_upload_item(
    connection: sqlite3.Connection,
    *,
    batch_id: str,
    item_id: str,
    message: str,
) -> dict[str, Any]:
    connection.execute(
        """
        UPDATE media_upload_items
        SET status = 'failed', error = ?, uploaded_at = ?
        WHERE id = ? AND batch_id = ?
        """,
        (message[:1000], now_iso(), item_id, batch_id),
    )
    _refresh_batch_totals(connection, batch_id)
    connection.commit()
    return get_upload_item(connection, batch_id, item_id)


def complete_upload_batch(
    *,
    batch_id: str,
    media_root: Path,
    media_database_path: Path,
) -> dict[str, Any]:
    with connect_media_library(media_database_path) as connection:
        batch = get_upload_batch(connection, batch_id)
        unfinished = [
            item for item in batch["items"] if item["status"] not in TERMINAL_ITEM_STATUSES
        ]
        if unfinished:
            raise MediaUploadError(
                "Todavía hay archivos pendientes de subir.", code="batch_incomplete"
            )
        uploaded_paths = [
            safe_stored_path(media_root, item["stored_relative_path"])
            for item in batch["items"]
            if item["status"] == "uploaded" and not item.get("asset_id")
        ]

    if uploaded_paths:
        ingested = ingest_uploaded_paths(
            uploaded_paths,
            root=media_root,
            database=media_database_path,
        )
    else:
        ingested = []

    with connect_media_library(media_database_path) as refreshed:
        for asset in ingested:
            item = refreshed.execute(
                """
                SELECT id, original_name FROM media_upload_items
                WHERE batch_id = ? AND stored_relative_path = ?
                """,
                (batch_id, asset["relative_path"]),
            ).fetchone()
            if item is None:
                continue
            refreshed.execute(
                """
                UPDATE media_upload_items SET asset_id = ?
                WHERE id = ?
                """,
                (asset["id"], item["id"]),
            )
            refreshed.execute(
                "UPDATE media_assets SET original_name = ? WHERE id = ?",
                (item["original_name"], asset["id"]),
            )
        refreshed.execute(
            """
            UPDATE media_upload_items
            SET asset_id = (
                SELECT a.id FROM media_assets a
                WHERE a.sha256 = media_upload_items.sha256 AND a.is_missing = 0
                ORDER BY a.first_seen_at LIMIT 1
            )
            WHERE batch_id = ? AND status = 'duplicate' AND asset_id IS NULL
            """,
            (batch_id,),
        )
        errors = refreshed.execute(
            "SELECT COUNT(*) FROM media_upload_items WHERE batch_id = ? AND status = 'failed'",
            (batch_id,),
        ).fetchone()[0]
        refreshed.execute(
            """
            UPDATE media_upload_batches
            SET status = ?, completed_at = ? WHERE id = ?
            """,
            ("completed_with_errors" if errors else "completed", now_iso(), batch_id),
        )
        _refresh_batch_totals(refreshed, batch_id)
        refreshed.commit()
        return get_upload_batch(refreshed, batch_id)


def ingest_uploaded_paths(
    paths: Iterable[Path],
    *,
    root: Path,
    database: Path,
) -> list[dict[str, Any]]:
    """Add only the uploaded paths without rebuilding existing human-curated bursts."""
    root = root.expanduser().resolve()
    seen_at = now_iso()
    results: list[dict[str, Any]] = []
    with connect_media_library(database) as connection:
        for candidate in paths:
            path = candidate.expanduser().resolve()
            try:
                relative_path = path.relative_to(root).as_posix()
            except ValueError as exc:
                raise MediaUploadError("El archivo quedó fuera de la biblioteca local.") from exc
            if not path.is_file():
                raise FileNotFoundError(path)
            extension = path.suffix.lower()
            kind = "image" if extension in {".jpg", ".jpeg"} else "video"
            stat = path.stat()
            modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(
                timespec="seconds"
            )
            technical = read_technical_metadata(path, kind)
            captured_at, captured_source = _capture_time_from_name(path)
            if captured_at is None and technical.get("captured_local_at"):
                captured_at = str(technical["captured_local_at"])
                captured_source = "exif"
            values = {
                "relative_path": relative_path,
                "original_name": path.name,
                "media_kind": kind,
                "mime_type": ALLOWED_EXTENSIONS[extension],
                "extension": extension,
                "size_bytes": stat.st_size,
                "modified_at": modified_at,
                "captured_local_at": captured_at,
                "captured_at_source": captured_source,
                "sha256": _sha256_file(path),
                "width": technical.get("width"),
                "height": technical.get("height"),
                "orientation": technical.get("orientation"),
                "duration_seconds": technical.get("duration_seconds"),
                "video_codec": technical.get("video_codec"),
                "has_audio": _bool_to_sql(technical.get("has_audio")),
                "camera_make": technical.get("camera_make"),
                "camera_model": technical.get("camera_model"),
                "gps_present": _bool_to_sql(technical.get("gps_present")),
                "scan_error": None,
                "last_seen_at": seen_at,
            }
            upsert_asset(connection, values)
            asset = connection.execute(
                "SELECT * FROM media_assets WHERE relative_path = ?", (relative_path,)
            ).fetchone()
            results.append(dict(asset))
        connection.commit()
    return results


def get_upload_item(
    connection: sqlite3.Connection, batch_id: str, item_id: str
) -> dict[str, Any]:
    row = connection.execute(
        "SELECT * FROM media_upload_items WHERE id = ? AND batch_id = ?",
        (item_id, batch_id),
    ).fetchone()
    if row is None:
        raise KeyError(item_id)
    return _serialize_item(row)


def get_upload_batch(connection: sqlite3.Connection, batch_id: str) -> dict[str, Any]:
    batch = _batch_row(connection, batch_id)
    items = connection.execute(
        "SELECT * FROM media_upload_items WHERE batch_id = ? ORDER BY position",
        (batch_id,),
    ).fetchall()
    return {**dict(batch), "items": [_serialize_item(item) for item in items]}


def list_upload_batches(
    connection: sqlite3.Connection, *, limit: int = 10
) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT id FROM media_upload_batches ORDER BY created_at DESC LIMIT ?",
        (max(1, min(limit, 50)),),
    ).fetchall()
    return [get_upload_batch(connection, row["id"]) for row in rows]


def safe_stored_path(media_root: Path, relative_path: str) -> Path:
    root = media_root.expanduser().resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise MediaUploadError("Ruta de archivo inválida.", code="unsafe_path") from exc
    return path


def sanitize_filename(name: str) -> str:
    basename = Path(name.replace("\\", "/")).name
    normalized = unicodedata.normalize("NFKD", basename).encode("ascii", "ignore").decode()
    normalized = SAFE_FILENAME_PATTERN.sub("-", normalized).strip(".-_")
    extension = Path(basename).suffix.lower()
    stem = Path(normalized).stem[:120].strip(".-_") or "archivo"
    return f"{stem}{extension}"


def _refresh_batch_totals(connection: sqlite3.Connection, batch_id: str) -> None:
    totals = connection.execute(
        """
        SELECT
            SUM(CASE WHEN status = 'uploaded' THEN 1 ELSE 0 END) AS uploaded_count,
            SUM(CASE WHEN status = 'duplicate' THEN 1 ELSE 0 END) AS duplicate_count,
            SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) AS error_count,
            COALESCE(SUM(CASE WHEN status IN ('uploaded', 'duplicate') THEN actual_size ELSE 0 END), 0)
                AS uploaded_bytes
        FROM media_upload_items WHERE batch_id = ?
        """,
        (batch_id,),
    ).fetchone()
    connection.execute(
        """
        UPDATE media_upload_batches
        SET uploaded_count = ?, duplicate_count = ?, error_count = ?, uploaded_bytes = ?
        WHERE id = ?
        """,
        (
            totals["uploaded_count"] or 0,
            totals["duplicate_count"] or 0,
            totals["error_count"] or 0,
            totals["uploaded_bytes"] or 0,
            batch_id,
        ),
    )


def _batch_row(connection: sqlite3.Connection, batch_id: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM media_upload_batches WHERE id = ?", (batch_id,)
    ).fetchone()
    if row is None:
        raise KeyError(batch_id)
    return row


def _serialize_item(row: sqlite3.Row) -> dict[str, Any]:
    item = dict(row)
    asset_id = item.get("asset_id")
    item["thumbnail_url"] = f"/api/media/assets/{asset_id}/thumbnail" if asset_id else None
    item["preview_url"] = f"/api/media/assets/{asset_id}/preview" if asset_id else None
    return item


def _capture_time_from_name(path: Path) -> tuple[str | None, str | None]:
    from .media_library import capture_time_from_filename

    parts = path.name.split("-", 2)
    original_name = parts[2] if len(parts) == 3 else path.name
    return capture_time_from_filename(Path(original_name))


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(1024 * 1024):
            digest.update(chunk)
    return digest.hexdigest()


def _positive_int(value: object) -> int:
    try:
        return int(value)
    except (TypeError, ValueError) as exc:
        raise MediaUploadError("El tamaño declarado no es válido.") from exc


def _bool_to_sql(value: object) -> int | None:
    if value is None:
        return None
    return 1 if bool(value) else 0


def _clean_optional(value: str | None, limit: int) -> str | None:
    cleaned = (value or "").strip()
    return cleaned[:limit] or None


def _format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KB", "MB", "GB"):
        if amount < 1024 or unit == "GB":
            return f"{amount:.0f} {unit}"
        amount /= 1024
    return f"{value} B"
