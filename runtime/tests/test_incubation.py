#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from web.app import create_app


class IncubationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.incubation_path = root / "incubation-events.jsonl"
        self.client = TestClient(
            create_app(
                inbox_path=root / "inbox.jsonl",
                usage_path=root / "usage-events.jsonl",
                review_events_path=root / "review-events.jsonl",
                operations_path=root / "operation-events.jsonl",
                structure_path=root / "structure-events.jsonl",
                incubation_path=self.incubation_path,
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def confirm(self, draft: dict) -> object:
        return self.client.post(
            f"/api/operations/incubation/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )

    def test_incubator_batch_and_history_require_ordered_confirmation(self) -> None:
        incubator = self.client.post(
            "/api/operations/incubation/incubator/drafts",
            json={"name": "Incubadora 314", "capacity": 314},
        ).json()
        batch = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator["id"],
                "start_date": "2026-06-27",
                "eggs_set": 60,
                "source_description": "Compra a Gallinería Nueva Londres",
            },
        ).json()
        events = [
            self.client.post(
                "/api/operations/incubation/event/drafts",
                json={
                    "batch_id": batch["id"],
                    "event_date": "2026-07-18",
                    "event_type": "candling",
                    "units_discarded": 4,
                },
            ).json(),
            self.client.post(
                "/api/operations/incubation/event/drafts",
                json={
                    "batch_id": batch["id"],
                    "event_date": "2026-07-19",
                    "event_type": "hatching_started",
                },
            ).json(),
            self.client.post(
                "/api/operations/incubation/event/drafts",
                json={
                    "batch_id": batch["id"],
                    "event_date": "2026-07-20",
                    "event_type": "discard",
                    "units_discarded": 1,
                    "reason": "Malformación",
                },
            ).json(),
            self.client.post(
                "/api/operations/incubation/event/drafts",
                json={
                    "batch_id": batch["id"],
                    "event_date": "2026-07-21",
                    "event_type": "discard",
                    "units_discarded": 2,
                },
            ).json(),
        ]

        blocked = self.confirm(batch)
        self.assertEqual(blocked.status_code, 422)
        self.assertEqual(blocked.json()["detail"]["code"], "invalid_dependency")

        self.assertEqual(self.confirm(incubator).status_code, 200)
        self.assertEqual(self.confirm(batch).status_code, 200)
        for event in events:
            self.assertEqual(self.confirm(event).status_code, 200)

        detail = self.client.get(
            f"/api/operations/incubation/batches/{batch['id']}"
        ).json()
        self.assertEqual(detail["summary"]["eggs_set"], 60)
        self.assertEqual(detail["summary"]["units_discarded"], 7)
        self.assertEqual(detail["summary"]["unresolved_units"], 53)
        self.assertFalse(detail["summary"]["closed"])
        self.assertEqual(len(detail["events"]), 4)

        invalid_closure = self.client.post(
            "/api/operations/incubation/event/drafts",
            json={
                "batch_id": batch["id"],
                "event_date": "2026-07-22",
                "event_type": "closure",
                "hatched_alive": 50,
                "eggs_unhatched": 1,
                "chicks_dead": 0,
                "chicks_malformed": 0,
            },
        ).json()
        mismatch = self.confirm(invalid_closure)
        self.assertEqual(mismatch.status_code, 422)
        self.assertEqual(mismatch.json()["detail"]["code"], "result_mismatch")

        closure = self.client.post(
            "/api/operations/incubation/event/drafts",
            json={
                "batch_id": batch["id"],
                "event_date": "2026-07-22",
                "event_type": "closure",
                "hatched_alive": 50,
                "eggs_unhatched": 2,
                "chicks_dead": 1,
                "chicks_malformed": 0,
            },
        ).json()
        self.assertEqual(self.confirm(closure).status_code, 200)

        closed_detail = self.client.get(
            f"/api/operations/incubation/batches/{batch['id']}"
        ).json()
        self.assertTrue(closed_detail["summary"]["closed"])
        self.assertEqual(closed_detail["summary"]["unresolved_units"], 0)
        self.assertEqual(
            closed_detail["summary"]["results"],
            {
                "hatched_alive": 50,
                "eggs_unhatched": 2,
                "chicks_dead": 1,
                "chicks_malformed": 0,
            },
        )

    def test_batch_capacity_is_checked_when_confirmed(self) -> None:
        incubator_draft = self.client.post(
            "/api/operations/incubation/incubator/drafts",
            json={"name": "Incubadora pequeña", "capacity": 10},
        ).json()
        self.assertEqual(self.confirm(incubator_draft).status_code, 200)
        oversized = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator_draft["id"],
                "start_date": "2026-07-21",
                "eggs_set": 11,
                "source_description": "Lote de prueba",
            },
        ).json()

        response = self.confirm(oversized)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"], "capacity_exceeded")

    def test_capacity_includes_other_open_batches(self) -> None:
        incubator = self.client.post(
            "/api/operations/incubation/incubator/drafts",
            json={"name": "Incubadora compartida", "capacity": 100},
        ).json()
        self.assertEqual(self.confirm(incubator).status_code, 200)

        first = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator["id"],
                "start_date": "2026-07-20",
                "eggs_set": 60,
                "source_description": "Primer lote",
            },
        ).json()
        second = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator["id"],
                "start_date": "2026-07-21",
                "eggs_set": 50,
                "source_description": "Segundo lote",
            },
        ).json()

        self.assertEqual(self.confirm(first).status_code, 200)
        response = self.confirm(second)
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["code"], "capacity_exceeded")

    def test_pending_incubation_record_can_be_cancelled(self) -> None:
        draft = self.client.post(
            "/api/operations/incubation/incubator/drafts",
            json={"name": "Incubadora en construcción", "capacity": 200},
        ).json()
        cancelled = self.client.post(
            f"/api/operations/incubation/{draft['id']}/cancel",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "reason": "Aún no está operativa",
            },
        )

        self.assertEqual(cancelled.status_code, 200)
        self.assertEqual(cancelled.json()["status"], "cancelled")
        self.assertEqual(
            self.client.get("/api/operations/incubation/pending").json(), []
        )


if __name__ == "__main__":
    unittest.main()
