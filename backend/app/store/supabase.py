"""Supabase store over the PostgREST API (plain httpx, no extra SDK).

Tables: see ../../data/schema.sql. Each application is one row; the full object lives in `data` (jsonb)
and a few columns are copied out for filtering. Use the SERVICE key here, on the server only.
Decks go to a private Supabase Storage bucket named "decks" (created by schema.sql) and are also kept on local
disk as a fallback. Render's free disk is wiped on every sleep or redeploy, so Storage is the copy that survives.
"""
from pathlib import Path

import httpx

from ..models import Application
from ..rubric import Rubric
from .file import FileStore


class SupabaseError(RuntimeError):
    pass


class SupabaseStore:
    name = "supabase"

    def __init__(self, url: str, service_key: str, data_dir: Path, client: httpx.Client | None = None):
        if not url or not service_key:
            raise SupabaseError("SUPABASE_URL and SUPABASE_SERVICE_KEY are required for STORE_BACKEND=supabase")
        self._http = client or httpx.Client(
            base_url=f"{url.rstrip('/')}/rest/v1",
            headers={"apikey": service_key, "Authorization": f"Bearer {service_key}"},
            timeout=15.0,
        )
        self._url = url.rstrip("/")
        self._decks = FileStore(data_dir)  # local fallback copy

    def _check(self, r: httpx.Response) -> httpx.Response:
        if r.status_code >= 300:
            raise SupabaseError(f"Supabase {r.request.method} {r.request.url.path} -> {r.status_code}: {r.text[:300]}")
        return r

    def list_applications(self) -> list[Application]:
        r = self._check(self._http.get("/applications", params={"select": "data", "order": "created_at.desc", "limit": "1000"}))
        return [Application.model_validate(row["data"]) for row in r.json()]

    def get_application(self, app_id: str) -> Application | None:
        r = self._check(self._http.get("/applications", params={"id": f"eq.{app_id}", "select": "data"}))
        rows = r.json()
        return Application.model_validate(rows[0]["data"]) if rows else None

    def save_application(self, app: Application) -> None:
        ev = app.evaluation
        row = {
            "id": app.id,
            "created_at": app.created_at,
            "status": app.status,
            "score": ev.overall_score if ev else None,
            "priority": ev.priority if ev else None,
            "decision": app.decision.decision if app.decision else None,
            "data": app.model_dump(),
        }
        self._check(self._http.post(
            "/applications", params={"on_conflict": "id"}, json=row,
            headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
        ))

    def delete_all(self) -> None:
        self._check(self._http.delete("/applications", params={"id": "not.is.null"}))

    def get_rubric(self) -> Rubric | None:
        r = self._check(self._http.get("/settings", params={"key": "eq.rubric", "select": "value"}))
        rows = r.json()
        return Rubric.model_validate(rows[0]["value"]) if rows else None

    def save_rubric(self, rubric: Rubric) -> None:
        self._check(self._http.post(
            "/settings", params={"on_conflict": "key"}, json={"key": "rubric", "value": rubric.model_dump()},
            headers={"Prefer": "resolution=merge-duplicates,return=minimal"},
        ))

    def _deck_object(self, app_id: str) -> str:
        safe = "".join(ch for ch in app_id if ch.isalnum() or ch in "-_")
        return f"{self._url}/storage/v1/object/decks/{safe}.pdf"

    def save_deck(self, app_id: str, data: bytes) -> None:
        self._decks.save_deck(app_id, data)  # local copy first: never lose an upload
        try:
            r = self._http.post(self._deck_object(app_id), content=data,
                                headers={"Content-Type": "application/pdf", "x-upsert": "true"})
            if r.status_code >= 300:
                raise SupabaseError(f"deck upload -> {r.status_code}: {r.text[:200]}")
        except (httpx.HTTPError, SupabaseError):
            pass  # the local copy still exists; analysis can proceed on this instance

    def get_deck(self, app_id: str) -> bytes | None:
        local = self._decks.get_deck(app_id)
        if local:
            return local
        try:
            r = self._http.get(self._deck_object(app_id))
        except httpx.HTTPError:
            return None
        return r.content if r.status_code == 200 and r.content.startswith(b"%PDF-") else None
