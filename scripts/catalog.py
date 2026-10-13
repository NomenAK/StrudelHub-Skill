#!/usr/bin/env python3
"""Catalogue of every sound name available in a StrudelHub session.

StrudelHub loads `@strudel/repl@1.3.0` whose prebake registers, in this order:
  synths (sine sawtooth square triangle supersaw pulse white pink brown crackle user …)
  zzfx (z_sine z_sawtooth z_square z_triangle z_tan z_noise)
  GM soundfonts (gm_* from packages/soundfonts/gm.mjs, same tag)
  samples: tidal-drum-machines, piano, Dirt-Samples, vcsl, mridangam (felixroos/dough-samples)
           uzu-drumkit (tidalcycles/uzu-drumkit/strudel.json)

Usage:
  catalog.py update                 fetch everything, write scripts/.catalog.json
  catalog.py find <substring>...    names containing every substring (case-insensitive); (broken: …) marks unloadable ones
  catalog.py list [bank|gm|vcsl|dirt|drums|synth|zzfx|mridangam|uzu]
  catalog.py banks                  drum-machine bank names with the hits each one has
  catalog.py info <name>            where a name comes from and how many files it has; (broken: …) if unloadable
  catalog.py range <vcsl_or_piano_name>   sampled note range of a pitched sample instrument
  catalog.py external <spec>        names in an external sample map: `github:user/repo[/branch]`
                                    or a strudel.json URL (what `samples(...)` in a track would add)

Any command other than `update` works offline from the cache; without a cache it
fetches once. Exit codes: 0 ok, 1 not found, 2 usage/network.
"""
import json
import os
import re
import sys
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, ".catalog.json")
STRUDEL_TAG = "@strudel/repl@1.3.0"  # version loaded by strudelhub.com (see references/api.md)
GM_URL = "https://codeberg.org/uzu/strudel/raw/tag/%s/packages/soundfonts/gm.mjs" % STRUDEL_TAG
DOUGH = "https://raw.githubusercontent.com/felixroos/dough-samples/main/"
SAMPLE_MAPS = {
    "drums": DOUGH + "tidal-drum-machines.json",
    "piano": DOUGH + "piano.json",
    "dirt": DOUGH + "Dirt-Samples.json",
    "vcsl": DOUGH + "vcsl.json",
    "mridangam": DOUGH + "mridangam.json",
    "uzu": "https://raw.githubusercontent.com/tidalcycles/uzu-drumkit/main/strudel.json",
}
ALIAS_URL = "https://raw.githubusercontent.com/todepond/samples/main/tidal-drum-machines-alias.json"
SYNTHS = ["sine", "sawtooth", "square", "triangle", "sin", "saw", "sqr", "tri", "pulse",
          "supersaw", "user", "white", "pink", "brown", "crackle", "bytebeat"]
ZZFX = ["z_sine", "z_sawtooth", "z_square", "z_triangle", "z_tan", "z_noise"]
TIMEOUT = 60

# Catalogued but unloadable in Chromium: GitHub serves these VCSL paths with a duplicate
# Content-Disposition header, so every fetch fails with
# net::ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_DISPOSITION (every .n() variant). {name: reason}.
BROKEN_SAMPLES = {
    name: ("Chromium cannot load it: GitHub serves …/%s/… with duplicate Content-Disposition headers "
           "(net::ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_DISPOSITION) for every variant; use tambourine instead" % folder)
    for name, folder in (("shaker_small", "Shaker%2C%20Small"), ("shaker_large", "Shaker%2C%20Large"))
}


