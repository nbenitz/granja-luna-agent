#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.operations import load_operation_events
from web.app import create_app


class FarmOperationsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tempdir = tempfile.TemporaryDirectory()
        root = Path(self.tempdir.name)
        self.operations_path = root / "operation-events.jsonl"
        self.client = TestClient(
            create_app(
                root / "inbox.jsonl",
                root / "usage-events.jsonl",
                root / "review-events.jsonl",
                self.operations_path,
            )
        )

    def tearDown(self) -> None:
        self.client.close()
        self.tempdir.cleanup()

    def test_purchase_requires_one_missing_datum_at_a_time(self) -> None:
        response = self.client.post(
            "/api/operations/movements/purchase/drafts",
            json={"source": "personal_agent_mcp", "actor": "chatgpt_remote_user"},
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["missing_field"], "effective_date")
        self.assertEqual(
            response.json()["detail"]["question"],
            "¿Cuál fue la fecha de compra?",
        )
        self.assertFalse(self.operations_path.exists())

    def test_purchase_rejects_inconsistent_declared_total(self) -> None:
        response = self.client.post(
            "/api/operations/movements/purchase/drafts",
            json={
                "effective_date": "2026-07-21",
                "supplier": "Proveedor de prueba",
                "items": [
                    {
                        "product": "Maíz",
                        "quantity": 2,
                        "unit": "bolsa",
                        "unit_price": 95000,
                    }
                ],
                "price_status": "confirmed",
                "currency": "PYG",
                "total_amount": 200000,
                "update_inventory": True,
            },
        )

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["detail"]["missing_field"], "total_amount")
        self.assertEqual(
            response.json()["detail"]["question"],
            "¿Cuál es el total correcto de la compra?",
        )
        self.assertFalse(self.operations_path.exists())

    def test_purchase_draft_confirmation_inventory_and_trace(self) -> None:
        drafted = self.client.post(
            "/api/operations/movements/purchase/drafts",
            json={
                "effective_date": "2026-07-21",
                "supplier": "Proveedor confirmado",
                "items": [
                    {
                        "product": "Maíz",
                        "quantity": 2,
                        "unit": "bolsa",
                        "unit_price": 95000,
                        "category": "alimento",
                    }
                ],
                "price_status": "confirmed",
                "currency": "PYG",
                "total_amount": None,
                "update_inventory": True,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
                "request_id": "request-1",
            },
        )

        self.assertEqual(drafted.status_code, 201)
        draft = drafted.json()
        self.assertEqual(draft["status"], "awaiting_confirmation")
        self.assertEqual(draft["data"]["total_amount"], 190000)
        self.assertEqual(draft["data"]["total_provenance"], "calculated")
        self.assertIsNone(draft["trace"]["confirmed"])
        self.assertIsNone(draft["trace"]["registered"])
        self.assertEqual(
            self.client.get("/api/operations/inventory").json()["items"], []
        )

        denied = self.client.post(
            f"/api/operations/movements/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": False,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
            },
        )
        self.assertEqual(denied.status_code, 422)
        self.assertEqual(
            denied.json()["detail"]["code"], "explicit_confirmation_required"
        )

        confirmed = self.client.post(
            f"/api/operations/movements/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
                "request_id": "request-2",
            },
        )

        self.assertEqual(confirmed.status_code, 200)
        movement = confirmed.json()
        self.assertEqual(movement["status"], "applied")
        self.assertTrue(movement["trace"]["confirmed"]["explicit"])
        self.assertEqual(movement["trace"]["registered"]["operation_status"], "applied")
        inventory = self.client.get("/api/operations/inventory").json()
        self.assertEqual(inventory["scope"], "confirmed_bridge_movements_only")
        self.assertEqual(inventory["items"][0]["quantity"], 2)
        self.assertEqual(inventory["items"][0]["unit"], "bolsa")

        replay = self.client.post(
            f"/api/operations/movements/{draft['id']}/confirm",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
            },
        )
        self.assertTrue(replay.json()["idempotent_replay"])
        self.assertEqual(len(load_operation_events(self.operations_path)), 2)

    def test_daily_summary_uses_only_applied_movements(self) -> None:
        egg_draft = self.client.post(
            "/api/operations/movements/egg_collection/drafts",
            json={
                "effective_date": "2026-07-21",
                "flock": "Reproductores norte",
                "eggs_total": 42,
                "eggs_healthy": 40,
                "eggs_broken": 2,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
            },
        ).json()
        self.client.post(
            "/api/operations/movements/expense/drafts",
            json={
                "effective_date": "2026-07-21",
                "description": "Flete",
                "category": "transporte",
                "amount": 50000,
                "currency": "PYG",
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
            },
        )

        pending = self.client.get(
            "/api/operations/movements?status=awaiting_confirmation"
        ).json()
        self.assertEqual(len(pending), 2)
        empty = self.client.get("/api/operations/daily-summary?date=2026-07-21").json()
        self.assertEqual(empty["confirmed_movements"], 0)

        self.client.post(
            f"/api/operations/movements/{egg_draft['id']}/confirm",
            json={
                "confirmation_code": egg_draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "source": "personal_agent_mcp",
                "actor": "chatgpt_remote_user",
            },
        )
        summary = self.client.get(
            "/api/operations/daily-summary?date=2026-07-21"
        ).json()
        self.assertEqual(summary["confirmed_movements"], 1)
        self.assertEqual(summary["eggs_collected"], 42)
        self.assertEqual(summary["by_type"], {"egg_collection": 1})

    def test_expense_and_sale_are_drafts_before_financial_summary(self) -> None:
        expense = self.client.post(
            "/api/operations/movements/expense/drafts",
            json={
                "effective_date": "2026-07-21",
                "description": "Flete de prueba",
                "category": "transporte",
                "amount": 20,
                "currency": "TEST",
            },
        ).json()
        sale = self.client.post(
            "/api/operations/movements/sale/drafts",
            json={
                "effective_date": "2026-07-21",
                "items": [
                    {"product": "Huevos de prueba", "quantity": 12, "unit": "unidad"}
                ],
                "total_amount": 120,
                "currency": "TEST",
                "update_inventory": False,
            },
        ).json()

        before = self.client.get("/api/operations/daily-summary?date=2026-07-21").json()
        self.assertEqual(before["confirmed_movements"], 0)
        for movement in (expense, sale):
            response = self.client.post(
                f"/api/operations/movements/{movement['id']}/confirm",
                json={
                    "confirmation_code": movement["confirmation"]["code"],
                    "explicit_confirmation": True,
                },
            )
            self.assertEqual(response.status_code, 200)

        summary = self.client.get(
            "/api/operations/daily-summary?date=2026-07-21"
        ).json()
        self.assertEqual(summary["by_type"], {"expense": 1, "sale": 1})
        self.assertEqual(summary["money"]["TEST"], {"expense": 20, "sale": 120})

    def test_no_delete_endpoint_is_exposed(self) -> None:
        response = self.client.delete("/api/operations/movements/anything")
        self.assertEqual(response.status_code, 405)

    def test_pending_movement_can_be_cancelled_without_inventory_effect(self) -> None:
        draft = self.client.post(
            "/api/operations/movements/egg_collection/drafts",
            json={
                "effective_date": "2026-07-21",
                "flock": "Plantel de prueba",
                "eggs_total": 22,
            },
        ).json()
        response = self.client.post(
            f"/api/operations/movements/{draft['id']}/cancel",
            json={
                "confirmation_code": draft["confirmation"]["code"],
                "explicit_confirmation": True,
                "reason": "Cantidad incorrecta",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "cancelled")
        self.assertEqual(
            response.json()["trace"]["cancelled"]["reason"], "Cantidad incorrecta"
        )
        self.assertEqual(
            self.client.get(
                "/api/operations/movements?status=awaiting_confirmation"
            ).json(),
            [],
        )


if __name__ == "__main__":
    unittest.main()
