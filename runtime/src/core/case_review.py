from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any


ReviewEntry = dict[str, Any]
Case = dict[str, Any]


def load_imported_cases(path: Path) -> list[Case]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = []
    for section in ("conversation_candidates", "synthetic_variants"):
        for item in payload.get(section, []):
            case = dict(item)
            case.setdefault("case_kind", section.rstrip("s"))
            case.setdefault("expected", build_expected_from_compact_case(case))
            cases.append(case)
    return cases


def build_expected_from_compact_case(case: Case) -> dict[str, Any]:
    return {
        "intent": case.get("expected_intent"),
        "candidate_intent": None,
        "primary_domain": case.get("primary_domain"),
        "secondary_domains": case.get("secondary_domains", []),
        "risk_level": case.get("risk_level"),
        "requires_confirmation": case.get("requires_confirmation"),
        "detected_data": {},
        "missing_data": case.get("missing_data", []),
        "suggested_drafts": [],
        "should_not_do": ["no registrar como hecho confirmado sin confirmacion"],
    }


def load_feedback_entries(path: Path) -> list[ReviewEntry]:
    if not path.exists():
        return []
    entries = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSONL at {path}:{line_number}: {exc}") from exc
    return entries


def latest_feedback_by_case(entries: list[ReviewEntry]) -> dict[str, ReviewEntry]:
    latest: dict[str, ReviewEntry] = {}
    for entry in entries:
        latest[entry["case_id"]] = entry
    return latest


def append_feedback(path: Path, entry: ReviewEntry) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(json.dumps(entry, ensure_ascii=False, sort_keys=True) + "\n")


def input_digest(case: Case) -> str:
    text = case.get("input_text", "")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def expected_snapshot(case: Case) -> dict[str, Any]:
    expected = case.get("expected", {})
    return {
        "intent": expected.get("intent"),
        "candidate_intent": expected.get("candidate_intent"),
        "primary_domain": expected.get("primary_domain"),
        "secondary_domains": expected.get("secondary_domains", []),
        "risk_level": expected.get("risk_level"),
        "requires_confirmation": expected.get("requires_confirmation"),
        "missing_data_count": len(expected.get("missing_data", [])),
    }


def runtime_snapshot(result: dict[str, Any]) -> dict[str, Any]:
    classification = result["classification"]
    return {
        "intent": classification["intent"],
        "primary_domain": classification["primary_domain"],
        "secondary_domains": classification.get("secondary_domains", []),
        "risk_level": classification["risk_level"],
        "requires_confirmation": classification["requires_confirmation"],
        "confidence": classification.get("confidence"),
        "missing_data_count": len(result.get("missing_data", [])),
        "side_effects": result.get("side_effects", []),
    }


def summarize_reviews(cases: list[Case], entries: list[ReviewEntry]) -> dict[str, Any]:
    latest = latest_feedback_by_case(entries)
    decisions = Counter(entry.get("review_decision", "unknown") for entry in latest.values())
    text_judgments = Counter(entry.get("text_judgment", "unknown") for entry in latest.values())
    expected_judgments = Counter(entry.get("expected_judgment", "unknown") for entry in latest.values())
    return {
        "total_cases": len(cases),
        "reviewed_cases": len(latest),
        "pending_cases": len(cases) - len(latest),
        "decisions": dict(decisions),
        "text_judgments": dict(text_judgments),
        "expected_judgments": dict(expected_judgments),
    }


def find_case(cases: list[Case], case_id: str) -> Case:
    for case in cases:
        if case.get("id") == case_id:
            return case
    raise KeyError(f"Case not found: {case_id}")


def truncate(text: str, max_length: int = 110) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."
