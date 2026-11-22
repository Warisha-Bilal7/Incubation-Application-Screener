# Role guides

One guide per person. Your list of issues is generated from the same source as `MILESTONES-AND-ISSUES.md`, so they always match.

## Team

| Person | Role | GitHub username | Main area |
|---|---|---|---|
| Warisha | team lead, backend and AI | @Warisha-Bilal7 | Lead, backend, AI, deploy |
| Amir | frontend lead | @TODO | Frontend lead |
| Aruba | frontend, documentation and QA | @TODO | Frontend, docs, QA |
| Hafsa | slides, wording and accessibility | @TODO | Slides, wording, accessibility |
| Aliyan | backend, database and AI testing | @TODO | Backend, database, auth, AI testing |
| Hammad | backend features, tests, QA and demo video | @TODO | Backend features, tests, QA, demo video |

## Who asks whom

```
Frontend question  ->  Amir      ->  Warisha
Backend question   ->  Aliyan or Hammad  ->  Warisha
Slides or story    ->  Hafsa     ->  Warisha
Anything blocking ->  say it in the team chat right away
```

## Rules for everyone

1. Work on your own branch, open a pull request, never push to `main`. See `CONTRIBUTING.md` for the commands.
2. One issue at a time. Move to the next only when the pull request is open.
3. Never commit a key, a password or a `.env` file. If you do, tell Warisha immediately so the key is replaced.
4. Do not add features that are not in an issue. Ideas go in a GitHub issue labelled `stretch`.
5. If something takes longer than its estimate by half again, tell Warisha so the plan can adjust.
6. The hackathon is first a learning experience. Take the task that scares you a little.

---

## Warisha: team lead, backend and AI

**Mission.** Make the AI analysis trustworthy and the whole system ship. You are also the reviewer and merger of every pull request, so your own list is deliberately short on feature work.

**You own.** `backend/app/pipeline.py`, `scoring.py`, `prompts.py`, `grounding.py`, `backend/data/rubric.default.json`, deployment, the final demo.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-01` Create the GitHub repo, push the starter, protect main, invite the team · 20 min
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-03` Get a Gemini API key and run the Gemini check · 15 min
  - [ ] `SET-09` Deploy once to Render in mock mode (de-risk deployment tonight) · 30 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `BE-01` Verify the real Gemini pipeline end to end · 15 min
  - [ ] `BE-02` Finalise the rubric with the team · 20 min
- *M2 Core build*
  - [ ] `AI-01` Run real Gemini on all 12 demo applicants and read every scorecard · 30 min
  - [ ] `AI-02` Tune the prompt and rubric anchors until the eval checks pass · 45 min
- *M3 Integration and trust*
  - [ ] `BE-05` Review scoring wording and the time-saved assumptions · 15 min
- *M4 Debugging*
  - [ ] `SEC-01` Run the security checklist · 20 min
- *M5 Deploy and rehearsal*
  - [ ] `DEP-01` Final production deploy on Render · 20 min
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min
  - [ ] `DEMO-02` Code freeze and release tag · 5 min

Total planned: 3h55 of work, plus shared issues.

**Rules for you.**

- Protect your time: Aliyan and Hammad take backend questions first, Amir takes frontend questions first.
- Review pull requests within 10 minutes of being asked. A small PR merged now beats a perfect one merged at the end.
- You are the only person who changes the prompt, the rubric weights or the scoring thresholds. Everyone else suggests.
- Call the freeze (DEMO-02) on time even if something is unfinished.

**When you are stuck.** You are the escalation point. Decide quickly and write the decision in docs/DEV-LOG.md.

---

## Amir: frontend lead

**Mission.** Make the app look and feel like a product a startup programme would actually use. The dashboard and detail page are what the judges will stare at, so they get your best hours.

