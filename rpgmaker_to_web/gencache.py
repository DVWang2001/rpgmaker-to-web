"""EasyRPG index.json generator (vendored from the `easyrpg-gencache` project).

Pure standard library, zero dependencies. Faithful reimplementation of EasyRPG/Tools
gencache. Kept as a single vendored file so this tool runs self-contained.
"""
from __future__ import annotations

import json
import os
import unicodedata
from datetime import date
from pathlib import Path

KEEP_EXTENSION = (".ini", ".po")
DEFAULT_DEPTH = 4


def _norm(name: str) -> str:
    return unicodedata.normalize("NFKC", name.lower())


def _strip_ext(name: str) -> str:
    dot = name.rfind(".")
    return name if dot < 0 else name[:dot]


def _keep_extension(lower_name: str) -> bool:
    return lower_name.endswith(KEEP_EXTENSION)


def _walk(path: Path, depth: int, first: bool = False) -> dict:
    if depth == 0:
        return {}
    try:
        entries = list(os.scandir(path))
    except OSError:
        return {}
    result: dict = {}
    if not first:
        result["_dirname"] = path.name
    for entry in entries:
        original = entry.name
        if original == "_dirname":
            continue
        lower = _norm(original)
        if entry.is_dir():
            sub = _walk(Path(entry.path), depth - 1)
            if sub:
                result[lower] = sub
        elif entry.is_file():
            if first or _keep_extension(lower):
                key = "exfont" if _strip_ext(lower) == "exfont" else lower
                result[key] = original
            else:
                result[_strip_ext(lower)] = original
    return result


def generate_index(game_dir, depth: int = DEFAULT_DEPTH) -> dict:
    cache = _walk(Path(game_dir), depth, first=True)
    return {
        "metadata": {"version": 2, "date": date.today().isoformat()},
        "cache": cache,
    }


def write_index(game_dir, output=None, depth: int = DEFAULT_DEPTH) -> Path:
    game_dir = Path(game_dir)
    output = Path(output) if output else game_dir / "index.json"
    data = generate_index(game_dir, depth)
    output.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
        encoding="utf-8",
    )
    return output
