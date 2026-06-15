#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.dry_run import build_dry_run


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


if __name__ == "__main__":
    unittest.main()
