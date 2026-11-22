# How we work together

Short version: **one issue, one branch, one pull request. Never push to `main`.** Warisha reviews and merges.

## First time setup (5 minutes)

```bash
git clone https://github.com/<owner>/shortlist.git
cd shortlist/backend
python -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
python -m pytest -q                # everything should pass
uvicorn app.main:app --reload      # open http://localhost:8000
```

The backend also serves the `frontend/` folder, so `http://localhost:8000` is the whole app. Edit a file in `frontend/`, refresh the browser. In the dashboard click **Load demo data** to get 12 applicants (with no API key you get the labelled MOCK analyzer).

Frontend only, with VS Code Live Server on another port? Set `API_BASE` in `frontend/js/config.js` to `http://localhost:8000`.

## The loop for every issue

```bash
git checkout main
git pull                                    # get everyone's latest work
git checkout -b aruba/fe-06                 # your name / issue code (lowercase)

# ...edit files, test in the browser...

git status                                  # see what changed
git add frontend/apply.html                 # add only the files you meant to change
git commit -m "FE-06: inline validation on apply form"
git push -u origin aruba/fe-06
```

Then on GitHub click **Compare and pull request**, fill in the template, and ask Warisha for review in the team chat. Put `Closes #<issue number>` in the description so the issue closes when it is merged.

While you wait for review, start the next issue on a new branch from `main`. Do not keep adding to a branch that already has an open pull request.

## Commit messages

`CODE: what changed`, present tense, short. Examples: `FE-04: score bars on dashboard`, `BE-03: add interview brief endpoint`, `DB-01: document Supabase setup`.

## If `git pull` or a merge says "conflict"

Do not panic and do not delete things. Tell Warisha or Amir, with the file name. Or: `git merge --abort` puts you back where you were.

## Never commit

- `backend/.env` or any file with a key, password or token (the `.gitignore` already blocks `.env`)
- The Supabase **service_role** key, anywhere, ever
- Large files (decks bigger than 1 MB, videos, screenshots over 500 KB)
- `backend/data/runtime/` (local data)

Committed a key by accident? Tell Warisha immediately. The key must be replaced; deleting the file does not remove it from history.

## Before every push

- Backend change: `cd backend && python -m pytest -q` must pass.
- Frontend change: open the page in the browser, press F12, look at the Console tab. It should have no red errors. Try it with and without demo data.
- Did you show any text from the API on the page? It must go through `ui.esc()` or `textContent`, never raw into `innerHTML`.

## Frontend rules

- Plain HTML, CSS and JavaScript. No build step, no frameworks, no npm install.
- Talk to the backend only through `frontend/js/api.js`. If you need a new call, add one function there, in the same style.
- Colours, spacing and fonts live in the `:root` block at the top of `frontend/css/base.css`. Change them there, not inline.
- Do not rename element `id`s without searching the page's script for them first.
- The data shapes are in `API-CONTRACT.md`. If the API does not give you something you need, open an issue labelled `backend`.

## Backend rules

- Everything has a test. A new endpoint or a bug fix needs one in `backend/tests/`. Copy an existing test.
- Do not edit `pipeline.py`, `scoring.py`, `prompts.py` or `rubric.default.json` without asking Warisha.
- Never send `founder_name`, `founder_email` or `organization` to the AI. A test checks this; do not remove it.

## Getting unstuck

1. Read the error message out loud. Most of them say what is wrong.
2. Browser: F12, Console and Network tabs. Backend: the terminal where `uvicorn` runs.
3. Search the repo (Ctrl+Shift+F in VS Code) for a word from the error.
4. Ask in the team chat. Include the file, what you did, and the exact error text or a screenshot. After 15 minutes of being stuck, always ask.

## Using AI coding tools (OpenCode, Antigravity, Lovable, others)

Allowed and encouraged, as the team agreed. Read `AGENTS.md`, which is written for them: give your tool that file first. You are still responsible for every line you commit: run it, read the diff before committing, and never paste a key into a tool's chat.
