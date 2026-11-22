# Milestones and issues

Everything the team does is one of these issues. `scripts/create_issues.sh` turns this file's source (`scripts/issues.tsv`) into real GitHub issues, milestones, labels and assignees.

**T+0:00** is the moment you sit down at the venue and start building. You have **4 hours**. Times below are relative to that.

## How we work (from the planning meeting)

- Milestone by milestone, issue by issue. One branch per issue: `name/code` (for example `amir/fe-04`).
- Open a pull request when the issue is done. Warisha reviews and merges. Write `Closes #n` in the PR so the issue closes itself.
- Debugging is a milestone of its own (M4), and deployment is the one after it (M5). Nothing new is added in M4 or M5.
- If you are stuck for more than 15 minutes, say so in the team chat. Asking early is the job, not a failure.

## Timeline

| Milestone | When | Goal |
|---|---|---|
| M0 Prep (tonight) | Tonight | Before the venue. Accounts, keys, repo access, local run, first Render deploy. |
| M1 Foundations | T+0:00 to 0:30 | Everyone runs the app locally, the real Gemini call works, rubric agreed, look and feel chosen. |
| M2 Core build | T+0:30 to 1:45 | Real AI analysis tuned on demo data, polished apply/dashboard/detail pages, Supabase storage verified. |
| M3 Integration and trust | T+1:45 to 2:45 | Reviewer login, blind review, interview brief, failure handling, eval numbers, slides complete. |
| M4 Debugging | T+2:45 to 3:20 | Bug bash, fixes, security checklist, README. Nothing new gets added here. |
| M5 Deploy and rehearsal | T+3:20 to 4:00 | Final deploy, seeded data, backup video, two timed rehearsals, code freeze. |

## Load per person

The build window is 240 minutes. Planned work should stay well under that so there is room for reviews, waiting and debugging.

| Person | Tonight (M0) | Build window (M1 to M5, core) | Stretch | Main area |
|---|---|---|---|---|
| Warisha | 1h05 | 2h50 | - | Lead, backend, AI, deploy |
| Amir | 30 min | 2h45 | 1h35 | Frontend lead |
| Aruba | 30 min | 2h45 | 25 min | Frontend, docs, QA |
| Hafsa | 30 min | 2h55 | - | Slides, wording, accessibility |
| Aliyan | 20 min | 2h40 | 30 min | Backend, database, auth, AI testing |
| Hammad | 30 min | 2h55 | 25 min | Backend features, tests, QA, demo video |
| Everyone | 20 min | 30 min | - | Whole team |

Planned work is an estimate, not a promise. Pull request reviews, waiting for each other and debugging come on top. If you fall behind, drop issues in the order given in the cut line in SCOPE.md. Stretch issues are only started when everything else on your list is merged.

## M0 Prep (tonight)  (Tonight)

Before the venue. Accounts, keys, repo access, local run, first Render deploy.

Planned work in this milestone: 3h45 across 10 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `SET-01` | Create the GitHub repo, push the starter, protect main, invite the team | Warisha | 20 min | - |
| `SET-02` | Send your GitHub username to Warisha (meeting action item) | Everyone | 5 min | - |
| `SET-03` | Get a Gemini API key and run the Gemini check | Warisha | 15 min | - |
| `SET-04` | Create the Supabase project and run the schema | Aliyan | 20 min | - |
| `SET-05` | Get the backend running on your laptop | Hammad | 30 min | - |
| `SET-06` | Run the project and read the API contract | Amir | 30 min | - |
| `SET-07` | Practise the Git workflow with a tiny pull request | Aruba | 30 min | - |
| `SET-08` | Create the slide deck skeleton and share the edit link | Hafsa | 30 min | - |
| `SET-09` | Deploy once to Render in mock mode (de-risk deployment tonight) | Warisha | 30 min | - |
| `SET-10` | Bring list and readiness check | Everyone | 15 min | - |

### SET-01  Create the GitHub repo, push the starter, protect main, invite the team

**Owner:** Warisha · **Estimate:** 20 min · **Labels:** setup

**Do:** Create a repo (suggested name: shortlist). In the project folder: git init, git add ., git commit, git remote add origin <url>, git push -u origin main. Settings > Branches: require a pull request before merging into main. Settings > Collaborators: add all five usernames. Copy scripts/team.env.example to scripts/team.env, fill the usernames, then run: bash scripts/create_issues.sh

**Done when:** All five teammates can clone. Every issue in MILESTONES-AND-ISSUES.md exists on GitHub with its milestone, labels and assignee. main requires a PR.

### SET-02  Send your GitHub username to Warisha (meeting action item)

**Owner:** Everyone · **Estimate:** 5 min · **Labels:** setup

**Do:** Message your GitHub username to Warisha in the team chat. If you do not have an account yet, create one at github.com and enable 2-factor sign-in.

