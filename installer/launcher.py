from __future__ import annotations

import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

APP_NAME = "Sentrix"
HOST = "127.0.0.1"
DEFAULT_PORT = 5000
STARTUP_TIMEOUT_SECONDS = 60


def _bundle_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(getattr(sys, "_MEIPASS", Path(sys.executable).parent))
    return Path(__file__).resolve().parents[1]


def _runtime_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parents[1]


def _user_data_dir() -> Path:
    local_app_data = os.getenv("LOCALAPPDATA")
    base = Path(local_app_data) if local_app_data else Path.home() / "AppData" / "Local"
    target = base / APP_NAME
    target.mkdir(parents=True, exist_ok=True)
    (target / "logs").mkdir(exist_ok=True)
    (target / "data").mkdir(exist_ok=True)
    return target


def _pick_port(preferred: int = DEFAULT_PORT) -> int:
    for port in range(preferred, preferred + 20):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((HOST, port))
                return port
            except OSError:
                continue
    raise RuntimeError("No free local port found for Sentrix.")


def _wait_until_ready(url: str) -> bool:
    deadline = time.time() + STARTUP_TIMEOUT_SECONDS
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status < 500:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def _open_browser_when_ready(url: str) -> None:
    if _wait_until_ready(url):
        webbrowser.open(url, new=2)


def _set_runtime_environment(port: int) -> Path:
    bundle = _bundle_root()
    user_data = _user_data_dir()

    os.environ.setdefault("HOST", HOST)
    os.environ["PORT"] = str(port)
    os.environ.setdefault("FLASK_DEBUG", "0")
    os.environ.setdefault("DATABASE_AUTO_CREATE", "1")
    os.environ.setdefault("SENTRIX_DESKTOP", "1")
    os.environ.setdefault("SENTRIX_DATA_DIR", str(user_data / "data"))
    os.environ.setdefault("SENTRIX_LOG_DIR", str(user_data / "logs"))

    os.chdir(bundle)
    return user_data


def _run_embedded_app(port: int) -> int:
    _set_runtime_environment(port)
    url = f"http://{HOST}:{port}/"
    threading.Thread(target=_open_browser_when_ready, args=(url,), daemon=True).start()

    try:
        from app import app

        app.run(host=HOST, port=port, debug=False, use_reloader=False, threaded=True)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        user_data = _user_data_dir()
        log_path = user_data / "logs" / "launcher-error.log"
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} {type(exc).__name__}: {exc}\n")
        raise


def main() -> int:
    port = _pick_port(int(os.getenv("PORT", DEFAULT_PORT)))
    return _run_embedded_app(port)


if __name__ == "__main__":
    raise SystemExit(main())
