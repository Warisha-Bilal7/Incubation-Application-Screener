# Dev log

One line per decision or finding, newest at the bottom, with the time. This is the evidence of how we worked. Aruba keeps it (DOC-01) but **everyone adds lines**.

Format: `HH:MM  Who  Decision or finding, and why`

## Decisions made before the event (Warisha, 20 Nov)

- **Idea:** application screener for incubators. Chosen over the AI co-founder idea because the problem is concrete for the judges (NIC and startup-community people) and many AI co-founder and idea-validation tools already exist.
- **Backend: Python (FastAPI), not PHP.** The planning meeting left PHP versus other options open ("up to you"). Python was chosen because the Gemini SDK, PDF handling and the verification code are all first-class in Python, and the starter backend with 43 tests already exists. Amir's PHP and Supabase experience goes into storage, login and the frontend instead. *Team: say now if you disagree.*
- **Frontend: plain HTML, CSS and JavaScript**, as discussed in the meeting, with no build step so the two learners can start immediately.
- **One URL:** the backend serves the frontend. Hostinger hosting stays optional (DEP-03).
- **Hosting:** Render, as agreed in the meeting.
- **Storage:** Supabase for applications and for decks (Render's free disk is wiped on every restart). A JSON file store exists for local use.
- **Reviewer auth:** shared reviewer key by default. Supabase login is stretch (BE-04, FE-08).
- **AI coding tools:** allowed (OpenCode, Antigravity, Lovable). `AGENTS.md` gives them the rules.
- **Working style from the meeting:** milestone by milestone, issue by issue, own branch, pull request. Debugging is its own milestone, then deploy.
- **Nothing was run against real Gemini before the event.** The Gemini call is tested against a fake client only. First real call: BE-01.

## Measurements to fill in

| What | Value | Who |
|---|---|---|
| Render cold-start time after 20 idle minutes (SET-09) | | |
| Gemini model that worked (BE-01) | | |
| Median analysis time per application (BE-01 / QA-02) | | |
| Tokens in and out per application (from `/api/stats`) | | |

## Log

```
HH:MM  Who  ...
```
