#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from web.app import create_app


class WebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.inbox_path = root / "inbox.jsonl"
        self.usage_path = root / "usage-events.jsonl"
        self.review_path = root / "review-events.jsonl"
        self.client = TestClient(create_app(self.inbox_path, self.usage_path, self.review_path))

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def capture_purchase(self) -> dict:
        response = self.client.post(
            "/api/inbox",
            json={
                "message": (
                    "Compre dos bolsas de iniciador a 110 mil cada una, "
                    "una bolsa de maiz a 90 mil y 3 kg de vitaminas a 25000"
                ),
                "context": None,
            },
        )
        self.assertEqual(response.status_code, 201)
        return response.json()

    def test_capture_correction_review_and_activity(self) -> None:
        health = self.client.get("/api/health")
        self.assertEqual(health.status_code, 200)

        entry = self.capture_purchase()
        self.assertEqual(entry["review_status"], "pending")
        self.assertEqual(entry["operation_status"], "draft")
        self.assertEqual(entry["structured_data"]["schema_id"], "purchase.v2")

        corrected = self.client.patch(
            f"/api/inbox/{entry['id']}/correction",
            json={
                "section": "purchase_general",
                "reason": "new_information",
                "note": "Datos agregados durante la revisión",
                "data": {
                    "fecha_compra": "2026-06-20",
                    "proveedor": "Proveedor de prueba",
                    "moneda": "PYG",
                    "comprobante": None,
                },
            },
        )
        self.assertEqual(corrected.status_code, 200)
        corrected_entry = corrected.json()
        self.assertEqual(corrected_entry["review"]["correction_count"], 1)
        self.assertEqual(corrected_entry["structured_data"]["provenance"]["fields"]["proveedor"], "enriched")

        reviewed = self.client.patch(
            f"/api/inbox/{entry['id']}/review",
            json={"decision": "confirm", "reason": None, "note": None},
        )
        self.assertEqual(reviewed.status_code, 200)
        self.assertEqual(reviewed.json()["review_status"], "validated")
        self.assertEqual(reviewed.json()["review"]["outcome"], "corrected")
        self.assertEqual(reviewed.json()["operation_status"], "draft")
        self.assertEqual(reviewed.json()["side_effects"], [])

        summary = self.client.get("/api/inbox/summary").json()
        self.assertEqual(summary["by_review_status"]["validated"], 1)
        event_types = {event["event_type"] for event in self.client.get("/api/activity").json()}
        self.assertIn("inbox_corrected", event_types)
        self.assertIn("inbox_reviewed", event_types)

        review_events = self.client.get(f"/api/review-events?entry_id={entry['id']}").json()
        self.assertEqual({event["event_type"] for event in review_events}, {"correction_saved", "review_completed"})
        correction = next(event for event in review_events if event["event_type"] == "correction_saved")
        self.assertIn("proveedor", {change["path"] for change in correction["changes"]})
        self.assertNotIn(entry["message"], self.review_path.read_text(encoding="utf-8"))

    def test_confirm_requires_complete_purchase_but_not_stock_decision(self) -> None:
        entry = self.capture_purchase()

        incomplete = self.client.patch(
            f"/api/inbox/{entry['id']}/review",
            json={"decision": "confirm", "reason": None, "note": None},
        )
        self.assertEqual(incomplete.status_code, 422)
        missing_paths = {field["path"] for field in incomplete.json()["detail"]["missing_fields"]}
        self.assertEqual(missing_paths, {"fecha_compra", "proveedor"})

    def test_deferred_correction_requires_note(self) -> None:
        entry = self.capture_purchase()

        response = self.client.patch(
            f"/api/inbox/{entry['id']}/review",
            json={"decision": "needs_correction", "reason": None, "note": None},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"], "Describe brevemente que debe corregirse.")

    def test_non_pending_entry_can_be_discarded(self) -> None:
        entry = self.capture_purchase()
        deferred = self.client.patch(
            f"/api/inbox/{entry['id']}/review",
            json={
                "decision": "needs_correction",
                "reason": "system_limitation",
                "note": "Falta soporte para un dato",
            },
        )
        self.assertEqual(deferred.json()["review_status"], "needs_correction")

        discarded = self.client.patch(
            f"/api/inbox/{entry['id']}/review",
            json={"decision": "reject", "reason": "not_relevant", "note": "Descartada por el usuario"},
        )

        self.assertEqual(discarded.status_code, 200)
        self.assertEqual(discarded.json()["review_status"], "rejected")
        self.assertEqual(discarded.json()["operation_status"], "draft")

    def test_capture_exposes_discount_and_declared_total(self) -> None:
        response = self.client.post(
            "/api/inbox",
            json={
                "message": (
                    "El uno de junio compre 7 bolsas de cascarilla de arroz a 10mil c/u, "
                    "total 100mil, con 5mil de descuento."
                ),
                "context": None,
            },
        )

        self.assertEqual(response.status_code, 201)
        values = response.json()["structured_data"]["values"]
        self.assertEqual(values["fecha_compra"], "2026-06-01")
        self.assertEqual(values["descuento"], {"tipo": "monto", "valor": 5000})
        self.assertEqual(values["total_declarado"], 100000)

    def test_classification_correction_is_recorded(self) -> None:
        entry = self.capture_purchase()

        response = self.client.patch(
            f"/api/inbox/{entry['id']}/correction",
            json={
                "section": "classification",
                "reason": "system_error",
                "note": None,
                "data": {"intent": "registrar_compra", "primary_domain": "finanzas", "risk_level": "medio"},
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["classification"]["primary_domain"], "finanzas")
        self.assertEqual(response.json()["classification_provenance"]["primary_domain"], "corrected")

    def test_index_and_missing_entry(self) -> None:
        index = self.client.get("/")
        self.assertEqual(index.status_code, 200)
        self.assertIn("Granja Luna", index.text)
        self.assertIn("viewport-fit=cover", index.text)
        self.assertIn('rel="manifest"', index.text)
        self.assertIn('crossorigin="use-credentials"', index.text)
        self.assertIn("default-src 'self'", index.headers["content-security-policy"])
        self.assertEqual(index.headers["permissions-policy"], "microphone=(self)")
        self.assertEqual(index.headers["cache-control"], "no-store")
        manifest = self.client.get("/static/manifest.webmanifest")
        self.assertEqual(manifest.status_code, 200)
        self.assertEqual(manifest.json()["display"], "standalone")
        worker = self.client.get("/service-worker.js")
        self.assertEqual(worker.status_code, 200)
        self.assertEqual(worker.headers["service-worker-allowed"], "/")
        self.assertEqual(self.client.get("/api/inbox/no-existe").status_code, 404)

    def test_mobile_navigation_has_one_column_per_destination(self) -> None:
        index = self.client.get("/")
        styles = self.client.get("/static/styles.css")
        script = self.client.get("/static/app.js")

        self.assertEqual(index.text.count('class="nav-button'), 5)
        self.assertIn("grid-template-columns: repeat(5, minmax(0, 1fr));", styles.text)
        self.assertIn('data-target="media"', index.text)
        self.assertIn("Analizar con Gemini", script.text)
        self.assertIn('id="media-upload-input"', index.text)
        self.assertIn('id="content-request-form"', index.text)
        self.assertIn("uploadMediaFile", script.text)
        self.assertIn("Estudio de contenido", index.text)


if __name__ == "__main__":
    unittest.main()