**You own.** `frontend/css/base.css`, `frontend/dashboard.html`, `frontend/application.html`, `frontend/login.html`, `frontend/rubric.html` (stretch), `frontend/js/api.js`.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-06` Run the project and read the API contract · 30 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `FE-01` Choose the look and feel and apply it to every page · 30 min
- *M2 Core build*
  - [ ] `FE-04` Polish the dashboard · 60 min
  - [ ] `FE-05` Polish the application detail page · 45 min
- *M3 Integration and trust*
  - [ ] `FE-08` Stretch: reviewer login page · 45 min
  - [ ] `FE-10` Stretch: How we score page · 30 min
- *M4 Debugging*
  - [ ] `QA-05` Fix the UI bugs · 30 min
- *M5 Deploy and rehearsal*
  - [ ] `DEP-03` Optional: host the frontend on Hostinger · 20 min
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min

Total planned: 4h50 of work, plus shared issues.

**Rules for you.**

- Never change the shape of an API call yourself. If you need something from the backend, open an issue labelled backend and tag Warisha.
- Never write text a user typed into `innerHTML` without `ui.esc()` (applicant text is untrusted; this was tested).
- The service_role Supabase key must never appear in any frontend file. Only the anon key may.
- Aruba and Hafsa are learning frontend with you: give each a small, well-defined task and review their pull requests kindly.

**When you are stuck.** Stuck on layout for more than 15 minutes? Ask Aruba to pair on it. Stuck on an API shape? Read API-CONTRACT.md, then ask Warisha.

---

## Aruba: frontend, documentation and QA

**Mission.** Learn real frontend and API integration by building the apply form and landing page, then become the person who makes sure the docs and the final submission are excellent. Documentation is as important as code.

**You own.** `frontend/index.html`, `frontend/apply.html`, `docs/DEV-LOG.md`, `docs/HOW-IT-WORKS.md`, `README.md`, the hackathon submission.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-07` Practise the Git workflow with a tiny pull request · 30 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `FE-02` Write the landing page (index.html) · 30 min
  - [ ] `DOC-01` Start the dev log · 10 min
- *M2 Core build*
  - [ ] `FE-06` Apply form: validation, errors and success state · 45 min
  - [ ] `DOC-02` Review and finish docs/HOW-IT-WORKS.md for judges · 20 min
- *M3 Integration and trust*
  - [ ] `FE-09` Stretch: blind review remembers the choice and shows a clear banner · 25 min
- *M4 Debugging*
  - [ ] `QA-04` Phone and laptop UI pass · 30 min
  - [ ] `DOC-04` Finish the README · 15 min
- *M5 Deploy and rehearsal*
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min
  - [ ] `DOC-05` Submit the project on the hackathon page · 15 min

Total planned: 3h40 of work, plus shared issues.

**Rules for you.**

- Work only on your own branch and open a pull request for every issue. Never push to main.
- Test with `ui.esc()` in mind: if you show text from the API in the page, escape it.
- Use the browser DevTools (F12) Console and Network tabs when something fails. Read the red text out loud to Amir.
- Write the dev log as you go, not at the end.

**When you are stuck.** First time with HTML, CSS and JavaScript is completely fine. Ask Amir early. Say 'I do not understand this' without apologising.

---

## Hafsa: slides, wording and accessibility

**Mission.** Own the story the judges hear. A clean 10-slide deck in the Y Combinator style (problem, solution, market, business model, team) can matter as much as the code, because three of the five judges work in startups.

