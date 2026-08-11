#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from web.app import create_app  # noqa: E402


class ContentDraftPreviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.content_requests = self.root / "content-state" / "content-requests.jsonl"
        self.drafts = self.content_requests.parent / "social-drafts"
        self.drafts.mkdir(parents=True)
        self.video = self.drafts / "2026-08-11-reel-prueba-v1.mp4"
        self.video.write_bytes(b"0123456789abcdef")
        (self.drafts / "privado.jpg").write_bytes(b"not listed")
        nested = self.drafts / "nested"
        nested.mkdir()
        (nested / "oculto.mp4").write_bytes(b"not listed")
        self.client = TestClient(
            create_app(
                inbox_path=self.root / "inbox.jsonl",
                usage_path=self.root / "usage.jsonl",
                review_events_path=self.root / "review.jsonl",
                content_requests_path=self.content_requests,
                media_database_path=self.root / "media.sqlite3",
                media_root=self.root / "media",
                media_derivatives_path=self.root / "derivatives",
                env_file=self.root / ".env",
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def test_lists_only_top_level_mp4_drafts(self) -> None:
        response = self.client.get("/api/content/drafts")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        draft = response.json()[0]
        self.assertEqual(draft["filename"], self.video.name)
        self.assertEqual(draft["status"], "local_draft_not_approved")
        self.assertEqual(draft["media_url"], f"/api/content/drafts/{self.video.name}/media")

    def test_streams_inline_and_supports_byte_ranges(self) -> None:
        full = self.client.get(f"/api/content/drafts/{self.video.name}/media")
        self.assertEqual(full.status_code, 200)
        self.assertEqual(full.content, b"0123456789abcdef")
        self.assertEqual(full.headers["content-type"], "video/mp4")
        self.assertEqual(full.headers["cache-control"], "private, no-store")
        self.assertTrue(full.headers["content-disposition"].startswith("inline"))

        partial = self.client.get(
            f"/api/content/drafts/{self.video.name}/media",
            headers={"Range": "bytes=2-5"},
        )
        self.assertEqual(partial.status_code, 206)
        self.assertEqual(partial.content, b"2345")
        self.assertEqual(partial.headers["content-range"], "bytes 2-5/16")

    def test_rejects_unsupported_or_missing_files(self) -> None:
        self.assertEqual(
            self.client.get("/api/content/drafts/privado.jpg/media").status_code,
            404,
        )
        self.assertEqual(
            self.client.get("/api/content/drafts/no-existe.mp4/media").status_code,
            404,
        )


if __name__ == "__main__":
    unittest.main()