**Done when:** Warisha has your username and has added you as a collaborator.

### SET-03  Get a Gemini API key and run the Gemini check

**Owner:** Warisha · **Estimate:** 15 min · **Labels:** ai,setup

**Do:** Open https://aistudio.google.com/apikey and create a key. Copy backend/.env.example to backend/.env and paste it as GEMINI_API_KEY. Run: cd backend and then python ../scripts/check_gemini.py. If the model test fails, use the model name the script suggests as GEMINI_MODEL. Aliyan and Hammad should each create their OWN free key so quota is not shared.

**Done when:** check_gemini.py prints PASS. GEMINI_MODEL in backend/.env is a model your key can call. The key is in .env only and was never committed or pasted in a public place.

### SET-04  Create the Supabase project and run the schema

**Owner:** Aliyan · **Estimate:** 20 min · **Labels:** database,setup

**Do:** At supabase.com create a new project. SQL Editor > New query > paste backend/data/schema.sql > Run. Project Settings > API: copy the Project URL, the anon key and the service_role key. Send them privately to Warisha. The service_role key must NEVER go into the frontend or the repo.

**Done when:** Tables applications and settings exist in Table Editor, both with RLS enabled. Warisha has URL, anon key and service_role key.

### SET-05  Get the backend running on your laptop

**Owner:** Hammad · **Estimate:** 30 min · **Labels:** setup,backend

**Do:** Install Python 3.11 or newer and git. Then: git clone <repo>, cd shortlist/backend, python -m venv .venv, activate it, pip install -r requirements.txt, python -m pytest -q, then uvicorn app.main:app --reload. Open http://localhost:8000 and click Reviewer dashboard, then Load demo data.

**Done when:** All tests pass on your machine and you can see 12 demo applicants ranked on the dashboard. Post a screenshot in the team chat.

### SET-06  Run the project and read the API contract

**Owner:** Amir · **Estimate:** 30 min · **Labels:** setup,frontend