def broken_suffix(name):
    """' (broken: reason)' for names in BROKEN_SAMPLES, else ''."""
    reason = BROKEN_SAMPLES.get(name.lower())
    return " (broken: %s)" % reason if reason else ""


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "strudelhub-catalog/1.0"})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_gm(text):
    """{gm_name: [file, ...]} ignoring //-commented entries."""
    result, current = {}, None
    for line in text.splitlines():
        pos = line.find("//")
        if pos >= 0:
            line = line[:pos]
        head = re.match(r"\s*(gm_[a-z0-9_]+)\s*:\s*\[?", line)
        if head:
            current = head.group(1)
            result[current] = []
        if current:
            result[current].extend(re.findall(r"'([^']+)'", line))
        if "]" in line and current:
            current = None
    return result


def build():
    cat = {"strudel_tag": STRUDEL_TAG, "sources": {}}
    gm = parse_gm(fetch(GM_URL))
    cat["sources"]["gm"] = {k: len(v) for k, v in gm.items()}
    for key, url in SAMPLE_MAPS.items():
        data = json.loads(fetch(url))
        cat["sources"][key] = {
            k: (len(v) if isinstance(v, (list, dict)) else 1)
            for k, v in data.items() if not k.startswith("_")
        }
    # bank aliases: `bank("tr909")` works because aliasBank registers `<alias>_<hit>` in lower case
    alias = json.loads(fetch(ALIAS_URL))
    aliased = {}
    for n, c in cat["sources"]["drums"].items():
        bank, _, hit = n.partition("_")
        names = alias.get(bank)
        for a in (names if isinstance(names, list) else [names] if names else []):
            aliased[("%s_%s" % (a, hit)).lower()] = c
    cat["sources"]["drums_alias"] = aliased
    cat["sources"]["synth"] = {s: 1 for s in SYNTHS}
    cat["sources"]["zzfx"] = {s: 1 for s in ZZFX}
    with open(CACHE, "w", encoding="utf-8") as f:
        json.dump(cat, f, indent=0, sort_keys=True)
    return cat


def load():
    if os.path.isfile(CACHE):
        with open(CACHE, encoding="utf-8") as f:
            return json.load(f)
    try:
        return build()
    except Exception as e:  # noqa: BLE001
        print("error: cannot build catalogue: %s" % e)
        sys.exit(2)


def all_names(cat):
    """{name: (source, count)}; drum-machine hits also exposed as bank/hit pairs."""
    out = {}
    for src, names in cat["sources"].items():
        for n, c in names.items():
            out[n] = (src, c)
    return out


def banks(cat):
    """{bank_name: {hits}} including lower-case aliases (tr909, linn, mpc60…)."""
    out = {}
    for src in ("drums", "drums_alias"):
        for n in cat["sources"].get(src, {}):
            bank, _, hit = n.partition("_")
            out.setdefault(bank, set()).add(hit)
    return out


def resolve(cat, name, bank=None):
    """Return (full_name, source, count) or None. `bank` applies the Strudel bank() prefix."""
    names = all_names(cat)
    if bank:
        full = "%s_%s" % (bank, name)
        if full in names:
            return (full,) + names[full]
        return None
    if name in names:
        return (name,) + names[name]
    return None


def sample_map_url(spec):
    """Turn a samples() argument into a strudel.json URL (same rule as superdough's `github:` shortcut)."""
    if spec.startswith("github:"):
        parts = spec[7:].split("/")
        user, repo = parts[0], parts[1]
        branch = parts[2] if len(parts) > 2 else "main"
        return "https://raw.githubusercontent.com/%s/%s/%s/strudel.json" % (user, repo, branch)
    if spec.startswith("http"):
        return spec if spec.endswith(".json") else spec.rstrip("/") + "/strudel.json"
    return None


def external_names(spec):
    """{name: count} for an external sample map; {} when the spec is not a URL/github shortcut."""
    url = sample_map_url(spec)
    if not url:
        return {}
    data = json.loads(fetch(url))
    return {k.lower(): (len(v) if isinstance(v, (list, dict)) else 1)
            for k, v in data.items() if not k.startswith("_")}


NOTE_RE = re.compile(r"^([A-Ga-g])([#sb]?)(-?\d+)$")


