"""Auth modes, the Supabase store (request shapes, via a mock transport) and the Gemini wrapper (fake client)."""
import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.ai import AnalysisError
from app.ai.gemini import GeminiAnalyzer
from app.config import Settings
from app.container import build_container
from app.main import create_app
from app.models import AIEvaluation, Application, ApplicationIn
from app.rubric import load_default_rubric
from app.store.supabase import SupabaseError, SupabaseStore

from .conftest import VALID, make_settings, submit


# ---------- auth ----------
def test_key_auth(tmp_path):
    c = TestClient(create_app(Settings(ai_mode="mock", data_dir=tmp_path, auth_mode="key", reviewer_key="s3cret")))
    assert c.get("/api/applications").status_code == 401
    assert c.get("/api/applications", headers={"X-Reviewer-Key": "wrong"}).status_code == 401
    assert c.get("/api/applications", headers={"X-Reviewer-Key": "s3cret"}).status_code == 200
    # applicants never need a key
    assert submit(c).status_code == 202
    assert c.get("/api/health").status_code == 200 and c.get("/api/rubric").status_code == 200


class _FakeAuthHttp:
    def __init__(self, users):
        self.users, self.calls = users, 0

    def get(self, url, headers=None, timeout=None):
        self.calls += 1
        tok = headers["Authorization"].removeprefix("Bearer ")
        if tok in self.users:
            return httpx.Response(200, json={"email": self.users[tok]}, request=httpx.Request("GET", url))
        return httpx.Response(401, json={}, request=httpx.Request("GET", url))


def _supabase_auth_client(tmp_path, emails):
    s = Settings(ai_mode="mock", data_dir=tmp_path, auth_mode="supabase", supabase_url="https://x.supabase.co",
                 supabase_anon_key="anon", reviewer_emails=emails)
    c = build_container(s)
    c.auth_http = _FakeAuthHttp({"good": "mahvish@example.com", "stranger": "random@example.com"})
    return TestClient(create_app(s, container=c)), c


def test_supabase_auth_allowlist(tmp_path):
    client, c = _supabase_auth_client(tmp_path, ("mahvish@example.com",))
    assert client.get("/api/applications").status_code == 401
    assert client.get("/api/applications", headers={"Authorization": "Bearer bad"}).status_code == 401
    assert client.get("/api/applications", headers={"Authorization": "Bearer stranger"}).status_code == 403
    assert client.get("/api/applications", headers={"Authorization": "Bearer good"}).status_code == 200


def test_supabase_auth_denies_everyone_without_allowlist(tmp_path):
    client, _ = _supabase_auth_client(tmp_path, ())
    assert client.get("/api/applications", headers={"Authorization": "Bearer good"}).status_code == 403


# ---------- supabase store ----------
def test_supabase_store_requires_credentials(tmp_path):
    with pytest.raises(SupabaseError):
        SupabaseStore("", "", tmp_path)


def _store(tmp_path, handler):
    http = httpx.Client(base_url="https://x.supabase.co/rest/v1", transport=httpx.MockTransport(handler))
    return SupabaseStore("https://x.supabase.co", "svc", tmp_path, client=http)


def test_supabase_store_request_shapes(tmp_path):
    seen = []

    def handler(req: httpx.Request):
        seen.append(req)
        if req.method == "GET" and req.url.params.get("id") == "eq.a1":
            return httpx.Response(200, json=[{"data": Application(
                id="a1", created_at="2026-11-21T10:00:00+00:00", input=ApplicationIn(**VALID)).model_dump()}])
        if req.method == "GET" and req.url.path.endswith("/settings"):
            return httpx.Response(200, json=[])
        if req.method == "GET":
            return httpx.Response(200, json=[])
        return httpx.Response(201)

    st = _store(tmp_path, handler)
    app = Application(id="a1", created_at="2026-11-21T10:00:00+00:00", input=ApplicationIn(**VALID))
    st.save_application(app)
    post = seen[-1]
    assert post.method == "POST" and post.url.params["on_conflict"] == "id"
    assert "merge-duplicates" in post.headers["prefer"]
    body = json.loads(post.content)
    assert body["id"] == "a1" and body["data"]["input"]["startup_name"] == "Sample Co"
    assert st.get_application("a1").input.startup_name == "Sample Co"
    assert st.get_rubric() is None
    st.save_rubric(load_default_rubric())
    assert json.loads(seen[-1].content)["key"] == "rubric"
    st.delete_all()
    assert seen[-1].method == "DELETE" and seen[-1].url.params["id"] == "not.is.null"


def test_supabase_store_raises_readable_errors(tmp_path):
    st = _store(tmp_path, lambda req: httpx.Response(401, text="Invalid API key"))
    with pytest.raises(SupabaseError, match="401"):
        st.list_applications()


# ---------- gemini wrapper ----------
class _Resp:
    def __init__(self, text=None, parsed=None):
        self.text, self.parsed = text, parsed

        class U:
            prompt_token_count, candidates_token_count = 1200, 340
        self.usage_metadata = U()


