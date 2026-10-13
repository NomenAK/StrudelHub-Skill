#!/usr/bin/env python3
"""Offline lint for a Strudel track before pushing it to StrudelHub.

Usage: check-track.py <track.js> [--update]

Checks (each finding is one line `LEVEL: message`):
  error  unknown sound name in s("...") / sound("...") — gm_*, samples, synths (catalog.py)
  error  unknown drum-machine bank in bank("...") or hit missing in that bank
  error  .n(i) / "name:i" index beyond the files a gm_* sound has (wraps for samples, errors for gm)
  error  sound in catalog.BROKEN_SAMPLES (shaker_small / shaker_large: Chromium cannot load them) — use tambourine
  error  function parameter or variable named `m` (shadows the mininotation global)
  error  const/let/var named after a Strudel control used in the file (shadows it)
  error  `$:` lanes whose arrange(...) totals differ (lanes drift on loop)
  warn   arrange section length that is not an integer literal (not summed)
  warn   string literal in an array that is .map/.forEach/.filter'd, or used as a key `obj["k"]` — the
         transpiler makes every "…" a mini-notation Pattern; use accessors (`p => p.kit`) instead
  warn   `${…}` inside a template literal passed to note( / s( / chord( / n( / sound( (Pattern interpolation)
  warn   backslash escapes that JSON.parse would reject if the JSON were hand-written
  info   total cycles per lane

Names are resolved against scripts/.catalog.json (built by `catalog.py update`,
built on first use if absent). --update rebuilds it first.

Exit codes: 0 no errors, 1 at least one error, 2 usage/file problem.
"""
import hashlib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import catalog  # noqa: E402
from catalog import BROKEN_SAMPLES  # noqa: E402

# Controls that users commonly name variables after; a `const room = …` breaks `.room()` for the
# whole file only when the control is used, so the check cross-references usages.
CONTROL_NAMES = {
    "s", "n", "note", "gain", "velocity", "pan", "room", "size", "dry", "delay", "orbit",
    "attack", "decay", "sustain", "release", "lpf", "hpf", "bpf", "cutoff", "clip", "speed",
    "begin", "end", "loop", "cut", "bank", "shape", "distort", "crush", "coarse", "vowel",
    "phaser", "tremolo", "postgain", "vib", "penv", "detune", "unison", "spread", "noise",
    "density", "label", "color", "freq", "chord", "scale", "voicing", "anchor", "mode",
    "stack", "cat", "seq", "arrange", "silence", "saw", "sine", "tri", "square", "rand",
    "perlin", "irand", "run", "off", "every", "mask", "struct", "late", "early", "fast", "slow",
    "ply", "rev", "jux", "echo", "swing", "degradeBy", "sometimes", "transpose", "add", "mul",
    "setcpm", "setcps", "hush",
}


def blank_out(src, keep_strings):
    """Replace comment contents (and string contents unless keep_strings) with spaces.

    Offsets and newlines are preserved so line numbers stay valid.
    """
    out = []
    i, n = 0, len(src)
    while i < n:
        c = src[i]
        if src.startswith("//", i):
            j = src.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif src.startswith("/*", i):
            j = src.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append(re.sub(r"[^\n]", " ", src[i:j]))
            i = j
        elif c in "\"'`":
            j = i + 1
            while j < n and src[j] != c:
                j += 2 if src[j] == "\\" else 1
            j = min(j + 1, n)
            if keep_strings:
                out.append(src[i:j])
            else:
                inner = re.sub(r"[^\n]", " ", src[i + 1:j - 1])
                out.append(c + inner + (c if j - i > 1 else ""))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def line_of(src, pos):
    return src.count("\n", 0, pos) + 1


def suggest(name, names):
    toks = [t for t in re.split(r"[_\d]+", name.replace("gm_", "")) if len(t) >= 3]
    scored = []
    for n in names:
        hits = sum(1 for t in toks if t in n) + sum(1 for t in toks if len(t) > 5 and t[:4] in n)
        if hits:
            scored.append((-hits, n.startswith("gm_") != name.startswith("gm_"), n))
    return [n for _, _, n in sorted(scored)[:6]]


def matching_paren(src, open_idx):
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "(":
            depth += 1
        elif src[i] == ")":
            depth -= 1
            if depth == 0:
                return i
    return -1


