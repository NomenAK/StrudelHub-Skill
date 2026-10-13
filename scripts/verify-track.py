#!/usr/bin/env python3
"""Targeted pinned-runtime check; never connects to a musical session.

Setup (once): python -m pip install playwright
              python -m playwright install chromium
Usage: python verify-track.py track.js [--begin 0] [--cycles 4]
           [--loop 48] [--render] [--ranges] [--labels]
           [--tours N --tour-len L] [--timeout 120] [--browser PATH]

Trusted local Strudel code only: JavaScript executes in a fresh browser context,
not a security sandbox. No API key or user browser profile is passed to it.
Default: evaluate without starting, query selected events, check sound registry.
--loop compares the same window one declared loop later (not the whole track).
--render additionally renders that window silently and measures peak/RMS.
--ranges adds `ranges` {sound: {min, max, events}} (MIDI over the queried window) for every gm_* and
         pitched sample (VCSL/piano) sound, plus `badNotes`: one entry per event (any sound, synths
         included) whose note is a number < 20, null/non-finite, or neither number nor string
         (typical `c6@.5` bugs; note names like "c0" are fine). A non-empty badNotes makes ok false.
--labels adds `labels` {label: event count} for the queried window; unlabeled events are under "".
--tours N --tour-len L: for k in 0..N-1 with base=k*L, reports sound set + label counts for windows
         [base+2,base+4), [base+L-15,base+L-13), [base+L-4,base+L), then whether cycle 0 equals
         cycle N*L (same note/s/bank/n/label/orbit signature) as tours.loop.matches (false => ok false).
All options extend the JSON output (ok, events, sounds, errors, limits, diagnostics, ...).
Exit: 0 checked successfully, 1 runtime/verification failure, 2 setup/usage error.
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

RECORDER = "https://strudelhub.com/api/recorder"


def positive(value):
    result = float(value)
    if not math.isfinite(result) or result <= 0:
        raise argparse.ArgumentTypeError("must be finite and greater than zero")
    return result


def nonnegative(value):
    result = float(value)
    if not math.isfinite(result) or result < 0:
        raise argparse.ArgumentTypeError("must be finite and nonnegative")
    return result


def positive_int(value):
    try:
        result = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError("must be an integer greater than zero") from None
    if result <= 0:
        raise argparse.ArgumentTypeError("must be an integer greater than zero")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("file", type=Path)
    parser.add_argument("--begin", type=nonnegative, default=0)
    parser.add_argument("--cycles", type=positive, default=4)
    parser.add_argument("--loop", type=positive, help="declared loop length; compare note/rhythm/instrument signatures")
    parser.add_argument("--render", action="store_true", help="silently render only the queried window")
    parser.add_argument("--ranges", action="store_true", help="min/max MIDI per gm_*/pitched sound + badNotes (note < 20 or non-numeric)")
    parser.add_argument("--labels", action="store_true", help="event count per label in the window (unlabeled under \"\")")
    parser.add_argument("--tours", type=positive_int, help="number of tours N; needs --tour-len")
    parser.add_argument("--tour-len", type=positive_int, help="cycles per tour L; needs --tours (L >= 16)")
    parser.add_argument("--timeout", type=positive, default=120, help="seconds for each load/evaluation stage")
    parser.add_argument("--browser", help="existing Chromium executable instead of Playwright's downloaded browser")
    args = parser.parse_args(argv)
    if (args.tours is None) != (args.tour_len is None):
        parser.error("--tours and --tour-len must be given together")
    if args.tour_len is not None and args.tour_len < 16:
        parser.error("--tour-len must be at least 16 (windows start at L-15)")
    try:
        code = args.file.read_text(encoding="utf-8")
        kernel = Path(__file__).with_suffix(".js").read_text(encoding="utf-8")
    except OSError as exc:
        print("verify-track: %s" % exc, file=sys.stderr)
        return 2
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("verify-track: install playwright, then run python -m playwright install chromium", file=sys.stderr)
        return 2
    diagnostics = []

    def collect_console(message):
        text = message.text
        if message.type in ("warning", "error") or "[voicing]: unknown chord" in text:
            diagnostics.append(text)

    try:
        with sync_playwright() as playwright:
            launch = {"headless": True, "args": ["--mute-audio"],
                      "env": {key: value for key, value in os.environ.items()
                              if key.upper() != "STRUDELHUB_API_KEY"}}
            if args.browser:
                launch["executable_path"] = args.browser
            browser = playwright.chromium.launch(**launch)
            try:
                page = browser.new_page()
                page.set_default_timeout(args.timeout * 1000)
                page.on("console", collect_console)
                page.on("pageerror", lambda exc: diagnostics.append(str(exc)))
                page.goto(RECORDER, wait_until="load")
                page.wait_for_function("!!document.getElementById('rec-editor')?.editor?.repl")
                # A page-side completion marker lets Playwright enforce a deadline even
                # when evaluation or rendering hangs. No polling by the calling agent.
                page.evaluate("""({kernel, options}) => {
                    window.verifyTrackDone = false;
                    const verify = (0, eval)('(' + kernel + ')');
                    verify(options).then(result => { window.verifyTrackResult = result; })
                        .catch(error => { window.verifyTrackResult = {errors: [String(error)]}; })
                        .finally(() => { window.verifyTrackDone = true; });
                }""", {"kernel": kernel, "options": {
                    "code": code, "begin": args.begin, "cycles": args.cycles,
                    "loop": args.loop, "render": args.render, "ranges": args.ranges, "labels": args.labels,
                    "tours": args.tours, "tourLen": args.tour_len,
                }})
                page.wait_for_function("window.verifyTrackDone === true")
                result = page.evaluate("window.verifyTrackResult")
                result["diagnostics"] = list(dict.fromkeys(diagnostics))
                # Unknown voicings and other runtime warnings can silently drop music.
                result["ok"] = not result.get("errors") and not diagnostics and not result.get("badNotes")
                print(json.dumps(result, ensure_ascii=True, indent=2))
                return 0 if result["ok"] else 1
            finally:
                browser.close()
    except Exception as exc:
        print(json.dumps({"ok": False, "errors": [str(exc)], "diagnostics": diagnostics}, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())
