#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from web.app import create_app


class EggStorageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.client = TestClient(
            create_app(
                inbox_path=root / "inbox.jsonl",
                usage_path=root / "usage.jsonl",
                review_events_path=root / "review.jsonl",
                operations_path=root / "operations.jsonl",
                structure_path=root / "structure.jsonl",
                incubation_path=root / "incubation.jsonl",
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def confirm_structure(self, draft: dict) -> dict:
        response = self.client.post(
            f"/api/operations/structure/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def confirm_movement(self, draft: dict) -> dict:
        response = self.client.post(
            f"/api/operations/movements/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def confirm_incubation(self, draft: dict) -> dict:
        response = self.client.post(
            f"/api/operations/incubation/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
            },
        )
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def create_source_structure(self) -> tuple[dict, dict, dict]:
        barn = self.confirm_structure(
            self.client.post(
                "/api/operations/structure/barn/drafts", json={"name": "Galpón 1"}
            ).json()
        )
        flock = self.confirm_structure(
            self.client.post(
                "/api/operations/structure/flock/drafts",
                json={
                    "name": "Plantel Reproductor Mixto RIR–Plymouth Barrada · Galpón 1",
                    "purpose": "reproducción",
                    "hen_breeds": [
                        "Rhode Island Red",
                        "Plymouth Rock barrada",
                        "Brahma",
                    ],
                    "rooster_breeds": ["Rhode Island Red"],
                    "bird_groups": [
                        {"breed": "Brahma", "sex": "hen", "count": 2}
                    ],
                    "barn_id": barn["id"],
                },
            ).json()
        )
        area = self.confirm_structure(
            self.client.post(
                "/api/operations/structure/egg_storage_area/drafts",
                json={
                    "name": "Almacén de huevos para incubación",
                    "purpose": "incubation_candidate",
                    "classification_mode": "mixed_batch_with_observations",
                },
            ).json()
        )
        return barn, flock, area

    def test_collection_creates_available_lot_and_incubation_allocates_it(self) -> None:
        barn, flock, area = self.create_source_structure()
        collection_response = self.client.post(
            "/api/operations/movements/egg_collection/drafts",
            json={
                "effective_date": "2026-07-22",
                "flock": flock["data"]["name"],
                "flock_id": flock["id"],
                "barn_id": barn["id"],
                "eggs_total": 12,
                "destination": area["data"]["name"],
                "storage_area_id": area["id"],
                "purpose": "incubation_candidate",
                "physical_separation": False,
                "identification_stage": "hatch",
                "classifications": [
                    {"axis": "shell_color", "value": "white", "quantity": 2},
                    {"axis": "shell_color", "value": "red", "quantity": 1},
                    {
                        "axis": "probable_maternal_origin",
                        "value": "Brahma",
                        "quantity": 2,
                        "certainty": "probable",
                    },
                    {
                        "axis": "expected_cross",
                        "value": "Brahma × Rhode Island Red",
                        "quantity": 2,
                        "certainty": "probable",
                    },
                    {
                        "axis": "probable_maternal_origin",
                        "value": "PRB",
                        "quantity": 9,
                        "certainty": "probable",
                    },
                ],
            },
        )
        self.assertEqual(collection_response.status_code, 201, collection_response.text)
        collection = self.confirm_movement(collection_response.json())
        lot_id = collection["data"]["lot_id"]

        lot = self.client.get(f"/api/operations/egg-storage/lots/{lot_id}").json()
        self.assertEqual(lot["quantity_available"], 12)
        self.assertFalse(lot["physical_separation"])
        self.assertEqual(lot["identification_stage"], "hatch")
        self.assertEqual(lot["storage_area_name"], area["data"]["name"])
        self.assertEqual(lot["classifications"][0]["method"], "manual")

        incubator = self.confirm_incubation(
            self.client.post(
                "/api/operations/incubation/incubator/drafts",
                json={"name": "Incubadora de prueba", "capacity": 20},
            ).json()
        )
        batch = self.client.post(
            "/api/operations/incubation/batch/drafts",
            json={
                "incubator_id": incubator["id"],
                "start_date": "2026-07-22",
                "eggs_set": 5,
                "source_description": "Almacén de huevos para incubación",
                "source_egg_lots": [{"lot_id": lot_id, "quantity": 5}],
            },
        ).json()
        self.confirm_incubation(batch)

        updated = self.client.get(f"/api/operations/egg-storage/lots/{lot_id}").json()
        self.assertEqual(updated["quantity_allocated"], 5)
        self.assertEqual(updated["quantity_available"], 7)

    def test_classification_axis_cannot_exceed_collection_total(self) -> None:
        barn, flock, area = self.create_source_structure()
        response = self.client.post(
            "/api/operations/movements/egg_collection/drafts",
            json={
                "effective_date": "2026-07-22",
                "flock": flock["data"]["name"],
                "flock_id": flock["id"],
                "barn_id": barn["id"],
                "eggs_total": 12,
                "storage_area_id": area["id"],
                "classifications": [
                    {"axis": "shell_color", "value": "white", "quantity": 7},
                    {"axis": "shell_color", "value": "red", "quantity": 6},
                ],
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["missing_field"], "classifications")


if __name__ == "__main__":
    unittest.main()
