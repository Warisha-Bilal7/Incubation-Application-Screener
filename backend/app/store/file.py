"""Zero-setup store: everything in memory, persisted to one JSON file. Decks live on local disk."""
import json
import os
import re
import threading
from pathlib import Path

from ..models import Application
from ..rubric import Rubric

_SAFE_ID = re.compile(r"[^A-Za-z0-9_-]")


class FileStore:
    name = "file"

    def __init__(self, data_dir: Path):
        self.dir = Path(data_dir)
        (self.dir / "uploads").mkdir(parents=True, exist_ok=True)
        self.path = self.dir / "store.json"
        self._lock = threading.RLock()
        self._apps: dict[str, Application] = {}
        self._rubric: Rubric | None = None
        if self.path.exists():
            try:
                raw = json.loads(self.path.read_text(encoding="utf-8"))
                for a in raw.get("applications", []):
                    app = Application.model_validate(a)
                    self._apps[app.id] = app
                if raw.get("rubric"):
                    self._rubric = Rubric.model_validate(raw["rubric"])
            except Exception:
                pass  # corrupt file: start clean rather than crash the demo

    def _flush(self) -> None:
        payload = {
            "applications": [a.model_dump() for a in self._apps.values()],
            "rubric": self._rubric.model_dump() if self._rubric else None,
        }
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        os.replace(tmp, self.path)

    def list_applications(self) -> list[Application]:
        with self._lock:
            return [a.model_copy(deep=True) for a in self._apps.values()]

    def get_application(self, app_id: str) -> Application | None:
        with self._lock:
            a = self._apps.get(app_id)
            return a.model_copy(deep=True) if a else None

    def save_application(self, app: Application) -> None:
        with self._lock:
            self._apps[app.id] = app.model_copy(deep=True)
            self._flush()

    def delete_all(self) -> None:
        with self._lock:
            self._apps.clear()
            self._flush()

    def get_rubric(self) -> Rubric | None:
        with self._lock:
            return self._rubric.model_copy(deep=True) if self._rubric else None

    def save_rubric(self, rubric: Rubric) -> None:
        with self._lock:
            self._rubric = rubric.model_copy(deep=True)
            self._flush()

    def _deck_path(self, app_id: str) -> Path:
        return self.dir / "uploads" / f"{_SAFE_ID.sub('', app_id)}.pdf"

    def save_deck(self, app_id: str, data: bytes) -> None:
        self._deck_path(app_id).write_bytes(data)

    def get_deck(self, app_id: str) -> bytes | None:
        p = self._deck_path(app_id)
        return p.read_bytes() if p.exists() else None
