#!/usr/bin/env bash
# Create a StrudelHub session and print its id + browser URL.
# Usage: new-session.sh
# Auth is optional: set STRUDELHUB_API_KEY to create a private session.
set -euo pipefail

BASE="https://strudelhub.com"

auth=()
if [ -n "${STRUDELHUB_API_KEY:-}" ]; then
  auth=(-H "Authorization: Bearer ${STRUDELHUB_API_KEY}")
fi

raw=$(curl -sS -X POST ${auth[@]+"${auth[@]}"} -w $'\n%{http_code}' "$BASE/api/sessions")
code=${raw##*$'\n'}
body=${raw%$'\n'*}

id=$(printf '%s' "$body" | jq -r '.id // empty' 2>/dev/null | tr -d '\r' || true)

if [ -z "$id" ]; then
  echo "new-session: no session id in response (HTTP $code):" >&2
  printf '%s\n' "$body" >&2
  exit 1
fi

echo "id:  $id"
echo "url: $BASE/sessions/$id"
