import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

BACKEND_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_ROOT / ".env")


def _flag(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class Settings:
    gemini_api_key: str = ""
    gemini_model: str = "gemini-flash-latest"
    ai_mode: str = "auto"  # auto | mock | gemini
    store_backend: str = "file"  # file | supabase
    data_dir: Path = BACKEND_ROOT / "data" / "runtime"
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_anon_key: str = ""
    auth_mode: str = "none"  # none | key | supabase
    reviewer_key: str = ""
    reviewer_emails: tuple = ()
    cors_origins: tuple = ("*",)
    max_deck_mb: int = 10
    rate_limit_per_hour: int = 30
    enable_dev_routes: bool = True
    assumed_manual_minutes: int = 15
    assumed_card_minutes: int = 3
    frontend_dir: Path | None = None  # served at / when set and the folder exists

    @property
    def effective_ai_mode(self) -> str:
        if self.ai_mode == "mock":
            return "mock"
        if self.ai_mode == "gemini":
            return "gemini"
        return "gemini" if self.gemini_api_key else "mock"


def get_settings() -> Settings:
    data_dir = Path(os.getenv("DATA_DIR", str(BACKEND_ROOT / "data" / "runtime")))
    if not data_dir.is_absolute():
        data_dir = BACKEND_ROOT / data_dir
    return Settings(
        gemini_api_key=os.getenv("GEMINI_API_KEY", "").strip(),
        gemini_model=os.getenv("GEMINI_MODEL", "gemini-flash-latest").strip(),
        ai_mode=os.getenv("AI_MODE", "auto").strip().lower(),
        store_backend=os.getenv("STORE_BACKEND", "file").strip().lower(),
        data_dir=data_dir,
        supabase_url=os.getenv("SUPABASE_URL", "").strip().rstrip("/"),
        supabase_service_key=os.getenv("SUPABASE_SERVICE_KEY", "").strip(),
        supabase_anon_key=os.getenv("SUPABASE_ANON_KEY", "").strip(),
        auth_mode=os.getenv("AUTH_MODE", "none").strip().lower(),
        reviewer_key=os.getenv("REVIEWER_KEY", "").strip(),
        reviewer_emails=tuple(
            e.strip().lower() for e in os.getenv("REVIEWER_EMAILS", "").split(",") if e.strip()
        ),
        cors_origins=tuple(o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()),
        max_deck_mb=int(os.getenv("MAX_DECK_MB", "10")),
        rate_limit_per_hour=int(os.getenv("RATE_LIMIT_PER_HOUR", "30")),
        enable_dev_routes=_flag("ENABLE_DEV_ROUTES", True),
        assumed_manual_minutes=int(os.getenv("ASSUMED_MANUAL_MINUTES", "15")),
        assumed_card_minutes=int(os.getenv("ASSUMED_CARD_MINUTES", "3")),
        frontend_dir=Path(os.getenv("FRONTEND_DIR", str(BACKEND_ROOT.parent / "frontend"))),
    )
