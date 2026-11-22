import csv
import io
import json
import time
import uuid
from pathlib import Path

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from .auth import require_reviewer
from .config import Settings, get_settings
from .container import Container, build_container, now_iso, process_application, process_many
from .models import IDENTITY_FIELDS, Application, ApplicationIn, DecisionIn, DecisionRecord
from .rubric import Rubric, load_default_rubric
from .seed import load_demo_applications

BLIND_TEXT = "Hidden (blind review)"
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


# ---------- views ----------
def _masked_input(inp: dict, blind: bool) -> dict:
    if not blind:
        return inp
    out = dict(inp)
    out["founder_name"] = BLIND_TEXT
    for f in IDENTITY_FIELDS:
        if f != "founder_name":
            out[f] = ""
    return out


def detail_view(app: Application, blind: bool) -> dict:
    d = app.model_dump()
    d["input"] = _masked_input(d["input"], blind)
    return d


def summary_view(app: Application, blind: bool) -> dict:
    ev, inp = app.evaluation, app.input
    return {
        "id": app.id,
        "created_at": app.created_at,
        "startup_name": inp.startup_name,
        "one_liner": inp.one_liner,
        "sector": inp.sector,
        "stage": inp.stage,
        "founder_name": BLIND_TEXT if blind else inp.founder_name,
        "status": app.status,
        "has_deck": app.has_deck,
        "overall_score": ev.overall_score if ev else None,
        "priority": ev.priority if ev else None,
        "confidence": ev.confidence if ev else None,
        "completeness": ev.completeness if ev else None,
        "red_flag_count": len(ev.red_flags) if ev else 0,
        "unverified_quotes": ev.unverified_quotes if ev else 0,
        "decision": app.decision.decision if app.decision else None,
        "ai_mode": app.ai_mode,
    }


