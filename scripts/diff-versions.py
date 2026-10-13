#!/usr/bin/env python3
"""Unified diff of a StrudelHub session's code between two versions.

Usage: diff-versions.py <session-id> <vA> <vB|current>
  `current` = code from /status, or from the SSE first event when /status is 401 (public session).
Exit codes: 0 ok, 1 HTTP/other error, 2 HTTP 401 (private session without key), 64 usage.
Prints nothing when both codes are identical.
"""
import difflib
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("hub", os.path.join(HERE, "hub.py"))
assert spec is not None and spec.loader is not None
hub = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hub)


def load(sid, ref):
    if ref == "current":
        return hub.fetch_current_code(sid)
    return hub.fetch_version_code(sid, ref)


def main():
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure:
            reconfigure(encoding="utf-8")
    if len(sys.argv) != 4:
        print("usage: diff-versions.py <session-id> <vA> <vB|current>", file=sys.stderr)
        return hub.EXIT_USAGE
    sid, a, b = sys.argv[1:]
    try:
        code_a = load(sid, a)
        code_b = load(sid, b)
    except hub.HubError as e:
        print("diff-versions: %s" % e, file=sys.stderr)
        return e.code
    diff = difflib.unified_diff(
        code_a.splitlines(keepends=True),
        code_b.splitlines(keepends=True),
        fromfile="v%s" % a if a != "current" else "current",
        tofile="v%s" % b if b != "current" else "current",
    )
    for line in diff:
        sys.stdout.write(line if line.endswith("\n") else line + "\n\\ No newline at end of file\n")
    return hub.EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
