"""SQLite persistence layer."""
from __future__ import annotations
import sqlite3
from contextlib import closing, contextmanager
from pathlib import Path
from typing import Any

class Database:
    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    @contextmanager
    def connect(self):
        """Yield a connection that is committed AND closed (releases the file lock on Windows)."""
        with closing(sqlite3.connect(self.path, timeout=10)) as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            with conn:
                yield conn

    def initialize(self) -> None:
        with self.connect() as conn:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS games (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    executable_path TEXT NOT NULL UNIQUE,
                    cover_path TEXT NOT NULL DEFAULT '',
                    added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );
            """)

    def add_game(self, name: str, executable_path: str, cover_path: str = "") -> int:
        name = name.strip()
        if not name or not executable_path.strip():
            raise ValueError("Game name and executable path are required.")
        with self.connect() as conn:
            cur = conn.execute("INSERT INTO games(name, executable_path, cover_path) VALUES (?, ?, ?)",
                               (name, executable_path, cover_path))
            return int(cur.lastrowid)

    def update_game(self, game_id: int, name: str, executable_path: str, cover_path: str = "") -> None:
        if not name.strip() or not executable_path.strip():
            raise ValueError("Game name and executable path are required.")
        with self.connect() as conn:
            cur = conn.execute("UPDATE games SET name=?, executable_path=?, cover_path=? WHERE id=?",
                               (name.strip(), executable_path, cover_path, game_id))
            if cur.rowcount == 0:
                raise LookupError("Game was not found.")

    def remove_game(self, game_id: int) -> None:
        with self.connect() as conn:
            conn.execute("DELETE FROM games WHERE id=?", (game_id,))

    def get_game(self, game_id: int) -> dict[str, Any] | None:
        with self.connect() as conn:
            row = conn.execute("SELECT * FROM games WHERE id=?", (game_id,)).fetchone()
            return dict(row) if row else None

    def list_games(self, search: str = "") -> list[dict[str, Any]]:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        with self.connect() as conn:
            rows = conn.execute("SELECT * FROM games WHERE name LIKE ? ESCAPE '\\' ORDER BY added_at DESC, id DESC",
                                (f"%{escaped}%",)).fetchall()
            return [dict(row) for row in rows]

    def set_setting(self, key: str, value: str) -> None:
        with self.connect() as conn:
            conn.execute("INSERT INTO settings(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                         (key, value))

    def get_settings(self) -> dict[str, str]:
        with self.connect() as conn:
            return {row["key"]: row["value"] for row in conn.execute("SELECT key,value FROM settings")}