def lane_totals(code):
    """Return [(line_no, total_or_None, note)] for each `$:` lane."""
    starts = [m.start() for m in re.finditer(r"^[ \t]*\$:", code, re.M)]
    lanes = []
    for k, start in enumerate(starts):
        end = starts[k + 1] if k + 1 < len(starts) else len(code)
        lane = code[start:end]
        line_no = line_of(code, start)
        a = lane.find("arrange(")
        if a < 0:
            lanes.append((line_no, None, "no arrange"))
            continue
        close = matching_paren(lane, a + len("arrange"))
        body = lane[a + len("arrange("):close] if close > 0 else lane[a:]
        total, odd = 0, []
        for sec in re.finditer(r"\[\s*([^,\]]+?)\s*,", body):
            tok = sec.group(1).strip()
            if re.fullmatch(r"\d+", tok):
                total += int(tok)
            else:
                odd.append(tok)
        note = ("non-integer section lengths not summed: " + ", ".join(odd)) if odd else ""
        lanes.append((line_no, total, note))
    return lanes


def string_literals(code_strings):
    """Yield (pos, text) for every quoted literal (quotes stripped)."""
    for m in re.finditer(r"\"((?:[^\"\\]|\\.)*)\"|'((?:[^'\\]|\\.)*)'|`((?:[^`\\]|\\.)*)`", code_strings):
        yield m.start(), (m.group(1) or m.group(2) or m.group(3) or "")


def mini_names(text):
    """Sound names used inside a mininotation string: ('name', index_or_None)."""
    out = []
    for tok in re.findall(r"[A-Za-z_][A-Za-z0-9_]*(?::\d+)?", text):
        name, _, idx = tok.partition(":")
        out.append((name, int(idx) if idx else None))
    return out


def call_args(code_strings, func):
    """Yield (pos, literal) for `.func("…")` / `func("…")` string arguments."""
    for m in re.finditer(r"(?<![A-Za-z0-9_])%s\s*\(\s*(\"[^\"]*\"|'[^']*'|`[^`]*`)" % func, code_strings):
        yield m.start(1), m.group(1)[1:-1]


def external_sample_names(code_strings):
    """Names added by samples(...) calls in the file: github shortcuts / strudel.json URLs are fetched
    (cached in scripts/.external-<hash>.json), inline object maps are parsed for their keys.
    Returns ({name: count}, [warnings])."""
    names, warns = {}, []
    for m in re.finditer(r"(?<![A-Za-z0-9_.])samples\s*\(\s*([\"'`])([^\"'`]+)\1", code_strings):
        spec = m.group(2)
        url = catalog.sample_map_url(spec)
        if not url:
            warns.append("line %d: samples(%r): cannot resolve; names from it are not checked"
                         % (line_of(code_strings, m.start()), spec))
            continue
        cache = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             ".external-%s.json" % hashlib.sha1(url.encode()).hexdigest()[:10])
        try:
            if os.path.isfile(cache):
                with open(cache, encoding="utf-8") as f:
                    ext = json.load(f)
            else:
                ext = catalog.external_names(spec)
                with open(cache, "w", encoding="utf-8") as f:
                    json.dump(ext, f)
            names.update(ext)
        except Exception as e:  # noqa: BLE001
            warns.append("line %d: samples(%r): fetch failed (%s); names from it are not checked"
                         % (line_of(code_strings, m.start()), spec, e))
    for m in re.finditer(r"(?<![A-Za-z0-9_.])samples\s*\(\s*\{", code_strings):
        close = matching_brace(code_strings, m.end() - 1)
        body = code_strings[m.end():close] if close > 0 else ""
        for key in re.findall(r"(?:^|[{,])\s*[\"']?([A-Za-z_][A-Za-z0-9_]*)[\"']?\s*:", body):
            names[key.lower()] = 1
    return names, warns


def matching_brace(src, open_idx):
    depth = 0
    for i in range(open_idx, len(src)):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return i
    return -1


