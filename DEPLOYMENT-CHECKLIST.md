# Deployment checklist

Owner: Warisha (deploy, security), Aliyan (Supabase). One public URL serves the app and the API from a single Render web service. Data lives in Supabase so a sleeping or restarted Render instance loses nothing.

## What Render's free tier does (from Render's own docs, checked 20 Nov 2026)

- A free web service **spins down after 15 minutes without traffic** and takes **about a minute** to wake. Browsers see a loading page meanwhile.
- The filesystem is **ephemeral**: uploads and local files are lost when the service redeploys, restarts or spins down. This is why decks and data go to Supabase.
- 750 free instance hours per month per workspace.

Source: https://render.com/docs/free

## A. Tonight (SET-03, SET-04, SET-09)

- [ ] Gemini key created at https://aistudio.google.com/apikey and `python scripts/check_gemini.py` prints PASS
- [ ] Supabase project created, `backend/data/schema.sql` run, tables `applications` and `settings` exist, bucket `decks` exists (Storage menu), RLS on
- [ ] Render account connected to the GitHub repo
- [ ] First deploy from `render.yaml` in **mock mode** works: `/api/health` returns `ai_mode: mock`, home page loads
- [ ] Cold-start time measured and written in `docs/DEV-LOG.md`

## B. Supabase (Aliyan)

1. New project. Pick a region close to Pakistan if offered; any region works.
2. SQL Editor, new query, paste all of `backend/data/schema.sql`, Run.
3. Project Settings, API: copy **Project URL**, **anon key**, **service_role key**.
4. Send the three values privately to Warisha. Never paste them in a public place or the repo.
5. Check Table Editor: `applications`, `settings`. Check Storage: bucket `decks` (private).
6. Verify RLS is enabled on both tables (shield icon). The service key bypasses it on the server; the anon key must not be able to read these tables.

## C. Render environment variables

Set in the Render dashboard (Environment). `render.yaml` creates the service and the non-secret ones; secrets are entered by hand because they are marked `sync: false`.

| Variable | Tonight (mock) | Demo (final) |
|---|---|---|
| `AI_MODE` | `mock` | `gemini` |
| `GEMINI_API_KEY` | (empty) | your key (secret) |
| `GEMINI_MODEL` | `gemini-flash-latest` | the model `check_gemini.py` confirmed |
| `STORE_BACKEND` | `file` | `supabase` |
| `SUPABASE_URL` | (empty) | project URL |
| `SUPABASE_SERVICE_KEY` | (empty) | service_role key (secret) |
| `AUTH_MODE` | `key` | `key` (or `supabase` if BE-04 and FE-08 are done) |
| `REVIEWER_KEY` | Render generates one | keep it; share it with teammates privately |
| `RATE_LIMIT_PER_HOUR` | `300` | `300` (the venue shares one IP) |
| `ENABLE_DEV_ROUTES` | `true` | `true` while seeding, then your decision in SEC-01 |
| `CORS_ORIGINS` | `*` | `*` when the frontend is served by Render, the Hostinger URL if you host separately |
| `SUPABASE_ANON_KEY`, `REVIEWER_EMAILS` | | only for `AUTH_MODE=supabase` |

After changing environment variables Render redeploys; wait for "Live".

If the build fails with a Python syntax error about `|` in type hints, set `PYTHON_VERSION` to a 3.11 or newer version in Render.

## D. Verify a deployment (copy and run, replace `URL` and `KEY`)

```bash
curl -s https://URL/api/health
# expect: "ai_mode":"gemini","store":"supabase","auth_mode":"key"

curl -s -o /dev/null -w "%{http_code}\n" https://URL/api/applications
# expect: 401 (no key)

curl -s -H "X-Reviewer-Key: KEY" https://URL/api/applications | head -c 300
# expect: {"total":...
```

Then in a browser: open `/`, `/apply.html?demo=1`, submit the example with the sample PDF, open `/dashboard.html`, enter the key, watch the row go Queued, Analyzing, Ready.

## E. Security checklist (SEC-01, tick every box or write a reason)

- [ ] No keys in git history: `git log -p | grep -iE "AIza|service_role|eyJ|sk-"` prints nothing. If it does, **rotate that key now**.
- [ ] `.env` is not tracked: `git ls-files | grep env` shows only `.env.example`
- [ ] The Supabase `service_role` key exists only in Render env vars and `backend/.env`. Search the frontend: `grep -ri service_role frontend/` prints nothing.
- [ ] Reviewer area asks for credentials: unauthenticated `GET /api/applications` returns 401
- [ ] `REVIEWER_KEY` is long and random, not `change-me`
- [ ] RLS is on for `applications` and `settings`
- [ ] The decks bucket is private
- [ ] `ENABLE_DEV_ROUTES`: decided and written down. If `true`, anyone with the reviewer key can wipe all data with `/api/dev/reset`. Prefer `false` after seeding.
- [ ] Applicant text is escaped everywhere it is shown (spot-check by submitting a startup named `<b>test</b>` and confirming it shows as plain text)
- [ ] Any key that was ever pasted into a chat or screenshot has been replaced
- [ ] The injection demo applicant still shows its warning after the final deploy

## F. T-30 minutes before judging

- [ ] Open the live URL; if it shows a loading page, wait. Leave one tab polling `/api/health`.
- [ ] `/api/health` shows `ai_mode: gemini`, `store: supabase`
- [ ] Dashboard (logged in) shows the 12 demo applicants with scores, **no MOCK badge**
- [ ] Do one live submission end to end now, then delete test junk in the Supabase Table Editor
- [ ] Gemini quota not exhausted: one fresh analysis completes
- [ ] Backup video on two devices; deck exported to PDF on two devices
- [ ] Phone hotspot on and tested; laptop charged
- [ ] Local fallback copy runs: `cd backend && uvicorn app.main:app` with demo data loaded

## G. If something goes wrong

| Symptom | Likely cause | Fix |
|---|---|---|
| Page shows "loading" for a minute | Render waking up | Wait, then it works |
| Applications stuck on "Analyzing" | The instance restarted mid-analysis | Open the application and press Retry (the button calls `POST /api/applications/{id}/analyze`) |
| `status: failed`, error mentions quota or 429 | Gemini rate limit | Wait a minute and Retry. Use your own key, not a shared one. |
| `ai_mode` says `mock` in production | `GEMINI_API_KEY` missing or `AI_MODE=mock` | Fix the variable, redeploy |
| 401 on the dashboard | Wrong or missing reviewer key | Close the tab (the key lives in `sessionStorage`), reopen, enter the key |
| Dashboard empty after restart | `STORE_BACKEND=file` on Render | Switch to `supabase`; the file store is wiped on restart |
| 429 on submit | Per-IP rate limit | Raise `RATE_LIMIT_PER_HOUR` |
| Supabase error text in the failed message | Wrong URL or key, or tables missing | Re-run `schema.sql`, re-check the two values |
