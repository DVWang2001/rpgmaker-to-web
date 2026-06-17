import json
from pathlib import Path

from rpgmaker_to_web import gencache


def _make_game(root: Path):
    (root / "RPG_RT.ldb").write_text("x")
    cs = root / "CharSet"
    cs.mkdir()
    (cs / "Hero.png").write_bytes(b"png")
    cfg = root / "Config"
    cfg.mkdir()
    (cfg / "settings.ini").write_text("a=b")


def test_root_keeps_extension_subdir_strips(tmp_path):
    _make_game(tmp_path)
    cache = gencache.generate_index(tmp_path)["cache"]
    assert cache["rpg_rt.ldb"] == "RPG_RT.ldb"
    assert cache["charset"]["_dirname"] == "CharSet"
    assert cache["charset"]["hero"] == "Hero.png"
    assert cache["config"]["settings.ini"] == "settings.ini"


def test_write_index(tmp_path):
    _make_game(tmp_path)
    out = gencache.write_index(tmp_path)
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["metadata"]["version"] == 2
