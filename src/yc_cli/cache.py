from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any

CACHE_DIR = Path.home() / ".cache" / "yc-cli"


def _cache_path(url: str) -> Path:
    h = hashlib.sha256(url.encode()).hexdigest()[:16]
    return CACHE_DIR / f"{h}.json"


def get(url: str, ttl_hours: int = 24) -> Any | None:
    path = _cache_path(url)
    if not path.exists():
        return None
    age_hours = (time.time() - path.stat().st_mtime) / 3600
    if age_hours > ttl_hours:
        return None
    try:
        return json.loads(path.read_text())
    except (json.JSONDecodeError, OSError):
        path.unlink(missing_ok=True)
        return None


def put(url: str, data: Any) -> None:
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        _cache_path(url).write_text(json.dumps(data))
    except OSError:
        pass


def clear() -> int:
    if not CACHE_DIR.exists():
        return 0
    count = 0
    for f in CACHE_DIR.glob("*.json"):
        f.unlink()
        count += 1
    return count
