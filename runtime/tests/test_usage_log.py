#!/usr/bin/env python3
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
import sys


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from core.usage_log import append_usage_event, build_usage_event, load_usage_events, summarize_usage


class UsageLogTests(unittest.TestCase):
    def test_append_load_and_summarize_events(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "usage-events.jsonl"
            created = build_usage_event(
                "inbox_created",
                related_entry_id="inbox-1",
                details={"risk_level": "medio", "message_length": 42},
                occurred_at="2026-06-20T08:00:00-03:00",
            )
            reviewed = build_usage_event(
                "inbox_reviewed",
                related_entry_id="inbox-1",
                occurred_at="2026-06-20T08:05:00-03:00",
            )
            append_usage_event(path, created)
            append_usage_event(path, reviewed)

            events = load_usage_events(path)
            summary = summarize_usage(events)

            self.assertEqual(len(events), 2)
            self.assertEqual(summary["total"], 2)
            self.assertEqual(summary["by_type"]["inbox_created"], 1)
            self.assertEqual(summary["last_event_at"], "2026-06-20T08:05:00-03:00")


if __name__ == "__main__":
    unittest.main()