def check_sounds(code_strings, cat):
    """Validate s()/sound() names, bank() names and indices. Returns (error lines, warning lines).

    Lookups are case-insensitive: superdough's getSound() lower-cases the name.
    """
    errs = []
    names = {k.lower(): v for k, v in catalog.all_names(cat).items()}
    ext, warns = external_sample_names(code_strings)
    names.update({k: ("external", c) for k, c in ext.items()})
    bank_hits = {k.lower(): v for k, v in catalog.banks(cat).items()}
    # bank(...) literals: collect the set of banks in use (for name resolution) and validate them
    banks_used = set()
    for pos, lit in list(call_args(code_strings, "bank")):
        for b, _ in mini_names(lit):
            if b.lower() not in bank_hits:
                key = re.sub(r"[^a-z0-9]", "", b.lower())
                hint = [x for x in sorted(catalog.banks(cat)) if key in x.lower() or x.lower()[-len(key):] in key or key[-3:] in x.lower()[-5:]][:5]
                errs.append("line %d: unknown bank %s%s" % (line_of(code_strings, pos), b,
                            (" (did you mean: %s)" % ", ".join(hint)) if hint else ""))
            else:
                banks_used.add(b.lower())
    for func in ("s", "sound"):
        for pos, lit in call_args(code_strings, func):
            for name, idx in mini_names(lit):
                name = name.lower()
                if name in ("~", "-", "_"):
                    continue
                if name in BROKEN_SAMPLES:
                    errs.append("line %d: %s is broken — %s" % (line_of(code_strings, pos), name, BROKEN_SAMPLES[name]))
                    continue
                if name in names:
                    src, count = names[name]
                    if idx is not None and src == "gm" and idx >= count:
                        errs.append("line %d: %s:%d — %s has only %d file(s) (.n(0..%d))"
                                    % (line_of(code_strings, pos), name, idx, name, count, count - 1))
                    continue
                if banks_used and any(("%s_%s" % (b, name)) in names for b in banks_used):
                    continue
                if banks_used and name in {h for b in banks_used for h in bank_hits.get(b, ())}:
                    continue
                # generic drum abbreviation with a bank that lacks it
                if banks_used and any(name in hits for hits in bank_hits.values()):
                    errs.append("line %d: hit %s not present in bank(s) %s" %
                                (line_of(code_strings, pos), name, ", ".join(sorted(banks_used))))
                    continue
                if name in ("bd", "sd", "hh", "oh", "cp", "rim", "cr", "rd", "ht", "mt", "lt",
                            "sh", "cb", "tb", "perc", "misc", "fx", "brk"):
                    continue  # uzu-drumkit defaults; resolved without a bank
                hint = suggest(name, names)
                errs.append("line %d: unknown sound %s%s" % (line_of(code_strings, pos), name,
                            (" (did you mean: %s)" % ", ".join(hint)) if hint else ""))
    # .n(i) literal on a gm_* sound in the same chain (single-line heuristic)
    for m in re.finditer(r"s\(\s*[\"'](gm_[a-z0-9_]+)[\"']\s*\)[^\n]*?\.n\(\s*(\d+)\s*\)", code_strings):
        name, idx = m.group(1), int(m.group(2))
        if name in names and idx >= names[name][1]:
            errs.append("line %d: .n(%d) but %s has only %d file(s)" %
                        (line_of(code_strings, m.start()), idx, name, names[name][1]))
    return errs, warns


