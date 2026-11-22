# Instructions for AI coding tools

(For OpenCode, Antigravity, Claude Code, Lovable, Cursor and similar. Humans: see `CONTRIBUTING.md`.)

## What this project is

**Shortlist** triages startup-programme applications. An applicant submits a form and optional PDF deck. Gemini scores it against a rubric with evidence quotes; code verifies the quotes, calculates the score and priority; reviewers see a ranked dashboard and make the decision. Read `PLANNER.md` (design) and `SCOPE.md` (what is in and out) before large changes.

## Commands

```bash
cd backend
pip install -r requirements.txt
python -m pytest -q                  # must pass before any commit
uvicorn app.main:app --reload        # http://localhost:8000 serves API and frontend
python ../scripts/run_eval.py --mock # plumbing check; drop --mock for real Gemini
python ../scripts/check_gemini.py    # needs GEMINI_API_KEY in backend/.env
```

## Layout

- `backend/app/` FastAPI. Routes in `main.py`. AI pipeline in `pipeline.py`. Scoring in `scoring.py`. Quote and injection checks in `grounding.py`. Data shapes in `models.py`. Storage in `store/`. Analyzers in `ai/`.
- `frontend/` plain HTML, CSS and JavaScript, **no build step, no frameworks, no npm**. API calls only through `frontend/js/api.js`. Shared helpers in `frontend/js/ui.js`.
- `API-CONTRACT.md` is the source of truth for request and response shapes.

## Hard rules

1. **Never send `founder_name`, `founder_email` or `organization` to the model.** `prompts.application_block` uses `CONTENT_FIELDS` only. A test enforces this.
2. **The model never computes the overall score, the priority or the confidence downgrade.** Those are code (`scoring.py`, `pipeline.py`).
3. **Applicant text and anything the model wrote is untrusted.** In the frontend use `ui.esc()` or `textContent`. Never concatenate it into `innerHTML` raw.
4. **Never write a secret into any file that is tracked by git.** Keys live in `backend/.env` (ignored) and Render environment variables. The Supabase `service_role` key never goes in `frontend/`.
5. **The UI never says accept or reject.** Output is review priority (`high|medium|low`); the human decision is `shortlist|interview|hold|decline`.
6. **No invented numbers.** Anything shown to users or judges is measured, or labelled as an assumption.
7. **Mock mode must stay labelled.** `ai_mode: "mock"` shows a red badge in the UI.
8. Do not add dependencies, frameworks or a build step without asking Warisha.
9. Do not change the shapes in `API-CONTRACT.md` or `models.py` without updating the contract, the tests and the frontend in the same change.

## Ask a human before changing

`backend/app/pipeline.py`, `scoring.py`, `prompts.py`, `backend/data/rubric.default.json`, `render.yaml`, `.github/workflows/`. Those are owned by Warisha.

## Style

- Python 3.11+, type hints, small functions, readable error messages (users and teammates see them).
- Every endpoint or bug fix gets a pytest test in `backend/tests/`, in the style of the existing ones. Tests must not call the network.
- Frontend: semantic HTML, labels on inputs, CSS variables from the `:root` block in `base.css`, works at phone width (no horizontal scroll).

## Good prompts for common tasks

- *"Read `AGENTS.md` and `API-CONTRACT.md`. In `frontend/dashboard.html` add a score bar to each row using the `.bar` class from `base.css`. Escape all API text with `ui.esc`. Do not change `api.js`."*
- *"Read `AGENTS.md`. Add `GET /api/applications/{id}/brief` to `backend/app/main.py` returning Markdown built by a new `backend/app/brief.py`. Reviewer-only (use `Depends(require_reviewer)`), 404 if the application has no evaluation. Add two tests in `backend/tests/test_api.py` in the same style as the others. Run `python -m pytest -q`."*
- *"Read `AGENTS.md`. Explain this error and propose the smallest fix: <paste exact error>."*

After any AI-generated change: run the tests, open the page, check the browser console for red errors, and read the diff before committing.
