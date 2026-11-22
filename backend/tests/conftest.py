import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import Settings  # noqa: E402
from app.main import create_app  # noqa: E402

SAMPLE_PDF = Path(__file__).resolve().parent.parent / "data" / "sample_deck.pdf"

VALID = {
    "startup_name": "Sample Co",
    "one_liner": "SMS reminders that cut clinic no-shows.",
    "sector": "Healthtech",
    "stage": "mvp",
    "problem": "Small clinics lose 30 percent of appointments to no-shows and receptionists call patients by hand.",
    "solution": "An SMS reminder tool that lets patients confirm or reschedule with one reply.",
    "target_customers": "Independent clinics in Peshawar with one to three doctors.",
    "traction": "Three clinics piloted for 8 weeks and no-shows fell from 30 percent to 18 percent.",
    "business_model": "Clinics pay PKR 3,000 per month per doctor.",
    "team_background": "A developer and a former clinic manager.",
    "ask": "Mentorship on selling to clinics.",
    "founder_name": "Test Founder",
    "founder_email": "test@example.com",
    "organization": "Test Org",
}


def make_settings(tmp_path, **kw) -> Settings:
    return Settings(ai_mode="mock", data_dir=tmp_path, auth_mode="none", **kw)


@pytest.fixture
def settings(tmp_path):
    return make_settings(tmp_path)


@pytest.fixture
def client(settings):
    return TestClient(create_app(settings))


@pytest.fixture
def valid_payload():
    return dict(VALID)


def submit(client, payload=None, deck_path=None, headers=None):
    data = {"payload": json.dumps(payload or VALID)}
    files = {"deck": ("deck.pdf", deck_path.read_bytes(), "application/pdf")} if deck_path else None
    return client.post("/api/applications", data=data, files=files, headers=headers or {})