def check_transpiler_traps(code, code_strings):
    """Warnings for the Strudel transpiler turning EVERY "…" literal into a mini-notation Pattern.

    `code` (strings blanked, quotes kept) is used for structure so text inside strings never matches.
    """
    warns = []
    for m in re.finditer(r"\[\s*\"[^\"]*\"(?:\s*,\s*\"[^\"]*\")*\s*\]\s*\.(map|forEach|filter)\b", code):
        warns.append("line %d: array of string literals followed by .%s(…): each \"…\" becomes a mini-notation "
                     "Pattern, not a JS string. This works only when the mapped value is passed straight to "
                     "s()/note() (they accept a pattern); as a key, in string ops or comparisons it silently "
                     "yields undefined/0 events. Use accessors (`p => p.kit`) instead of string keys"
                     % (line_of(code, m.start()), m.group(1)))
    for m in re.finditer(r"[\w\])]\[\s*\"", code):
        warns.append("line %d: indexing with a quoted literal `x[\"…\"]`: the literal becomes a mini-notation "
                     "Pattern, so the lookup returns undefined (0 events, no error). Use an accessor "
                     "(`o => o.key`) or dot access instead" % line_of(code, m.start()))
    for m in re.finditer(r"(?<![A-Za-z0-9_])(note|s|chord|n|sound)\s*\(\s*`((?:[^`\\]|\\.)*)`", code_strings):
        if code[m.start(1)] != m.group(1)[0] or "${" not in m.group(2):
            continue
        warns.append("line %d: `${…}` inside the template literal passed to %s(): interpolating a Pattern "
                     "inserts a Pattern object and the mini parser fails (`parse error … but \"\\\"\" found`). Write the mini string "
                     "in full (`!N` for repeats), or combine patterns with methods (.add, stack) instead"
                     % (line_of(code_strings, m.start()), m.group(1)))
    return warns


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print((__doc__ or "").strip())
        return 2
    path = argv[1]
    if not os.path.isfile(path):
        print("error: file not found: %s" % path)
        return 2
    cat = catalog.build() if "--update" in argv[2:] else catalog.load()
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    code = blank_out(raw, keep_strings=False)
    code_strings = blank_out(raw, keep_strings=True)
    errors = 0

    # 1. sound / bank names and indices (incl. names added by samples(...) calls)
    sound_errs, sound_warns = check_sounds(code_strings, cat)
    for w in sound_warns:
        print("warn: " + w)
    for e in sound_errs:
        errors += 1
        print("error: " + e)

    # 2. `m` as a parameter or variable name
    m_lines = sorted({line_of(code, u.start()) for u in
                      re.finditer(r"(?:^|[(,\s\[])m\s*(?:=>|,|\)|\])|\b(?:const|let|var)\s+m\b", code, re.M)})
    for ln in m_lines:
        errors += 1
        print("error: line %d: `m` used as a name (shadows the mininotation global); rename it" % ln)

    # 3. names declared as variables that the file also uses as a Strudel function/control
    for decl in re.finditer(r"\b(?:const|let|var|function)\s+([A-Za-z_]\w*)", code):
        name = decl.group(1)
        if name not in CONTROL_NAMES:
            continue
        rest = code[decl.end():]
        if re.search(r"\.%s\s*\(" % name, rest) or re.search(r"(?<![\w.$])%s\s*\(" % name, rest):
            errors += 1
            print("error: line %d: `%s` declared as a variable but also used as a Strudel function; rename it"
                  % (line_of(code, decl.start()), name))

    # 4. lane totals
    totals = []
    for line_no, total, note in lane_totals(code):
        if total is None:
            print("info: lane at line %d: %s" % (line_no, note))
            continue
        totals.append(total)
        print("info: lane at line %d: arrange total = %d cycles" % (line_no, total))
        if note:
            print("warn: line %d: %s" % (line_no, note))
    if len(set(totals)) > 1:
        errors += 1
        print("error: arrange lanes have different totals %s; they will drift when looping" % sorted(set(totals)))

    # 6. duckorbit(N) whose target orbit N is never addressed by .orbit(N) in the file.
    # The orbit is created lazily by its first event; a kick ducking it before that logs
    # `duck target orbit N does not exist`. We can only check existence statically, not timing.
    orbits_used = set(re.findall(r"\.orbit\(\s*(\d+)\s*\)", code_strings))
    orbits_used |= {o for lit in re.findall(r"\.orbit\(\s*\"([^\"]*)\"", code_strings) for o in re.findall(r"\d+", lit)}
    for m in re.finditer(r"\.duck(?:orbit)?\(\s*(?:\"([^\"]*)\"|(\d+))\s*\)", code_strings):
        for target in re.findall(r"\d+", m.group(1) or m.group(2)):
            if target not in orbits_used:
                print("warn: line %d: duckorbit(%s) but nothing in the file uses .orbit(%s); the browser will log "
                      "`duck target orbit %s does not exist`" % (line_of(code_strings, m.start()), target, target, target))
            else:
                print("info: line %d: duckorbit(%s) — make sure an .orbit(%s) layer plays from cycle 0 (or add a silent primer)"
                      % (line_of(code_strings, m.start()), target, target))
    # 5. escapes that break hand-written JSON (harmless when pushed via jq/json.dumps)
    for esc in re.finditer(r"\\[^\"\\/bfnrtu\n]", raw):
        print("warn: line %d: escape %r is invalid in JSON; fine when pushed via push.sh/hub.py"
              % (line_of(raw, esc.start()), esc.group(0)))
    # 7. mininotation operators followed by a leading-dot decimal (`c6@.5`, `x*.5`, `bd!.5`).
    # The 1.3.0 mini parser reads `@.5` as weight 0 + a separate `.5` step (`.` is also the
    # "elongate"/layer token), yielding number steps like 0.5 or -11.5 instead of notes:
    # `[getTrigger] error: no soundfont zone found for preset` with no note name in the message.
    for pos, text in string_literals(code_strings):
        for m in re.finditer(r"[@*!/]\s*\.\d", text):
            errors += 1
            print("error: line %d: mininotation %r — write a leading zero (`@0.5`, `*0.5`); "
                  "`@.5` is parsed as weight 0 plus a `.5` step" % (line_of(code_strings, pos), m.group(0)))

    # 8-9. transpiler string-literal traps (array .map / quoted keys / Pattern interpolation)
    for w in check_transpiler_traps(code, code_strings):
        print("warn: " + w)

    print("result: %d error(s)" % errors)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
