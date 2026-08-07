#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.media_library import (  # noqa: E402
    connect_media_library,
    list_media_clusters,
    scan_media_library,
    summarize_media_library,
)


def fake_metadata(path: Path, kind: str) -> dict[str, object]:
    if kind == "image":
        return {
            "width": 4000,
            "height": 3000,
            "orientation": 1,
            "camera_make": "Test",
            "camera_model": "Camera",
            "gps_present": path.name.endswith("000000.jpg"),
        }
    return {
        "width": 1920,
        "height": 1080,
        "duration_seconds": 12.5,
        "video_codec": "hevc",
        "has_audio": True,
    }


class MediaLibraryTests(unittest.TestCase):
    def test_scan_persists_assets_and_builds_temporal_and_exact_clusters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "inbox"
            root.mkdir()
            database = Path(tmpdir) / "media.sqlite3"
            (root / "20260801_000000.jpg").write_bytes(b"same-image")
            (root / "20260801_000010.jpg").write_bytes(b"same-image")
            (root / "20260801_000040.jpg").write_bytes(b"different-image")
            (root / "20260801_000100.mp4").write_bytes(b"video")

            result = scan_media_library(
                root, database, burst_seconds=15, metadata_reader=fake_metadata
            )

            self.assertEqual(result["total"], 4)
            self.assertEqual(result["images"], 3)
            self.assertEqual(result["videos"], 1)
            self.assertEqual(result["gps_assets"], 1)
            self.assertEqual(result["clusters"]["temporal_burst"], 1)
            self.assertEqual(result["cluster_members"]["temporal_burst"], 2)
            self.assertEqual(result["clusters"]["exact_duplicate"], 1)

            with connect_media_library(database) as connection:
                temporal = list_media_clusters(connection, cluster_type="temporal_burst")
                exact = list_media_clusters(connection, cluster_type="exact_duplicate")
            self.assertEqual(temporal[0]["item_count"], 2)
            self.assertEqual(exact[0]["item_count"], 2)

    def test_rescan_is_idempotent_and_marks_removed_assets_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "inbox"
            root.mkdir()
            database = Path(tmpdir) / "media.sqlite3"
            first = root / "20260801_120000.jpg"
            second = root / "20260801_120005.jpg"
            first.write_bytes(b"first")
            second.write_bytes(b"second")

            initial = scan_media_library(root, database, metadata_reader=fake_metadata)
            repeated = scan_media_library(root, database, metadata_reader=fake_metadata)
            second.unlink()
            removed = scan_media_library(root, database, metadata_reader=fake_metadata)

            self.assertEqual(initial["total"], 2)
            self.assertEqual(repeated["total"], 2)
            self.assertEqual(removed["total"], 1)
            self.assertEqual(removed["missing"], 1)
            with connect_media_library(database) as connection:
                summary = summarize_media_library(connection)
                stored = connection.execute("SELECT COUNT(*) FROM media_assets").fetchone()[0]
            self.assertEqual(summary["total"], 1)
            self.assertEqual(stored, 2)

    def test_rescan_reuses_metadata_when_file_is_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "inbox"
            root.mkdir()
            database = Path(tmpdir) / "media.sqlite3"
            (root / "20260801_120000.jpg").write_bytes(b"image")
            calls = 0

            def counting_metadata(path: Path, kind: str) -> dict[str, object]:
                nonlocal calls
                calls += 1
                return fake_metadata(path, kind)

            scan_media_library(root, database, metadata_reader=counting_metadata)
            scan_media_library(root, database, metadata_reader=counting_metadata)

            self.assertEqual(calls, 1)


if __name__ == "__main__":
    unittest.main()
