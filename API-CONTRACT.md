# API contract

The frontend and backend meet here. **If you need a change, open an issue labelled `backend` and tag Warisha: do not work around it.**
Everything below was copied from the running backend (mock AI mode, so the numbers are illustrative).

- Base URL: same origin as the page (`""` in `frontend/js/config.js`). Locally: `http://localhost:8000`.
- All bodies are JSON unless stated. Errors look like `{"detail": "message"}`. Validation errors (422) have `detail` as a list of `{loc, msg}`.
- Interactive docs generated from the code: **`/docs`** (Swagger UI). Try calls there before writing frontend code.
- Reviewer routes need auth (see Auth). Applicant routes (`POST /api/applications`, `GET /api/rubric`, `GET /api/health`) do not.
- Everything in `input` and every text field the AI wrote is **untrusted text**. Escape it with `ui.esc()` before putting it in `innerHTML`.

## Auth

| `AUTH_MODE` | What the frontend sends | Notes |
|---|---|---|
| `none` | nothing | Local development only. |
| `key` (**default for the demo**) | header `X-Reviewer-Key: <key>` | `ui.withAuth()` prompts for it on a 401 and stores it in `sessionStorage`. |
| `supabase` (stretch) | header `Authorization: Bearer <Supabase access token>` | The user's email must be in the server's `REVIEWER_EMAILS`. |

`401` = missing or wrong credentials. `403` = logged in but not allowed to review.
Files (`/deck`, `/export.csv`) cannot be opened with a plain link when auth is on, because a link cannot send headers. Use `api.openDeck(id)` and `api.downloadCsv(blind)` from `frontend/js/api.js`.

## Quick reference

| Method and path | Auth | Purpose |
|---|---|---|
| `GET /api/health` | no | Which AI mode, model and store the server is using. |
| `GET /api/rubric` | no | The scoring criteria and weights (so we can show them publicly). |
| `PUT /api/rubric` | reviewer | Replace the rubric. Version number goes up by 1. |
| `POST /api/applications` | no | Submit an application (multipart: `payload` JSON string + optional `deck` PDF). Returns `202`. |
| `GET /api/applications` | reviewer | List with sort, filters and blind mode. |
| `GET /api/applications/{id}` | reviewer | One application with the full evaluation. |
| `GET /api/applications/{id}/deck` | reviewer | The uploaded PDF. |
| `POST /api/applications/{id}/analyze` | reviewer | Run the AI again (keeps the reviewer decision). Returns `202`. |
| `PUT /api/applications/{id}/decision` | reviewer | Record the human decision. |
| `GET /api/stats` | reviewer | Numbers for the dashboard strip. |
| `GET /api/export.csv` | reviewer | All applications as CSV (`?blind=true` hides names). |
| `POST /api/dev/seed` | reviewer | Load the demo applicants (`?analyze=true&reset=false`). Disabled when `ENABLE_DEV_ROUTES=false`. |
| `POST /api/dev/reset` | reviewer | Delete everything. Disabled when `ENABLE_DEV_ROUTES=false`. |
| `GET /api/applications/{id}/brief` | reviewer | **Planned (BE-03, Hammad):** one-page Markdown interview brief. |

## `GET /api/health`

```json
{
  "status": "ok",
  "ai_mode": "mock",
  "model": "mock-heuristic",
  "store": "file",
  "auth_mode": "none",
  "dev_routes": true
}
```

`ai_mode` is `"mock"` or `"gemini"`. **If it says `mock` the demo is not using the real AI.** The dashboard shows a red MOCK badge in that case.

## `POST /api/applications` (applicant)

Send `multipart/form-data` with:

- `payload`: a **string** containing this JSON object
- `deck`: optional file, must be a real PDF, at most `MAX_DECK_MB` (default 10)

| Field | Required | Rules |
|---|---|---|
| `startup_name` | yes | 2 to 120 characters |
| `one_liner` | yes | 5 to 300 |
| `sector` | no | up to 80 |
| `stage` | no (default `idea`) | `idea`, `prototype`, `mvp`, `launched`, `revenue` |
| `problem` | yes | 10 to 4000 |
| `solution` | yes | 10 to 4000 |
| `target_customers`, `traction`, `business_model`, `team_background` | no | up to 3000 each |
| `ask` | no | up to 2000 |
| `founder_name` | yes | 2 to 120 (**never sent to the AI**) |
| `founder_email` | yes | valid email (**never sent to the AI**) |
| `organization` | no | up to 160 (**never sent to the AI**) |

