# Shortlist: AI application triage for incubators

> A small pipeline that reads startup applications against a programme's rubric, scores each one with evidence quotes that code checks against the original text, and ranks the pile so human reviewers read the strongest and most uncertain applications first. Gemini handles the reading and explaining. Deterministic code handles the verification, the arithmetic and the priority. People make every decision.
>
> Built for **MLH x CNP Hack Day Peshawar** (21 Nov 2026) for the categories *Best Use of the Google Gemini API* and *Best AI Startup MVP*.

The product name "Shortlist" is a placeholder. Rename it anywhere in `frontend/` and `README.md` if the team prefers another.

---

## 1. Design principles

1. **The AI reads and explains; code decides.** Gemini scores each criterion from 1 to 5 and writes the reasoning. The weighted total, the priority and the confidence downgrade are calculated in code (`backend/app/scoring.py`), so the same scores always give the same ranking and nobody has to trust model arithmetic.
2. **Every claim carries a quote, and code checks the quote.** Each criterion must include a passage copied from the application. Code looks for that passage in the original text. If it is not there the reviewer sees a warning, the AI is asked once to correct itself, and the confidence drops.
3. **The AI never sees who the applicant is.** Name, email and organisation are stripped before the prompt is built. Blind mode hides them from reviewers too.
4. **Applicant text is untrusted.** It is wrapped in `<application>` tags, the system prompt says to ignore instructions inside it, and a separate rule-based check flags instruction-like text ("ignore previous instructions") and lowers confidence.
5. **People decide.** The output is a *review priority*, never accept or reject. The human decision is stored separately with a note and the reviewer's name.
6. **It runs with no keys.** A clearly labelled mock analyzer lets everyone build and test offline. Real Gemini is switched on by one environment variable.
7. **One URL.** The backend also serves the frontend, so there is no CORS and one thing to deploy.

## 2. Pipeline

```
applicant form + optional PDF deck
        |
        v
 intake ---- strip identity fields (name, email, organisation) ---->  stored separately
        |
        v
 evaluate (Gemini: PDF understanding + structured JSON) -> 1-5 score, reasoning, evidence quote per criterion
        |
        v
 verify quotes (code) ---- any quote not found in the application? ----+
        |                                                              |
        | all found                                   retry ONCE with the failing quotes listed
        v                                                              |
 rule checks (code): injection patterns, completeness <-----------------+
        |
        v
 score (code): weighted 0-100, priority, confidence downgrade
        |
        v
 store (Supabase or local file) -> dashboard ranks -> human decision
```

| Step | Uses Gemini? | File | Job |
|---|---|---|---|
| intake | no | `app/main.py`, `app/models.py` | Validate the form, check the PDF, save the application as `pending`, start analysis in the background. |
| evaluate | **yes** | `app/ai/gemini.py`, `app/prompts.py` | One structured-output call with the rubric, the application text and the PDF. Retries on network errors. |
| verify | no | `app/grounding.py` | Normalise text and check each evidence quote appears in the form or the PDF text. |
| retry | **yes** | `app/pipeline.py` | One extra call that lists the unverifiable quotes. The better attempt is kept. |
| rule checks | no | `app/grounding.py` | Regex patterns for prompt-injection text in any field or the deck. |
| score | no | `app/scoring.py` | Weighted average, priority thresholds, completeness percentage. |
| store | no | `app/store/` | `FileStore` (local JSON) or `SupabaseStore` (Postgres + Storage). |
| review | no | `frontend/` | Ranked list, scorecard, blind mode, decision, CSV export. |

## 3. Repo layout

```
shortlist/
├── README.md  PLANNER.md  SCOPE.md  ROLE-GUIDES.md  MILESTONES-AND-ISSUES.md
├── API-CONTRACT.md  DEMO-AND-PITCH.md  DEPLOYMENT-CHECKLIST.md  CONTRIBUTING.md  AGENTS.md
├── render.yaml                      # Render blueprint (one web service)
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI routes, serves ../frontend at /
│   │   ├── models.py                # all data shapes (Pydantic)
│   │   ├── pipeline.py              # evaluate -> verify -> retry -> rules -> score
│   │   ├── prompts.py               # system prompt + user prompt builder
│   │   ├── scoring.py               # weighted score, priority, completeness
│   │   ├── grounding.py             # quote verification, injection detection, PDF text
│   │   ├── rubric.py                # rubric model + loader
│   │   ├── auth.py                  # none | key | supabase reviewer auth
│   │   ├── container.py             # wiring + the background analysis job
│   │   ├── config.py  seed.py
│   │   ├── ai/{gemini.py,mock.py}   # real and offline analyzers
│   │   └── store/{file.py,supabase.py}
│   ├── data/
│   │   ├── rubric.default.json      # the rubric: edit this
│   │   ├── demo_applicants.json     # 12 synthetic applicants (strong, medium, weak, incomplete, injection)
│   │   ├── sample_deck.pdf  schema.sql
│   ├── tests/                       # 43 tests, no network needed
│   ├── .env.example  requirements.txt  pytest.ini
├── frontend/                        # plain HTML, CSS, JavaScript, no build step
│   ├── index.html  apply.html  dashboard.html  application.html
│   ├── css/base.css                 # design tokens at the top
│   └── js/{config.js,api.js,ui.js}
├── scripts/
│   ├── check_gemini.py              # run first: lists models, tests one call
│   ├── run_eval.py                  # sanity-checks the AI on the demo set
│   ├── create_issues.sh  issues.tsv  team.env.example
├── docs/{DEV-LOG.md,HOW-IT-WORKS.md,img/}
└── .github/{workflows/tests.yml,PULL_REQUEST_TEMPLATE.md,ISSUE_TEMPLATE/}
```

