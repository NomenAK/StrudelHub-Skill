#!/usr/bin/env python3
"""Print the playable MIDI range of the soundfont files behind a Strudel gm_* name.

Usage: sf-range.py <gm_name> [index]

Strudel's `.n(i)` selects entry i of the gm.mjs list for <gm_name>. For each
entry (or only <index>) this fetches the soundfont JS and prints:

    index file lowMIDI-highMIDI (lowNote-highNote) zones=N

Note names use sharps, octave numbering of Strudel (MIDI 60 = c4).
Exit codes: 0 ok, 1 some file failed to fetch/parse, 2 usage / unknown name / bad index.
"""
import re
import sys
import urllib.error
import urllib.request

GM_URL = "https://codeberg.org/uzu/strudel/raw/tag/@strudel/repl@1.3.0/packages/soundfonts/gm.mjs"  # tag loaded by strudelhub.com
SF_URL = "https://felixroos.github.io/webaudiofontdata/sound/{}.js"
TIMEOUT = 30
NOTES = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]


def note_name(midi):
    return "%s%d" % (NOTES[midi % 12], midi // 12 - 1)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "strudelhub-sf-range/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_comment(line):
    pos = line.find("//")
    return line if pos < 0 else line[:pos]


def parse_gm(text):
    """Return {gm_name: [file, ...]} ignoring // commented lines/entries."""
    lines = [strip_comment(l) for l in text.splitlines()]
    header = re.compile(r"^\s*['\"]?(gm_\w+)['\"]?\s*:\s*\[(.*)$")
    result = {}
    i = 0
    while i < len(lines):
        m = header.match(lines[i])
        if not m:
            i += 1
            continue
        name, rest = m.group(1), m.group(2)
        chunk = [rest]
        while "]" not in chunk[-1]:
            i += 1
            if i >= len(lines):
                break
            chunk.append(lines[i])
        body = "\n".join(chunk)
        body = body[: body.index("]")] if "]" in body else body
        result[name] = re.findall(r"['\"]([^'\"]+)['\"]", body)
        i += 1
    return result


def zone_range(js):
    lows = [int(v) for v in re.findall(r"keyRangeLow\s*:\s*(\d+)", js)]
    highs = [int(v) for v in re.findall(r"keyRangeHigh\s*:\s*(\d+)", js)]
    if not lows or not highs:
        raise ValueError("no keyRangeLow/keyRangeHigh found")
    return min(lows), max(highs), len(lows)


def main(argv):
    if len(argv) not in (2, 3) or argv[1] in ("-h", "--help"):
        print("usage: sf-range.py <gm_name> [index]", file=sys.stderr)
        return 2
    gm_name = argv[1]
    only = None
    if len(argv) == 3:
        try:
            only = int(argv[2])
        except ValueError:
            print("index must be an integer: %r" % argv[2], file=sys.stderr)
            return 2

    try:
        gm = parse_gm(fetch(GM_URL))
    except (urllib.error.URLError, OSError) as e:
        print("cannot fetch gm.mjs: %s" % e, file=sys.stderr)
        return 1

    files = gm.get(gm_name)
    if files is None:
        near = sorted(k for k in gm if gm_name in k or k in gm_name)
        print("unknown gm name: %s" % gm_name, file=sys.stderr)
        if near:
            print("similar: " + ", ".join(near), file=sys.stderr)
        return 2
    if only is not None and not 0 <= only < len(files):
        print("index %d out of range for %s (0..%d)" % (only, gm_name, len(files) - 1), file=sys.stderr)
        return 2

    failed = False
    for idx, f in enumerate(files):
        if only is not None and idx != only:
            continue
        try:
            lo, hi, zones = zone_range(fetch(SF_URL.format(f)))
        except (urllib.error.URLError, OSError, ValueError) as e:
            failed = True
            print("%d %s ERROR: %s" % (idx, f, e))
            continue
        print("%d %s %d-%d (%s-%s) zones=%d" % (idx, f, lo, hi, note_name(lo), note_name(hi), zones))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
