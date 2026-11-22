"""Wires settings, store and analyzer together, and holds the background job that analyzes one application."""
import time
from dataclasses import dataclass, field

from .ai import Analyzer
from .ai.gemini import GeminiAnalyzer
from .ai.mock import MockAnalyzer
from .config import Settings
from .models import Application
from .pipeline import run_analysis
from .rubric import Rubric, load_default_rubric
from .store import Store
from .store.file import FileStore
from .store.supabase import SupabaseStore


@dataclass
class Container:
    settings: Settings
    store: Store
    analyzer: Analyzer
    auth_http: object | None = None  # injectable for tests
    submissions: dict = field(default_factory=dict)  # ip -> [timestamps]

    def get_rubric(self) -> Rubric:
        return self.store.get_rubric() or load_default_rubric()


def build_container(settings: Settings, store: Store | None = None, analyzer: Analyzer | None = None) -> Container:
    if store is None:
        if settings.store_backend == "supabase":
            store = SupabaseStore(settings.supabase_url, settings.supabase_service_key, settings.data_dir)
        else:
            store = FileStore(settings.data_dir)
    if analyzer is None:
        if settings.effective_ai_mode == "gemini":
            if not settings.gemini_api_key:
                raise RuntimeError("AI_MODE=gemini but GEMINI_API_KEY is empty")
            analyzer = GeminiAnalyzer(settings.gemini_api_key, settings.gemini_model)
        else:
            analyzer = MockAnalyzer()
    return Container(settings=settings, store=store, analyzer=analyzer)


def now_iso() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def process_application(c: Container, app_id: str) -> None:
    """Background job: analyze one application and save the result. Never raises."""
    app = c.store.get_application(app_id)
    if app is None:
        return
    app.status, app.error = "analyzing", None
    c.store.save_application(app)
    t0 = time.time()
    try:
        pdf = c.store.get_deck(app_id) if app.has_deck else None
        ev = run_analysis(app.input, c.get_rubric(), c.analyzer, pdf)
        app.evaluation, app.status = ev, "done"
    except Exception as e:
        app.status, app.error = "failed", f"{type(e).__name__}: {e}"[:400]
    app.analysis_seconds = round(time.time() - t0, 2)
    app.ai_mode, app.model = c.analyzer.name, c.analyzer.model
    c.store.save_application(app)


def process_many(c: Container, ids: list[str]) -> None:
    for i in ids:  # sequential on purpose: friendly to API rate limits
        process_application(c, i)
