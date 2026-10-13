#!/usr/bin/env bash
# Push a Strudel file without starting/restarting playback unless --play is given.
# Usage: push.sh <session-id> <file.js> [--play]
# Auth is optional: set STRUDELHUB_API_KEY for private sessions.
set -euo pipefail

BASE="https://strudelhub.com"

usage() { echo "usage: push.sh <session-id> <file.js> [--play]" >&2; exit 64; }

id=""
file=""
play=0
for arg in "$@"; do
  case "$arg" in
    --play) play=1 ;;
    -*) echo "push: unknown option $arg" >&2; usage ;;
    *)
      if [ -z "$id" ]; then id="$arg"
      elif [ -z "$file" ]; then file="$arg"
      else usage
      fi ;;
  esac
done
[ -n "$id" ] && [ -n "$file" ] || usage
[ -f "$file" ] || { echo "push: file not found: $file" >&2; exit 66; }

auth=()
if [ -n "${STRUDELHUB_API_KEY:-}" ]; then
  auth=(-H "Authorization: Bearer ${STRUDELHUB_API_KEY}")
fi

# post <path> [json-body-on-stdin]: sets HTTP_CODE and BODY
post() {
  local path=$1 raw
  shift
  raw=$(curl -sS -X POST ${auth[@]+"${auth[@]}"} "$@" -w $'\n%{http_code}' "$BASE$path")
  HTTP_CODE=${raw##*$'\n'}
  BODY=${raw%$'\n'*}
}

jq -n --arg code "$(cat "$file")" '{code: $code}' > "${TMPDIR:-/tmp}/strudelhub-push.$$.json"
trap 'rm -f "${TMPDIR:-/tmp}/strudelhub-push.$$.json"' EXIT

post "/api/sessions/$id/code" -H 'Content-Type: application/json' \
  --data-binary "@${TMPDIR:-/tmp}/strudelhub-push.$$.json"
status=$(printf '%s' "$BODY" | jq -r '.status // empty' 2>/dev/null | tr -d '\r' || true)
version=$(printf '%s' "$BODY" | jq -r '.version // empty' 2>/dev/null | tr -d '\r' || true)
echo "code: HTTP $HTTP_CODE status=${status:-<none>}${version:+ version=$version}"
if [ "$status" = "pending_review" ]; then
  echo "review mode: stored as a draft; the owner must click \"Accept Changes\" in the browser. Not playing." >&2
  exit 3
fi
if [ "$status" != "accepted" ]; then
  echo "push: code not accepted:" >&2
  printf '%s\n' "$BODY" >&2
  exit 1
fi

if [ "$play" -eq 0 ]; then
  echo "play: unchanged (use --play to start/restart)"
  exit 0
fi

post "/api/sessions/$id/play"
echo "play: HTTP $HTTP_CODE"
printf '%s\n' "$BODY"
case "$HTTP_CODE" in
  2??) ;;
  *) echo "push: play failed" >&2; exit 1 ;;
esac
