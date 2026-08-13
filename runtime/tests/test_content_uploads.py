#!/usr/bin/env python3
from __future__ import annotations

from io import BytesIO
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.content_requests import supersede_content_request  # noqa: E402
from core.media_library import connect_media_library  # noqa: E402
from web.app import create_app  # noqa: E402


class ContentUploadTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.media_root = self.root / "media"
        self.media_root.mkdir()
        self.database = self.root / "media.sqlite3"
        self.content_requests = self.root / "content-requests.jsonl"
        self.client = TestClient(
            create_app(
                inbox_path=self.root / "inbox.jsonl",
                usage_path=self.root / "usage.jsonl",
                review_events_path=self.root / "reviews.jsonl",
                operations_path=self.root / "operations.jsonl",
                structure_path=self.root / "structure.jsonl",
                incubation_path=self.root / "incubation.jsonl",
                brooding_path=self.root / "brooding.jsonl",
                content_requests_path=self.content_requests,
                media_database_path=self.database,
                media_root=self.media_root,
                media_derivatives_path=self.root / "derivatives",
                env_file=self.root / ".env",
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    @staticmethod
    def jpeg_bytes(color: tuple[int, int, int] = (80, 120, 60)) -> bytes:
        from PIL import Image

        buffer = BytesIO()
        Image.new("RGB", (64, 48), color).save(buffer, "JPEG")
        return buffer.getvalue()

    def create_batch(self, files: list[tuple[str, bytes]], context: str = "Contexto real") -> dict:
        response = self.client.post(
            "/api/media/upload-batches",
            json={
                "context": context,
                "files": [
                    {"name": name, "size": len(content), "type": "image/jpeg"}
                    for name, content in files
                ],
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        return response.json()

    def test_multiple_upload_persists_context_files_and_inventory(self) -> None:
        files = [
            ("20260808_090000.jpg", self.jpeg_bytes()),
            ("../20260808_090001.jpg", self.jpeg_bytes((120, 90, 50))),
        ]
        batch = self.create_batch(files, "Pollitos durante la mañana")

        for item, (_, content) in zip(batch["items"], files, strict=True):
            uploaded = self.client.put(
                f"/api/media/upload-batches/{batch['id']}/items/{item['id']}",
                content=content,
                headers={"Content-Type": "image/jpeg"},
            )
            self.assertEqual(uploaded.status_code, 200, uploaded.text)
            self.assertEqual(uploaded.json()["status"], "uploaded")

        completed = self.client.post(
            f"/api/media/upload-batches/{batch['id']}/complete"
        )
        self.assertEqual(completed.status_code, 200, completed.text)
        receipt = completed.json()
        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["context"], "Pollitos durante la mañana")
        self.assertEqual(receipt["uploaded_count"], 2)
        self.assertTrue(all(item["asset_id"] for item in receipt["items"]))
        self.assertTrue(all(".." not in item["stored_relative_path"] for item in receipt["items"]))
        self.assertTrue(all((self.media_root / item["stored_relative_path"]).is_file() for item in receipt["items"]))

        with connect_media_library(self.database) as connection:
            assets = connection.execute(
                "SELECT original_name FROM media_assets ORDER BY captured_local_at"
            ).fetchall()
        self.assertEqual(
            [row["original_name"] for row in assets],
            ["20260808_090000.jpg", "20260808_090001.jpg"],
        )

    def test_duplicate_is_linked_without_copying_original_again(self) -> None:
        content = self.jpeg_bytes()
        first = self.create_batch([("primera.jpg", content)])
        first_item = first["items"][0]
        self.assertEqual(
            self.client.put(
                f"/api/media/upload-batches/{first['id']}/items/{first_item['id']}",
                content=content,
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.post(f"/api/media/upload-batches/{first['id']}/complete").status_code,
            200,
        )

        duplicate = self.create_batch([("copia.jpg", content)])
        duplicate_item = duplicate["items"][0]
        uploaded = self.client.put(
            f"/api/media/upload-batches/{duplicate['id']}/items/{duplicate_item['id']}",
            content=content,
        )
        self.assertEqual(uploaded.status_code, 200)
        self.assertEqual(uploaded.json()["status"], "duplicate")
        receipt = self.client.post(
            f"/api/media/upload-batches/{duplicate['id']}/complete"
        ).json()
        self.assertEqual(receipt["duplicate_count"], 1)
        self.assertEqual(receipt["uploaded_count"], 0)

    def test_duplicate_inside_same_batch_keeps_one_binary_and_links_both_items(self) -> None:
        content = self.jpeg_bytes()
        batch = self.create_batch([("uno.jpg", content), ("dos.jpg", content)])
        statuses = []
        for item in batch["items"]:
            response = self.client.put(
                f"/api/media/upload-batches/{batch['id']}/items/{item['id']}",
                content=content,
            )
            self.assertEqual(response.status_code, 200)
            statuses.append(response.json()["status"])
        self.assertEqual(statuses, ["uploaded", "duplicate"])
        receipt = self.client.post(
            f"/api/media/upload-batches/{batch['id']}/complete"
        ).json()
        self.assertTrue(all(item["asset_id"] for item in receipt["items"]))
        self.assertEqual(len(list((self.media_root / "imports").rglob("*.jpg"))), 1)

    def test_invalid_signature_is_rejected_and_batch_can_complete_with_errors(self) -> None:
        content = b"not-a-jpeg"
        batch = self.create_batch([("falsa.jpg", content)])
        item = batch["items"][0]
        response = self.client.put(
            f"/api/media/upload-batches/{batch['id']}/items/{item['id']}",
            content=content,
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"], "invalid_signature")
        receipt = self.client.post(
            f"/api/media/upload-batches/{batch['id']}/complete"
        ).json()
        self.assertEqual(receipt["status"], "completed_with_errors")
        self.assertEqual(receipt["error_count"], 1)
        self.assertFalse(any(self.media_root.rglob("*.part")))

    @unittest.skipUnless(shutil.which("ffmpeg"), "ffmpeg is required for the MP4 upload check")
    def test_mp4_upload_is_validated_and_inventoried(self) -> None:
        source = self.root / "pollitos-prueba.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-loglevel",
                "error",
                "-f",
                "lavfi",
                "-i",
                "color=c=black:s=64x48:d=0.25",
                "-c:v",
                "mpeg4",
                "-pix_fmt",
                "yuv420p",
                "-y",
                str(source),
            ],
            check=True,
        )
        content = source.read_bytes()
        response = self.client.post(
            "/api/media/upload-batches",
            json={
                "context": "Video de prueba del cargador",
                "files": [
                    {
                        "name": source.name,
                        "size": len(content),
                        "type": "video/mp4",
                    }
                ],
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        batch = response.json()
        item = batch["items"][0]
        uploaded = self.client.put(
            f"/api/media/upload-batches/{batch['id']}/items/{item['id']}",
            content=content,
            headers={"Content-Type": "video/mp4"},
        )
        self.assertEqual(uploaded.status_code, 200, uploaded.text)
        receipt = self.client.post(
            f"/api/media/upload-batches/{batch['id']}/complete"
        ).json()
        self.assertEqual(receipt["status"], "completed")
        self.assertTrue(receipt["items"][0]["asset_id"])

        with connect_media_library(self.database) as connection:
            asset = connection.execute(
                "SELECT media_kind, duration_seconds, has_audio FROM media_assets"
            ).fetchone()
        self.assertEqual(asset["media_kind"], "video")
        self.assertGreater(asset["duration_seconds"], 0)
        self.assertEqual(asset["has_audio"], 0)

    def test_content_studio_intake_is_append_only_and_links_upload_batch(self) -> None:
        batch = self.create_batch([("foto.jpg", self.jpeg_bytes())])
        response = self.client.post(
            "/api/content/requests",
            json={
                "instruction": "Prepará un reel sobre el cuidado durante el frío.",
                "content_type": "reel",
                "channels": ["facebook"],
                "source_stage": "actual",
                "media_batch_ids": [batch["id"]],
                "objective": "Generar confianza",
                "audience": "Familias amantes de animales",
            },
        )
        self.assertEqual(response.status_code, 201, response.text)
        request_item = response.json()
        self.assertEqual(request_item["status"], "idea")
        self.assertEqual(request_item["media_batch_ids"], [batch["id"]])
        self.assertTrue(request_item["publication_requires_approval"])
        listed = self.client.get("/api/content/requests").json()
        self.assertEqual(listed[0]["id"], request_item["id"])
        self.assertEqual(len(self.content_requests.read_text(encoding="utf-8").splitlines()), 1)

    def test_content_request_supersession_appends_revision_and_collapses_listing(self) -> None:
        first = self.client.post(
            "/api/content/requests",
            json={"instruction": "Primera versión", "content_type": "reel"},
        ).json()
        replacement = self.client.post(
            "/api/content/requests",
            json={"instruction": "Versión vinculada", "content_type": "reel"},
        ).json()

        revised = supersede_content_request(
            self.content_requests,
            request_id=first["id"],
            replacement_id=replacement["id"],
            reason="El usuario registró una versión con la tanda correcta.",
        )

        self.assertEqual(revised["status"], "superseded")
        self.assertEqual(revised["superseded_by"], replacement["id"])
        listed = self.client.get("/api/content/requests").json()
        self.assertEqual(len(listed), 2)
        self.assertEqual(listed[0]["id"], replacement["id"])
        self.assertEqual(listed[1]["status"], "superseded")
        self.assertEqual(len(self.content_requests.read_text(encoding="utf-8").splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