Success `202`: `{"id": "6db1bc233997", "status": "pending"}`. The analysis runs in the background; there is no applicant-facing result by design.

Errors: `413` deck too large, `422` bad field or not a PDF, `429` too many submissions from one address (`RATE_LIMIT_PER_HOUR`, default 30 per IP: raise it for the demo, the venue Wi-Fi shares one IP).

Validation error example (`422`):

```json
[
  {
    "type": "string_too_short",
    "loc": [
      "startup_name"
    ],
    "msg": "String should have at least 2 characters",
    "input": "x"
  },
  {
    "type": "missing",
    "loc": [
      "one_liner"
    ],
    "msg": "Field required",
    "input": {
      "startup_name": "x"
    }
  }
]
```

## `GET /api/applications` (list)

Query parameters (all optional): `sort` = `score` (default) | `newest` | `name`; `priority` = `high|medium|low`; `status` = `pending|analyzing|done|failed`; `decision` = `shortlist|interview|hold|decline|undecided`; `q` (search text); `blind` = `true|false`.

```json
{ "total": 12, "items": [ ... ] }
```

One item:

```json
{
  "id": "demo-01",
  "created_at": "2026-11-20T11:12:45+00:00",
  "startup_name": "MedRoute KP",
  "one_liner": "Ambulance dispatch routing that cuts response time for district hospitals.",
  "sector": "Healthtech",
  "stage": "mvp",
  "founder_name": "Demo Founder 01",
  "status": "done",
  "has_deck": false,
  "overall_score": 90.0,
  "priority": "high",
  "confidence": "medium",
  "completeness": 100.0,
  "red_flag_count": 0,
  "unverified_quotes": 0,
  "decision": null,
  "ai_mode": "mock"
}
```

- `status` moves `pending` → `analyzing` → `done` (or `failed`). **Poll every 2 to 3 seconds while any item is `pending` or `analyzing`.** The dashboard already does this.
- `overall_score`, `priority`, `confidence`, `completeness` are `null` until `status` is `done`.
- With `blind=true`, `founder_name` is `"Hidden (blind review)"` and search ignores names.
- `unverified_quotes` is how many evidence quotes the code could not find in the application. Show it as a warning, not an error.

## `GET /api/applications/{id}` (detail)

`?blind=true` hides `founder_name`, `founder_email` and `organization`. Shortened example (long strings cut, lists trimmed to one item):

```json
{
  "id": "demo-01",
  "created_at": "2026-11-20T11:12:45+00:00",
  "status": "done",
  "error": null,
  "input": {
    "startup_name": "MedRoute KP",
    "one_liner": "Ambulance dispatch routing that cuts response time for di...",
    "sector": "Healthtech",
    "stage": "mvp",
    "problem": "Dispatchers at district hospitals assign ambulances by ph...",
    "solution": "A simple web dashboard and SMS flow that shows free ambul...",
    "target_customers": "District and tehsil hospitals and Rescue-style emergency ...",
    "traction": "Live pilot at two hospitals since September. 612 dispatch...",
    "business_model": "Annual subscription per hospital, priced per ambulance, p...",
    "team_background": "Two final-year software engineering students and one form...",
    "ask": "Introductions to the provincial health department, mentor...",
    "founder_name": "Demo Founder 01",
    "founder_email": "demo01@example.com",
    "organization": "Demo University A"
  },
  "has_deck": false,
  "deck_filename": null,
  "evaluation": {
    "summary": "[MOCK] MedRoute KP: Ambulance dispatch routing that cuts response time for distr",
    "criteria": [
      {
        "key": "problem",
        "name": "Problem & customer pain",
        "weight": 20.0,
        "score": 5,
        "reasoning": "Heuristic score from detail and specifics (280 characters).",
        "evidence_quote": "Dispatchers at district hospitals assign ambulances by phone",
        "evidence_verified": true
      }
    ],
    "strengths": [
      "Detailed on: Problem & customer pain"
    ],
    "risks": [
      "(mock) none detected"
    ],
    "riskiest_assumptions": [
      "Target customers will pay for: A simple web dashboard and SMS flow that shows free ambulances on a map, suggest"
    ],
    "interview_questions": [
      "What is the strongest evidence that 'Dispatchers at district hospitals assign ambulances by phone' is painful enough to pay to fix?"
    ],
    "red_flags": [],
    "missing_info": [],
    "confidence": "medium",
    "overall_score": 90.0,
    "priority": "high",
    "completeness": 100.0,
    "unverified_quotes": 0,
    "injection_detected": false,
    "attempts": 1,
    "warnings": [],
    "rubric_version": 1,
    "tokens_in": null,
    "tokens_out": null
  },
  "decision": null,
  "ai_mode": "mock",
  "model": "mock-heuristic",
  "analysis_seconds": 0.0
}
```

