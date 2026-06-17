import io
import json
import tarfile
from pathlib import Path

from rpgmaker_to_web import webify


def _fake_player_tarball(path: Path):
    html = (b'<!doctype html><html><head><title>EasyRPG Player</title>'
            b'<meta name="viewport" content="width=device-width, initial-scale=1.0"></head>'
            b'<body><script async src="index.js"></script>'
            b'<script>createEasyRpgPlayer({ game: undefined, saveFs: undefined });</script>'
            b'</body></html>')
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        for name, data in [("index.html", html), ("index.js", b"// js"), ("index.wasm", b"\0asm")]:
            info = tarfile.TarInfo(name)
            info.size = len(data)
            tar.addfile(info, io.BytesIO(data))
    path.write_bytes(buf.getvalue())


def _game(root: Path):
    root.mkdir()
    (root / "RPG_RT.ldb").write_text("x")
    (root / "CharSet").mkdir()
    (root / "CharSet" / "Hero.png").write_bytes(b"png")


def test_build_produces_embeddable_web_files(tmp_path):
    tarball = tmp_path / "player.tar.gz"
    _fake_player_tarball(tarball)
    game = tmp_path / "MyGame"
    _game(game)
    out = tmp_path / "dist"

    result = webify.build(game, out=out, player_cache=tmp_path / "cache",
                          player_url=tarball.resolve().as_uri(),
                          soundfont=None, log=lambda *_: None)

    assert result == out
    assert (out / "index.js").exists()
    assert (out / "index.wasm").exists()
    assert (out / "games" / "mygame" / "index.json").exists()
    page = (out / "index.html").read_text(encoding="utf-8")
    assert 'game: "mygame"' in page          # 該遊戲被烤進去
    assert "<title>MyGame</title>" in page    # 標題＝資料夾名

    # The reliability pipeline: service worker + precache + page wiring.
    assert (out / "service-worker.js").exists()
    assert "navigator.serviceWorker.register('service-worker.js')" in page
    assert "track('AudioContext')" in page  # audio unlock shim injected
    assert 'fetch("precache-"+SLUG+".json")' in page
    precache = json.loads((out / "precache-mygame.json").read_text(encoding="utf-8"))
    assert "index.js" in precache and "index.wasm" in precache and "index.html" in precache
    assert "games/mygame/CharSet/Hero.png" in precache  # game assets get precached
    assert "games/mygame/index.json" in precache


def test_build_custom_title(tmp_path):
    tarball = tmp_path / "player.tar.gz"
    _fake_player_tarball(tarball)
    game = tmp_path / "g"
    _game(game)
    out = webify.build(game, out=tmp_path / "d", title="勇者傳說",
                       player_cache=tmp_path / "c",
                       player_url=tarball.resolve().as_uri(),
                       soundfont=None, log=lambda *_: None)
    assert "<title>勇者傳說</title>" in (out / "index.html").read_text(encoding="utf-8")


def test_build_stages_custom_soundfont(tmp_path):
    tarball = tmp_path / "player.tar.gz"
    _fake_player_tarball(tarball)
    game = tmp_path / "g"
    _game(game)
    sf = tmp_path / "my.sf2"
    sf.write_bytes(b"RIFF....sfbk fake")
    out = webify.build(game, out=tmp_path / "d", player_cache=tmp_path / "c",
                       player_url=tarball.resolve().as_uri(),
                       soundfont=sf, log=lambda *_: None)
    staged = out / "games" / "g" / "easyrpg.soundfont"
    assert staged.exists() and staged.read_bytes() == sf.read_bytes()
    precache = json.loads((out / "precache-g.json").read_text(encoding="utf-8"))
    assert "games/g/easyrpg.soundfont" in precache


def test_build_rejects_non_game(tmp_path):
    bad = tmp_path / "bad"
    bad.mkdir()
    (bad / "readme.txt").write_text("nope")
    try:
        webify.build(bad, out=tmp_path / "d", log=lambda *_: None)
        assert False, "should reject non-RPG-Maker folder"
    except webify.BuildError:
        pass


def test_iframe_snippet():
    s = webify.iframe_snippet()
    assert "<iframe" in s and 'src="index.html"' in s and "allowfullscreen" in s
