#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


RUNTIME_DIR = Path(__file__).resolve().parents[2]
SRC_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REVIEW_EVENTS = RUNTIME_DIR / "state" / "review-events.jsonl"

sys.path.insert(0, str(SRC_DIR))

from core.review_log import (  # noqa: E402
    append_review_event,
    build_curation_event,
    load_review_events,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Curate one human review event without rewriting history")
    parser.add_argument("event_id", help="ID del evento de revision original")
    parser.add_argument("--review-events", type=Path, default=DEFAULT_REVIEW_EVENTS)
    parser.add_argument("--primary-reason", required=True)
    parser.add_argument("--label", action="append", default=[])
    parser.add_argument(
        "--training-eligibility",
        required=True,
        choices=("eligible", "not_for_extraction", "needs_review", "exclude"),
    )
    parser.add_argument(
        "--note-usage",
        required=True,
        choices=("evidence", "product_feedback", "mixed", "none"),
    )
    parser.add_argument("--explanation", required=True)
    parser.add_argument("--supersedes", help="ID de una curaduria anterior que queda reemplazada")
    args = parser.parse_args()

    events = load_review_events(args.review_events)
    source = next((event for event in events if event.get("id") == args.event_id), None)
    if source is None:
        print(f"Review event not found: {args.event_id}", file=sys.stderr)
        return 1
    if not args.supersedes and any(event.get("source_review_event_id") == args.event_id for event in events):
        print(f"Review event already curated: {args.event_id}", file=sys.stderr)
        return 2
    curation = build_curation_event(
        source,
        primary_reason=args.primary_reason,
        labels=args.label,
        training_eligibility=args.training_eligibility,
        explanation=args.explanation,
        note_usage=args.note_usage,
        supersedes_curation_event_id=args.supersedes,
    )
    append_review_event(args.review_events, curation)
    print(json.dumps(curation, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
