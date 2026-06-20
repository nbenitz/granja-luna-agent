#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.dry_run import build_dry_run
from core.inbox import (
    append_inbox_entry,
    build_inbox_entry,
    filter_inbox_entries,
    find_inbox_entry,
    format_inbox_detail,
    load_inbox_entries,
    summarize_inbox,
    update_inbox_entry_status,
    write_inbox_entries,
)


class InboxTests(unittest.TestCase):
    def test_build_inbox_entry_from_dry_run(self) -> None:
        dry_run = build_dry_run(
            "Compre 2 bolsas de maiz a 95000 cada una",
            today="2026-06-16",
        )

        entry = build_inbox_entry(dry_run, created_at="2026-06-16T10:30:00-03:00")

        self.assertTrue(entry["id"].startswith("inbox-20260616T103000-"))
        self.assertEqual(entry["status"], "pending_review")
        self.assertEqual(entry["information_status"], "pending_review")
        self.assertEqual(entry["side_effects"], [])
        self.assertEqual(entry["classification"]["intent"], "registrar_compra")
        self.assertEqual(entry["classification"]["primary_domain"], "compras")
        self.assertTrue(entry["classification"]["requires_confirmation"])
        self.assertEqual(entry["dry_run"]["mode"], "dry_run")
        self.assertEqual(entry["dry_run"]["side_effects"], [])

    def test_append_load_find_filter_and_summarize(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox_path = Path(tmpdir) / "inbox.jsonl"
            purchase = build_inbox_entry(
                build_dry_run("Compre una bolsa de balanceado", today="2026-06-16"),
                created_at="2026-06-16T08:00:00-03:00",
            )
            task = build_inbox_entry(
                build_dry_run("Manana revisar el galpon", today="2026-06-16"),
                created_at="2026-06-16T09:00:00-03:00",
            )
            append_inbox_entry(inbox_path, purchase)
            append_inbox_entry(inbox_path, task)

            entries = load_inbox_entries(inbox_path)
            self.assertEqual(len(entries), 2)
            self.assertEqual(find_inbox_entry(entries, purchase["id"])["message"], purchase["message"])
            self.assertEqual(len(filter_inbox_entries(entries, "pending_review")), 2)

            summary = summarize_inbox(entries)
            self.assertEqual(summary["total"], 2)
            self.assertEqual(summary["by_status"]["pending_review"], 2)
            self.assertEqual(summary["requires_confirmation"], 1)
            self.assertEqual(summary["by_primary_domain"]["compras"], 1)

    def test_format_detail_marks_pending_without_side_effects(self) -> None:
        entry = build_inbox_entry(
            build_dry_run("Manana revisar el galpon", today="2026-06-16"),
            created_at="2026-06-16T09:00:00-03:00",
        )

        detail = format_inbox_detail(entry)

        self.assertIn("Estado: pending_review", detail)
        self.assertIn("No se aplicaron cambios operativos. side_effects: []", detail)

    def test_update_status_keeps_entry_as_non_operational(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            inbox_path = Path(tmpdir) / "inbox.jsonl"
            entry = build_inbox_entry(
                build_dry_run("Manana revisar el galpon", today="2026-06-16"),
                created_at="2026-06-16T09:00:00-03:00",
            )
            append_inbox_entry(inbox_path, entry)

            entries = load_inbox_entries(inbox_path)
            updated = update_inbox_entry_status(
                entries,
                entry["id"],
                "needs_edit",
                reviewed_at="2026-06-16T10:00:00-03:00",
                notes="Falta responsable",
            )
            write_inbox_entries(inbox_path, entries)

            reloaded = load_inbox_entries(inbox_path)
            self.assertEqual(len(reloaded), 1)
            self.assertEqual(updated["status"], "needs_edit")
            self.assertEqual(reloaded[0]["review"]["notes"], "Falta responsable")
            self.assertEqual(reloaded[0]["side_effects"], [])


if __name__ == "__main__":
    unittest.main()