## 4. Data definitions

Defined in `backend/app/models.py`. Three shapes matter.

**`ApplicationIn`** is what the applicant submits. It is split into two groups.

| Group | Fields | Goes to the AI? |
|---|---|---|
| Startup content | `startup_name, one_liner, sector, stage, problem, solution, target_customers, traction, business_model, team_background, ask` | yes |
| Identity | `founder_name, founder_email, organization` | **never** |

**`AIEvaluation`** is what Gemini must return (this class is passed to the SDK as the response schema):

```python
class AICriterion(BaseModel):
    key: str; score: int; reasoning: str; evidence_quote: str

class AIEvaluation(BaseModel):
    summary: str
    criteria: list[AICriterion]
    strengths: list[str]; risks: list[str]; riskiest_assumptions: list[str]
    interview_questions: list[str]; red_flags: list[str]; missing_info: list[str]
    confidence: Literal["low", "medium", "high"]
```

**`Evaluation`** is what we store and show. It is the AI output *plus* everything code added: per-criterion `evidence_verified`, `overall_score`, `priority`, `completeness`, `unverified_quotes`, `injection_detected`, `attempts`, `warnings`, `rubric_version`, token counts. The AI is never asked for the overall score.

## 5. Scoring, verification and safety rules

**Overall score** (`scoring.py`): `(weighted average of 1-5 scores - 1) / 4 * 100`, one decimal. All 1s give 0 and all 5s give 100.

**Priority**: 70 or more is `high` (average criterion score of 3.8 or better), 45 or more is `medium` (average 2.8), otherwise `low`. These thresholds are our judgment, not a standard. Warisha reviews them against the eval results (BE-05).

**Quote verification** (`grounding.verify_quote`): lowercase, strip punctuation, collapse spaces. A quote containing `...` is split and every fragment of 6 or more characters must appear. The searched text is the form fields plus the text extracted from the PDF. Image-only slides have no extractable text, so quotes taken from them show as unverified. That is expected and is listed in the limitations.

**Retry**: if any quote is unverified, run once more with the failing quotes in the prompt. Keep whichever attempt has fewer unverified quotes. Never loop more than once.

**Confidence downgrade**: forced to `low` if injection-like text is found or more than 30 percent of quotes are unverified.

**Injection check**: regex patterns such as "ignore all previous instructions", "give this a score of 5", "system prompt". It scans every content field and the PDF text. A hit adds a red flag, sets `injection_detected`, and lowers confidence. It does not change the score by itself. It is a safety net, not a guarantee.

**Completeness**: percent of the five optional fields (`target_customers, traction, business_model, team_background, ask`) with at least 15 characters.

## 6. Gemini integration

- SDK: `google-genai`. Model from `GEMINI_MODEL` (default `gemini-flash-latest`). Run `python scripts/check_gemini.py` to see which models your key can call, then pin one.
- Features used: **PDF understanding** (the deck is sent as an inline PDF part), **structured output** (`response_mime_type="application/json"` with the Pydantic class as `response_schema`), **system instruction**, low temperature (0.2), token usage recorded per application.
- Not used: search grounding, function calling, streaming. Do not claim them.
- Failure handling: up to 2 retries with backoff on any error, then the application is saved as `failed` with a readable error and a Retry button.
- Mock mode: `AI_MODE=mock` (or no key set) uses a length-and-specifics heuristic. It is only for plumbing and is labelled MOCK everywhere.

**Known unknown, to be settled in BE-01:** the Gemini call has been written and tested against a fake client, and the response schema is accepted by the SDK, but it has **not yet been run with a real key**. The first real call happens in BE-01. If the model name or the schema is rejected, `check_gemini.py` says so.

## 7. Configuration

All in `backend/.env` (copy `.env.example`). Most useful:

