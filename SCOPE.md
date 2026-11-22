# Scope of development

This file defines exactly what we are building in 4 hours, what we are not, and what to drop first if we run late. If something is not in here, it is not in scope: open a GitHub issue labelled `stretch`.

## 1. The product in one paragraph

Startup programmes receive far more applications than they can read carefully. **Shortlist** lets an applicant submit a form and an optional pitch deck, has Gemini score it against the programme's rubric with evidence quotes that code verifies, and gives reviewers a ranked dashboard with scorecards, suggested interview questions and a blind-review mode. The AI sets reading order; a person makes every decision.

## 2. Users

| User | Needs | What they do in the product |
|---|---|---|
| **Applicant** (student founder) | A simple form, confidence the process is fair | Fills the form, optionally uploads a PDF deck, gets a reference id. No account. |
| **Reviewer** (programme staff) | Read the right applications first; defend decisions | Opens the ranked dashboard, reads scorecards, checks the evidence, toggles blind mode, records a decision and a note. |
| **Programme manager** | See the pipeline, export, tune the rubric | Dashboard stats, CSV export, rubric view (editing is by API only in this MVP). |

## 3. In scope, by priority

**Must have (the demo fails without these)**

| # | Feature | Acceptance test | Issues |
|---|---|---|---|
| M1 | Application form with PDF upload | A founder submits all required fields and a PDF and gets a reference id. Bad input shows readable messages. | FE-03, FE-06 |
| M2 | Real Gemini analysis with the rubric | A submission becomes `done` with a score, 7 criteria with reasoning, strengths, risks, riskiest assumptions, interview questions. `/api/health` says `ai_mode: gemini`. | BE-01, BE-02, AI-01, AI-02 |
| M3 | Evidence verification | Each criterion shows its quote with a verified or not-found mark. A fabricated quote triggers one retry and a warning. | (built; tested in AI-01, AI-03) |
| M4 | Ranked dashboard | Applications sorted by score with priority, confidence, flags, decision. Updates while analysing. Filter by priority, search. | FE-04 |
| M5 | Scorecard detail page | One screen shows score, per-criterion bars, reasoning, evidence, risks, questions, red flags, missing info. | FE-05 |
| M6 | Blind review | With blind on, name, email and organisation are hidden in list, detail, search and CSV. | (built) |
| M7 | Human decision | A reviewer records shortlist, interview, hold or decline with a note. It persists and survives re-analysis. | (built) |
| M8 | Prompt-injection example | The demo applicant that says "ignore previous instructions" is flagged, not high priority, confidence low. | AI-02 |
| M9 | Persistent storage | Data survives a server restart (Supabase). | DB-01, DB-02 |
| M10 | Deployed and reachable | One public URL, reviewer area protected by a key. | SET-09, DEP-01 |
| M11 | Pitch deck and rehearsed demo | 10-slide deck, two timed rehearsals, backup video. | SLD-01 to SLD-04, DEMO-01, DEP-04 |
| M12 | Honest documentation | README, how-it-works, eval results, dev log, known limitations. | DOC-01 to DOC-05, QA-02 |

**Should have**

| # | Feature | Issues |
|---|---|---|
| S1 | Failure handling you can show: bad key gives a readable error and a Retry button that works | AI-04 |
| S2 | CSV export | (built) |
| S3 | Dashboard stats strip with the assumption labelled | (built), BE-05 |
| S4 | Interview brief download | BE-03 (Hammad) |
| S5 | Edge-case demo applicants (Urdu, very long, identity in free text) | AI-05 |
| S6 | Accessibility pass | FE-07 |

**Could have (stretch, only when your core list is merged)**

| # | Feature | Issues |
|---|---|---|
| C1 | Reviewer login with Supabase auth | BE-04, FE-08 |
| C2 | "How we score" public page | FE-10 |
| C3 | Blind mode remembered across pages with a banner | FE-09 |
| C4 | Brief download button | FE-11 |
| C5 | Frontend on Hostinger | DEP-03 |

## 4. Out of scope (say no, kindly)

- Applicant accounts, login or status tracking for applicants
- Email or WhatsApp notifications
- Multiple reviewers scoring the same application, reviewer disagreement analysis
- Editing the rubric in the UI (the API supports it; the UI does not)
- Automatic accept or reject decisions of any kind
- Interview scheduling, applicant messaging, payments
- Fine-tuning or training any model
- Support for decks that are not PDF (PowerPoint, Google Slides links)
- Web research about the startup or founders (we only score what the applicant submitted)
- Anything that needs real applicant data. We use synthetic applicants only.

