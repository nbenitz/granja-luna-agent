#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.dry_run import build_dry_run
from core.inbox import build_inbox_entry
from core.intent_forms import ensure_structured_data, update_structured_values, validate_structured_data


class IntentFormTests(unittest.TestCase):
    def test_purchase_form_preserves_multiple_detected_items(self) -> None:
        entry = build_inbox_entry(
            build_dry_run(
                "Compre 2 bolsas de maiz a 95000 cada una y "
                "1 bolsa de balanceado a 120000",
                today="2026-06-20",
            )
        )

        structured = entry["structured_data"]
        self.assertEqual(structured["schema_id"], "purchase.v2")
        self.assertEqual(len(structured["values"]["items"]), 2)
        self.assertEqual(structured["values"]["items"][0]["subtotal_inferido"], 190000)
        self.assertEqual(structured["values"]["items"][1]["subtotal_inferido"], 120000)

    def test_purchase_form_validation_reports_item_paths(self) -> None:
        entry = build_inbox_entry(build_dry_run("Compre una bolsa de maiz", today="2026-06-20"))
        update_structured_values(
            entry,
            {
                "fecha_compra": "2026-06-20",
                "proveedor": "Proveedor de prueba",
                "moneda": "PYG",
                "items": [{"producto": "maiz", "cantidad": None, "unidad": "bolsa"}],
            },
        )

        missing = validate_structured_data(entry)

        self.assertEqual(missing, [{"path": "items.0.cantidad", "label": "Cantidad del item 1"}])

    def test_purchase_v1_is_migrated_without_stock_decision(self) -> None:
        entry = build_inbox_entry(build_dry_run("Compre una bolsa de maiz", today="2026-06-20"))
        entry["structured_data"]["schema_id"] = "purchase.v1"
        entry["structured_data"]["values"]["impacto_stock"] = "confirmar_entrada"

        structured = ensure_structured_data(entry)

        self.assertEqual(structured["schema_id"], "purchase.v2")
        self.assertNotIn("impacto_stock", structured["values"])
        self.assertEqual(structured["provenance"]["fields"]["moneda"], "suggested")

    def test_existing_purchase_v2_extracts_new_adjustment_fields_from_source(self) -> None:
        entry = build_inbox_entry(
            build_dry_run(
                "Compre 7 bolsas de cascarilla a 10mil c/u, total 100mil, con 5mil de descuento",
                today="2026-06-20",
            )
        )
        entry["structured_data"]["values"].pop("descuento")
        entry["structured_data"]["values"].pop("total_declarado")

        structured = ensure_structured_data(entry)

        self.assertEqual(structured["values"]["descuento"], {"tipo": "monto", "valor": 5000})
        self.assertEqual(structured["values"]["total_declarado"], 100000)
        self.assertEqual(structured["provenance"]["fields"]["descuento"], "extracted")


if __name__ == "__main__":
    unittest.main()
