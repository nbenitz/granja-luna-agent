from __future__ import annotations

import json
from pathlib import Path
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from core.case_review import (  # noqa: E402
    append_feedback,
    expected_snapshot,
    input_digest,
    latest_feedback_by_case,
    load_feedback_entries,
    load_imported_cases,
    summarize_reviews,
)


EXAMPLES_PATH = Path(__file__).resolve().parents[1] / "examples" / "imported-cases-pending-review.json"


class CaseReviewTests(unittest.TestCase):
    def test_imported_cases_load_as_reviewable_cases(self) -> None:
        cases = load_imported_cases(EXAMPLES_PATH)

        self.assertEqual(len(cases), 24)
        first = cases[0]
        self.assertEqual(first["id"], "gl-001-ivermectina-agua-26-aves")
        self.assertEqual(expected_snapshot(first)["primary_domain"], "sanidad")
        self.assertEqual(len(input_digest(first)), 16)

    def test_feedback_jsonl_round_trip_and_summary(self) -> None:
        cases = load_imported_cases(EXAMPLES_PATH)
        with tempfile.TemporaryDirectory() as directory:
            feedback_path = Path(directory) / "feedback.jsonl"
            append_feedback(
                feedback_path,
                {
                    "case_id": cases[0]["id"],
                    "review_decision": "keep_pending",
                    "text_judgment": "representative",
                    "expected_judgment": "accepted",
                },
            )
            append_feedback(
                feedback_path,
                {
                    "case_id": cases[0]["id"],
                    "review_decision": "promote_to_learning_dataset",
                    "text_judgment": "representative",
                    "expected_judgment": "corrected",
                },
            )

            entries = load_feedback_entries(feedback_path)
            latest = latest_feedback_by_case(entries)
            summary = summarize_reviews(cases, entries)

        self.assertEqual(len(entries), 2)
        self.assertEqual(latest[cases[0]["id"]]["review_decision"], "promote_to_learning_dataset")
        self.assertEqual(summary["reviewed_cases"], 1)
        self.assertEqual(summary["pending_cases"], 23)
        self.assertEqual(summary["decisions"]["promote_to_learning_dataset"], 1)

    def test_invalid_feedback_jsonl_reports_line_number(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            feedback_path = Path(directory) / "feedback.jsonl"
            feedback_path.write_text(json.dumps({"case_id": "ok"}) + "\n{bad json}\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "feedback.jsonl:2"):
                load_feedback_entries(feedback_path)


if __name__ == "__main__":
    unittest.main()
