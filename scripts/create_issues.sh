#!/usr/bin/env bash
# Creates all labels, milestones and issues from scripts/issues.tsv.
#
#   1. gh auth login                       (once)
#   2. cp scripts/team.env.example scripts/team.env   and fill in the GitHub usernames
#   3. run from inside the cloned repo:    bash scripts/create_issues.sh
#
# DRY_RUN=1 bash scripts/create_issues.sh   prints what it would do and changes nothing.
# Safe to re-run: issues whose title already exists are skipped.
set -euo pipefail
cd "$(dirname "$0")/.."

DRY_RUN="${DRY_RUN:-0}"
[ -f scripts/team.env ] && source scripts/team.env || echo "note: scripts/team.env not found, issues will not be assigned to people"

run() { if [ "$DRY_RUN" = "1" ]; then echo "[dry-run] $*"; else "$@"; fi; }

mk_label_all() {
  echo "Creating labels..."
  if [ "$DRY_RUN" = "1" ]; then echo "[dry-run] (20 labels)"; return; fi
  gh label create "backend" --color 0E8A16 --force >/dev/null
  gh label create "frontend" --color 1D76DB --force >/dev/null
  gh label create "ai" --color 5319E7 --force >/dev/null
  gh label create "database" --color FBCA04 --force >/dev/null
  gh label create "docs" --color C5DEF5 --force >/dev/null
  gh label create "slides" --color F9D0C4 --force >/dev/null
  gh label create "security" --color B60205 --force >/dev/null
  gh label create "deploy" --color D93F0B --force >/dev/null
  gh label create "qa" --color BFD4F2 --force >/dev/null
  gh label create "bug" --color EE0701 --force >/dev/null
  gh label create "setup" --color EDEDED --force >/dev/null
  gh label create "demo" --color FF7619 --force >/dev/null
  gh label create "stretch" --color CCCCCC --force >/dev/null
  gh label create "owner:warisha" --color 6F42C1 --force >/dev/null
  gh label create "owner:amir" --color 6F42C1 --force >/dev/null
  gh label create "owner:aruba" --color 6F42C1 --force >/dev/null
  gh label create "owner:hafsa" --color 6F42C1 --force >/dev/null
  gh label create "owner:aliyan" --color 6F42C1 --force >/dev/null
  gh label create "owner:hammad" --color 6F42C1 --force >/dev/null
  gh label create "owner:all" --color 6F42C1 --force >/dev/null
}

mk_milestone() {
  # $1 title, $2 description
  if [ "$DRY_RUN" = "1" ]; then echo "[dry-run] milestone: $1"; return; fi
  gh api "repos/{owner}/{repo}/milestones" -f title="$1" -f description="$2" >/dev/null 2>&1 \
    && echo "milestone: $1" || echo "milestone exists or failed: $1"
}

mk_label_all
echo "Creating milestones..."
  mk_milestone "M0 Prep (tonight)" "Before the venue. Accounts, keys, repo access, local run, first Render deploy. (Tonight)"
  mk_milestone "M1 Foundations" "Everyone runs the app locally, the real Gemini call works, rubric agreed, look and feel chosen. (T+0:00 to 0:30)"
  mk_milestone "M2 Core build" "Real AI analysis tuned on demo data, polished apply/dashboard/detail pages, Supabase storage verified. (T+0:30 to 1:45)"
  mk_milestone "M3 Integration and trust" "Reviewer login, blind review, interview brief, failure handling, eval numbers, slides complete. (T+1:45 to 2:45)"
  mk_milestone "M4 Debugging" "Bug bash, fixes, security checklist, README. Nothing new gets added here. (T+2:45 to 3:20)"
  mk_milestone "M5 Deploy and rehearsal" "Final deploy, seeded data, backup video, two timed rehearsals, code freeze. (T+3:20 to 4:00)"

EXISTING=""
if [ "$DRY_RUN" != "1" ]; then
  EXISTING="$(gh issue list --state all --limit 500 --json title --jq '.[].title')"
fi

echo "Creating issues..."
tail -n +2 scripts/issues.tsv | while IFS=$'\t' read -r code milestone owner labels est title body; do
  full="[$code] $title"
  if [ -n "$EXISTING" ] && printf '%s\n' "$EXISTING" | grep -Fxq "$full"; then
    echo "skip (exists): $full"; continue
  fi
  var="GH_$(echo "$owner" | tr '[:lower:]' '[:upper:]')"
  assignee="${!var:-}"
  args=(--title "$full" --body "$(printf '%b' "$body")" --milestone "$milestone" --label "$labels,owner:$owner")
  [ -n "$assignee" ] && args+=(--assignee "$assignee")
  run gh issue create "${args[@]}"
done
echo "Done. Open the Issues tab, then Milestones."
