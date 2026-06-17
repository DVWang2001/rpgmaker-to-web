"""Download, cache and extract the official EasyRPG web player (WASM)."""
from __future__ import annotations

import shutil
import tarfile
import urllib.request
from pathlib import Path

PLAYER_URL = "https://easyrpg.org/downloads/player/latest/easyrpg-player-latest-js.tar.gz"


def _download(url: str, dest: Path, timeout: int = 120) -> None:
    with urllib.request.urlopen(url, timeout=timeout) as resp, open(dest, "wb") as f:
        shutil.copyfileobj(resp, f)


def _find_player_root(extracted: Path) -> Path:
    for wasm in extracted.rglob("index.wasm"):
        return wasm.parent
    raise FileNotFoundError("index.wasm not found after extraction — player format may have changed.")


def ensure_player(cache_dir, url: str = PLAYER_URL, refresh: bool = False) -> Path:
    """Return a directory containing index.html/index.js/index.wasm (download + cache once)."""
    cache_dir = Path(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)
    tarball = cache_dir / "easyrpg-player-latest-js.tar.gz"
    extracted = cache_dir / "player"

    if refresh:
        if tarball.exists():
            tarball.unlink()
        if extracted.exists():
            shutil.rmtree(extracted)

    if not tarball.exists():
        _download(url, tarball)
    if not extracted.exists():
        extracted.mkdir(parents=True)
        with tarfile.open(tarball, "r:gz") as tar:
            try:
                tar.extractall(extracted, filter="data")  # safe extraction (Py 3.12+/backports)
            except TypeError:
                tar.extractall(extracted)  # older Python without the filter arg

    return _find_player_root(extracted)
