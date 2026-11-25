# SIFO GAME HUB

A lightweight, offline-first Windows desktop game library and PC monitor built with Python, CustomTkinter and SQLite.

## Features

- Dashboard with real library count, recent additions and live system summary.
- Game library: add Windows executables, search, launch, edit and remove entries. Removing an entry never deletes game files.
- PC monitor: CPU and memory usage, RAM totals/availability, disk usage, CPU label and OS details. FPS is not measured.
- Game tools: open the temporary folder, read installed-app guidance and open the Windows Startup folder. No silent cleanup/deletion.
- Settings: dark/light/system appearance and local database location display.
- SQLite persistence, parameterized SQL, local log file and automated tests.

## Requirements

- Windows 10/11 64-bit
- Python 3.11 or newer (Python 3.11 is recommended for the supplied build script)
- 4 GB RAM minimum; 8 GB recommended

## Install and run from source

1. Install Python 3.11+ from https://www.python.org/ and enable **Add Python to PATH**.
2. Open Command Prompt in the project directory.
3. Create and activate a virtual environment:

   ```bat
   py -3.11 -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```bat
   python -m sifo_game_hub
   ```

The database and log are stored under `%APPDATA%\SIFOGameHub\`.

## Build the Windows executable

Double-click `build_windows.bat` or run it from Command Prompt. It installs pinned dependencies and invokes PyInstaller. The output is a windowed, onedir build at `dist\SIFO GAME HUB\SIFO GAME HUB.exe`. The first launch may take a moment while Windows initializes the packaged application. Build on Windows; a Linux build is not a Windows executable.

## Tests

Install `pytest` and run:

```bat
python -m pytest -q
```

## Notes and limitations

- Game launching is designed for Windows executables. The launcher refuses unsupported executable formats and never uses `shell=True`.
- Installed-app management intentionally links users to Windows Settings guidance instead of modifying installed software.
- Temporary-folder access only opens the folder; it does not remove files.
- System metric availability depends on OS permissions and `psutil` support.
- The app does not measure FPS.
- Optional cover images can be selected when adding or editing a game and are displayed in the library when the image remains accessible.
