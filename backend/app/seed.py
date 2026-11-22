import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .models import Application, ApplicationIn

DEMO_PATH = Path(__file__).resolve().parent.parent / "data" / "demo_applicants.json"
_META = {"id", "tier"}


def load_demo_applications() -> list[Application]:
    rows = json.loads(DEMO_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc)
    apps = []
    for i, row in enumerate(rows):
        fields = {k: v for k, v in row.items() if k not in _META}
        apps.append(Application(
            id=row["id"],
            created_at=(now - timedelta(minutes=5 * (len(rows) - i))).isoformat(timespec="seconds"),
            input=ApplicationIn(**fields),
        ))
    return apps
