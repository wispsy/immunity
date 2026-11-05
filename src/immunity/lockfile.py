"""Deterministic lockfile reader and writer."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Sequence

from immunity.models import PluginLock, PluginSpec


def build_lock_data(
    results: Sequence[tuple[PluginSpec, Path | None, PluginLock | None]],
) -> dict[str, Any]:
    """Build structured lockfile dictionary from sync results."""
    plugins_map: dict[str, Any] = {}
    for spec, _, lock in results:
        if lock is not None:
            plugins_map[spec.target] = lock.to_dict()

    return {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plugins": plugins_map,
    }


def write_lockfile(path: Path | str, lock_data: dict[str, Any]) -> None:
    """Save lockfile data formatted as readable JSON."""
    file_path = Path(path).expanduser().resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(lock_data, f, indent=2, sort_keys=True)
        f.write("\n")


def read_lockfile(path: Path | str) -> dict[str, Any] | None:
    """Load lockfile JSON if it exists."""
    file_path = Path(path).expanduser().resolve()
    if not file_path.is_file():
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return None
