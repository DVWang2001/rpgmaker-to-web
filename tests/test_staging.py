import os
import stat
from pathlib import Path

from rpgmaker_to_web import staging


def test_stage_copies_applies_ignore_and_soundfont(tmp_path):
    game = tmp_path / "game"
    (game / "Music").mkdir(parents=True)
    (game / "RPG_RT.ldb").write_text("db")
    (game / "Music" / "bgm.mid").write_bytes(b"MThd")
    (game / "notes.bak").write_text("ignore me")  # matches *.bak
    sf = tmp_path / "sound.sf2"
    sf.write_bytes(b"SF2")
    dest = tmp_path / "out"

    staging.stage_game(game, dest, soundfont=sf)

    assert (dest / "RPG_RT.ldb").read_text() == "db"
    assert (dest / "Music" / "bgm.mid").exists()
    assert not (dest / "notes.bak").exists()              # ignored
    assert (dest / "easyrpg.soundfont").read_bytes() == b"SF2"


def test_force_rmtree_handles_readonly(tmp_path):
    d = tmp_path / "ro"
    d.mkdir()
    f = d / "x.mid"
    f.write_bytes(b"x")
    os.chmod(f, stat.S_IREAD)
    staging.force_rmtree(d)
    assert not d.exists()