**You own.** The slide deck, the slide text in `DEMO-AND-PITCH.md`, the wording in `frontend/apply.html`, the accessibility pass, the screenshots in `docs/img/`.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-08` Create the slide deck skeleton and share the edit link · 30 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `FE-03` Improve the wording on the apply form · 20 min
  - [ ] `SLD-01` Slide draft 1: all 10 slides with text · 30 min
- *M2 Core build*
  - [ ] `FE-07` Accessibility pass on all pages · 20 min
  - [ ] `SLD-02` Slide draft 2: add the business model and market slides properly · 35 min
- *M3 Integration and trust*
  - [ ] `DOC-03` Take screenshots for the slides and the README · 20 min
  - [ ] `SLD-03` Slide draft 3: screenshots in and timing · 30 min
- *M5 Deploy and rehearsal*
  - [ ] `SLD-04` Final deck export and offline copy · 20 min
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min

Total planned: 3h25 of work, plus shared issues.

**Rules for you.**

- No more than about 30 words per slide. Big text, plain background, one idea per slide.
- Every number on a slide must come from SCOPE.md, docs/EVAL-RESULTS.md or be labelled as an assumption.
- Do not claim the product has customers, pilots or results it does not have.
- When you change HTML, work on your own branch and open a pull request.

**When you are stuck.** Not sure a claim is true? Ask Warisha before it goes on a slide.

---

## Aliyan: backend, database and AI testing

**Mission.** Make storage and failure handling solid, and add reviewer login if time allows. You are Warisha's second pair of hands on the backend and the person who proves it works with Supabase and with real PDFs.

**You own.** Supabase project and tables, `backend/app/store/supabase.py`, `backend/app/auth.py`, the failure-handling tests, production data.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-04` Create the Supabase project and run the schema · 20 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `DB-01` Connect the backend to Supabase and prove one submission lands in the table · 25 min
- *M2 Core build*
  - [ ] `AI-03` Test the PDF path with real Gemini and real decks · 30 min
  - [ ] `DB-02` Seed Supabase with the demo set and prove persistence · 30 min
- *M3 Integration and trust*
  - [ ] `BE-04` Stretch: turn on reviewer login with Supabase auth and test it · 30 min
  - [ ] `AI-04` Prove Gemini failures are handled gracefully · 30 min
- *M4 Debugging*
  - [ ] `QA-06` Fix the backend bugs · 30 min
- *M5 Deploy and rehearsal*
  - [ ] `DEP-02` Seed production and verify the demo data · 15 min
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min

Total planned: 3h30 of work, plus shared issues.

**Rules for you.**

- The Supabase service_role key goes in backend/.env and Render environment variables only. Never in the repo, never in the frontend.
- Row Level Security stays ON for both tables.
- Change `pipeline.py`, `scoring.py` or `prompts.py` only after asking Warisha.
- Add a test for every bug you fix.

**When you are stuck.** If Supabase errors are confusing, copy the exact error into the dev log and ask Warisha: the store raises readable messages that include the HTTP status.

---

## Hammad: backend features, tests, QA and demo video

**Mission.** Add a small real backend feature (the interview brief), grow the test suite, and be the person who breaks the app on purpose before the judges do.

**You own.** `backend/app/brief.py` (new), the brief button on `frontend/application.html`, `backend/tests/`, `backend/data/demo_applicants.json` (edge cases), `docs/EVAL-RESULTS.md`, the backup demo video.

**Your issues, in order:**

- *M0 Prep (tonight)*
  - [ ] `SET-02` Send your GitHub username to Warisha (meeting action item) (everyone) · 5 min
  - [ ] `SET-05` Get the backend running on your laptop · 30 min
  - [ ] `SET-10` Bring list and readiness check (everyone) · 15 min
- *M1 Foundations*
  - [ ] `QA-01` Write three new backend tests · 30 min
- *M2 Core build*
  - [ ] `BE-03` Add the interview brief endpoint · 45 min
- *M3 Integration and trust*
  - [ ] `FE-11` Stretch: download interview brief button · 25 min
  - [ ] `AI-05` Add 3 edge-case demo applicants · 25 min
  - [ ] `QA-02` Record the final eval numbers · 20 min
- *M4 Debugging*
  - [ ] `QA-03` Backend bug bash with odd inputs · 35 min
- *M5 Deploy and rehearsal*
  - [ ] `DEP-04` Record a 90-second backup demo video · 20 min
  - [ ] `DEMO-01` Two timed rehearsals and the Q and A drill (everyone) · 30 min

Total planned: 3h50 of work, plus shared issues.

**Rules for you.**

- Read two existing tests before writing yours; copy the style.
- A test that fails is information, not embarrassment. Tell Warisha what failed and what you expected.
- Run `python -m pytest -q` before every push.
- When you find a bug, make a GitHub issue with the exact input that caused it.

**When you are stuck.** Stuck on Python errors? Paste the last 10 lines of the error to Aliyan first, then Warisha.
