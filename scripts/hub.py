#!/usr/bin/env python3
"""StrudelHub client (stdlib only).

Usage:
  hub.py new [--from-piece PIECE_ID]        create a session (optionally forked from a gallery piece)
  hub.py info <id>                           metadata: name, visibility, agent_mode, pending draft
  hub.py status <id>                         code + isPlaying + diff (needs an API key, any visibility)
  hub.py peek <id>                           code + isPlaying via SSE first event (no key on public sessions)
  hub.py push <id> <file.js> [--play]        push without starting; --play explicitly starts/restarts after acceptance
  hub.py play <id> | stop <id>
  hub.py versions <id> [--limit N] [--offset N]
  hub.py version <id> <v> [-o FILE]
  hub.py revert <id> <v>
  hub.py explore [-q TEXT] [--tag T] [--sort recent|popular] [--limit N]   browse the public gallery
  hub.py piece <piece_id> [-o FILE]          code of a gallery piece

Auth is optional: set STRUDELHUB_API_KEY for private sessions (never printed).
Exit codes: 0 ok, 1 HTTP/other error, 2 HTTP 401 (public session or missing/
invalid API key), 3 push stored as a draft (review mode), 64 usage, 66 missing file.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://strudelhub.com"
USER_AGENT = "strudelhub-skill/1.1 (+python-urllib)"
TIMEOUT = 30

EXIT_OK, EXIT_ERR, EXIT_401, EXIT_DRAFT, EXIT_USAGE, EXIT_NOFILE = 0, 1, 2, 3, 64, 66


class HubError(Exception):
    def __init__(self, message, code=EXIT_ERR):
        super().__init__(message)
        self.code = code


def _headers(accept="application/json"):
    headers = {"User-Agent": USER_AGENT, "Accept": accept}
    key = os.environ.get("STRUDELHUB_API_KEY")
    if key:
        headers["Authorization"] = "Bearer " + key
    return headers


def request(method, path, body=None, params=None):
    """Return (http_status, decoded JSON or raw text). Raise HubError on failure."""
    url = BASE + path
    if params:
        url += "?" + urllib.parse.urlencode(params, doseq=True)
    headers = _headers()
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    elif method == "POST":
        data = b""
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            status = resp.status
            text = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        if e.code == 401:
            raise HubError("401 %s (public session without key, or wrong key)" % text.strip(), EXIT_401)
        if e.code == 403:
            raise HubError("403 forbidden: the key does not own this session", EXIT_ERR)
        raise HubError("HTTP %d\n%s" % (e.code, text), EXIT_ERR)
    except urllib.error.URLError as e:
        raise HubError("request failed: %s" % e.reason, EXIT_ERR)
    except (TimeoutError, OSError) as e:
        raise HubError("request failed: %s" % e, EXIT_ERR)
    try:
        return status, json.loads(text) if text.strip() else None
    except ValueError:
        return status, text


def read_file(path):
    if not os.path.isfile(path):
        raise HubError("file not found: %s" % path, EXIT_NOFILE)
    with open(path, encoding="utf-8") as f:
        return f.read()


def _write_or_print(code, output):
    if output:
        with open(output, "w", encoding="utf-8", newline="") as f:
            f.write(code)
        print("wrote %s (%d chars)" % (output, len(code)))
    else:
        sys.stdout.write(code if code.endswith("\n") else code + "\n")


def cmd_new(args):
    body = {"piece_id": args.from_piece} if args.from_piece else None
    _, data = request("POST", "/api/sessions", body=body)
    if not isinstance(data, dict) or "id" not in data:
        raise HubError("new: unexpected response:\n%s" % (data,))
    print("id: %s" % data["id"])
    print("url: %s/sessions/%s" % (BASE, data["id"]))
    print("visibility: %s" % data.get("visibility", "?"))


def cmd_info(args):
    _, data = request("GET", "/api/sessions/%s" % args.id)
    if not isinstance(data, dict):
        raise HubError("info: unexpected response:\n%s" % (data,))
    for k in ("name", "visibility", "agent_mode", "owner_id", "created_at"):
        print("%s: %s" % (k, data.get(k)))
    print("draft_pending: %s" % json.dumps(data.get("draft_code") is not None))
    if data.get("draft_created_at"):
        print("draft_created_at: %s" % data["draft_created_at"])


def cmd_status(args):
    _, data = request("GET", "/api/sessions/%s/status" % args.id)
    if not isinstance(data, dict):
        raise HubError("status: unexpected response:\n%s" % (data,))
    print("isPlaying: %s" % json.dumps(data.get("isPlaying")))
    print("agentMode: %s  hasDraft: %s" % (data.get("agentMode"), json.dumps(data.get("hasDraft"))))
    print("diff: %s" % json.dumps(data.get("diff"), ensure_ascii=False))
    print("--- code ---")
    print(data.get("code") or "")


def sse_events(sid):
    """Return the events queued on connect: [update, (draft)]. No key needed on public sessions."""
    url = BASE + "/api/sessions/%s/events" % sid
    req = urllib.request.Request(url, headers=_headers("text/event-stream"))
    try:
        resp = urllib.request.urlopen(req, timeout=TIMEOUT)
    except urllib.error.HTTPError as e:
        if e.code == 401:
            raise HubError("401: private session, key required", EXIT_401)
        raise HubError("HTTP %d" % e.code)
    events = []
    try:
        # First event (update) arrives immediately; a draft event follows only if one is pending,
        # otherwise the stream is silent until the 30 s keepalive — so wait briefly, then stop.
        while len(events) < 2:
            if events:
                sock = getattr(resp, "fp", None)
                raw = getattr(getattr(sock, "raw", None), "_sock", None) or getattr(sock, "_sock", None)
                if raw is not None:
                    raw.settimeout(1.5)
            try:
                line = resp.readline().decode("utf-8", errors="replace")
            except (TimeoutError, OSError):
                break
            if not line:
                break
            if line.startswith("data:"):
                events.append(json.loads(line[5:].strip()))
            elif line.startswith(":"):
                break  # keepalive: nothing more queued
    finally:
        resp.close()
    if not events:
        raise HubError("peek: no event received")
    return events


def fetch_current_code(sid):
    """Current code via /status (key) or, on 401, via the SSE first event."""
    try:
        _, data = request("GET", "/api/sessions/%s/status" % sid)
    except HubError as e:
        if e.code != EXIT_401:
            raise
        return sse_events(sid)[0].get("code") or ""
    if not isinstance(data, dict) or data.get("code") is None:
        raise HubError("status: no code in response:\n%s" % (data,))
    return data["code"]


def fetch_version_code(sid, v):
    _, data = request("GET", "/api/sessions/%s/versions/%s" % (sid, v))
    if not isinstance(data, dict) or data.get("code") is None:
        raise HubError("version %s: no code in response:\n%s" % (v, data))
    return data["code"]


def cmd_peek(args):
    events = sse_events(args.id)
    first = events[0]
    print("isPlaying: %s" % json.dumps(first.get("isPlaying")))
    draft = next((e for e in events if e.get("type") == "draft"), None)
    print("draft_pending: %s" % json.dumps(draft is not None))
    if args.output:
        _write_or_print(first.get("code") or "", args.output)
    else:
        print("--- code ---")
        print(first.get("code") or "")
    if draft and args.show_draft:
        print("--- draft ---")
        print(draft.get("draftCode") or "")


def cmd_push(args):
    code = read_file(args.file)
    status, data = request("POST", "/api/sessions/%s/code" % args.id, {"code": code})
    result = data.get("status") if isinstance(data, dict) else None
    if isinstance(data, dict) and result == "pending_review":
        print("code: HTTP %d status=pending_review (draft %s)" % (status, data.get("draftCreatedAt")))
        print("review mode: the owner must click \"Accept Changes\" in the browser; nothing is playing yet")
        sys.exit(EXIT_DRAFT)
    print("code: HTTP %d status=%s version=%s" % (status, result or "<none>",
                                                 data.get("version") if isinstance(data, dict) else "?"))
    if result != "accepted":
        raise HubError("push: code not accepted:\n%s" % (data,))
    if not args.play:
        print("play: unchanged (use --play to start/restart)")
        return
    status, data = request("POST", "/api/sessions/%s/play" % args.id)
    print("play: HTTP %d %s" % (status, json.dumps(data) if not isinstance(data, str) else data))


def cmd_play(args):
    status, data = request("POST", "/api/sessions/%s/play" % args.id)
    print("play: HTTP %d %s" % (status, json.dumps(data) if not isinstance(data, str) else data))


def cmd_stop(args):
    status, data = request("POST", "/api/sessions/%s/stop" % args.id)
    print("stop: HTTP %d %s" % (status, json.dumps(data) if not isinstance(data, str) else data))


def cmd_versions(args):
    params = {}
    if args.limit is not None:
        params["limit"] = args.limit
    if args.offset is not None:
        params["offset"] = args.offset
    _, data = request("GET", "/api/sessions/%s/versions" % args.id, params=params)
    if not isinstance(data, dict):
        raise HubError("versions: unexpected response:\n%s" % (data,))
    for it in data.get("versions", []):
        print("%s %s %s" % (it.get("version", "?"), it.get("source", "?"), it.get("created_at", "")))
    print("total: %s" % data.get("total"))


def cmd_version(args):
    _write_or_print(fetch_version_code(args.id, args.v), args.output)


def cmd_revert(args):
    _, data = request("POST", "/api/sessions/%s/versions/%s/revert" % (args.id, args.v))
    if not isinstance(data, dict):
        raise HubError("revert: unexpected response:\n%s" % (data,))
    print("reverted from v%s -> new version v%s" % (data.get("revertedFrom"), data.get("newVersion")))


def cmd_explore(args):
    params = {"limit": args.limit, "sort": args.sort}
    if args.q:
        params["q"] = args.q
    if args.tag:
        params["tag"] = args.tag
    _, data = request("GET", "/api/explore", params=params)
    if not isinstance(data, dict):
        raise HubError("explore: unexpected response:\n%s" % (data,))
    for p in data.get("pieces", []):
        tags = ",".join(p.get("tags") or [])
        print("%s  %-40s  %s" % (p.get("id"), (p.get("title") or "")[:40], tags))
        desc = (p.get("description") or "").strip().splitlines()
        if desc:
            print("    %s" % desc[0][:120])
    print("total: %s" % data.get("total", "?"))


def cmd_piece(args):
    _, data = request("GET", "/api/pieces/%s" % args.piece_id)
    if not isinstance(data, dict) or data.get("code") is None:
        raise HubError("piece: no code in response:\n%s" % (data,))
    if not args.output:
        print("// %s — %s" % (data.get("title"), ",".join(data.get("tags") or [])))
    _write_or_print(data["code"], args.output)


class Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print("hub: %s" % message, file=sys.stderr)
        sys.exit(EXIT_USAGE)


def build_parser():
    p = Parser(prog="hub.py", description="StrudelHub client")
    sub = p.add_subparsers(dest="cmd", required=True, parser_class=Parser)
    s = sub.add_parser("new")
    s.add_argument("--from-piece", metavar="PIECE_ID")
    s.set_defaults(fn=cmd_new)
    for name, fn in (("info", cmd_info), ("status", cmd_status), ("play", cmd_play), ("stop", cmd_stop)):
        s = sub.add_parser(name)
        s.add_argument("id")
        s.set_defaults(fn=fn)
    s = sub.add_parser("peek")
    s.add_argument("id")
    s.add_argument("-o", "--output")
    s.add_argument("--show-draft", action="store_true")
    s.set_defaults(fn=cmd_peek)
    s = sub.add_parser("push")
    s.add_argument("id")
    s.add_argument("file")
    s.add_argument("--play", action="store_true", help="start/restart only after code is accepted")
    s.set_defaults(fn=cmd_push)
    s = sub.add_parser("versions")
    s.add_argument("id")
    s.add_argument("--limit", type=int)
    s.add_argument("--offset", type=int)
    s.set_defaults(fn=cmd_versions)
    s = sub.add_parser("version")
    s.add_argument("id")
    s.add_argument("v")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_version)
    s = sub.add_parser("revert")
    s.add_argument("id")
    s.add_argument("v")
    s.set_defaults(fn=cmd_revert)
    s = sub.add_parser("explore")
    s.add_argument("-q")
    s.add_argument("--tag", action="append")
    s.add_argument("--sort", default="recent")
    s.add_argument("--limit", type=int, default=10)
    s.set_defaults(fn=cmd_explore)
    s = sub.add_parser("piece")
    s.add_argument("piece_id")
    s.add_argument("-o", "--output")
    s.set_defaults(fn=cmd_piece)
    return p


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    args = build_parser().parse_args(argv)
    try:
        args.fn(args)
    except HubError as e:
        print("hub: %s" % e, file=sys.stderr)
        return e.code
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