Meaning of the important fields:

| Field | Meaning |
|---|---|
| `evaluation.overall_score` | 0 to 100. Calculated **by code** from the 1 to 5 criterion scores and the rubric weights. |
| `evaluation.priority` | `high` (70 or more), `medium` (45 or more), else `low`. **This is reading order, not a verdict.** Never label it accept or reject in the UI. |
| `evaluation.confidence` | `low|medium|high`. Forced to `low` when injection-like text is found or more than 30 percent of quotes are unverified. |
| `evaluation.criteria[].evidence_quote` | A passage the AI says supports the score. |
| `evaluation.criteria[].evidence_verified` | `true` found in the application, `false` NOT found (show a warning), `null` no quote given. |
| `evaluation.injection_detected` | The applicant text contained instruction-like text (for example "ignore previous instructions"). It was ignored. Show a prominent banner. |
| `evaluation.warnings` | Plain-language problems to show the reviewer. |
| `evaluation.attempts` | 2 means the first answer had unverifiable quotes and the AI was asked once to correct them. |
| `status = "failed"` | `error` holds a readable reason. Offer a Retry button that calls `POST .../analyze`. |
| `ai_mode` | `mock` or `gemini`. Show the MOCK badge for `mock`. |

## `PUT /api/applications/{id}/decision`

Body: `{"decision": "shortlist|interview|hold|decline", "note": "optional", "reviewer": "optional name"}`. Returns the full application (not blind). Result stored in `decision`:

```json
{
  "decision": "interview",
  "note": "Strong pilot data",
  "reviewer": "Mahvish",
  "decided_at": "2026-11-20T12:12:45+00:00"
}
```

Any other `decision` value returns `422`. A decision survives re-analysis.

## `GET /api/stats`

```json
{
  "total": 12,
  "by_status": {
    "done": 12
  },
  "by_priority": {
    "medium": 5,
    "low": 3,
    "high": 4
  },
  "by_decision": {
    "undecided": 12
  },
  "avg_score": 60.4,
  "avg_analysis_seconds": 0.0,
  "avg_tokens_in": null,
  "avg_tokens_out": null,
  "unverified_quote_rate": 0.0,
  "assumed_manual_review_minutes": 15,
  "assumed_card_review_minutes": 3,
  "estimated_minutes_saved": 144,
  "assumption_note": "Time saved uses the two assumed minute values above. Replace them with real figures.",
  "ai_mode": "mock"
}
```

`estimated_minutes_saved` is **arithmetic on two assumed numbers** (`assumed_manual_review_minutes`, `assumed_card_review_minutes`), not a measurement. Always show the assumption next to it, as the dashboard does.

## `GET /api/rubric` and `PUT /api/rubric`

```json
{ "version": 1, "name": "...", "criteria": [
   { "key": "problem", "name": "Problem & customer pain", "weight": 20, "description": "...",
     "anchors": { "1": "...", "3": "...", "5": "..." }, "hint_fields": ["problem"] } ] }
```

`PUT` needs at least 2 criteria and unique `key`s (lowercase letters, digits, underscore). The server sets `version` itself.

## `GET /api/export.csv`

Columns: `id, startup, founder, sector, stage, overall_score, priority, confidence, red_flags, unverified_quotes, decision, decision_note` then one column per rubric criterion key. `?blind=true` replaces the founder with `Hidden (blind review)`.

## Changing the contract

1. Open a GitHub issue labelled `backend` describing the field you need.
2. Warisha (or Aliyan) changes `backend/app/models.py` and the test, updates this file, and tells the frontend.
3. Only then does the frontend start relying on it.