## 5. The cut line: drop in this order if we are behind

1. DEP-03 (Hostinger), FE-10, FE-11, FE-09
2. BE-04 and FE-08 (Supabase login). Use the shared reviewer key.
3. BE-03 (interview brief)
4. AI-05 (edge cases) and FE-07 (accessibility pass)
5. DB-02 (seed Supabase with the full set: seed 4 instead)
6. Never cut: M1 to M12, AI-04's retry check, SEC-01, DEMO-01, DEP-04 (the backup video).

## 6. Definition of done for the MVP

All of these are true at the freeze (DEMO-02):

- [ ] The live URL opens and `/api/health` says `ai_mode: gemini`, `store: supabase`
- [ ] A new application submitted live (with a PDF) is analysed in front of a person and appears in the ranked list
- [ ] The 12 demo applicants are loaded with real Gemini scores
- [ ] The injection example is flagged
- [ ] Blind mode hides identity in list and detail
- [ ] A reviewer decision can be recorded and survives a refresh
- [ ] No secret is in the repo and the reviewer area asks for the key
- [ ] `pytest` passes and `docs/EVAL-RESULTS.md` matches the real output
- [ ] The deck and the backup video are on two devices
- [ ] The project is submitted on the MLH page for both categories

## 7. Non-functional targets

These are **targets to be measured in BE-01 and QA-02**, not facts yet.

| Area | Target | How we will check |
|---|---|---|
| Analysis time | under 60 seconds per application | `run_eval.py` latency line |
| Unverified quotes | under 10 percent | `run_eval.py` check |
| Upload limit | 10 MB PDF | test in QA-03 |
| Pages usable on a phone | no sideways scrolling, readable text | QA-04 |
| Concurrent users | a handful (judges plus teammates) | not load-tested; do not claim scale |

## 8. Business model (hypotheses to say out loud, labelled as such)

**Who pays:** programmes that run application rounds: incubators, accelerators, fellowships, competitions, university innovation offices.

**What they pay for:** reviewer time saved and a more defensible, consistent shortlist.

**How (hypothesis, not tested):** a fee per application round (cohort) or a small annual licence, with a free tier for small programmes. A tiny pilot with one programme comes before any pricing.

**Worked illustration (every input is an assumption to replace):** a programme with 300 applications per round. If a careful first read takes 15 minutes, that is 75 reviewer-hours. If triage cut each first read to 3 minutes, that is 15 hours: 60 hours returned to the team. Use the real figure from Warisha's NIC experience, or leave the number out of the deck.

**Cost to serve (to be measured, not assumed):** the Gemini tokens per application are recorded by the app (`avg_tokens_in` and `avg_tokens_out` on `/api/stats`). After the real run, work out the cost per application from Google's current pricing page and put that number, with its date, on the slide.

**Not claimed:** customers, pilots, revenue, or market size. We have none and we did not research the market size.

## 9. Competition (what we found, and what we did not)

Searched on 20 Nov 2026. We read the pages we could open; claims below are limited to what they said.

| Product | What we found | Our honest position |
|---|---|---|
| **AcceleratorApp** | Application-management platform for accelerators, incubators, grant programmes and universities. It publishes guidance on AI application scoring. We could not confirm the product's AI feature details. | A full platform. We are a lightweight triage layer, not an application-management system. |
| **Sopact** | Describes an applications workflow where AI suggests criterion-based scores with source evidence, uncertainty and a reviewer action (confirm or override). | **Closest in concept.** We cannot claim criterion scoring with evidence is new. |
| **Submittable, F6S, Fluxx** | General submission, programme and grant management platforms. We did not verify any AI scoring features. | Different product category; potential integration partners rather than rivals. |
| **CohortFilter AI** | A hackathon project with a very similar name and purpose is listed on lablab.ai. We could not open the page. | Do not claim to be the first. |

**What we can honestly emphasise** (we did not find these specifics on the competitor pages we could read, but we have not proven competitors lack them, so phrase it as "what we focused on", never "what they lack"):

1. Evidence quotes **checked by code** against the original text, with unverified quotes flagged.
2. Identity removed from the AI's input by construction, plus a blind-review mode for people.
3. A built-in prompt-injection example and detection, shown live.
4. An evaluation script anyone can re-run.
5. Built for programmes in Khyber Pakhtunkhwa and similar settings: light, open and cheap to run.
