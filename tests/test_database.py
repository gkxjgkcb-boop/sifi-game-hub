from pathlib import Path
import pytest
from sifo_game_hub.database import Database

def test_game_crud_and_search(tmp_path: Path):
    db = Database(tmp_path / "hub.db")
    gid = db.add_game("Portal 2", "/games/portal2.exe")
    assert db.get_game(gid)["name"] == "Portal 2"
    assert len(db.list_games("port")) == 1
    db.update_game(gid, "Portal 2 Updated", "/games/p2.exe", "cover.png")
    assert db.get_game(gid)["cover_path"] == "cover.png"
    db.remove_game(gid)
    assert db.get_game(gid) is None

def test_duplicate_path_rejected(tmp_path: Path):
    db = Database(tmp_path / "hub.db")
    db.add_game("One", "/same.exe")
    with pytest.raises(Exception): db.add_game("Two", "/same.exe")

def test_settings_upsert(tmp_path: Path):
    db = Database(tmp_path / "hub.db")
    db.set_setting("theme", "dark"); db.set_setting("theme", "light")
    assert db.get_settings()["theme"] == "light"

def test_validation(tmp_path: Path):
    db = Database(tmp_path / "hub.db")
    with pytest.raises(ValueError): db.add_game("", "/x.exe")
