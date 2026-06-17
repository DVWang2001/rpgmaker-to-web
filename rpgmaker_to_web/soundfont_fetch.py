"""Download and cache a free General MIDI soundfont for MIDI playback.

Default is GeneralUser GS by S. Christian Collins, which its license lets anyone
redistribute and bundle (including commercially, no attribution required). The
maintainer's GitHub repo is the sanctioned source for automated packaging, so
fetching the raw file from there is appropriate.
"""
from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

SOUNDFONT_URL = (
    "https://raw.githubusercontent.com/mrbumpy409/GeneralUser-GS/main/GeneralUser-GS.sf2"
)
SOUNDFONT_NAME = "GeneralUser-GS.sf2"


def ensure_soundfont(cache_dir, url: str = SOUNDFONT_URL, refresh: bool = False) -> Path:
    """Return a path to the cached soundfont, downloading it once if needed."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    dest = cache_dir / SOUNDFONT_NAME

    if refresh and dest.exists():
        dest.unlink()

    if not dest.exists():
        tmp = dest.with_name(dest.name + ".part")
        with urllib.request.urlopen(url, timeout=300) as resp, open(tmp, "wb") as f:
            shutil.copyfileobj(resp, f)
        tmp.replace(dest)  # atomic: never leave a half-written soundfont cached

    return dest
