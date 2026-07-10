#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.review_log import (
    append_review_event,
    build_changes,
    build_curation_event,
    build_review_event,
    load_review_events,
)


class ReviewLogTests(unittest.TestCase):
    def test_build_changes_tracks_nested_purchase_fields(self) -> None:
        changes = build_changes(
            {"proveedor": None, "items": [{"producto": "maiz", "cantidad": 1}]},
            {"proveedor": "Proveedor A", "items": [{"producto": "maiz", "cantidad": 2}]},
        )

        self.assertEqual(
            changes,
            [
                {"path": "items.0.cantidad", "before": 1, "after": 2, "change_type": "changed"},
                {"path": "proveedor", "before": None, "after": "Proveedor A", "change_type": "added"},
            ],
        )

    def test_review_events_are_append_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "review-events.jsonl"
            event = build_review_event(
                "correction_saved",
                "inbox-1",
                before={"proveedor": None},
                after={"proveedor": "Proveedor A"},
                section="purchase_general",
                reason="new_information",
                occurred_at="2026-06-20T10:00:00-03:00",
            )
            append_review_event(path, event)

            loaded = load_review_events(path)

            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["changes"][0]["path"], "proveedor")
            self.assertEqual(loaded[0]["reason"], "new_information")

    def test_curation_preserves_original_feedback_reference(self) -> None:
        source = build_review_event(
            "correction_saved",
            "inbox-1",
            reason="new_information",
            occurred_at="2026-06-20T10:00:00-03:00",
        )

        curated = build_curation_event(
            source,
            primary_reason="system_error",
            labels=["extraction_miss"],
            training_eligibility="eligible",
            explanation="El dato ya estaba en el texto.",
            note_usage="evidence",
            occurred_at="2026-06-20T11:00:00-03:00",
        )

        self.assertEqual(curated["source_review_event_id"], source["id"])
        self.assertEqual(curated["curation"]["original_reason"], "new_information")
        self.assertEqual(curated["curation"]["primary_reason"], "system_error")


if __name__ == "__main__":
    unittest.main()