**Do:** Run the backend as in SET-05 (the backend serves the frontend folder at http://localhost:8000). Read API-CONTRACT.md fully. Open each page and note what you want to change. Decide the look: colours, font, product feel. Sketch the dashboard layout on paper.

**Done when:** You can run everything locally and have a short design direction (3 to 5 bullet points) posted in the team chat.

### SET-07  Practise the Git workflow with a tiny pull request

**Owner:** Aruba · **Estimate:** 30 min · **Labels:** setup

**Do:** Install VS Code and git. Clone the repo. Create a branch: git checkout -b aruba/hello. Add your GitHub username to the team table in ROLE-GUIDES.md, then git add, git commit -m, git push -u origin aruba/hello, and open a pull request on GitHub. Read CONTRIBUTING.md first.

**Done when:** Your pull request is merged by Warisha. You can explain branch, commit, push and pull request in one sentence each.

### SET-08  Create the slide deck skeleton and share the edit link

**Owner:** Hafsa · **Estimate:** 30 min · **Labels:** slides,setup

**Do:** Create a deck in Google Slides or Canva (a plain white or dark background, big text). Add 10 empty slides titled exactly as in the slide list in DEMO-AND-PITCH.md. Share the edit link with the team.

**Done when:** A shared deck with 10 titled slides exists. Everyone on the team can edit it.

### SET-09  Deploy once to Render in mock mode (de-risk deployment tonight)

**Owner:** Warisha · **Estimate:** 30 min · **Labels:** deploy,setup

**Do:** Render dashboard > New > Blueprint > pick the repo (render.yaml is at the root). Leave AI_MODE=mock for now. Open the URL, check /api/health, then open the home page. Wait 20 minutes and open it again to see how long the free instance takes to wake up. Write the cold start time in docs/DEV-LOG.md.

**Done when:** The live URL serves the home page and /api/health. You know the cold-start time.

### SET-10  Bring list and readiness check

**Owner:** Everyone · **Estimate:** 15 min · **Labels:** setup

**Do:** Laptop and charger, power strip if you can, phone hotspot as a backup for venue Wi-Fi, repo cloned with tests passing, VS Code, and you are logged in to GitHub, Supabase, Render and Google AI Studio as relevant to your role. Sleep.

**Done when:** You can run the app locally with no internet except for installing packages.

## M1 Foundations  (T+0:00 to 0:30)

Everyone runs the app locally, the real Gemini call works, rubric agreed, look and feel chosen.

Planned work in this milestone: 3h30 across 9 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `BE-01` | Verify the real Gemini pipeline end to end | Warisha | 15 min | SET-03 |
| `BE-02` | Finalise the rubric with the team | Warisha | 20 min | - |
| `DB-01` | Connect the backend to Supabase and prove one submission lands in the table | Aliyan | 25 min | SET-04 |
| `FE-01` | Choose the look and feel and apply it to every page | Amir | 30 min | SET-06 |
| `FE-02` | Write the landing page (index.html) | Aruba | 30 min | SET-07 |
| `FE-03` | Improve the wording on the apply form | Hafsa | 20 min | SET-07 |
| `QA-01` | Write three new backend tests | Hammad | 30 min | SET-05 |
| `DOC-01` | Start the dev log | Aruba | 10 min | SET-07 |
| `SLD-01` | Slide draft 1: all 10 slides with text | Hafsa | 30 min | SET-08 |

### BE-01  Verify the real Gemini pipeline end to end

**Owner:** Warisha · **Estimate:** 15 min · **Labels:** backend,ai · **Depends on:** SET-03

**Do:** In backend/.env set AI_MODE=gemini (or leave auto with the key set). Run: python ../scripts/run_eval.py --limit 3. Then start the server and submit one application with sample_deck.pdf from backend/data/. Note the model name and median latency in docs/DEV-LOG.md.

**Done when:** Three applicants are analysed by Gemini without errors, one PDF-backed submission completes, and the dashboard no longer shows the MOCK badge.

### BE-02  Finalise the rubric with the team

**Owner:** Warisha · **Estimate:** 20 min · **Labels:** backend,ai

**Do:** Edit backend/data/rubric.default.json: criteria, weights and the 1, 3, 5 anchors. Base it on what real incubator reviewers look for. Weights must sum to 100. If you change the NUMBER of criteria, update test_default_rubric_weights_sum_to_100 in backend/tests/test_core.py and the 7 in test_api.py and test_core.py.

**Done when:** pytest passes. Every criterion has anchors for 1, 3 and 5. The team has seen the final rubric.

### DB-01  Connect the backend to Supabase and prove one submission lands in the table

**Owner:** Aliyan · **Estimate:** 25 min · **Labels:** database,backend · **Depends on:** SET-04

**Do:** In backend/.env set STORE_BACKEND=supabase, SUPABASE_URL and SUPABASE_SERVICE_KEY. Start the server, submit an application at /apply.html, then open Table Editor > applications and look at the row. Stop and restart the server and confirm the application is still listed on the dashboard.

**Done when:** A row exists in Supabase with status done after analysis. The dashboard still shows it after a restart. Write any error you hit and its fix in docs/DEV-LOG.md.

### FE-01  Choose the look and feel and apply it to every page

**Owner:** Amir · **Estimate:** 30 min · **Labels:** frontend · **Depends on:** SET-06

**Do:** Edit the :root tokens at the top of frontend/css/base.css (colours, radius, font). Put the final product name and a simple text logo in the header of all four pages. Add a favicon. Do not rename element ids that the scripts use (they start with a hash selector in each page script).

**Done when:** All four pages share one consistent look and the header matches. Pull request merged.

### FE-02  Write the landing page (index.html)

**Owner:** Aruba · **Estimate:** 30 min · **Labels:** frontend · **Depends on:** SET-07

**Do:** In frontend/index.html add: a headline, a short subtitle, three steps (Submit, AI scorecard with evidence, A person decides), and a Responsible AI box that says: applicant identity is hidden from the AI, every score shows an evidence quote you can check, people make every decision.

**Done when:** The landing page explains the product in 10 seconds to someone who has never heard of it. Pull request merged.

### FE-03  Improve the wording on the apply form

**Owner:** Hafsa · **Estimate:** 20 min · **Labels:** frontend,docs · **Depends on:** SET-07

**Do:** In frontend/apply.html make every label and hint clear for a first-time founder. Add placeholder text with a realistic example for each field (look at backend/data/demo_applicants.json for style). Check spelling. Do not change the id or name attributes.

**Done when:** A founder could fill the form without asking anyone what a field means. Pull request merged.

### QA-01  Write three new backend tests

**Owner:** Hammad · **Estimate:** 30 min · **Labels:** qa,backend · **Depends on:** SET-05

**Do:** Open backend/tests/test_api.py and read two existing tests. Add: (1) a problem text longer than 4000 characters returns 422, (2) an invalid priority filter value on GET /api/applications returns 422, (3) GET /api/applications/<id>/deck for an application with no deck returns 404. Run python -m pytest -q.

**Done when:** Running python -m pytest -q shows 3 more passed tests than before you started (write down the before and after numbers). Pull request merged.

### DOC-01  Start the dev log

**Owner:** Aruba · **Estimate:** 10 min · **Labels:** docs · **Depends on:** SET-07

**Do:** Create docs/DEV-LOG.md. Add one line per decision with the time, for example: 10:35 Backend is Python FastAPI, not PHP, because the Gemini SDK and PDF handling are first-class in Python. Keep adding lines until the end of the day. This becomes the evidence of how the team worked.

**Done when:** The file exists with at least 4 entries by the end of M1.

### SLD-01  Slide draft 1: all 10 slides with text

**Owner:** Hafsa · **Estimate:** 30 min · **Labels:** slides · **Depends on:** SET-08

**Do:** DEMO-AND-PITCH.md already contains draft text for every slide. Copy it into the deck, rewrite it in your own words, and cut it to about 30 words per slide. Take numbers and claims only from SCOPE.md and DEMO-AND-PITCH.md and mark assumptions as assumptions. Leave screenshot boxes empty for now.

**Done when:** All 10 slides have text. Warisha has read it once.

## M2 Core build  (T+0:30 to 1:45)

Real AI analysis tuned on demo data, polished apply/dashboard/detail pages, Supabase storage verified.

Planned work in this milestone: 6h45 across 11 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `AI-01` | Run real Gemini on all 12 demo applicants and read every scorecard | Warisha | 30 min | BE-01, BE-02 |
| `AI-02` | Tune the prompt and rubric anchors until the eval checks pass | Warisha | 45 min | AI-01 |
| `AI-03` | Test the PDF path with real Gemini and real decks | Aliyan | 30 min | BE-01 |
| `BE-03` | Add the interview brief endpoint | Hammad | 45 min | SET-05 |
| `FE-04` | Polish the dashboard | Amir | 60 min | FE-01 |
| `FE-05` | Polish the application detail page | Amir | 45 min | FE-01 |
| `FE-06` | Apply form: validation, errors and success state | Aruba | 45 min | FE-03 |
| `FE-07` | Accessibility pass on all pages | Hafsa | 20 min | FE-03 |
| `DB-02` | Seed Supabase with the demo set and prove persistence | Aliyan | 30 min | DB-01, BE-01 |
| `DOC-02` | Review and finish docs/HOW-IT-WORKS.md for judges | Aruba | 20 min | BE-02 |
| `SLD-02` | Slide draft 2: add the business model and market slides properly | Hafsa | 35 min | SLD-01 |

### AI-01  Run real Gemini on all 12 demo applicants and read every scorecard

**Owner:** Warisha · **Estimate:** 30 min · **Labels:** ai · **Depends on:** BE-01, BE-02

**Do:** Run python ../scripts/run_eval.py and then open the dashboard with demo data analysed by Gemini. Read each scorecard. Write the problems you see in docs/DEV-LOG.md: scores too generous or too harsh, unverified quotes, vague reasoning, wrong tier ordering.

**Done when:** A written list of at most 5 concrete problems with the example application for each.

### AI-02  Tune the prompt and rubric anchors until the eval checks pass

**Owner:** Warisha · **Estimate:** 45 min · **Labels:** ai · **Depends on:** AI-01

**Do:** Edit backend/app/prompts.py (SYSTEM text) and the anchors in backend/data/rubric.default.json. Change one thing at a time and re-run scripts/run_eval.py. Stop after three rounds. The three checks are: strong beats weak, injection test is flagged and not high priority, unverified quotes under 10 percent.

**Done when:** The three eval checks pass, or you have written down honestly which one does not and why. Final numbers are saved for QA-02.

### AI-03  Test the PDF path with real Gemini and real decks

**Owner:** Aliyan · **Estimate:** 30 min · **Labels:** ai,qa · **Depends on:** BE-01

**Do:** Upload backend/data/sample_deck.pdf and two other decks (your own made-up decks or public-domain ones) through /apply.html with Gemini on. Check that Gemini mentions content from the deck and that quotes from the deck are marked verified. Note: slides that are only images have no text, so their quotes cannot be verified. That is expected: write it in the dev log.

**Done when:** Three PDF-backed submissions are analysed. Any failure is logged as a GitHub issue with the file and the error.

### BE-03  Add the interview brief endpoint

**Owner:** Hammad · **Estimate:** 45 min · **Labels:** backend · **Depends on:** SET-05

**Do:** Create backend/app/brief.py with build_brief(application) that returns a Markdown string: startup name and one-liner, score and priority, riskiest assumptions, suggested interview questions, red flags, missing info. Add GET /api/applications/{app_id}/brief in backend/app/main.py (reviewer only, returns text/markdown, 404 if no evaluation yet). Add two tests in tests/test_api.py.

**Done when:** Calling the endpoint on a demo application returns a readable one-page Markdown brief. Tests pass. Pull request merged.

### FE-04  Polish the dashboard

**Owner:** Amir · **Estimate:** 60 min · **Labels:** frontend · **Depends on:** FE-01

**Do:** In frontend/dashboard.html: score bars in the table, sticky header, good empty and loading states, card layout on phones, readable stats strip. Keep the polling that refreshes while applications are analysing. Test with 12 demo applicants and with 0.

**Done when:** The dashboard looks finished on a laptop and a phone and still polls correctly. Pull request merged.

### FE-05  Polish the application detail page

**Owner:** Amir · **Estimate:** 45 min · **Labels:** frontend · **Depends on:** FE-01

**Do:** In frontend/application.html: make the scorecard the hero (a bar per criterion), make verified and unverified evidence quotes visually clear, keep the decision form simple. Red flags and the injection warning must stay prominent.

**Done when:** A judge can read one application in 20 seconds and see why it scored what it did. Pull request merged.

### FE-06  Apply form: validation, errors and success state

**Owner:** Aruba · **Estimate:** 45 min · **Labels:** frontend · **Depends on:** FE-03

**Do:** In frontend/apply.html show a message next to any field that is empty or too short before submitting (the backend minimums are in API-CONTRACT.md). Show character counters for the long text fields. Keep the loading state on the button. Never use innerHTML with text the user typed.

**Done when:** Submitting a broken form shows helpful messages and does not call the API. A good submission shows the reference id. Pull request merged.

### FE-07  Accessibility pass on all pages

**Owner:** Hafsa · **Estimate:** 20 min · **Labels:** frontend,qa · **Depends on:** FE-03

**Do:** Check every page: every input has a label, buttons can be reached with the Tab key, focus is visible, colour contrast is readable, the page works at 200 percent zoom. Fix small issues in HTML and CSS and list bigger ones as GitHub issues for Amir.

**Done when:** A short list of fixes made and issues opened. Pull request merged.

### DB-02  Seed Supabase with the demo set and prove persistence

**Owner:** Aliyan · **Estimate:** 30 min · **Labels:** database · **Depends on:** DB-01, BE-01

**Do:** With STORE_BACKEND=supabase and AI_MODE=gemini run the server and click Load demo data on the dashboard (or POST /api/dev/seed). Wait until all 12 are done. Restart the server. Check that all 12 still show with scores. Export the table as CSV from Supabase as a backup.

**Done when:** 12 analysed applications live in Supabase and survive a restart. A CSV backup is saved outside the repo.

### DOC-02  Review and finish docs/HOW-IT-WORKS.md for judges

**Owner:** Aruba · **Estimate:** 20 min · **Labels:** docs · **Depends on:** BE-02

**Do:** A draft already exists in docs/HOW-IT-WORKS.md. Read it slowly. Check every claim against the running app (does blind mode really hide the name? do unverified quotes really show a warning?). Fix anything untrue, simplify the wording for a non-technical judge, and add a simple pipeline picture made in Excalidraw or draw.io saved as docs/img/pipeline.png.

**Done when:** Every sentence in the document is true of the app as it runs today. A non-technical judge can read it in 3 minutes. Pull request merged.

### SLD-02  Slide draft 2: add the business model and market slides properly

**Owner:** Hafsa · **Estimate:** 35 min · **Labels:** slides · **Depends on:** SLD-01

**Do:** Use the numbers in SCOPE.md under Business model. Show them as assumptions with a label. Add one slide that shows the problem in terms the judges know: reading hundreds of applications by hand. Keep the NIC advice: do not overload slides.

**Done when:** The business model slide states who pays, how much (as an assumption) and why. Warisha has reviewed it.

## M3 Integration and trust  (T+1:45 to 2:45)

Reviewer login, blind review, interview brief, failure handling, eval numbers, slides complete.

Planned work in this milestone: 4h55 across 11 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `BE-04` | Stretch: turn on reviewer login with Supabase auth and test it | Aliyan | 30 min | DB-01 |
| `FE-08` | Stretch: reviewer login page | Amir | 45 min | BE-04 |
| `FE-09` | Stretch: blind review remembers the choice and shows a clear banner | Aruba | 25 min | FE-04 |
| `FE-10` | Stretch: How we score page | Amir | 30 min | FE-01 |
| `FE-11` | Stretch: download interview brief button | Hammad | 25 min | BE-03 |
| `AI-04` | Prove Gemini failures are handled gracefully | Aliyan | 30 min | BE-01 |
| `AI-05` | Add 3 edge-case demo applicants | Hammad | 25 min | QA-01 |
| `QA-02` | Record the final eval numbers | Hammad | 20 min | AI-02 |
| `BE-05` | Review scoring wording and the time-saved assumptions | Warisha | 15 min | AI-02 |
| `DOC-03` | Take screenshots for the slides and the README | Hafsa | 20 min | FE-04, FE-05 |
| `SLD-03` | Slide draft 3: screenshots in and timing | Hafsa | 30 min | SLD-02, DOC-03 |

### BE-04  Stretch: turn on reviewer login with Supabase auth and test it

**Owner:** Aliyan · **Estimate:** 30 min · **Labels:** backend,security,stretch · **Depends on:** DB-01

**Do:** In Supabase: Authentication > Users > Add user (email and password) for two reviewers. In backend/.env set AUTH_MODE=supabase, SUPABASE_ANON_KEY and REVIEWER_EMAILS=comma separated emails. Get a token with: curl -X POST SUPABASE_URL/auth/v1/token?grant_type=password with header apikey set to the anon key and JSON body email and password. Call GET /api/applications with header Authorization: Bearer <access_token>.

**Done when:** 200 with a listed reviewer token, 401 with no token, 403 with a valid Supabase user whose email is not in REVIEWER_EMAILS. Steps written into DEPLOYMENT-CHECKLIST.md.

### FE-08  Stretch: reviewer login page

**Owner:** Amir · **Estimate:** 45 min · **Labels:** frontend,security,stretch · **Depends on:** BE-04

**Do:** Create frontend/login.html using supabase-js from a pinned CDN version. On success store the access token in sessionStorage and make api.js send it as Authorization: Bearer. If a page gets 401 it redirects to login.html. Keep the existing reviewer-key prompt as the fallback when the server runs AUTH_MODE=key.

**Done when:** In supabase mode the dashboard is only reachable after login. A wrong password shows a clear error. Logout works.

### FE-09  Stretch: blind review remembers the choice and shows a clear banner

**Owner:** Aruba · **Estimate:** 25 min · **Labels:** frontend,stretch · **Depends on:** FE-04

**Do:** Persist the blind checkbox in sessionStorage so it survives navigation. When blind is on show a banner on the detail page: Applicant identity is hidden for fair review. Make sure the dashboard links carry the blind flag.

**Done when:** Turn blind on, open any application, the name and email are hidden and the banner is visible. Pull request merged.

### FE-10  Stretch: How we score page

**Owner:** Amir · **Estimate:** 30 min · **Labels:** frontend,stretch · **Depends on:** FE-01

**Do:** Create frontend/rubric.html that reads GET /api/rubric and shows each criterion with its weight and the 1, 3, 5 anchors. Add a short note that the AI never sees names and that people decide. Link it from the header.

**Done when:** Judges can see exactly what we score and how it is weighted.

### FE-11  Stretch: download interview brief button

**Owner:** Hammad · **Estimate:** 25 min · **Labels:** frontend,stretch · **Depends on:** BE-03

**Do:** On frontend/application.html add a button that fetches /api/applications/{id}/brief with the auth headers (copy the openBlob pattern in frontend/js/api.js) and downloads it as a .md file.

**Done when:** Clicking the button downloads a readable brief for a demo application.

### AI-04  Prove Gemini failures are handled gracefully

**Owner:** Aliyan · **Estimate:** 30 min · **Labels:** ai,backend · **Depends on:** BE-01

**Do:** Run the server with a wrong GEMINI_API_KEY and submit an application. It must end in status failed with a readable error, and the Retry button on the detail page must work after you put the right key back. Also try submitting 5 applications quickly and watch for 429 quota errors. Write what you saw and any change you made in the dev log.

**Done when:** No crash, no application stuck forever in analyzing, and the retry works. If a stuck one is possible, write it in the known issues list.

### AI-05  Add 3 edge-case demo applicants

**Owner:** Hammad · **Estimate:** 25 min · **Labels:** ai,qa · **Depends on:** QA-01

**Do:** Add three entries to backend/data/demo_applicants.json: (1) an application written in Urdu or Roman Urdu, (2) a very long rambling one, (3) one whose text mentions the founder gender and university in the free text. Then make the tests that hard-code the number 12 use len(load_demo_applications()) instead (search for 12 in tests/test_api.py). Run the eval and record how the AI treats each one.

**Done when:** Tests pass with 15 demo applicants. The dev log says honestly how the AI handled each edge case.

### QA-02  Record the final eval numbers

**Owner:** Hammad · **Estimate:** 20 min · **Labels:** qa,ai · **Depends on:** AI-02

**Do:** After AI-02 is merged run python ../scripts/run_eval.py --csv eval.csv. Create docs/EVAL-RESULTS.md with the date, the model name, the table of scores, which checks passed and the median latency. Do not round up or leave out failures.

**Done when:** docs/EVAL-RESULTS.md exists and matches the real output.

### BE-05  Review scoring wording and the time-saved assumptions

**Owner:** Warisha · **Estimate:** 15 min · **Labels:** backend,ai · **Depends on:** AI-02

**Do:** Check that no screen or endpoint says accept or reject: only priority and the human decision. Replace ASSUMED_MANUAL_MINUTES and ASSUMED_CARD_MINUTES in backend/.env with the numbers you actually saw at NIC (how long a reviewer spends per application), or remove the time-saved tile. Re-check the 70 and 45 priority thresholds against the eval scores.

**Done when:** Language is consistent and every number shown to judges is either measured or labelled as an assumption.

### DOC-03  Take screenshots for the slides and the README

**Owner:** Hafsa · **Estimate:** 20 min · **Labels:** docs,slides · **Depends on:** FE-04, FE-05

**Do:** Once FE-04 and FE-05 are merged take clean screenshots of the dashboard, a detail page, blind mode and the apply page (demo data loaded, no MOCK badge). Save them in docs/img/ (PNG, under 500 KB each) and open a pull request so Aruba can use them in the README.

**Done when:** Four named screenshots in docs/img/, merged.

### SLD-03  Slide draft 3: screenshots in and timing

**Owner:** Hafsa · **Estimate:** 30 min · **Labels:** slides · **Depends on:** SLD-02, DOC-03

**Do:** Place the screenshots, trim words, and add the single most convincing number from docs/EVAL-RESULTS.md. Time a read-through with Warisha: the whole pitch must fit the time the organisers give.

**Done when:** The deck is complete and a full read-through is under the time limit.

## M4 Debugging  (T+2:45 to 3:20)

Bug bash, fixes, security checklist, README. Nothing new gets added here.

Planned work in this milestone: 2h40 across 6 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `QA-03` | Backend bug bash with odd inputs | Hammad | 35 min | BE-05 |
| `QA-04` | Phone and laptop UI pass | Aruba | 30 min | FE-04, FE-05 |
| `QA-05` | Fix the UI bugs | Amir | 30 min | QA-04 |
| `QA-06` | Fix the backend bugs | Aliyan | 30 min | QA-03 |
| `SEC-01` | Run the security checklist | Warisha | 20 min | - |
| `DOC-04` | Finish the README | Aruba | 15 min | DOC-03 |

### QA-03  Backend bug bash with odd inputs

**Owner:** Hammad · **Estimate:** 35 min · **Labels:** qa,backend · **Depends on:** BE-05

**Do:** Using the live-style setup try: emoji in every field, 4000-character fields, Urdu text, a PDF over 10 MB, a renamed .txt file as a deck, an image-only PDF, the same startup submitted twice, double click on Submit. Log each failure as a GitHub issue with label bug and the exact input.

**Done when:** A list of bugs as issues, ranked by how bad they would look in the demo.

### QA-04  Phone and laptop UI pass

**Owner:** Aruba · **Estimate:** 30 min · **Labels:** qa,frontend · **Depends on:** FE-04, FE-05

**Do:** Open the deployed or local app on a real phone and on a laptop. Go through apply, dashboard, detail, blind mode, login. Log every layout bug or confusing text as an issue with label bug and a screenshot.

**Done when:** A list of UI bugs as issues with screenshots.

### QA-05  Fix the UI bugs

**Owner:** Amir · **Estimate:** 30 min · **Labels:** frontend,qa · **Depends on:** QA-04

**Do:** Fix the issues labelled bug and frontend, worst first. Close each with Closes #n in the pull request. Do not start new features.

**Done when:** No open UI bug that would be visible in the demo.

### QA-06  Fix the backend bugs

**Owner:** Aliyan · **Estimate:** 30 min · **Labels:** backend,qa · **Depends on:** QA-03

**Do:** Fix the issues labelled bug and backend, worst first. Add a test for each fix. Ask Warisha before changing anything in backend/app/pipeline.py or scoring.py.

**Done when:** No open backend bug that would be visible in the demo. pytest passes.

### SEC-01  Run the security checklist

**Owner:** Warisha · **Estimate:** 20 min · **Labels:** security

**Do:** Go through the Security section of DEPLOYMENT-CHECKLIST.md: no keys in git history (git log -p | grep for key patterns), REVIEWER_KEY or Supabase auth on, RLS enabled, CORS set to the real URL, decide ENABLE_DEV_ROUTES for the demo, rotate any key that was ever pasted into a chat.

**Done when:** Every box in the security checklist is ticked or has a written reason.

### DOC-04  Finish the README

**Owner:** Aruba · **Estimate:** 15 min · **Labels:** docs · **Depends on:** DOC-03

**Do:** README.md is already drafted. Add the screenshots from docs/img/, the real eval numbers from docs/EVAL-RESULTS.md, the live URL, the real GitHub usernames in the team table, and delete every line that says TODO. Run the 5 commands in Quick start on a clean clone to be sure they work.

**Done when:** A stranger could run the project from the README alone.

## M5 Deploy and rehearsal  (T+3:20 to 4:00)

Final deploy, seeded data, backup video, two timed rehearsals, code freeze.

Planned work in this milestone: 2h25 across 8 issues.

| Code | Issue | Owner | Est. | Depends on |
|---|---|---|---|---|
| `DEP-01` | Final production deploy on Render | Warisha | 20 min | SEC-01, QA-06, QA-05 |
| `DEP-02` | Seed production and verify the demo data | Aliyan | 15 min | DEP-01 |
| `DEP-03` | Optional: host the frontend on Hostinger | Amir | 20 min | DEP-01 |
| `DEP-04` | Record a 90-second backup demo video | Hammad | 20 min | DEP-01 |
| `SLD-04` | Final deck export and offline copy | Hafsa | 20 min | SLD-03, DEP-01 |
| `DEMO-01` | Two timed rehearsals and the Q and A drill | Everyone | 30 min | DEP-01, SLD-04, DEP-04 |
| `DEMO-02` | Code freeze and release tag | Warisha | 5 min | DEMO-01 |
| `DOC-05` | Submit the project on the hackathon page | Aruba | 15 min | DEP-01, DEP-04, DOC-04 |

### DEP-01  Final production deploy on Render

**Owner:** Warisha · **Estimate:** 20 min · **Labels:** deploy · **Depends on:** SEC-01, QA-06, QA-05

**Do:** Set the Render environment variables from DEPLOYMENT-CHECKLIST.md: AI_MODE=gemini, GEMINI_API_KEY, GEMINI_MODEL, STORE_BACKEND=supabase, SUPABASE_URL, SUPABASE_SERVICE_KEY, AUTH_MODE, reviewer settings, CORS_ORIGINS. Deploy the main branch. Open /api/health: it must show ai_mode gemini and store supabase.

**Done when:** The live URL works end to end: submit an application, see it analysed and ranked.

### DEP-02  Seed production and verify the demo data

**Owner:** Aliyan · **Estimate:** 15 min · **Labels:** database,deploy · **Depends on:** DEP-01

**Do:** Against the live URL log in as a reviewer and load the demo data (or confirm the 12 already exist). Confirm scores are present. Do not leave test junk like Evil Co in the production table: delete rows in the Supabase Table Editor if needed.

**Done when:** The production dashboard shows the clean demo set and nothing embarrassing.

### DEP-03  Optional: host the frontend on Hostinger

**Owner:** Amir · **Estimate:** 20 min · **Labels:** frontend,deploy,stretch · **Depends on:** DEP-01

**Do:** Only if time allows. Upload the frontend folder to Hostinger, set API_BASE in js/config.js to the Render URL and CORS_ORIGINS on Render to the Hostinger URL. The team mentioned this as a plus point, but the single Render URL is the reliable fallback.

**Done when:** Both URLs work, or you stop and the Render URL stays the primary link.

### DEP-04  Record a 90-second backup demo video

**Owner:** Hammad · **Estimate:** 20 min · **Labels:** demo,qa · **Depends on:** DEP-01

**Do:** Screen-record the whole flow on the live URL: submit with a deck, watch the analysis, the ranked dashboard, a scorecard with evidence quotes, blind mode, the injection example, making a decision. No narration needed beyond captions. Save the video on two laptops and a phone.

**Done when:** A watchable video exists in three places.

### SLD-04  Final deck export and offline copy

**Owner:** Hafsa · **Estimate:** 20 min · **Labels:** slides,demo · **Depends on:** SLD-03, DEP-01

**Do:** Export the deck to PDF, save it on two laptops and your phone, and add a QR code to the live URL on the last slide.

**Done when:** The deck opens with no internet on two devices.

### DEMO-01  Two timed rehearsals and the Q and A drill

**Owner:** Everyone · **Estimate:** 30 min · **Labels:** demo · **Depends on:** DEP-01, SLD-04, DEP-04

**Do:** Run the demo script in DEMO-AND-PITCH.md twice with a timer. Decide who speaks and who drives the laptop. Everyone practises two answers from the judge questions list. Practise the fallback: if the live site is down switch to the backup video without comment.

**Done when:** Two full runs inside the time limit and everyone has said an answer out loud.

### DEMO-02  Code freeze and release tag

**Owner:** Warisha · **Estimate:** 5 min · **Labels:** demo · **Depends on:** DEMO-01

**Do:** At the agreed freeze time merge the last approved pull request, then run: git tag v1.0-demo and git push origin v1.0-demo. After this nothing is merged until the demo is over.

**Done when:** Tag exists. Nobody pushes to main.

### DOC-05  Submit the project on the hackathon page

**Owner:** Aruba · **Estimate:** 15 min · **Labels:** docs · **Depends on:** DEP-01, DEP-04, DOC-04

**Do:** On the MLH event page use Submit Project. Paste the live URL, the GitHub URL, the description (reuse the top of README.md) and the demo video. Choose both prize categories: Best Use of the Google Gemini API and Best AI Startup MVP. Double-check the links in a private window.

**Done when:** Submission confirmation received and the links open for a logged-out person.

## Critical path

The demo needs these in order, so they get priority over everything else:

`SET-03` Gemini key → `BE-01` real pipeline works → `AI-02` scores are sensible → `FE-04` and `FE-05` readable UI → `SEC-01` secure → `DEP-01` live deploy → `DEMO-01` rehearsal.

Anything not on this path can be cut. See the cut line in SCOPE.md.

## Labels

`backend` `frontend` `ai` `database` `docs` `slides` `security` `deploy` `qa` `bug` `setup` `demo` `stretch`, plus one `owner:<name>` label per person.
