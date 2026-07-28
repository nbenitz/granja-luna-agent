#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from web.app import create_app


class FarmStructureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.structure_path = root / "structure-events.jsonl"
        self.client = TestClient(
            create_app(
                root / "inbox.jsonl",
                root / "usage-events.jsonl",
                root / "review-events.jsonl",
                root / "operation-events.jsonl",
                self.structure_path,
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def test_barn_and_flock_require_draft_then_confirmation(self) -> None:
        barn_draft = self.client.post(
            "/api/operations/structure/barn/drafts",
            json={"name": "Galpón reproductores"},
        ).json()

        self.assertEqual(barn_draft["status"], "awaiting_confirmation")
        self.assertEqual(self.client.get("/api/operations/barns").json(), [])

        barn = self.client.post(
            f"/api/operations/structure/{barn_draft['id']}/confirm",
            json={
                "confirmation_code": barn_draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        ).json()

        self.assertEqual(barn["status"], "applied")
        self.assertEqual(len(self.client.get("/api/operations/barns").json()), 1)

        flock_draft = self.client.post(
            "/api/operations/structure/flock/drafts",
            json={
                "name": "Plantel Reproductor Mixto RIR–Plymouth Barrada · Galpón 1",
                "purpose": "reproducción",
                "bird_count": 12,
                "hen_breeds": ["Rhode Island Red", "Plymouth Rock barrada"],
                "rooster_breeds": ["Rhode Island Red"],
                "egg_label": "Huevos fértiles de origen mixto: RIR puro / Black Star",
                "barn_id": barn["id"],
            },
        ).json()

        self.assertEqual(flock_draft["data"]["barn_id"], barn["id"])
        self.assertEqual(flock_draft["data"]["bird_count"], 12)
        self.assertEqual(self.client.get("/api/operations/flocks").json(), [])

        flock = self.client.post(
            f"/api/operations/structure/{flock_draft['id']}/confirm",
            json={
                "confirmation_code": flock_draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        ).json()

        self.assertEqual(flock["status"], "applied")
        self.assertEqual(
            self.client.get("/api/operations/flocks").json()[0]["data"]["egg_label"],
            "Huevos fértiles de origen mixto: RIR puro / Black Star",
        )

    def test_flock_can_be_created_without_barn_and_barn_must_be_confirmed(self) -> None:
        unassigned = self.client.post(
            "/api/operations/structure/flock/drafts",
            json={"name": "Plantel sin ubicación", "hen_breeds": ["Rhode Island Red"]},
        )
        self.assertEqual(unassigned.status_code, 201)
        self.assertIsNone(unassigned.json()["data"]["barn_id"])
        self.assertIsNone(unassigned.json()["data"]["bird_count"])

        pending_barn = self.client.post(
            "/api/operations/structure/barn/drafts",
            json={"name": "Galpón pendiente"},
        ).json()
        invalid = self.client.post(
            "/api/operations/structure/flock/drafts",
            json={
                "name": "Plantel inválido",
                "hen_breeds": ["Plymouth Rock barrada"],
                "barn_id": pending_barn["id"],
            },
        )

        self.assertEqual(invalid.status_code, 422)
        self.assertEqual(invalid.json()["detail"]["missing_field"], "barn_id")

        invalid_count = self.client.post(
            "/api/operations/structure/flock/drafts",
            json={
                "name": "Plantel con cantidad inválida",
                "hen_breeds": ["Rhode Island Red"],
                "bird_count": 0,
            },
        )
        self.assertEqual(invalid_count.status_code, 422)
        self.assertEqual(invalid_count.json()["detail"]["missing_field"], "bird_count")

    def test_duplicate_confirmed_name_is_rejected(self) -> None:
        draft = self.client.post(
            "/api/operations/structure/barn/drafts",
            json={"name": "Galpón 1"},
        ).json()
        first = self.client.post(
            f"/api/operations/structure/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )
        duplicate = self.client.post(
            "/api/operations/structure/barn/drafts",
            json={"name": "galpón 1"},
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(duplicate.status_code, 409)
        self.assertEqual(duplicate.json()["detail"]["code"], "conflict")

    def test_pending_structure_record_can_be_cancelled(self) -> None:
        draft = self.client.post(
            "/api/operations/structure/barn/drafts", json={"name": "Galpón temporal"}
        ).json()
        cancelled = self.client.post(
            f"/api/operations/structure/{draft['id']}/cancel",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "reason": "No forma parte de la infraestructura activa",
            },
        )

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["status"], "cancelled")
        self.assertEqual(
            self.client.get("/api/operations/structure/pending").json(), []
        )


if __name__ == "__main__":
    unittest.main()
