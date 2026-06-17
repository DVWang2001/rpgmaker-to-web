"""Copy an RPG Maker game folder into the output (with ignore rules + optional soundfont)."""
from __future__ import annotations

import fnmatch
import os
import shutil
import stat
import sys
from pathlib import Path

DEFAULT_IGNORE = ("*.bak", "*.trans", "index.json", "Thumbs.db", ".*", "gencache*")
SOUNDFONT_NAME = "easyrpg.soundfont"


def force_rmtree(path) -> None:
    """shutil.rmtree that clears the read-only bit first.

    RPG Maker assets are often read-only; on Windows plain rmtree then fails with
    WinError 5 (access denied) when re-cleaning an output folder.
    """
    if not os.path.exists(path):
        return

    def on_error(func, p, _exc):
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if sys.version_info >= (3, 12):
        shutil.rmtree(path, onexc=on_error)
    else:
        shutil.rmtree(path, onerror=on_error)


def _ignored(name: str, ignore_globs) -> bool:
    return any(fnmatch.fnmatch(name, pat) for pat in ignore_globs)


def stage_game(game_dir, dest, *, ignore_globs=DEFAULT_IGNORE, soundfont=None) -> None:
    game_dir = Path(game_dir)
    dest = Path(dest)
    force_rmtree(dest)
    dest.mkdir(parents=True)
    for item in game_dir.rglob("*"):
        rel = item.relative_to(game_dir)
        if any(_ignored(part, ignore_globs) for part in rel.parts):
            continue
        target = dest / rel
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        else:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(item, target)
    if soundfont:
        shutil.copy2(Path(soundfont), dest / SOUNDFONT_NAME)