def _good_json():
    from app.ai.mock import MockAnalyzer
    return MockAnalyzer().analyze(ApplicationIn(**VALID), load_default_rubric()).model_dump_json()


class _FakeClient:
    def __init__(self, behaviours):
        self.behaviours, self.calls = list(behaviours), 0
        outer = self

        class Models:
            def generate_content(self, model, contents, config):
                outer.calls += 1
                b = outer.behaviours.pop(0)
                if isinstance(b, Exception):
                    raise b
                return b
        self.models = Models()


def test_gemini_parses_text_and_records_usage():
    g = GeminiAnalyzer("k", "m", client=_FakeClient([_Resp(text=_good_json())]), sleep=lambda s: None)
    ev = g.analyze(ApplicationIn(**VALID), load_default_rubric(), None)
    assert isinstance(ev, AIEvaluation) and g.last_usage == (1200, 340)


def test_gemini_sends_pdf_part_and_prompt():
    captured = {}

    class C(_FakeClient):
        pass
    client = C([_Resp(text=_good_json())])
    orig = client.models.generate_content

    def spy(model, contents, config):
        captured["parts"] = contents[0].parts
        captured["cfg"] = config
        return orig(model, contents, config)
    client.models.generate_content = spy
    g = GeminiAnalyzer("k", "m", client=client, sleep=lambda s: None)
    g.analyze(ApplicationIn(**VALID), load_default_rubric(), b"%PDF-1.4 fake")
    assert len(captured["parts"]) == 2
    assert captured["parts"][0].inline_data.mime_type == "application/pdf"
    assert "<application>" in captured["parts"][1].text
    assert "founder_name" not in captured["parts"][1].text and "Test Founder" not in captured["parts"][1].text
    assert captured["cfg"].response_mime_type == "application/json"


def test_gemini_retries_then_succeeds_and_then_gives_up():
    g = GeminiAnalyzer("k", "m", client=_FakeClient([RuntimeError("503"), _Resp(text=_good_json())]), sleep=lambda s: None)
    assert g.analyze(ApplicationIn(**VALID), load_default_rubric(), None)
    g2 = GeminiAnalyzer("k", "m", client=_FakeClient([RuntimeError("a"), RuntimeError("b"), RuntimeError("c")]), sleep=lambda s: None)
    with pytest.raises(AnalysisError):
        g2.analyze(ApplicationIn(**VALID), load_default_rubric(), None)
    g3 = GeminiAnalyzer("k", "m", client=_FakeClient([_Resp(text="")] * 3), sleep=lambda s: None)
    with pytest.raises(AnalysisError, match="empty"):
        g3.analyze(ApplicationIn(**VALID), load_default_rubric(), None)


def test_failed_analysis_is_recorded_not_crashed(tmp_path):
    class Boom:
        name, model, last_usage = "gemini", "m", (None, None)

        def analyze(self, *a, **k):
            raise AnalysisError("quota exceeded")
    s = make_settings(tmp_path)
    c = build_container(s, analyzer=Boom())
    client = TestClient(create_app(s, container=c))
    app_id = submit(client).json()["id"]
    d = client.get(f"/api/applications/{app_id}").json()
    assert d["status"] == "failed" and "quota exceeded" in d["error"]


def test_gemini_schema_is_accepted_by_the_sdk():
    """The Pydantic schema must convert to a Gemini response schema without errors."""
    from google import genai
    from google.genai import _transformers

    client = genai.Client(api_key="fake-key-for-schema-test")
    schema = _transformers.t_schema(client._api_client, AIEvaluation)
    assert schema is not None


def test_supabase_store_decks_use_storage_and_survive_a_wiped_disk(tmp_path):
    storage, seen = {}, []

    def handler(req: httpx.Request):
        seen.append(req)
        if req.url.path.startswith("/storage/v1/object/decks/"):
            if req.method == "POST":
                storage[req.url.path] = req.content
                return httpx.Response(200, json={"Key": "decks/a1.pdf"})
            if req.url.path in storage:
                return httpx.Response(200, content=storage[req.url.path])
            return httpx.Response(400, json={"statusCode": "404", "error": "not_found"})
        return httpx.Response(200, json=[])

    st = _store(tmp_path / "disk1", handler)
    pdf = b"%PDF-1.4 hello"
    st.save_deck("a1", pdf)
    up = [r for r in seen if r.method == "POST"][0]
    assert up.url.path == "/storage/v1/object/decks/a1.pdf" and up.headers["x-upsert"] == "true"
    assert up.headers["content-type"] == "application/pdf"
    # a brand-new instance with an empty disk (what Render does after a restart) still finds the deck
    st2 = _store(tmp_path / "disk2", handler)
    assert st2.get_deck("a1") == pdf
    assert st2.get_deck("missing") is None


def test_supabase_deck_upload_failure_does_not_lose_the_local_copy(tmp_path):
    st = _store(tmp_path, lambda req: httpx.Response(500, text="boom"))
    st.save_deck("a2", b"%PDF-1.4 x")
    assert st.get_deck("a2") == b"%PDF-1.4 x"
