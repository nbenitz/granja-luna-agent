from __future__ import annotations

import hashlib
import json
import mimetypes
import re
import shutil
import sqlite3
import subprocess
from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


SCHEMA_VERSION = 4
SUPPORTED_EXTENSIONS = {".jpeg", ".jpg", ".mp4"}
IMAGE_EXTENSIONS = {".jpeg", ".jpg"}
FILENAME_CAPTURE_PATTERN = re.compile(
    r"^(?P<date>\d{8})_(?P<time>\d{6})(?:[^0-9].*)?$", re.IGNORECASE
)

MetadataReader = Callable[[Path, str], dict[str, Any]]


def connect_media_library(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    connection.execute("PRAGMA journal_mode = WAL")
    ensure_media_schema(connection)
    return connection


def ensure_media_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS media_schema (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_scan_runs (
            id TEXT PRIMARY KEY,
            root_path TEXT NOT NULL,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            status TEXT NOT NULL,
            files_seen INTEGER NOT NULL DEFAULT 0,
            errors INTEGER NOT NULL DEFAULT 0,
            summary_json TEXT
        );

        CREATE TABLE IF NOT EXISTS media_assets (
            id TEXT PRIMARY KEY,
            relative_path TEXT NOT NULL UNIQUE,
            original_name TEXT NOT NULL,
            media_kind TEXT NOT NULL CHECK (media_kind IN ('image', 'video')),
            mime_type TEXT NOT NULL,
            extension TEXT NOT NULL,
            size_bytes INTEGER NOT NULL,
            modified_at TEXT NOT NULL,
            captured_local_at TEXT,
            captured_at_source TEXT,
            sha256 TEXT NOT NULL,
            width INTEGER,
            height INTEGER,
            orientation INTEGER,
            duration_seconds REAL,
            video_codec TEXT,
            has_audio INTEGER,
            camera_make TEXT,
            camera_model TEXT,
            gps_present INTEGER,
            curation_status TEXT NOT NULL DEFAULT 'new',
            scan_error TEXT,
            first_seen_at TEXT NOT NULL,
            last_seen_at TEXT NOT NULL,
            is_missing INTEGER NOT NULL DEFAULT 0
        );

        CREATE INDEX IF NOT EXISTS idx_media_assets_kind
            ON media_assets(media_kind, is_missing);
        CREATE INDEX IF NOT EXISTS idx_media_assets_captured
            ON media_assets(captured_local_at, is_missing);
        CREATE INDEX IF NOT EXISTS idx_media_assets_sha256
            ON media_assets(sha256, is_missing);
        CREATE INDEX IF NOT EXISTS idx_media_assets_status
            ON media_assets(curation_status, is_missing);

        CREATE TABLE IF NOT EXISTS media_clusters (
            id TEXT PRIMARY KEY,
            cluster_type TEXT NOT NULL,
            label TEXT NOT NULL,
            threshold_seconds INTEGER,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_cluster_members (
            cluster_id TEXT NOT NULL REFERENCES media_clusters(id) ON DELETE CASCADE,
            asset_id TEXT NOT NULL REFERENCES media_assets(id) ON DELETE CASCADE,
            position INTEGER NOT NULL,
            PRIMARY KEY (cluster_id, asset_id)
        );

        CREATE INDEX IF NOT EXISTS idx_media_cluster_members_asset
            ON media_cluster_members(asset_id);

        CREATE TABLE IF NOT EXISTS media_asset_analysis (
            asset_id TEXT PRIMARY KEY REFERENCES media_assets(id) ON DELETE CASCADE,
            thumbnail_path TEXT NOT NULL,
            analysis_path TEXT NOT NULL,
            brightness_mean REAL NOT NULL,
            contrast_stddev REAL NOT NULL,
            sharpness_score REAL NOT NULL,
            perceptual_hash TEXT NOT NULL,
            warnings_json TEXT NOT NULL,
            analyzed_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_cluster_curation (
            cluster_id TEXT PRIMARY KEY REFERENCES media_clusters(id) ON DELETE CASCADE,
            editorial_intents_json TEXT NOT NULL,
            campaign_slots_json TEXT NOT NULL DEFAULT '[]',
            shot_types_json TEXT NOT NULL DEFAULT '[]',
            content_pillars_json TEXT NOT NULL DEFAULT '[]',
            subject_tags_json TEXT NOT NULL DEFAULT '[]',
            group_decision TEXT NOT NULL DEFAULT 'keep',
            primary_asset_id TEXT REFERENCES media_assets(id),
            primary_intent TEXT,
            primary_reasons_json TEXT NOT NULL DEFAULT '[]',
            primary_campaign_slots_json TEXT NOT NULL DEFAULT '[]',
            secondary_asset_id TEXT REFERENCES media_assets(id),
            secondary_intent TEXT,
            secondary_reasons_json TEXT NOT NULL DEFAULT '[]',
            secondary_campaign_slots_json TEXT NOT NULL DEFAULT '[]',
            note TEXT,
            updated_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS media_gemini_analyses (
            id TEXT PRIMARY KEY,
            cluster_id TEXT NOT NULL REFERENCES media_clusters(id) ON DELETE CASCADE,
            model TEXT NOT NULL,
            requested_at TEXT NOT NULL,
            result_json TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_media_gemini_cluster
            ON media_gemini_analyses(cluster_id, requested_at);

        CREATE TABLE IF NOT EXISTS media_upload_batches (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'uploading', 'completed', 'completed_with_errors')
            ),
            context TEXT,
            source TEXT NOT NULL,
            expected_count INTEGER NOT NULL,
            expected_bytes INTEGER NOT NULL,
            uploaded_count INTEGER NOT NULL DEFAULT 0,
            uploaded_bytes INTEGER NOT NULL DEFAULT 0,
            duplicate_count INTEGER NOT NULL DEFAULT 0,
            error_count INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT
        );

        CREATE TABLE IF NOT EXISTS media_upload_items (
            id TEXT PRIMARY KEY,
            batch_id TEXT NOT NULL REFERENCES media_upload_batches(id) ON DELETE CASCADE,
            position INTEGER NOT NULL,
            original_name TEXT NOT NULL,
            stored_relative_path TEXT NOT NULL UNIQUE,
            claimed_mime TEXT NOT NULL,
            detected_mime TEXT,
            expected_size INTEGER NOT NULL,
            actual_size INTEGER,
            sha256 TEXT,
            status TEXT NOT NULL CHECK (
                status IN ('pending', 'uploading', 'uploaded', 'duplicate', 'failed')
            ),
            error TEXT,
            asset_id TEXT REFERENCES media_assets(id),
            created_at TEXT NOT NULL,
            uploaded_at TEXT,
            UNIQUE(batch_id, position)
        );

        CREATE INDEX IF NOT EXISTS idx_media_upload_batches_created
            ON media_upload_batches(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_media_upload_items_batch
            ON media_upload_items(batch_id, position);
        """
    )
    curation_columns = {
        row[1] for row in connection.execute("PRAGMA table_info(media_cluster_curation)")
    }
    curation_column_definitions = {
        "campaign_slots_json": "TEXT NOT NULL DEFAULT '[]'",
        "shot_types_json": "TEXT NOT NULL DEFAULT '[]'",
        "content_pillars_json": "TEXT NOT NULL DEFAULT '[]'",
        "subject_tags_json": "TEXT NOT NULL DEFAULT '[]'",
        "group_decision": "TEXT NOT NULL DEFAULT 'keep'",
        "primary_reasons_json": "TEXT NOT NULL DEFAULT '[]'",
        "primary_campaign_slots_json": "TEXT NOT NULL DEFAULT '[]'",
        "secondary_reasons_json": "TEXT NOT NULL DEFAULT '[]'",
        "secondary_campaign_slots_json": "TEXT NOT NULL DEFAULT '[]'",
    }
    for column, definition in curation_column_definitions.items():
        if column not in curation_columns:
            connection.execute(
                f"ALTER TABLE media_cluster_curation ADD COLUMN {column} {definition}"
            )
    connection.execute(
        """
        UPDATE media_cluster_curation
        SET primary_campaign_slots_json = campaign_slots_json
        WHERE primary_asset_id IS NOT NULL
          AND primary_campaign_slots_json = '[]'
          AND secondary_campaign_slots_json = '[]'
          AND campaign_slots_json != '[]'
        """
    )
    if connection.execute(
        "SELECT 1 FROM media_schema WHERE version = ?", (SCHEMA_VERSION,)
    ).fetchone() is None:
        connection.execute(
            "INSERT INTO media_schema(version, applied_at) VALUES (?, ?)",
            (SCHEMA_VERSION, now_iso()),
        )
    connection.commit()


def scan_media_library(
    root: Path,
    database: Path,
    *,
    burst_seconds: int = 15,
    metadata_reader: MetadataReader | None = None,
) -> dict[str, Any]:
    if burst_seconds < 1:
        raise ValueError("burst_seconds must be at least 1")
    root = root.expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(f"Media root does not exist or is not a directory: {root}")

    reader = metadata_reader or read_technical_metadata
    scan_id = f"media-scan-{uuid4().hex[:12]}"
    started_at = now_iso()
    files_seen = 0
    errors = 0

    with connect_media_library(database) as connection:
        connection.execute(
            """
            INSERT INTO media_scan_runs(id, root_path, started_at, status)
            VALUES (?, ?, ?, 'running')
            """,
            (scan_id, str(root), started_at),
        )
        connection.execute("UPDATE media_assets SET is_missing = 1")

        for path in iter_supported_media(root):
            files_seen += 1
            kind = media_kind(path)
            stat = path.stat()
            relative_path = path.relative_to(root).as_posix()
            modified_at = datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(
                timespec="seconds"
            )
            captured_at, captured_source = capture_time_from_filename(path)
            scan_error: str | None = None
            technical: dict[str, Any] = {}
            cached = connection.execute(
                """
                SELECT * FROM media_assets
                WHERE relative_path = ? AND size_bytes = ? AND modified_at = ?
                    AND scan_error IS NULL
                """,
                (relative_path, stat.st_size, modified_at),
            ).fetchone()
            if cached is not None:
                technical = {
                    key: cached[key]
                    for key in (
                        "width",
                        "height",
                        "orientation",
                        "duration_seconds",
                        "video_codec",
                        "has_audio",
                        "camera_make",
                        "camera_model",
                        "gps_present",
                    )
                }
                if captured_at is None:
                    captured_at = cached["captured_local_at"]
                    captured_source = cached["captured_at_source"]
                sha256 = cached["sha256"]
            else:
                try:
                    technical = reader(path, kind)
                    if captured_at is None and technical.get("captured_local_at"):
                        captured_at = technical["captured_local_at"]
                        captured_source = "exif"
                except Exception as exc:  # A broken asset must not abort the library scan.
                    errors += 1
                    scan_error = f"{type(exc).__name__}: {exc}"[:1000]
                sha256 = sha256_file(path)

            values = {
                "relative_path": relative_path,
                "original_name": path.name,
                "media_kind": kind,
                "mime_type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                "extension": path.suffix.lower(),
                "size_bytes": stat.st_size,
                "modified_at": modified_at,
                "captured_local_at": captured_at,
                "captured_at_source": captured_source,
                "sha256": sha256,
                "width": technical.get("width"),
                "height": technical.get("height"),
                "orientation": technical.get("orientation"),
                "duration_seconds": technical.get("duration_seconds"),
                "video_codec": technical.get("video_codec"),
                "has_audio": bool_to_sql(technical.get("has_audio")),
                "camera_make": technical.get("camera_make"),
                "camera_model": technical.get("camera_model"),
                "gps_present": bool_to_sql(technical.get("gps_present")),
                "scan_error": scan_error,
                "last_seen_at": started_at,
            }
            upsert_asset(connection, values)

        rebuild_clusters(connection, burst_seconds=burst_seconds, created_at=started_at)
        summary = summarize_media_library(connection)
        connection.execute(
            """
            UPDATE media_scan_runs
            SET completed_at = ?, status = 'completed', files_seen = ?, errors = ?, summary_json = ?
            WHERE id = ?
            """,
            (now_iso(), files_seen, errors, json.dumps(summary, sort_keys=True), scan_id),
        )
        connection.commit()

    return {"scan_id": scan_id, "root": str(root), "database": str(database), **summary}


def iter_supported_media(root: Path) -> Iterator[Path]:
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix().lower()):
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS:
            yield path


def media_kind(path: Path) -> str:
    if path.suffix.lower() in IMAGE_EXTENSIONS:
        return "image"
    if path.suffix.lower() == ".mp4":
        return "video"
    raise ValueError(f"Unsupported media extension: {path.suffix.lower()}")


def capture_time_from_filename(path: Path) -> tuple[str | None, str | None]:
    match = FILENAME_CAPTURE_PATTERN.match(path.stem)
    if match is None:
        return None, None
    try:
        captured = datetime.strptime(
            f"{match.group('date')}{match.group('time')}", "%Y%m%d%H%M%S"
        )
    except ValueError:
        return None, None
    return captured.isoformat(timespec="seconds"), "filename"


def sha256_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        while chunk := file.read(chunk_size):
            digest.update(chunk)
    return digest.hexdigest()


def read_technical_metadata(path: Path, kind: str) -> dict[str, Any]:
    return read_image_metadata(path) if kind == "image" else read_video_metadata(path)


def read_image_metadata(path: Path) -> dict[str, Any]:
    try:
        from PIL import ExifTags, Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required to inspect image metadata") from exc

    with Image.open(path) as image:
        exif = image.getexif()
        captured = exif.get(ExifTags.Base.DateTimeOriginal) or exif.get(ExifTags.Base.DateTime)
        return {
            "width": image.width,
            "height": image.height,
            "orientation": integer_or_none(exif.get(ExifTags.Base.Orientation)),
            "camera_make": clean_text(exif.get(ExifTags.Base.Make)),
            "camera_model": clean_text(exif.get(ExifTags.Base.Model)),
            "gps_present": bool(exif.get_ifd(ExifTags.IFD.GPSInfo)),
            "captured_local_at": normalize_exif_datetime(captured),
        }


def read_video_metadata(path: Path) -> dict[str, Any]:
    if shutil.which("ffprobe"):
        return read_video_metadata_ffprobe(path)
    if shutil.which("gst-discoverer-1.0"):
        return read_video_metadata_gstreamer(path)
    raise RuntimeError("ffprobe or gst-discoverer-1.0 is required to inspect video metadata")


def read_video_metadata_ffprobe(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration:stream=codec_type,codec_name,width,height",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    payload = json.loads(result.stdout)
    streams = payload.get("streams", [])
    video = next((stream for stream in streams if stream.get("codec_type") == "video"), {})
    return {
        "width": integer_or_none(video.get("width")),
        "height": integer_or_none(video.get("height")),
        "duration_seconds": float_or_none(payload.get("format", {}).get("duration")),
        "video_codec": clean_text(video.get("codec_name")),
        "has_audio": any(stream.get("codec_type") == "audio" for stream in streams),
    }


def read_video_metadata_gstreamer(path: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["gst-discoverer-1.0", str(path)],
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    report = result.stdout
    duration_match = re.search(r"^  Duration: (\d+):(\d+):([0-9.]+)$", report, re.MULTILINE)
    width_match = re.search(r"^      Width: (\d+)$", report, re.MULTILINE)
    height_match = re.search(r"^      Height: (\d+)$", report, re.MULTILINE)
    codec_match = re.search(r"^    video #[0-9]+: (.+)$", report, re.MULTILINE)
    duration = None
    if duration_match:
        duration = (
            int(duration_match.group(1)) * 3600
            + int(duration_match.group(2)) * 60
            + float(duration_match.group(3))
        )
    return {
        "width": integer_or_none(width_match.group(1) if width_match else None),
        "height": integer_or_none(height_match.group(1) if height_match else None),
        "duration_seconds": duration,
        "video_codec": clean_text(codec_match.group(1) if codec_match else None),
        "has_audio": bool(re.search(r"^    audio #[0-9]+:", report, re.MULTILINE)),
    }


def upsert_asset(connection: sqlite3.Connection, values: dict[str, Any]) -> None:
    existing = connection.execute(
        "SELECT id, first_seen_at FROM media_assets WHERE relative_path = ?",
        (values["relative_path"],),
    ).fetchone()
    asset_id = existing["id"] if existing else f"asset-{uuid4().hex[:16]}"
    first_seen_at = existing["first_seen_at"] if existing else values["last_seen_at"]
    connection.execute(
        """
        INSERT INTO media_assets (
            id, relative_path, original_name, media_kind, mime_type, extension, size_bytes,
            modified_at, captured_local_at, captured_at_source, sha256, width, height, orientation,
            duration_seconds, video_codec, has_audio, camera_make, camera_model, gps_present,
            scan_error, first_seen_at, last_seen_at, is_missing
        ) VALUES (
            :id, :relative_path, :original_name, :media_kind, :mime_type, :extension, :size_bytes,
            :modified_at, :captured_local_at, :captured_at_source, :sha256, :width, :height,
            :orientation, :duration_seconds, :video_codec, :has_audio, :camera_make, :camera_model,
            :gps_present, :scan_error, :first_seen_at, :last_seen_at, 0
        )
        ON CONFLICT(relative_path) DO UPDATE SET
            original_name = excluded.original_name,
            media_kind = excluded.media_kind,
            mime_type = excluded.mime_type,
            extension = excluded.extension,
            size_bytes = excluded.size_bytes,
            modified_at = excluded.modified_at,
            captured_local_at = excluded.captured_local_at,
            captured_at_source = excluded.captured_at_source,
            sha256 = excluded.sha256,
            width = excluded.width,
            height = excluded.height,
            orientation = excluded.orientation,
            duration_seconds = excluded.duration_seconds,
            video_codec = excluded.video_codec,
            has_audio = excluded.has_audio,
            camera_make = excluded.camera_make,
            camera_model = excluded.camera_model,
            gps_present = excluded.gps_present,
            scan_error = excluded.scan_error,
            last_seen_at = excluded.last_seen_at,
            is_missing = 0
        """,
        {"id": asset_id, "first_seen_at": first_seen_at, **values},
    )


def rebuild_clusters(
    connection: sqlite3.Connection, *, burst_seconds: int, created_at: str
) -> None:
    connection.execute("DELETE FROM media_cluster_members")
    active_cluster_ids: list[str] = []
    rows = connection.execute(
        """
        SELECT id, relative_path, captured_local_at
        FROM media_assets
        WHERE media_kind = 'image' AND is_missing = 0 AND captured_local_at IS NOT NULL
        ORDER BY captured_local_at, relative_path
        """
    ).fetchall()

    groups: list[list[sqlite3.Row]] = []
    current: list[sqlite3.Row] = []
    previous: datetime | None = None
    for row in rows:
        captured = datetime.fromisoformat(row["captured_local_at"])
        if (
            previous is None
            or captured.date() != previous.date()
            or (captured - previous).total_seconds() > burst_seconds
        ):
            if len(current) >= 2:
                groups.append(current)
            current = [row]
        else:
            current.append(row)
        previous = captured
    if len(current) >= 2:
        groups.append(current)

    for group in groups:
        active_cluster_ids.append(insert_cluster(
            connection,
            cluster_type="temporal_burst",
            label=f"Rafaga {group[0]['captured_local_at']}",
            members=[row["id"] for row in group],
            threshold_seconds=burst_seconds,
            created_at=created_at,
        ))

    duplicate_groups = connection.execute(
        """
        SELECT sha256, GROUP_CONCAT(id) AS asset_ids
        FROM media_assets
        WHERE is_missing = 0
        GROUP BY sha256
        HAVING COUNT(*) > 1
        ORDER BY sha256
        """
    ).fetchall()
    for group in duplicate_groups:
        active_cluster_ids.append(insert_cluster(
            connection,
            cluster_type="exact_duplicate",
            label=f"Duplicado exacto {group['sha256'][:12]}",
            members=group["asset_ids"].split(","),
            threshold_seconds=None,
            created_at=created_at,
        ))

    if active_cluster_ids:
        placeholders = ",".join("?" for _ in active_cluster_ids)
        connection.execute(
            f"DELETE FROM media_clusters WHERE id NOT IN ({placeholders})",
            active_cluster_ids,
        )
    else:
        connection.execute("DELETE FROM media_clusters")


def insert_cluster(
    connection: sqlite3.Connection,
    *,
    cluster_type: str,
    label: str,
    members: list[str],
    threshold_seconds: int | None,
    created_at: str,
) -> str:
    seed = f"{cluster_type}|{'|'.join(sorted(members))}"
    cluster_id = f"cluster-{hashlib.sha256(seed.encode()).hexdigest()[:16]}"
    connection.execute(
        """
        INSERT INTO media_clusters(id, cluster_type, label, threshold_seconds, created_at)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            label = excluded.label,
            threshold_seconds = excluded.threshold_seconds
        """,
        (cluster_id, cluster_type, label, threshold_seconds, created_at),
    )
    connection.executemany(
        """
        INSERT INTO media_cluster_members(cluster_id, asset_id, position)
        VALUES (?, ?, ?)
        """,
        [(cluster_id, asset_id, position) for position, asset_id in enumerate(members, start=1)],
    )
    return cluster_id


def summarize_media_library(connection: sqlite3.Connection) -> dict[str, Any]:
    totals = connection.execute(
        """
        SELECT COUNT(*) AS total, COALESCE(SUM(size_bytes), 0) AS bytes,
            SUM(CASE WHEN media_kind = 'image' THEN 1 ELSE 0 END) AS images,
            SUM(CASE WHEN media_kind = 'video' THEN 1 ELSE 0 END) AS videos,
            SUM(CASE WHEN gps_present = 1 THEN 1 ELSE 0 END) AS gps_assets,
            SUM(CASE WHEN scan_error IS NOT NULL THEN 1 ELSE 0 END) AS errors
        FROM media_assets WHERE is_missing = 0
        """
    ).fetchone()
    cluster_rows = connection.execute(
        "SELECT cluster_type, COUNT(*) AS clusters FROM media_clusters GROUP BY cluster_type"
    ).fetchall()
    member_rows = connection.execute(
        """
        SELECT c.cluster_type, COUNT(DISTINCT m.asset_id) AS members
        FROM media_clusters c JOIN media_cluster_members m ON m.cluster_id = c.id
        GROUP BY c.cluster_type
        """
    ).fetchall()
    return {
        "total": totals["total"],
        "bytes": totals["bytes"],
        "images": totals["images"] or 0,
        "videos": totals["videos"] or 0,
        "gps_assets": totals["gps_assets"] or 0,
        "errors": totals["errors"] or 0,
        "missing": connection.execute(
            "SELECT COUNT(*) FROM media_assets WHERE is_missing = 1"
        ).fetchone()[0],
        "clusters": {row["cluster_type"]: row["clusters"] for row in cluster_rows},
        "cluster_members": {row["cluster_type"]: row["members"] for row in member_rows},
    }


def list_media_clusters(
    connection: sqlite3.Connection,
    *,
    cluster_type: str | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    parameters: list[Any] = []
    where = ""
    if cluster_type:
        where = "WHERE c.cluster_type = ?"
        parameters.append(cluster_type)
    limit_clause = ""
    if limit is not None:
        limit_clause = "LIMIT ?"
        parameters.append(max(limit, 0))
    rows = connection.execute(
        f"""
        SELECT c.id, c.cluster_type, c.label, c.threshold_seconds,
            COUNT(m.asset_id) AS item_count
        FROM media_clusters c JOIN media_cluster_members m ON m.cluster_id = c.id
        {where}
        GROUP BY c.id
        ORDER BY c.cluster_type, item_count DESC, c.label
        {limit_clause}
        """,
        parameters,
    ).fetchall()
    clusters: list[dict[str, Any]] = []
    for row in rows:
        members = connection.execute(
            """
            SELECT a.id, a.relative_path, a.captured_local_at, a.size_bytes
            FROM media_cluster_members m JOIN media_assets a ON a.id = m.asset_id
            WHERE m.cluster_id = ? ORDER BY m.position
            """,
            (row["id"],),
        ).fetchall()
        clusters.append(
            {
                "id": row["id"],
                "cluster_type": row["cluster_type"],
                "label": row["label"],
                "threshold_seconds": row["threshold_seconds"],
                "item_count": row["item_count"],
                "members": [dict(member) for member in members],
            }
        )
    return clusters


def normalize_exif_datetime(value: object) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return datetime.strptime(value.strip(), "%Y:%m:%d %H:%M:%S").isoformat(
            timespec="seconds"
        )
    except ValueError:
        return None


def clean_text(value: object) -> str | None:
    if value is None:
        return None
    return str(value).strip() or None


def integer_or_none(value: object) -> int | None:
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def float_or_none(value: object) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def bool_to_sql(value: object) -> int | None:
    if value is None:
        return None
    return 1 if bool(value) else 0


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")
