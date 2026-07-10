from __future__ import annotations

from pathlib import Path
import sys
import tempfile

import uvicorn


ROOT_DIR = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT_DIR / "runtime" / "src"))

from web.app import create_app  # noqa: E402


TEMP_STATE = tempfile.TemporaryDirectory()
STATE_DIR = Path(TEMP_STATE.name)
app = create_app(
    STATE_DIR / "inbox.jsonl",
    STATE_DIR / "usage-events.jsonl",
    STATE_DIR / "review-events.jsonl",
)


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8011, log_level="warning")
