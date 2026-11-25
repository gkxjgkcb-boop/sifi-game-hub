"""Operating-system services used by the UI."""
from __future__ import annotations
import os
import platform
import subprocess
import tempfile
from pathlib import Path
from typing import Any

class GameLauncher:
    @staticmethod
    def launch(executable_path: str) -> subprocess.Popen[Any]:
        path = Path(executable_path).expanduser()
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"Game executable not found: {path}")
        suffix = path.suffix.lower()
        if suffix not in {".exe", ".com", ".sh"}:
            raise ValueError("Unsupported executable file type.")
        if os.name == "nt":
            if suffix == ".sh":
                raise ValueError("Shell scripts cannot be launched on Windows.")
            try:
                return subprocess.Popen([str(path)], cwd=str(path.parent))
            except OSError as exc:
                if getattr(exc, "winerror", None) == 740:  # game requires administrator rights
                    os.startfile(str(path))  # type: ignore[attr-defined]  # triggers the UAC prompt
                    return None  # type: ignore[return-value]
                raise
        if suffix == ".sh":
            return subprocess.Popen([str(path)], cwd=str(path.parent))
        raise OSError("Launching Windows games is supported on Windows only.")

class SystemMonitor:
    @staticmethod
    def snapshot() -> dict[str, Any]:
        data: dict[str, Any] = {"cpu_percent": None, "ram_percent": None, "ram_total": None,
                                "ram_available": None, "cpu_name": platform.processor() or "Unavailable",
                                "windows_version": platform.platform(), "disk_percent": None,
                                "disk_total": None, "disk_free": None}
        try:
            import psutil
            vm = psutil.virtual_memory()
            data.update(cpu_percent=psutil.cpu_percent(interval=None), ram_percent=vm.percent,
                        ram_total=vm.total, ram_available=vm.available)
            root = Path.home().anchor or "/"
            disk = psutil.disk_usage(root)
            data.update(disk_percent=disk.percent, disk_total=disk.total, disk_free=disk.free)
        except (ImportError, OSError, PermissionError):
            pass
        if os.name == "nt":
            data["windows_version"] = f"Windows {platform.version()} ({platform.machine()})"
        return data

class GameTools:
    @staticmethod
    def open_temp_folder() -> None:
        path = Path(tempfile.gettempdir())
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])

    @staticmethod
    def open_startup_folder() -> None:
        if os.name != "nt":
            raise OSError("Startup folder shortcut is available on Windows only.")
        subprocess.Popen(["explorer.exe", "shell:startup"])

    @staticmethod
    def installed_apps_guidance() -> str:
        return "Windows: open Settings → Apps → Installed apps to review or uninstall software. SIFO GAME HUB does not uninstall apps."
