#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.media_curation import (  # noqa: E402
    analyze_cluster_locally,
    get_cluster,
    save_cluster_curation,
    validate_gemini_burst_result,
)
from core.media_library import connect_media_library, list_media_clusters, scan_media_library  # noqa: E402


PIL_AVAILABLE = importlib.util.find_spec("PIL") is not None


def fake_metadata(_path: Path, _kind: str) -> dict[str, object]:
    return {"width": 640, "height": 480, "orientation": 1, "gps_present": False}


@unittest.skipUnless(PIL_AVAILABLE, "Pillow no está instalado en este entorno de pruebas")
class MediaCurationTests(unittest.TestCase):
    def test_local_analysis_curation_and_rescan_preserve_human_selection(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "inbox"
            root.mkdir()
            derivatives = Path(tmpdir) / "derivatives"
            database = Path(tmpdir) / "media.sqlite3"
            first = root / "20260801_120000.jpg"
            second = root / "20260801_120005.jpg"
            Image.new("RGB", (640, 480), (90, 130, 70)).save(first, exif=b"Exif\x00\x00")
            Image.new("RGB", (640, 480), (150, 170, 90)).save(second)
            originals = {first: first.read_bytes(), second: second.read_bytes()}
            scan_media_library(root, database, metadata_reader=fake_metadata)

            with connect_media_library(database) as connection:
                cluster_id = list_media_clusters(connection, cluster_type="temporal_burst")[0]["id"]
                cluster = analyze_cluster_locally(
                    connection,
                    cluster_id,
                    media_root=root,
                    derivative_root=derivatives,
                )
                primary, secondary = [member["id"] for member in cluster["members"]]
                saved = save_cluster_curation(
                    connection,
                    cluster_id,
                    shot_types=["panoramica_paisaje", "retrato_detalle"],
                    content_pillars=["vida_libre_y_naturaleza"],
                    subject_tags=["pollitos", "pastoreo"],
                    primary_asset_id=primary,
                    primary_intent="panoramica_paisaje",
                    primary_reasons=["muestra_mejor_el_entorno"],
                    primary_campaign_slots=["facebook_portada"],
                    secondary_asset_id=secondary,
                    secondary_intent="retrato_detalle",
                    secondary_reasons=["aporta_otro_angulo"],
                    secondary_campaign_slots=["facebook_bienvenida"],
                    note="Principal panorámica y detalle secundario.",
                )

            self.assertEqual(saved["campaign_slots"], ["facebook_portada", "facebook_bienvenida"])
            self.assertEqual(saved["content_pillars"], ["vida_libre_y_naturaleza"])
            self.assertEqual(saved["primary_reasons"], ["muestra_mejor_el_entorno"])
            self.assertTrue(all(member["thumbnail_url"] for member in cluster["members"]))
            self.assertTrue(all(member["preview_url"] for member in cluster["members"]))
            self.assertTrue(all(member["perceptual_hash"] for member in cluster["members"]))
            self.assertEqual({path: path.read_bytes() for path in originals}, originals)

            scan_media_library(root, database, metadata_reader=fake_metadata)
            with connect_media_library(database) as connection:
                persisted = get_cluster(connection, cluster_id)
            self.assertEqual(persisted["curation"]["primary_asset_id"], primary)
            self.assertEqual(persisted["curation"]["secondary_asset_id"], secondary)

    def test_group_can_be_reviewed_without_forcing_a_favorite(self) -> None:
        from PIL import Image

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "inbox"
            root.mkdir()
            database = Path(tmpdir) / "media.sqlite3"
            Image.new("RGB", (640, 480), (90, 130, 70)).save(root / "20260801_120000.jpg")
            Image.new("RGB", (640, 480), (120, 150, 80)).save(root / "20260801_120005.jpg")
            scan_media_library(root, database, metadata_reader=fake_metadata)
            with connect_media_library(database) as connection:
                cluster_id = list_media_clusters(connection, cluster_type="temporal_burst")[0]["id"]
                saved = save_cluster_curation(
                    connection,
                    cluster_id,
                    group_decision="no_usable",
                    note="No representa el objetivo de la toma.",
                )
            self.assertEqual(saved["group_decision"], "no_usable")
            self.assertIsNone(saved["primary_asset_id"])

    def test_gemini_result_must_reference_the_exact_candidates(self) -> None:
        candidates = ["foto-1.jpg", "foto-2.jpg"]
        result = {
            "valid_json": True,
            "analysis": {
                "mejor_archivo": "foto-1.jpg",
                "sin_candidata_adecuada": False,
                "favoritos_por_intencion": [
                    {"archivo": "foto-1.jpg", "prioridad": "principal"}
                ],
                "ranking": [
                    {"archivo": "foto-1.jpg"},
                    {"archivo": "foto-2.jpg"},
                ],
                "afirmaciones_que_requieren_verificacion": [],
                "requiere_eleccion_humana": True,
                "confianza_0_a_1": 0.8,
            },
        }

        valid = validate_gemini_burst_result(result, candidates)
        self.assertTrue(valid["valid"])

        result["analysis"]["mejor_archivo"] = "foto-ajena.jpg"
        invalid = validate_gemini_burst_result(result, candidates)
        self.assertFalse(invalid["valid"])
        self.assertIn("La mejor foto indicada no pertenece al grupo.", invalid["errors"])

        result["analysis"]["mejor_archivo"] = "foto-1.jpg"
        result["analysis"]["favoritos_por_intencion"][0]["motivo"] = (
            "Permite evaluar pureza racial."
        )
        risky_claim = validate_gemini_burst_result(result, candidates)
        self.assertFalse(risky_claim["valid"])
        self.assertTrue(
            any("evaluar pureza" in error for error in risky_claim["errors"])
        )

    def test_gemini_no_candidate_cannot_keep_favorites(self) -> None:
        validation = validate_gemini_burst_result(
            {
                "valid_json": True,
                "analysis": {
                    "mejor_archivo": "",
                    "sin_candidata_adecuada": True,
                    "favoritos_por_intencion": [
                        {"archivo": "foto-1.jpg", "prioridad": "principal"}
                    ],
                    "ranking": [{"archivo": "foto-1.jpg"}],
                    "afirmaciones_que_requieren_verificacion": [],
                    "requiere_eleccion_humana": True,
                    "confianza_0_a_1": 0.9,
                },
            },
            ["foto-1.jpg"],
        )

        self.assertFalse(validation["valid"])
        self.assertIn(
            "Gemini indicó que ninguna sirve, pero también eligió favoritas.",
            validation["errors"],
        )


if __name__ == "__main__":
    unittest.main()
