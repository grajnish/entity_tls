import json
import os
import random
import sys
from pathlib import Path

import app.state as state
from app.constants import DEFAULT_CONFIG

def _cfg_dir() -> Path:
    # Always use %APPDATA%\EntityTLS so the EXE needs no companion files
    base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    d = base / "EntityTLS"
    d.mkdir(parents=True, exist_ok=True)
    return d

CFG_FILE = _cfg_dir() / "entity_config.json"


def _as_list(v):
    """Normalize a tier value — legacy string or new list — to a list of non-empty paths."""
    if isinstance(v, list):
        return [p for p in v if p]
    return [v] if v else []


def load_config():
    if CFG_FILE.exists():
        with open(CFG_FILE, encoding="utf-8") as f:
            loaded = json.load(f)
        merged = {**DEFAULT_CONFIG, **loaded}
        # Merge tiers: keep all custom keys; normalize every value to a list
        default_tiers = {k: [] for k in DEFAULT_CONFIG["tiers"]}
        merged["tiers"] = {
            **default_tiers,
            **{k: _as_list(v) for k, v in loaded.get("tiers", {}).items()},
        }
        merged["default_video"] = _as_list(loaded.get("default_video", []))
    else:
        merged = DEFAULT_CONFIG.copy()
        merged["tiers"] = {k: [] for k in DEFAULT_CONFIG["tiers"]}
        merged["default_video"] = []
        # write defaults so the file exists for next launch
        with open(CFG_FILE, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2, ensure_ascii=False)
    state.config.clear()
    state.config.update(merged)
    return state.config


def save_config():
    with open(CFG_FILE, "w", encoding="utf-8") as f:
        json.dump(state.config, f, indent=2, ensure_ascii=False)


def get_video(coins):
    tiers = state.config.get("tiers", {})
    # Build thresholds dynamically from whatever keys exist, sorted descending
    thresholds = sorted(
        ((int(k), k) for k in tiers if k.isdigit()),
        reverse=True,
    )
    for lower, key in thresholds:
        if coins >= lower:
            paths = _as_list(tiers.get(key, []))
            if paths:
                return random.choice(paths)
    # Fallback pool
    default = _as_list(state.config.get("default_video", []))
    return random.choice(default) if default else None
