#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys

from fastapi.testclient import TestClient


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.media_library import scan_media_library  # noqa: E402
from web.app import create_app  # noqa: E402


PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None


def fake_metadata(_path: Path, _kind: str) -> dict[str, object]:
    return {"width": 640, "height": 480, "orientation": 1, "gps_present": False}


@unittest.skipUnless(PIL_AVAILABLE, "Pillow no está instalado en este entorno de pruebas")
class MediaWebTests(unittest.TestCase):
    def test_curation_api_and_explicit_gemini_action_use_sanitized_derivatives(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            media_root = root / "inbox"
            media_root.mkdir()
            database = root / "media.sqlite3"
            derivatives = root / "derivatives"
            Image.new("RGB", (640, 480), (80, 120, 60)).save(media_root / "20260801_120000.jpg")
            Image.new("RGB", (640, 480), (130, 160, 80)).save(media_root / "20260801_120005.jpg")
            scan_media_library(media_root, database, metadata_reader=fake_metadata)
            analyzer_calls: list[dict[str, object]] = []

            def fake_analyzer(**kwargs):
                analyzer_calls.append(kwargs)
                for path in kwargs["images"]:
                    self.assertIn(derivatives / "analysis", Path(path).parents)
                    with Image.open(path) as sanitized:
                        self.assertFalse(sanitized.getexif())
                return {
                    "model": kwargs["model"],
                    "valid_json": True,
                    "analysis": {
                        "resumen_de_la_escena": "Dos candidatas reales.",
                        "mejor_archivo": kwargs["candidate_names"][0],
                        "sin_candidata_adecuada": False,
                        "favoritos_por_intencion": [
                            {
                                "archivo": kwargs["candidate_names"][0],
                                "prioridad": "principal",
                                "intencion": "panoramica_paisaje",
                                "motivo": "Mejor encuadre.",
                            }
                        ],
                        "ranking": [
                            {"archivo": name} for name in kwargs["candidate_names"]
                        ],
                        "riesgos": [],
                        "afirmaciones_que_requieren_verificacion": [],
                        "requiere_eleccion_humana": True,
                        "confianza_0_a_1": 0.8,
                    },
                }

            app = create_app(
                inbox_path=root / "inbox.jsonl",
                usage_path=root / "usage.jsonl",
                review_events_path=root / "review.jsonl",
                media_database_path=database,
                media_root=media_root,
                media_derivatives_path=derivatives,
                env_file=root / ".env",
                gemini_image_analyzer=fake_analyzer,
            )
            with TestClient(app) as client:
                cluster = client.get("/api/media/clusters").json()[0]
                analyzed = client.post(
                    f"/api/media/clusters/{cluster['id']}/technical-analysis"
                )
                self.assertEqual(analyzed.status_code, 200)
                members = analyzed.json()["members"]
                thumbnail = client.get(members[0]["thumbnail_url"])
                self.assertEqual(thumbnail.status_code, 200)
                self.assertEqual(thumbnail.headers["content-type"], "image/jpeg")
                preview = client.get(members[0]["preview_url"])
                self.assertEqual(preview.status_code, 200)
                with Image.open(Path(derivatives / "analysis" / f"{members[0]['id']}.jpg")) as image:
                    self.assertLessEqual(max(image.size), 1600)

                curation = client.patch(
                    f"/api/media/clusters/{cluster['id']}/curation",
                    json={
                        "shot_types": ["panoramica_paisaje", "retrato_detalle"],
                        "content_pillars": ["vida_libre_y_naturaleza"],
                        "subject_tags": ["pollitos"],
                        "primary_asset_id": members[0]["id"],
                        "primary_shot_type": "panoramica_paisaje",
                        "primary_reasons": ["muestra_mejor_el_entorno"],
                        "primary_campaign_slots": ["facebook_portada"],
                        "secondary_asset_id": members[1]["id"],
                        "secondary_shot_type": "retrato_detalle",
                        "secondary_reasons": ["aporta_otro_angulo"],
                        "secondary_campaign_slots": ["facebook_bienvenida"],
                        "note": "Objetivo de lanzamiento.",
                    },
                )
                self.assertEqual(curation.status_code, 200)
                self.assertEqual(curation.json()["campaign_slots"], ["facebook_portada", "facebook_bienvenida"])

                denied = client.post(
                    f"/api/media/clusters/{cluster['id']}/gemini",
                    json={
                        "shot_types": ["panoramica_paisaje"],
                        "content_pillars": ["vida_libre_y_naturaleza"],
                        "subject_tags": ["pollitos"],
                        "confirm_external_processing": False,
                        "confirm_privacy_review": True,
                    },
                )
                self.assertEqual(denied.status_code, 422)
                privacy_denied = client.post(
                    f"/api/media/clusters/{cluster['id']}/gemini",
                    json={
                        "confirm_external_processing": True,
                        "confirm_privacy_review": False,
                    },
                )
                self.assertEqual(privacy_denied.status_code, 422)
                self.assertIn("personas", privacy_denied.json()["detail"])
                accepted = client.post(
                    f"/api/media/clusters/{cluster['id']}/gemini",
                    json={
                        "shot_types": ["panoramica_paisaje"],
                        "content_pillars": ["vida_libre_y_naturaleza"],
                        "subject_tags": ["pollitos"],
                        "campaign_slots": ["facebook_portada"],
                        "confirm_external_processing": True,
                        "confirm_privacy_review": True,
                    },
                )
                self.assertEqual(accepted.status_code, 200)
                self.assertTrue(accepted.json()["result"]["semantic_validation"]["valid"])
                self.assertTrue(
                    accepted.json()["result"]["external_processing"][
                        "privacy_review_confirmed"
                    ]
                )
                self.assertEqual(len(analyzer_calls), 1)
                self.assertIn("facebook_portada", analyzer_calls[0]["editorial_intent"])
                self.assertIn("pollitos", analyzer_calls[0]["editorial_intent"])

                private = client.patch(
                    f"/api/media/clusters/{cluster['id']}/curation",
                    json={
                        "group_decision": "private",
                        "primary_asset_id": members[0]["id"],
                    },
                )
                self.assertEqual(private.status_code, 200)
                blocked = client.post(
                    f"/api/media/clusters/{cluster['id']}/gemini",
                    json={
                        "confirm_external_processing": True,
                        "confirm_privacy_review": True,
                    },
                )
                self.assertEqual(blocked.status_code, 422)
                self.assertIn("privado", blocked.json()["detail"])

                discarded = client.patch(
                    f"/api/media/clusters/{cluster['id']}/curation",
                    json={
                        "group_decision": "no_usable",
                        "primary_asset_id": None,
                        "secondary_asset_id": None,
                    },
                )
                self.assertEqual(discarded.status_code, 200)
                self.assertIsNone(discarded.json()["primary_asset_id"])
                blocked = client.post(
                    f"/api/media/clusters/{cluster['id']}/gemini",
                    json={
                        "confirm_external_processing": True,
                        "confirm_privacy_review": True,
                    },
                )
                self.assertEqual(blocked.status_code, 422)
                self.assertIn("descartado", blocked.json()["detail"])


if __name__ == "__main__":
    unittest.main()
