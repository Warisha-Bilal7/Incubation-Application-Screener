# Shortlist

**Read the strongest startup applications first.**

Startup programmes receive more applications than staff can read carefully. Shortlist lets founders submit a form and a pitch deck, has Gemini score each application against the programme's rubric with evidence quotes that **code checks against the original text**, and gives reviewers a ranked dashboard with scorecards, interview questions and a blind-review mode. The AI sets reading order. A person makes every decision.

Built at **MLH x CNP Hack Day Peshawar**, 21 November 2026, for *Best Use of the Google Gemini API* and *Best AI Startup MVP*.

**Live demo:** TODO (add the Render URL)

<!-- TODO (DOC-04): add screenshots from docs/img/ here -->

## What it does

- **Applicants** submit a form and an optional PDF deck. No account needed.
- **Gemini** reads the form and the deck and returns a structured scorecard: a 1 to 5 score, reasoning and an evidence quote for each rubric criterion, plus strengths, risks, riskiest assumptions, suggested interview questions, red flags and missing information.
- **Code** verifies every quote against the original text, retries once if any quote was invented, calculates the weighted 0 to 100 score and the review priority, and flags manipulation attempts such as "ignore previous instructions".
- **Reviewers** see applications ranked by score, can hide applicant identity (blind review), open a scorecard, export CSV, and record a decision with a note.

## Why you can trust the output (and where not to)

| Safeguard | What it does |
|---|---|
| Evidence quotes checked by code | A claim without a findable quote is flagged and lowers confidence |
| Identity never sent to the AI | Name, email and organisation are removed before the prompt is built |
| Blind review | Hides identity from reviewers in the list, detail view, search and CSV |
| Injection flag | Instruction-like text in an application is flagged and ignored |
| Score by code | The AI scores criteria; the overall score and priority are arithmetic in code |
| Human decides | The output is a reading order, not accept or reject |

Read the limitations in [`PLANNER.md`](PLANNER.md) section 11. In short: identity can still leak through free text, the rubric is generic, we evaluated on 12 synthetic applicants we wrote ourselves, and "time saved" is an assumption.

## Quick start

```bash
git clone https://github.com/Warisha-Bilal7/Incubation-Application-Screener.git && cd Incubation-Application-Screener/backend
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env                                    # works as is: runs the labelled MOCK analyzer
uvicorn app.main:app --reload                           # open http://localhost:8000, click "Load demo data"
```

For real Gemini analysis put `GEMINI_API_KEY` in `backend/.env` (get one at https://aistudio.google.com/apikey), then run `python ../scripts/check_gemini.py`.

Run the tests: `python -m pytest -q`. Check the AI on the demo set: `python ../scripts/run_eval.py`.

## How it is built

```
form + PDF -> strip identity -> Gemini (PDF + structured JSON) -> verify quotes (code) -> retry once
          -> injection check (code) -> score + priority (code) -> Supabase -> ranked dashboard
```

| Part | Technology |
|---|---|
| AI | Google Gemini API (`google-genai`): PDF understanding, structured output, system instruction |
| Backend | Python, FastAPI, Pydantic |
| Storage | Supabase (Postgres tables and a private Storage bucket); a JSON file store for local use |
| Frontend | Plain HTML, CSS and JavaScript, no build step. Served by the backend. |
| Hosting | Render (one web service) |

More: [`docs/HOW-IT-WORKS.md`](docs/HOW-IT-WORKS.md) (plain language), [`PLANNER.md`](PLANNER.md) (design), [`API-CONTRACT.md`](API-CONTRACT.md), `docs/EVAL-RESULTS.md` (what we measured, created in QA-02).

## Project documents

| File | What it is |
|---|---|
| [`SCOPE.md`](SCOPE.md) | Exactly what is in and out of scope, the cut line, the definition of done |
| [`PLANNER.md`](PLANNER.md) | Design, pipeline, data definitions, schedule, risks |
| [`ROLE-GUIDES.md`](ROLE-GUIDES.md) | What every person does, in order |
| [`MILESTONES-AND-ISSUES.md`](MILESTONES-AND-ISSUES.md) | Milestones and every issue with owner and estimate |
| [`API-CONTRACT.md`](API-CONTRACT.md) | Request and response shapes |
| [`DEPLOYMENT-CHECKLIST.md`](DEPLOYMENT-CHECKLIST.md) | Deploy, security checklist, pre-demo checklist |
| [`DEMO-AND-PITCH.md`](DEMO-AND-PITCH.md) | Slides, demo script, judge Q and A |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Git workflow and rules |
| [`AGENTS.md`](AGENTS.md) | Instructions for AI coding tools |

## Team

| Person | Role | GitHub |
|---|---|---|
| Warisha | Team lead, backend, AI | [@Warisha-Bilal7](https://github.com/Warisha-Bilal7) |
| Asim | Frontend lead | [@Asim56791](https://github.com/Asim56791) |
| Aruba | Frontend, documentation | [@arubajamil264-del](https://github.com/arubajamil264-del) |
| Hafsa | Slides, wording, accessibility | [@shahhafsa698-arch](https://github.com/shahhafsa698-arch) |
| Aliyan | Backend, database | [@Aliyan4848](https://github.com/Aliyan4848) |
| Hamdan | Backend features, tests, QA | [@Hamdan7Khan](https://github.com/Hamdan7Khan) |

## Licence

TODO (choose one, for example MIT, and add a LICENSE file).