def create_app(settings: Settings | None = None, container: Container | None = None) -> FastAPI:
    settings = settings or get_settings()
    c = container or build_container(settings)
    app = FastAPI(title="Shortlist API", version="0.1.0")
    app.state.c = c
    app.add_middleware(
        CORSMiddleware, allow_origins=list(settings.cors_origins), allow_methods=["*"], allow_headers=["*"],
    )

    def get_c(request: Request) -> Container:
        return request.app.state.c

    # ---------- public ----------
    @app.get("/api/health")
    def health(c: Container = Depends(get_c)):
        s = c.settings
        return {
            "status": "ok", "ai_mode": c.analyzer.name, "model": c.analyzer.model,
            "store": c.store.name, "auth_mode": s.auth_mode, "dev_routes": s.enable_dev_routes,
        }

    @app.get("/api/rubric")
    def get_rubric(c: Container = Depends(get_c)):
        return c.get_rubric().model_dump()

    @app.post("/api/applications", status_code=202)
    async def submit_application(
        request: Request, background: BackgroundTasks,
        payload: str = Form(...), deck: UploadFile | None = File(None),
        c: Container = Depends(get_c),
    ):
        s = c.settings
        # naive per-IP rate limit so a stray script cannot burn the Gemini quota
        ip = (request.headers.get("x-forwarded-for", "").split(",")[0].strip()
              or (request.client.host if request.client else "unknown"))
        now = time.time()
        recent = [t for t in c.submissions.get(ip, []) if now - t < 3600]
        if len(recent) >= s.rate_limit_per_hour:
            raise HTTPException(429, "Too many submissions from this address. Try again later.")
        c.submissions[ip] = recent + [now]

        try:
            inp = ApplicationIn.model_validate(json.loads(payload))
        except json.JSONDecodeError:
            raise HTTPException(422, "payload must be a JSON string.")
        except ValidationError as e:
            raise HTTPException(422, e.errors(include_url=False, include_context=False))

        data, filename = None, None
        if deck is not None and (deck.filename or ""):
            limit = s.max_deck_mb * 1024 * 1024
            data = await deck.read(limit + 1)
            if len(data) > limit:
                raise HTTPException(413, f"Deck is larger than {s.max_deck_mb} MB.")
            if not data.startswith(b"%PDF-"):
                raise HTTPException(422, "Deck must be a PDF file.")
            filename = deck.filename[:120]

        app_id = uuid.uuid4().hex[:12]
        rec = Application(id=app_id, created_at=now_iso(), input=inp,
                          has_deck=data is not None, deck_filename=filename)
        if data is not None:
            c.store.save_deck(app_id, data)
        c.store.save_application(rec)
        background.add_task(process_application, c, app_id)
        return {"id": app_id, "status": "pending"}

    # ---------- reviewer ----------
    @app.put("/api/rubric")
    def put_rubric(rubric: Rubric, c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        current = c.get_rubric()
        rubric.version = current.version + 1
        c.store.save_rubric(rubric)
        return rubric.model_dump()

    @app.get("/api/applications")
    def list_applications(
        sort: str = Query("score", pattern="^(score|newest|name)$"),
        priority: str | None = Query(None, pattern="^(high|medium|low)$"),
        status: str | None = Query(None, pattern="^(pending|analyzing|done|failed)$"),
        decision: str | None = Query(None, pattern="^(shortlist|interview|hold|decline|undecided)$"),
        q: str | None = None, blind: bool = False,
        c: Container = Depends(get_c), _: str = Depends(require_reviewer),
    ):
        apps = c.store.list_applications()
        if priority:
            apps = [a for a in apps if a.evaluation and a.evaluation.priority == priority]
        if status:
            apps = [a for a in apps if a.status == status]
        if decision:
            apps = [a for a in apps if (a.decision.decision if a.decision else "undecided") == decision]
        if q:
            ql = q.lower()
            def hay(a: Application) -> str:
                i = a.input
                parts = [i.startup_name, i.one_liner, i.sector]
                if not blind:
                    parts += [i.founder_name, i.organization]
                return " ".join(parts).lower()
            apps = [a for a in apps if ql in hay(a)]
        if sort == "score":
            apps.sort(key=lambda a: (a.evaluation is None, -(a.evaluation.overall_score if a.evaluation else 0)))
        elif sort == "newest":
            apps.sort(key=lambda a: a.created_at, reverse=True)
        else:
            apps.sort(key=lambda a: a.input.startup_name.lower())
        return {"total": len(apps), "items": [summary_view(a, blind) for a in apps]}

    @app.get("/api/applications/{app_id}")
    def get_application(app_id: str, blind: bool = False, c: Container = Depends(get_c),
                        _: str = Depends(require_reviewer)):
        a = c.store.get_application(app_id)
        if not a:
            raise HTTPException(404, "Application not found.")
        return detail_view(a, blind)

    @app.get("/api/applications/{app_id}/deck")
    def get_deck(app_id: str, c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        data = c.store.get_deck(app_id)
        if not data:
            raise HTTPException(404, "No deck for this application.")
        return Response(data, media_type="application/pdf",
                        headers={"Content-Disposition": f'inline; filename="{app_id}.pdf"'})

    @app.post("/api/applications/{app_id}/analyze", status_code=202)
    def reanalyze(app_id: str, background: BackgroundTasks, c: Container = Depends(get_c),
                  _: str = Depends(require_reviewer)):
        a = c.store.get_application(app_id)
        if not a:
            raise HTTPException(404, "Application not found.")
        a.status, a.error = "pending", None
        c.store.save_application(a)
        background.add_task(process_application, c, app_id)
        return {"id": app_id, "status": "pending"}

    @app.put("/api/applications/{app_id}/decision")
    def set_decision(app_id: str, body: DecisionIn, c: Container = Depends(get_c),
                     who: str = Depends(require_reviewer)):
        a = c.store.get_application(app_id)
        if not a:
            raise HTTPException(404, "Application not found.")
        a.decision = DecisionRecord(decision=body.decision, note=body.note,
                                    reviewer=body.reviewer or who, decided_at=now_iso())
        c.store.save_application(a)
        return detail_view(a, blind=False)

    @app.get("/api/stats")
    def stats(c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        apps = c.store.list_applications()
        done = [a for a in apps if a.evaluation]
        secs = [a.analysis_seconds for a in done if a.analysis_seconds is not None]
        tin = [a.evaluation.tokens_in for a in done if a.evaluation.tokens_in]
        tout = [a.evaluation.tokens_out for a in done if a.evaluation.tokens_out]
        s = c.settings
        saved = len(done) * max(0, s.assumed_manual_minutes - s.assumed_card_minutes)
        count = lambda it: {k: sum(1 for x in it if x == k) for k in set(it)}  # noqa: E731
        return {
            "total": len(apps),
            "by_status": count([a.status for a in apps]),
            "by_priority": count([a.evaluation.priority for a in done]),
            "by_decision": count([a.decision.decision if a.decision else "undecided" for a in apps]),
            "avg_score": round(sum(a.evaluation.overall_score for a in done) / len(done), 1) if done else None,
            "avg_analysis_seconds": round(sum(secs) / len(secs), 1) if secs else None,
            "avg_tokens_in": round(sum(tin) / len(tin)) if tin else None,
            "avg_tokens_out": round(sum(tout) / len(tout)) if tout else None,
            "unverified_quote_rate": (
                round(sum(a.evaluation.unverified_quotes for a in done)
                      / max(1, sum(len(a.evaluation.criteria) for a in done)), 3) if done else None),
            "assumed_manual_review_minutes": s.assumed_manual_minutes,
            "assumed_card_review_minutes": s.assumed_card_minutes,
            "estimated_minutes_saved": saved,
            "assumption_note": "Time saved uses the two assumed minute values above. Replace them with real figures.",
            "ai_mode": c.analyzer.name,
        }

    @app.get("/api/export.csv")
    def export_csv(blind: bool = False, c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        rubric = c.get_rubric()
        apps = c.store.list_applications()
        apps.sort(key=lambda a: -(a.evaluation.overall_score if a.evaluation else -1))
        buf = io.StringIO()
        w = csv.writer(buf)
        head = ["id", "startup", "founder", "sector", "stage", "overall_score", "priority", "confidence",
                "red_flags", "unverified_quotes", "decision", "decision_note"] + [k.key for k in rubric.criteria]
        w.writerow(head)
        for a in apps:
            ev = a.evaluation
            by_key = {r.key: r.score for r in ev.criteria} if ev else {}
            w.writerow([
                a.id, a.input.startup_name, BLIND_TEXT if blind else a.input.founder_name,
                a.input.sector, a.input.stage,
                ev.overall_score if ev else "", ev.priority if ev else "", ev.confidence if ev else "",
                len(ev.red_flags) if ev else "", ev.unverified_quotes if ev else "",
                a.decision.decision if a.decision else "", a.decision.note if a.decision else "",
            ] + [by_key.get(k.key, "") for k in rubric.criteria])
        return Response(buf.getvalue(), media_type="text/csv",
                        headers={"Content-Disposition": 'attachment; filename="shortlist-export.csv"'})

    # ---------- dev helpers (disable with ENABLE_DEV_ROUTES=false) ----------
    @app.post("/api/dev/seed", status_code=202)
    def seed(background: BackgroundTasks, analyze: bool = True, reset: bool = False,
             c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        if not c.settings.enable_dev_routes:
            raise HTTPException(404, "Not found.")
        if reset:
            c.store.delete_all()
        existing = {a.id for a in c.store.list_applications()}
        new_ids = []
        for a in load_demo_applications():
            if a.id not in existing:
                c.store.save_application(a)
                new_ids.append(a.id)
        if analyze and new_ids:
            background.add_task(process_many, c, new_ids)
        return {"created": len(new_ids), "analyzing": new_ids if analyze else []}

    @app.post("/api/dev/reset")
    def reset(c: Container = Depends(get_c), _: str = Depends(require_reviewer)):
        if not c.settings.enable_dev_routes:
            raise HTTPException(404, "Not found.")
        c.store.delete_all()
        return {"ok": True}

    # serve the frontend from the same origin (one URL, no CORS). Must be mounted LAST.
    if settings.frontend_dir and Path(settings.frontend_dir).is_dir():
        app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")

    return app


app = create_app()
