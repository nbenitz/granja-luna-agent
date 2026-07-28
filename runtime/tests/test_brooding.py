#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from web.app import create_app


class BroodingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.client = TestClient(
            create_app(
                inbox_path=root / "inbox.jsonl",
                usage_path=root / "usage-events.jsonl",
                review_events_path=root / "review-events.jsonl",
                operations_path=root / "operation-events.jsonl",
                structure_path=root / "structure-events.jsonl",
                incubation_path=root / "incubation-events.jsonl",
                brooding_path=root / "brooding-events.jsonl",
            )
        )
        self.source_batch_id = self._closed_incubation_batch()

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def confirm(self, namespace: str, draft: dict) -> object:
        return self.client.post(
            f"/api/operations/{namespace}/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )

    def _closed_incubation_batch(self) -> str:
        incubator = self.client.post(
            "/api/operations/incubation/incubator/drafts",
            json={"name": "Incubadora", "capacity": 100},
        ).json()
        self.assertEqual(self.confirm("incubation", incubator).status_code, 200)
        batch = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator["id"],
                "start_date": "2026-06-27",
                "eggs_set": 60,
                "source_description": "Lote de prueba",
            },
        ).json()
        self.assertEqual(self.confirm("incubation", batch).status_code, 200)
        closure = self.client.post(
            "/api/operations/incubation/event/drafts",
            json={
                "batch_id": batch["id"],
                "event_date": "2026-07-21",
                "event_type": "closure",
                "hatched_alive": 52,
                "eggs_unhatched": 8,
                "chicks_dead": 0,
                "chicks_malformed": 0,
            },
        ).json()
        self.assertEqual(self.confirm("incubation", closure).status_code, 200)
        return batch["id"]

    def test_brooding_batch_tracks_source_count_and_events(self) -> None:
        area = self.client.post(
            "/api/operations/brooding/area/drafts",
            json={"name": "Zona de cría", "capacity": 80},
        ).json()
        batch = self.client.post(
            "/api/operations/brooding/batch/drafts",
            json={
                "area_id": area["id"],
                "start_date": "2026-07-21",
                "chicks_received": 52,
                "source_incubation_batch_id": self.source_batch_id,
                "source_description": "Lote cerrado de incubación",
                "age_min_days": 1,
                "age_max_days": 2,
            },
        ).json()

        blocked = self.confirm("brooding", batch)
        self.assertEqual(blocked.status_code, 422)
        self.assertEqual(blocked.json()["detail"]["code"], "invalid_dependency")
        self.assertEqual(self.confirm("brooding", area).status_code, 200)
        self.assertEqual(self.confirm("brooding", batch).status_code, 200)

        mortality = self.client.post(
            "/api/operations/brooding/event/drafts",
            json={
                "batch_id": batch["id"],
                "event_date": "2026-07-22",
                "event_type": "mortality",
                "quantity": 2,
                "reason": "Bajas observadas",
            },
        ).json()
        self.assertEqual(self.confirm("brooding", mortality).status_code, 200)

        detail = self.client.get(f"/api/operations/brooding/batches/{batch['id']}").json()
        self.assertEqual(detail["summary"]["chicks_received"], 52)
        self.assertEqual(detail["summary"]["mortality"], 2)
        self.assertEqual(detail["summary"]["current_count"], 50)
        self.assertFalse(detail["summary"]["closed"])

        duplicate = self.client.post(
            "/api/operations/brooding/batch/drafts",
            json={
                "area_id": area["id"],
                "start_date": "2026-07-22",
                "chicks_received": 1,
                "source_incubation_batch_id": self.source_batch_id,
                "source_description": "Asignación duplicada",
            },
        ).json()
        exceeded = self.confirm("brooding", duplicate)
        self.assertEqual(exceeded.status_code, 422)
        self.assertEqual(exceeded.json()["detail"]["code"], "source_quantity_exceeded")

    def test_pending_brooding_draft_can_be_cancelled_but_not_applied_record(self) -> None:
        area = self.client.post(
            "/api/operations/brooding/area/drafts",
            json={"name": "Zona temporal"},
        ).json()
        cancelled = self.client.post(
            f"/api/operations/brooding/{area['id']}/cancel",
            json={
                "confirmation_code": area["confirmation"]["code"],
                "explicit_confirmation": True,
                "reason": "Borrador de prueba",
            },
        )
        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["status"], "cancelled")
        self.assertEqual(self.client.get("/api/operations/brooding/pending").json(), [])
        rejected = self.confirm("brooding", area)
        self.assertEqual(rejected.status_code, 422)
        self.assertEqual(rejected.json()["detail"]["code"], "invalid_status")


if __name__ == "__main__":
    unittest.main()
