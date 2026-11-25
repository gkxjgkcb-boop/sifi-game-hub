from pathlib import Path
import pytest
from sifo_game_hub.services import GameLauncher, SystemMonitor, GameTools

def test_launcher_missing_file():
    with pytest.raises(FileNotFoundError): GameLauncher.launch("/definitely/not/a/game.exe")

def test_launcher_rejects_unsupported_file(tmp_path: Path):
    file = tmp_path / "game.txt"; file.write_text("x")
    with pytest.raises(ValueError): GameLauncher.launch(str(file))

def test_monitor_returns_expected_keys():
    data = SystemMonitor.snapshot()
    assert {"cpu_percent", "ram_percent", "ram_total", "windows_version", "disk_percent"} <= data.keys()

def test_installed_apps_guidance():
    assert "Settings" in GameTools.installed_apps_guidance()