def note_midi(name):
    m = NOTE_RE.match(name)
    if not m:
        return None
    base = {"c": 0, "d": 2, "e": 4, "f": 5, "g": 7, "a": 9, "b": 11}[m.group(1).lower()]
    acc = {"#": 1, "s": 1, "b": -1, "": 0}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + base + acc


def pitched_range(name):
    """(low, high, count) of a note-keyed sample (VCSL / piano); None if unpitched or unknown."""
    for key, url in SAMPLE_MAPS.items():
        if key not in ("vcsl", "piano"):
            continue
        data = json.loads(fetch(url))
        entry = data.get(name)
        if isinstance(entry, dict):
            midis = [v for v in (note_midi(k) for k in entry) if v is not None]
            if midis:
                return min(midis), max(midis), len(entry)
        if entry is not None:
            return None
    return None


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print((__doc__ or "").strip())
        return 2
    cmd, args = argv[1], argv[2:]
    if cmd == "update":
        cat = build()
        print("catalogue written: %s" % CACHE)
        for src, names in sorted(cat["sources"].items()):
            print("  %-10s %d names" % (src, len(names)))
        return 0
    cat = load()
    if cmd == "find":
        if not args:
            print("usage: catalog.py find <substring>...")
            return 2
        toks = [a.lower() for a in args]
        hits = [(n, s, c) for n, (s, c) in sorted(all_names(cat).items()) if all(t in n.lower() for t in toks)]
        for n, s, c in hits:
            print("%-40s %-10s %d%s" % (n, s, c, broken_suffix(n)))
        return 0 if hits else 1
    if cmd == "list":
        src = args[0] if args else None
        if src == "bank":
            for b in sorted(banks(cat)):
                print(b)
            return 0
        srcs = [src] if src else sorted(cat["sources"])
        for s in srcs:
            if s not in cat["sources"]:
                print("error: unknown source %s (choose: %s)" % (s, ", ".join(sorted(cat["sources"]))))
                return 2
            for n, c in sorted(cat["sources"][s].items()):
                print("%-40s %-10s %d%s" % (n, s, c, broken_suffix(n)))
        return 0
    if cmd == "banks":
        for b, hits in sorted(banks(cat).items()):
            print("%-24s %s" % (b, " ".join(sorted(hits))))
        return 0
    if cmd == "info":
        if not args:
            print("usage: catalog.py info <name>")
            return 2
        r = resolve(cat, args[0])
        if not r:
            print("not found: %s" % args[0])
            return 1
        print("%s: source=%s files=%d (.n(0..%d))%s" % (r[0], r[1], r[2], max(r[2] - 1, 0), broken_suffix(r[0])))
        return 0
    if cmd == "range":
        if not args:
            print("usage: catalog.py range <name>")
            return 2
        r = pitched_range(args[0])
        if r is None:
            print("%s: unpitched sample or not a VCSL/piano name (gm_*: use sf-range.py)" % args[0])
            return 1
        lo, hi, n = r
        names = ["c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b"]
        nn = lambda v: "%s%d" % (names[v % 12], v // 12 - 1)
        print("%s: %d samples, %s-%s (midi %d-%d); outside this range the nearest sample is pitch-shifted"
              % (args[0], n, nn(lo), nn(hi), lo, hi))
        return 0
    if cmd == "external":
        if not args:
            print("usage: catalog.py external <github:user/repo[/branch] | url>")
            return 2
        try:
            ext = external_names(args[0])
        except Exception as e:  # noqa: BLE001
            print("error: cannot fetch %s: %s" % (args[0], e))
            return 2
        if not ext:
            print("not a resolvable sample map: %s" % args[0])
            return 1
        for n, c in sorted(ext.items()):
            print("%-40s %d" % (n, c))
        print("total: %d" % len(ext))
        return 0
    print("unknown command: %s" % cmd)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