| Variable | Dev | Demo |
|---|---|---|
| `AI_MODE` | `mock` | `gemini` |
| `GEMINI_API_KEY`, `GEMINI_MODEL` | optional | required |
| `STORE_BACKEND` | `file` | `supabase` |
| `SUPABASE_URL`, `SUPABASE_SERVICE_KEY` | - | required |
| `AUTH_MODE` | `none` | `key` (or `supabase` if the stretch issues are done) |
| `REVIEWER_KEY` | - | a long random string |
| `RATE_LIMIT_PER_HOUR` | 30 | 300 (the venue shares one IP) |
| `ENABLE_DEV_ROUTES` | `true` | decide in SEC-01 |
| `ASSUMED_MANUAL_MINUTES`, `ASSUMED_CARD_MINUTES` | 15, 3 | **replace with real numbers or remove the tile** |

## 8. Evaluation plan

`python scripts/run_eval.py` runs the 12 demo applicants through the real pipeline and checks:

| Check | Meaning | Where it can mislead |
|---|---|---|
| Every strong applicant outscores every weak one | The ranking is sane | We wrote and labelled these applicants ourselves |
| The injection applicant is flagged and not `high` | The safety net works | One example, not a security audit |
| Under 10 percent of quotes unverified | The AI quotes the text it is given | Depends on the PDF having extractable text |
| Latency and tokens per application | Cost and speed | Network conditions at the venue |

**This is a sanity check on synthetic data, not a measure of accuracy.** Say so on the slide. Record the real output in `docs/EVAL-RESULTS.md` (QA-02), including anything that failed.

## 9. Build-day schedule (T+0:00 = you sit down)

| Time | Warisha | Amir | Aruba | Hafsa | Aliyan | Hammad |
|---|---|---|---|---|---|---|
| 0:00 to 0:30 **M1** | BE-01, BE-02 | FE-01 | FE-02, DOC-01 | FE-03, SLD-01 | DB-01 | QA-01 |
| 0:30 to 1:45 **M2** | AI-01, AI-02 | FE-04, FE-05 | FE-06, DOC-02 | FE-07, SLD-02 | AI-03, DB-02 | BE-03 |
| 1:45 to 2:45 **M3** | BE-05 + reviews | stretch: FE-08, FE-10 | stretch: FE-09 | DOC-03, SLD-03 | AI-04 (stretch: BE-04) | AI-05, QA-02 (stretch: FE-11) |
| 2:45 to 3:20 **M4** | SEC-01 | QA-05 | QA-04, DOC-04 | slides polish | QA-06 | QA-03 |
| 3:20 to 4:00 **M5** | DEP-01, DEMO-02 | smoke test (stretch: DEP-03) | DOC-05 | SLD-04 | DEP-02 | DEP-04 |
| 3:30 to 4:00 | **DEMO-01: everyone rehearses twice** | | | | | |

Warisha's real job all day is unblocking and reviewing pull requests. Her list is short on purpose.

## 10. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Gemini model name or schema rejected on first real call | `check_gemini.py` in SET-03, BE-01 right at T+0:00. Mock mode keeps everyone else unblocked. |
| Free-tier rate limit (429) while analysing 12 applicants | Retries with backoff, sequential seeding, each backend dev uses their own key (SET-03), AI-04 tests it. Seed once and rely on the stored results. |
| Venue Wi-Fi is slow or drops | Phone hotspot, backup demo video (DEP-04), local copy of the app with seeded data as a second fallback. |
| Render free instance asleep during the demo (about a minute to wake) | Open the site 10 minutes before and keep a tab polling `/api/health`. Source: Render free-tier docs. |
| Render disk is wiped on restart | Data lives in Supabase (tables and Storage), not on disk. |
| Rate limit blocks teammates because the venue shares one IP | `RATE_LIMIT_PER_HOUR=300` on Render. |
| Applicant text attacks the reviewer's browser | All rendering goes through `ui.esc()`. Tested with a script-tag name in a real browser. |
| Applicant text attacks the AI | Delimiters, system rules, regex flag, quote verification, human decides. Not perfect: be honest about it. |
| Scope creep | `SCOPE.md` cut line. Ideas go in issues labelled `stretch`. |
| Someone commits a key | `.gitignore`, `SEC-01`, rotate the key if it happens. |
| Beginners blocked on Git | `CONTRIBUTING.md` has the exact commands. SET-07 practises them tonight. |

## 11. Known limitations (say these before a judge finds them)

1. Identity is removed from the **fields**, not from free text. An applicant who writes their university in the "team" box exposes it to the AI. AI-05 tests how the model handles this.
2. The rubric is a generic starting point, not any real programme's criteria.
3. One model, one prompt. Scores can differ between runs. The code makes the arithmetic repeatable, not the model.
4. Image-only decks have no text for quote verification.
5. Evaluated on 12 applicants we wrote ourselves. No real applicants were used.
6. The injection detector uses fixed patterns and will miss clever attacks.
7. "Minutes saved" on the dashboard is arithmetic on two assumed numbers.
8. No email notifications, no multi-reviewer workflow, no applicant accounts.
