"""Load explicitly allowed local secrets without logging their values."""

from __future__ import annotations

import os
from pathlib import Path


def get_local_secret(name: str, env_file: Path) -> str:
    """Return an environment variable or its value from a simple local .env file."""
    inherited = os.environ.get(name, "").strip()
    if inherited:
        return inherited

    if not env_file.is_file():
        raise RuntimeError(f"Falta {name}; no existe el archivo local {env_file}")

    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line.removeprefix("export ").strip()
        key, separator, raw_value = line.partition("=")
        if separator and key.strip() == name:
            value = raw_value.strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
                value = value[1:-1]
            if value:
                return value
            break

    raise RuntimeError(f"{name} esta vacia o ausente en {env_file}")
