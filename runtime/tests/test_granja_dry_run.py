#!/usr/bin/env python3
from __future__ import annotations

import unittest
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.dry_run import build_dry_run
from core.summary import format_summary

EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "dry-run-cases.json"


class GranjaDryRunTests(unittest.TestCase):
    def test_purchase_with_stock_proposal(self) -> None:
        result = build_dry_run(
            "Compre 2 bolsas de maiz a 95000 cada una",
            today="2026-06-14",
        )

        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(result["side_effects"], [])
        self.assertEqual(result["classification"]["intent"], "registrar_compra")
        self.assertEqual(result["classification"]["primary_domain"], "compras")
        self.assertIn("stock-insumos", result["classification"]["secondary_domains"])
        self.assertTrue(result["classification"]["requires_confirmation"])
        self.assertEqual(result["classification"]["confidence"], "medium")
        self.assertIn("compras", result["classification"]["matched_signals"])
        self.assertNotIn("bolsa", result["classification"]["matched_signals"]["stock-insumos"])
        self.assertEqual(result["ui_response"]["response_type"], "review")
        self.assertTrue(result["ui_response"]["requires_confirmation"])

        item = result["detected_data"]["items"][0]
        self.assertEqual(item["producto"], "maiz")
        self.assertEqual(item["cantidad"], 2)
        self.assertEqual(item["unidad"], "bolsa")
        self.assertEqual(item["precio_unitario"], 95000)
        self.assertEqual(item["subtotal_inferido"], 190000)

        purchase = result["drafts"]["purchase"]
        self.assertIsNotNone(purchase)
        self.assertEqual(purchase["total_inferido"], 190000)
        self.assertEqual(len(result["drafts"]["stock_movements"]), 1)

    def test_task_signal_creates_suggested_task(self) -> None:
        result = build_dry_run("Manana revisar el galpon", today="2026-06-14")

        self.assertEqual(result["mode"], "dry_run")
        self.assertEqual(result["side_effects"], [])
        self.assertEqual(result["ui_response"]["response_type"], "review")
        self.assertIn(result["classification"]["primary_domain"], {"infraestructura", "tareas-mantenimiento"})
        self.assertEqual(len(result["suggested_tasks"]), 1)
        self.assertEqual(result["drafts"]["purchase"], None)

    def test_summary_format_for_inventory_analysis(self) -> None:
        result = build_dry_run(
            "Tengo una bolsa de maiz molido de 40 kilogramos al 70 por ciento. "
            "Hasta cuando dura y que debo comprar?",
            today="2026-06-15",
        )

        summary = format_summary(result)

        self.assertIn("Intencion: analizar_existencias_reposicion", summary)
        self.assertIn("Dominio principal: stock-insumos", summary)
        self.assertIn("Existencias detectadas", summary)
        self.assertIn("maiz molido", summary)
        self.assertIn("Datos faltantes:", summary)
        self.assertIn("side_effects: []", summary)

    def test_context_guides_classification_without_side_effects(self) -> None:
        result = build_dry_run(
            "Quiero saber si en ese momento puedo usar su huevo para meter en la incubadora. "
            "Yo solo meto en la incubadora, no consumo.",
            today="2026-06-15",
            context={
                "text": "Conversacion sobre uso de huevos de aves medicadas para incubacion, no consumo.",
                "source": "source_context",
                "information_status": "pending_review",
            },
        )

        self.assertEqual(result["side_effects"], [])
        self.assertTrue(result["detected_data"]["context_used"])
        self.assertEqual(result["input"]["context"]["source"], "source_context")
        self.assertEqual(result["classification"]["intent"], "analizar_decision_operativa")
        self.assertEqual(result["classification"]["primary_domain"], "incubacion")
        self.assertIn("sanidad", result["classification"]["secondary_domains"])
        self.assertEqual(result["classification"]["risk_level"], "alto")
        self.assertIn("producto administrado", result["missing_data"])
        self.assertEqual(result["detected_data"]["items"], [])
        self.assertEqual(result["detected_data"]["stock_observations"], [])

    def test_examples_dataset(self) -> None:
        cases = json.loads(EXAMPLES_PATH.read_text(encoding="utf-8"))
        for case in cases:
            with self.subTest(case=case["id"]):
                result = build_dry_run(case["message"], today="2026-06-14", context=case.get("context"))
                expected = case["expected"]
                classification = result["classification"]

                self.assertEqual(classification["intent"], expected["intent"])
                self.assertEqual(classification["primary_domain"], expected["primary_domain"])
                self.assertEqual(classification["risk_level"], expected["risk_level"])
                self.assertEqual(classification["requires_confirmation"], expected["requires_confirmation"])
                self.assertEqual(classification["confidence"], expected["confidence"])

                for domain in expected.get("secondary_domains_include", []):
                    self.assertIn(domain, classification["secondary_domains"])
                for missing in expected.get("missing_data_include", []):
                    self.assertIn(missing, result["missing_data"])
                for domain, signals in expected.get("matched_signals_include", {}).items():
                    self.assertIn(domain, classification["matched_signals"])
                    for signal in signals:
                        self.assertIn(signal, classification["matched_signals"][domain])

                purchase_present = result["drafts"]["purchase"] is not None
                self.assertEqual(purchase_present, expected.get("purchase_present", False))
                self.assertEqual(
                    len(result["drafts"]["stock_movements"]),
                    expected.get("stock_movements_count", 0),
                )
                self.assertEqual(
                    len(result["suggested_tasks"]),
                    expected.get("suggested_tasks_count", len(result["suggested_tasks"])),
                )
                inventory_observations = result["drafts"].get("inventory_observations", [])
                if "inventory_observations_count" in expected:
                    self.assertEqual(
                        len(inventory_observations),
                        expected["inventory_observations_count"],
                    )
                for product in expected.get("inventory_products_include", []):
                    self.assertIn(
                        product,
                        [observation["producto"] for observation in inventory_observations],
                    )
                task_titles = [task["titulo"] for task in result["suggested_tasks"]]
                for title_part in expected.get("suggested_task_titles_include", []):
                    self.assertTrue(
                        any(title_part in title for title in task_titles),
                        f"{title_part!r} not found in suggested task titles: {task_titles}",
                    )


if __name__ == "__main__":
    unittest.main()
