"""API tests with the mock analyzer. Background tasks run before TestClient returns."""
from .conftest import SAMPLE_PDF, VALID, make_settings, submit


def test_health(client):
    r = client.get("/api/health").json()
    assert r["status"] == "ok" and r["ai_mode"] == "mock" and r["store"] == "file"


def test_rubric_is_public(client):
    r = client.get("/api/rubric").json()
    assert len(r["criteria"]) == 7


def test_submit_then_analyzed_and_listed(client):
    r = submit(client)
    assert r.status_code == 202
    app_id = r.json()["id"]
    d = client.get(f"/api/applications/{app_id}").json()
    assert d["status"] == "done" and d["evaluation"]["overall_score"] > 0
    assert d["ai_mode"] == "mock"
    lst = client.get("/api/applications").json()
    assert lst["total"] == 1 and lst["items"][0]["id"] == app_id


def test_submit_with_pdf_deck(client):
    r = submit(client, deck_path=SAMPLE_PDF)
    assert r.status_code == 202
    d = client.get(f"/api/applications/{r.json()['id']}").json()
    assert d["has_deck"] is True and d["status"] == "done"
    assert client.get(f"/api/applications/{r.json()['id']}/deck").headers["content-type"] == "application/pdf"


def test_rejects_non_pdf_deck(client):
    import json
    r = client.post("/api/applications", data={"payload": json.dumps(VALID)},
                    files={"deck": ("x.pdf", b"hello world", "application/pdf")})
    assert r.status_code == 422


def test_rejects_invalid_payload(client):
    bad = {**VALID, "founder_email": "nope", "problem": "short"}
    r = submit(client, bad)
    assert r.status_code == 422
    r = client.post("/api/applications", data={"payload": "{not json"})
    assert r.status_code == 422


def test_oversize_deck_rejected(tmp_path):
    from fastapi.testclient import TestClient
    from app.main import create_app
    import json
    c = TestClient(create_app(make_settings(tmp_path, max_deck_mb=1)))
    big = b"%PDF-" + b"0" * (1024 * 1024 + 10)
    r = c.post("/api/applications", data={"payload": json.dumps(VALID)}, files={"deck": ("b.pdf", big, "application/pdf")})
    assert r.status_code == 413


def test_seed_sorting_filters_and_blind_mode(client):
    assert client.post("/api/dev/seed").json()["created"] == 12
    items = client.get("/api/applications").json()["items"]
    assert len(items) == 12 and all(i["status"] == "done" for i in items)
    scores = [i["overall_score"] for i in items]
    assert scores == sorted(scores, reverse=True)
    # idempotent
    assert client.post("/api/dev/seed").json()["created"] == 0
    # filters
    high = client.get("/api/applications", params={"priority": "high"}).json()["items"]
    assert all(i["priority"] == "high" for i in high)
    assert client.get("/api/applications", params={"q": "medroute"}).json()["total"] == 1
    # blind mode hides identity in list, detail, search
    blind = client.get("/api/applications", params={"blind": "true"}).json()["items"]
    assert all(i["founder_name"].startswith("Hidden") for i in blind)
    assert client.get("/api/applications", params={"blind": "true", "q": "Demo Founder 01"}).json()["total"] == 0
    d = client.get("/api/applications/demo-01", params={"blind": "true"}).json()
    assert d["input"]["founder_email"] == "" and d["input"]["founder_name"].startswith("Hidden")


def test_demo_set_behaves_sensibly_in_mock_mode(client):
    client.post("/api/dev/seed")
    by_id = {i["id"]: i for i in client.get("/api/applications").json()["items"]}
    assert by_id["demo-01"]["overall_score"] > by_id["demo-10"]["overall_score"]
    assert by_id["demo-12"]["red_flag_count"] >= 1  # injection text caught by code
    assert by_id["demo-12"]["confidence"] == "low"


def test_decision_flow_and_reanalyze_keeps_decision(client):
    client.post("/api/dev/seed")
    r = client.put("/api/applications/demo-04/decision", json={"decision": "interview", "note": "Strong fit", "reviewer": "Mahvish"})
    assert r.status_code == 200 and r.json()["decision"]["decision"] == "interview"
    assert client.put("/api/applications/demo-04/decision", json={"decision": "maybe"}).status_code == 422
    assert client.post("/api/applications/demo-04/analyze").status_code == 202
    d = client.get("/api/applications/demo-04").json()
    assert d["status"] == "done" and d["decision"]["note"] == "Strong fit"
    assert client.get("/api/applications", params={"decision": "interview"}).json()["total"] == 1
    assert client.get("/api/applications", params={"decision": "undecided"}).json()["total"] == 11


def test_404s(client):
    assert client.get("/api/applications/nope").status_code == 404
    assert client.put("/api/applications/nope/decision", json={"decision": "hold"}).status_code == 404
    assert client.post("/api/applications/nope/analyze").status_code == 404


def test_stats(client):
    client.post("/api/dev/seed")
    s = client.get("/api/stats").json()
    assert s["total"] == 12 and sum(s["by_priority"].values()) == 12
    assert s["estimated_minutes_saved"] == 12 * (15 - 3)
    assert "assumption_note" in s


def test_csv_export(client):
    client.post("/api/dev/seed")
    txt = client.get("/api/export.csv", params={"blind": "true"}).text
    lines = txt.strip().splitlines()
    assert len(lines) == 13 and lines[0].startswith("id,startup,founder")
    assert "Demo Founder" not in txt


def test_rubric_update_bumps_version_and_is_used(client):
    r = client.get("/api/rubric").json()
    r["criteria"] = r["criteria"][:3]
    put = client.put("/api/rubric", json=r)
    assert put.status_code == 200 and put.json()["version"] == 2
    bad = {**r, "criteria": [r["criteria"][0], r["criteria"][0]]}
    assert client.put("/api/rubric", json=bad).status_code == 422
    app_id = submit(client).json()["id"]
    d = client.get(f"/api/applications/{app_id}").json()
    assert len(d["evaluation"]["criteria"]) == 3 and d["evaluation"]["rubric_version"] == 2


def test_rate_limit(tmp_path):
    from fastapi.testclient import TestClient
    from app.main import create_app
    c = TestClient(create_app(make_settings(tmp_path, rate_limit_per_hour=2)))
    assert submit(c).status_code == 202 and submit(c).status_code == 202
    assert submit(c).status_code == 429


def test_dev_routes_can_be_disabled(tmp_path):
    from fastapi.testclient import TestClient
    from app.main import create_app
    c = TestClient(create_app(make_settings(tmp_path, enable_dev_routes=False)))
    assert c.post("/api/dev/seed").status_code == 404
    assert c.post("/api/dev/reset").status_code == 404


def test_store_persists_across_restarts(tmp_path):
    from fastapi.testclient import TestClient
    from app.main import create_app
    c1 = TestClient(create_app(make_settings(tmp_path)))
    app_id = submit(c1).json()["id"]
    c2 = TestClient(create_app(make_settings(tmp_path)))
    assert c2.get(f"/api/applications/{app_id}").json()["status"] == "done"
