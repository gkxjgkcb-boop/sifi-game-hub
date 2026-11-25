from __future__ import annotations
import logging
from .config import APP_DIR, LOG_PATH

def main() -> None:
    APP_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        from .ui.app import HubApp
        app = HubApp()
        app.mainloop()
    except ModuleNotFoundError as exc:
        logging.exception("A required application dependency is missing")
        if exc.name == "customtkinter":
            raise SystemExit("CustomTkinter is not installed. Run: python -m pip install -r requirements.txt") from exc
        raise
    except Exception:
        logging.exception("Application startup failed")
        raise

if __name__ == "__main__": main()
