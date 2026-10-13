#!/usr/bin/env bash
# Read the status of a StrudelHub session (code, isPlaying, diff).
# Usage: status.sh <session-id>
# Exit codes: 0 ok, 1 other error, 2 HTTP 401 (public session, no API key).
set -euo pipefail

BASE="https://strudelhub.com"

[ $# -eq 1 ] || { echo "usage: status.sh <session-id>" >&2; exit 64; }
id=$1

auth=()
if [ -n "${STRUDELHUB_API_KEY:-}" ]; then
  auth=(-H "Authorization: Bearer ${STRUDELHUB_API_KEY}")
fi

raw=$(curl -sS ${auth[@]+"${auth[@]}"} -w $'\n%{http_code}' "$BASE/api/sessions/$id/status")
code=${raw##*$'\n'}
body=${raw%$'\n'*}

if [ "$code" = "401" ]; then
  echo "public session: status not readable without API key; work from local file" >&2
  exit 2
fi

case "$code" in
  2??) ;;
  *)
    echo "status: HTTP $code" >&2
    printf '%s\n' "$body" >&2
    exit 1 ;;
esac

printf '%s' "$body" | jq -r '
  "isPlaying: \(.isPlaying)",
  "diff: \(.diff | tojson)",
  "--- code ---",
  (.code // "")'
