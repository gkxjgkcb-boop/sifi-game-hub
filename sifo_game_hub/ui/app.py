"""CustomTkinter user interface."""
from __future__ import annotations
import logging
import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from pathlib import Path
import customtkinter as ctk
from PIL import Image
from ..config import APP_NAME, APP_VERSION, DB_PATH, DEFAULT_SETTINGS
from ..database import Database
from ..services import GameLauncher, GameTools, SystemMonitor

BG = "#0B0B10"; PANEL = "#15151F"; PANEL2 = "#1C1B29"; PURPLE = "#9B5CFF"; MUTED = "#A5A2B3"

class HubApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_NAME}  •  v{APP_VERSION}")
        self.geometry("1120x720"); self.minsize(900, 600)
        self.configure(fg_color=BG)
        self.db = Database(DB_PATH)
        settings = DEFAULT_SETTINGS | self.db.get_settings()
        ctk.set_appearance_mode(settings.get("theme", "dark"))
        ctk.set_default_color_theme("dark-blue")
        self.selected_game: int | None = None
        try:
            self.refresh_ms = max(1, int(settings.get("refresh_seconds", "3"))) * 1000
        except ValueError:
            self.refresh_ms = 3000
        SystemMonitor.snapshot()  # primes psutil.cpu_percent so the first displayed value is real
        self.sidebar = ctk.CTkFrame(self, width=215, corner_radius=0, fg_color="#101018")
        self.sidebar.pack(side="left", fill="y"); self.sidebar.pack_propagate(False)
        self.content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        self.content.pack(side="right", fill="both", expand=True)
        self._build_sidebar(); self.show_dashboard()

    def _build_sidebar(self):
        ctk.CTkLabel(self.sidebar, text="SIFO  /  GAME HUB", font=ctk.CTkFont(size=19, weight="bold"), text_color="white").pack(padx=18, pady=(28, 4), anchor="w")
        ctk.CTkLabel(self.sidebar, text="YOUR GAMING SPACE", text_color=PURPLE, font=ctk.CTkFont(size=10, weight="bold")).pack(padx=20, pady=(0, 28), anchor="w")
        for label, callback in [("⌂   Dashboard", self.show_dashboard), ("▣   Game Library", self.show_library),
                                ("◉   PC Monitor", self.show_monitor), ("⚙   Game Tools", self.show_tools),
                                ("☷   Settings", self.show_settings), ("ⓘ   About", self.show_about)]:
            ctk.CTkButton(self.sidebar, text=label, anchor="w", height=43, fg_color="transparent", hover_color=PANEL2,
                          text_color="#E8E5F0", command=callback).pack(fill="x", padx=12, pady=3)
        ctk.CTkLabel(self.sidebar, text=f"VERSION {APP_VERSION}\nMADE BY SIFO", text_color="#686575", justify="left").pack(side="bottom", padx=20, pady=22, anchor="w")

    def _clear(self):
        pending = getattr(self, "monitor_after_id", None)
        if pending is not None:
            try: self.after_cancel(pending)
            except tk.TclError: pass
            self.monitor_after_id = None
        self.monitor_values = {}
        for widget in self.content.winfo_children(): widget.destroy()

    def _header(self, title: str, subtitle: str):
        ctk.CTkLabel(self.content, text=title, font=ctk.CTkFont(size=29, weight="bold"), text_color="white").pack(anchor="w", padx=30, pady=(27, 2))
        ctk.CTkLabel(self.content, text=subtitle, text_color=MUTED).pack(anchor="w", padx=31, pady=(0, 20))

    def _panel(self, parent=None):
        return ctk.CTkFrame(parent or self.content, fg_color=PANEL, corner_radius=14, border_width=1, border_color="#282638")

    def show_dashboard(self):
        self._clear(); self._header("Welcome back, Player.", "Your games. Your system. One place.")
        hero = ctk.CTkFrame(self.content, fg_color="#211633", corner_radius=16, height=155)
        hero.pack(fill="x", padx=30, pady=(0, 18)); hero.pack_propagate(False)
        ctk.CTkLabel(hero, text="READY WHEN YOU ARE", text_color="#C7A6FF", font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=24, pady=(22, 4))
        ctk.CTkLabel(hero, text="Your next adventure starts here.", text_color="white", font=ctk.CTkFont(size=23, weight="bold")).pack(anchor="w", padx=24)
        ctk.CTkButton(hero, text="＋  Add a game", fg_color=PURPLE, hover_color="#8043D8", command=self.add_game_dialog).pack(anchor="w", padx=24, pady=12)
        games = self.db.list_games(); monitor = SystemMonitor.snapshot()
        row = ctk.CTkFrame(self.content, fg_color="transparent"); row.pack(fill="x", padx=25)
        for title, value in [("GAMES IN LIBRARY", str(len(games))), ("CPU LOAD", self._pct(monitor.get("cpu_percent"))), ("MEMORY LOAD", self._pct(monitor.get("ram_percent")))]:
            card = self._panel(row); card.pack(side="left", fill="x", expand=True, padx=5, pady=4)
            ctk.CTkLabel(card, text=title, text_color=MUTED, font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=16, pady=(15, 4))
            ctk.CTkLabel(card, text=value, text_color="white", font=ctk.CTkFont(size=25, weight="bold")).pack(anchor="w", padx=16, pady=(0, 15))
        ctk.CTkLabel(self.content, text="RECENTLY ADDED", text_color=MUTED, font=ctk.CTkFont(size=11, weight="bold")).pack(anchor="w", padx=31, pady=(22, 8))
        recent = games[:4]
        if not recent: ctk.CTkLabel(self.content, text="No games yet. Add your first game to build your library.", text_color=MUTED).pack(anchor="w", padx=31)
        for game in recent:
            ctk.CTkLabel(self.content, text=f"▸  {game['name']}", text_color="#E8E5F0").pack(anchor="w", padx=34, pady=3)

    @staticmethod
    def _pct(value): return f"{value:.0f}%" if isinstance(value, (int, float)) else "Unavailable"

    def show_library(self):
        self._clear(); self._header("Game Library", "Manage and launch your installed games.")
        bar = ctk.CTkFrame(self.content, fg_color="transparent"); bar.pack(fill="x", padx=30, pady=(0, 12))
        search = ctk.CTkEntry(bar, placeholder_text="Search your games…", width=300); search.pack(side="left")
        ctk.CTkButton(bar, text="＋ Add game", fg_color=PURPLE, command=self.add_game_dialog).pack(side="right")
        listing = ctk.CTkScrollableFrame(self.content, fg_color="transparent"); listing.pack(fill="both", expand=True, padx=25, pady=4)
        def render(*_):
            for child in listing.winfo_children(): child.destroy()
            games = self.db.list_games(search.get())
            if not games: ctk.CTkLabel(listing, text="No matching games. Add a game using its .exe file.", text_color=MUTED).pack(pady=35); return
            for game in games:
                card = self._panel(listing); card.pack(fill="x", pady=6, padx=3)
                if game.get("cover_path") and Path(game["cover_path"]).is_file():
                    try:
                        cover = ctk.CTkImage(light_image=Image.open(game["cover_path"]), size=(54, 54))
                        cover_label = ctk.CTkLabel(card, text="", image=cover)
                        cover_label.image = cover
                        cover_label.pack(side="left", padx=(12, 0), pady=8)
                    except (OSError, ValueError):
                        logging.exception("Could not load cover image: %s", game["cover_path"])
                ctk.CTkLabel(card, text=game["name"], font=ctk.CTkFont(size=16, weight="bold"), text_color="white").pack(side="left", padx=17, pady=17)
                ctk.CTkButton(card, text="PLAY", width=75, fg_color=PURPLE, command=lambda g=game: self.launch_game(g)).pack(side="right", padx=6, pady=10)
                ctk.CTkButton(card, text="Edit", width=65, fg_color=PANEL2, command=lambda g=game: self.edit_game_dialog(g)).pack(side="right", padx=4)
                ctk.CTkButton(card, text="Remove", width=75, fg_color="#552B39", hover_color="#713448", command=lambda g=game: self.remove_game(g)).pack(side="right", padx=4)
        search.bind("<KeyRelease>", render); render()

    def add_game_dialog(self):
        path = filedialog.askopenfilename(title="Choose game executable", filetypes=[("Windows executable", "*.exe"), ("All files", "*.*")])
        if not path: return
        name = simpledialog.askstring("Add game", "Game name:", initialvalue=Path(path).stem, parent=self)
        if not name: return
        cover = filedialog.askopenfilename(title="Choose an optional cover image (Cancel to skip)", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")])
        try: self.db.add_game(name, path, cover); self.show_library()
        except Exception as exc: logging.exception("Could not add game"); messagebox.showerror("Add game failed", str(exc))

    def edit_game_dialog(self, game):
        name = simpledialog.askstring("Edit game", "Game name:", initialvalue=game["name"], parent=self)
        if not name: return
        path = filedialog.askopenfilename(title="Choose executable", initialdir=str(Path(game["executable_path"]).parent), filetypes=[("Windows executable", "*.exe"), ("All files", "*.*")])
        if not path: return
        cover = filedialog.askopenfilename(title="Choose an optional cover image (Cancel to keep current)", filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")]) or game.get("cover_path", "")
        try: self.db.update_game(game["id"], name, path, cover); self.show_library()
        except Exception as exc: logging.exception("Could not update game"); messagebox.showerror("Edit failed", str(exc))

    def remove_game(self, game):
        if messagebox.askyesno("Remove game", f"Remove {game['name']} from your library?\n\nThe game files will NOT be deleted."):
            self.db.remove_game(game["id"]); self.show_library()

    def launch_game(self, game):
        try: GameLauncher.launch(game["executable_path"]); messagebox.showinfo("Game launched", f"Started {game['name']}.")
        except Exception as exc: logging.exception("Game launch failed"); messagebox.showerror("Could not launch game", str(exc))

    def show_monitor(self):
        self._clear(); self._header("PC Monitor", "Live system overview. FPS measurement is not implemented.")
        self.monitor_values = {}
        for key, label in [("cpu_percent", "CPU usage"), ("ram_percent", "RAM usage"), ("ram_total", "Total RAM"), ("ram_available", "Available RAM"), ("disk_percent", "Disk usage"), ("disk_free", "Free disk space"), ("cpu_name", "CPU"), ("windows_version", "Operating system")]:
            card = self._panel(self.content); card.pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(card, text=label, text_color=MUTED).pack(side="left", padx=16, pady=12)
            value = ctk.CTkLabel(card, text="…", text_color="white", font=ctk.CTkFont(weight="bold")); value.pack(side="right", padx=16)
            self.monitor_values[key] = value
        self._refresh_monitor()

    def _refresh_monitor(self):
        if not hasattr(self, "monitor_values") or not self.winfo_exists(): return
        data = SystemMonitor.snapshot()
        for key, widget in self.monitor_values.items():
            value = data.get(key)
            if key.endswith("_percent"): text = self._pct(value)
            elif key in {"ram_total", "ram_available", "disk_free"}: text = f"{value / (1024**3):.1f} GB" if isinstance(value, int) else "Unavailable"
            else: text = str(value or "Unavailable")
            widget.configure(text=text)
        self.monitor_after_id = self.after(self.refresh_ms, self._refresh_monitor)

    def show_tools(self):
        self._clear(); self._header("Game Tools", "Useful Windows shortcuts. Nothing is deleted automatically.")
        self._tool_button("Open temporary folder", "Opens your operating system temporary directory.", GameTools.open_temp_folder)
        self._tool_button("Installed applications", GameTools.installed_apps_guidance(), lambda: messagebox.showinfo("Installed apps", GameTools.installed_apps_guidance()))
        self._tool_button("Startup folder", "Open the Windows Startup folder to review shortcuts that launch at sign-in.", self._startup)
        note = self._panel(); note.pack(fill="x", padx=30, pady=12)
        ctk.CTkLabel(note, text="Safety note", text_color=PURPLE, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=16, pady=(12, 3))
        ctk.CTkLabel(note, text="This hub does not clean or delete temporary files. Review files yourself in Windows before removing anything.", text_color=MUTED, wraplength=700).pack(anchor="w", padx=16, pady=(0, 12))

    def _tool_button(self, title, description, command):
        card = self._panel(); card.pack(fill="x", padx=30, pady=7)
        ctk.CTkLabel(card, text=title, text_color="white", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=16, pady=(12, 2))
        ctk.CTkLabel(card, text=description, text_color=MUTED, wraplength=700).pack(anchor="w", padx=16, pady=(0, 8))
        ctk.CTkButton(card, text="Open", width=90, fg_color=PURPLE, command=lambda: self._safe_tool(command)).pack(anchor="e", padx=14, pady=(0, 12))

    def _safe_tool(self, command):
        try: command()
        except Exception as exc: logging.exception("Tool failed"); messagebox.showerror("Tool unavailable", str(exc))
    def _startup(self): self._safe_tool(GameTools.open_startup_folder)

    def show_settings(self):
        self._clear(); self._header("Settings", "Preferences are saved locally on this PC.")
        current = DEFAULT_SETTINGS | self.db.get_settings()
        card = self._panel(); card.pack(fill="x", padx=30, pady=7)
        ctk.CTkLabel(card, text="Appearance", text_color="white", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", padx=16, pady=(14, 5))
        theme = ctk.CTkOptionMenu(card, values=["dark", "light", "system"], command=self._save_theme); theme.set(current["theme"]); theme.pack(anchor="w", padx=16, pady=(0, 14))
        info = self._panel(); info.pack(fill="x", padx=30, pady=7)
        for label, value in [("Application version", APP_VERSION), ("Database location", str(DB_PATH))]:
            ctk.CTkLabel(info, text=f"{label}:\n{value}", text_color=MUTED, justify="left", wraplength=750).pack(anchor="w", padx=16, pady=9)

    def _save_theme(self, value):
        self.db.set_setting("theme", value); ctk.set_appearance_mode(value)

    def show_about(self):
        self._clear(); self._header("About SIFO GAME HUB", "A lightweight home for your PC games.")
        card = self._panel(); card.pack(fill="x", padx=30, pady=10)
        ctk.CTkLabel(card, text="SIFO GAME HUB", font=ctk.CTkFont(size=26, weight="bold"), text_color="white").pack(anchor="w", padx=20, pady=(20, 6))
        ctk.CTkLabel(card, text=f"Version {APP_VERSION}\nDeveloper: SIFO\nSupport: support information coming soon.\nCore features work offline; no account or paid API required.", text_color=MUTED, justify="left").pack(anchor="w", padx=20, pady=(0, 20))
