# Strudel gotchas (verified against `@strudel/repl@1.3.0` — the version strudelhub.com loads — docs and live sessions, October 2026)

## Errors and their cause

| Symptom (red bar) | Cause | Fix |
|---|---|---|
| `[getTrigger] error: sound gm_xxx not found! Is it loaded?` | The name does not exist in the session's sound map. GM names are Strudel's, not the official table: `gm_epiano1` exists, `gm_electric_piano_1` does not. Same for samples (`vibraphone` exists in VCSL, `vibes` does not). | `python scripts/check-track.py track.js` before pushing; `python scripts/catalog.py find <word>` to list candidates across GM, VCSL, drum machines. |
| `[eval] error: m is not a function` | A parameter/variable named `m` shadows the global the transpiler uses for every `"…"` string (`"<a b>"` → `m("<a b>")`). | Rename (`p`, `pat`, `mel`). Also avoid naming things after Strudel functions used in the body (`note`, `s`, `stack`, `dry`, `room`…). |
| `[getTrigger] error: no soundfont zone found for preset` | Note outside `keyRangeLow..keyRangeHigh` of the soundfont file (`fontloader.mjs findZone`). | `scripts/sf-range.py`. Options: shift octave, other index `.n(i)`, another GM sound or sample bank, or an oscillator if the timbre fits. |
| `[getTrigger] error: no soundfont zone found for preset` **with no note in the message** and a note range that looks fine | A leading-dot decimal after a mininotation operator: `c6@.5`, `x*.5`. The 1.3.0 mini parser reads `@.5` as weight 0 **plus a separate `.5` step** (`.` is also a token), so the lane emits numeric steps like `0.5` or `-11.5` (after `transpose(-12)`) → MIDI 0 → no zone. | Always write the leading zero: `c6@0.5`, `x*0.5`. `check-track.py` flags `[@*!/].N`. Diagnose by querying events and listing `typeof note === 'number' && note < 20`. |
| `Unexpected token (l:c)` | JS syntax (often a missing comma in `arrange`, unbalanced parenthesis). | Read the indicated line. |
| `[warn]: Can't do arithmetic on control pattern.` | `.add(5)` on a control pattern; needs `.add(note(5))`. | Transpose control patterns with `.add(note(n))` or `.transpose(n)`. |
| Silence after `/play`, no error | Audio-unlock overlay not clicked, or the user is on a different session URL. | Ask the user to click the overlay / confirm the URL. |
| `[superdough] error: duck target orbit N does not exist` | `duckorbit(N)` on a carrier (kick) fired before any event had played on orbit N — orbits are created lazily by the first event routed to them (`audioController.getOrbit` runs for the carrier's own orbit, then `duck()` looks the target up). Typical: kick on cycle 0, bass/pad entering later. | Make sure an orbit-N layer plays from cycle 0, or add a silent primer `s("sine").gain(0).orbit(N)` in the carrier's first section. `check-track.py` warns when no `.orbit(N)` exists for a `duckorbit(N)`. |

## Mininotation
- `@N` = **relative weight** in the current sequence. Inside `<…>` (one entry per cycle) `@3` stretches the entry over **3 cycles**, not 3 beats: `"<a5@3 [g5 f#5 e5]>"` lasts 4 cycles. For "A5 one bar, then a descent": `"<a5 [g5@2 f#5 e5]>"`.
- Inside `[...]`, `@` splits the bar: `"[d5@3 e5@3 f#5@2]"` = 3+3+2 eighths.
- `,` inside `[...]` = chord; `~` = rest; `*N` = repeat in time; `!N` = repeat as steps; `?` = random drop.
- Note names: regex `^[a-gA-G][#bsf]*-?[0-9]*$` → `f#5`, `bb1`, `eb3`, `as4` (s = sharp) are valid.
- Odd meters: at a fixed `setcpm`, one cycle stays one 4/4 bar. For 3/4 or 6/8 feel, put 6 (or 3, 12) events per cycle — two waltz bars per cycle. `setcpm` stays unchanged, so the pulse does not change; it is a feel change, not a signature change.
- **Decimals need a leading zero**: `@0.5`, `*0.5`, `!0.5` — never `@.5` (see the errors table).

## The transpiler rewrites every string literal — silent zero-event bugs
Every `"…"` / `'…'` / `` `…` `` literal in the code becomes `m("…")` (a mini pattern), **wherever it appears**. Verified in a session (2026-10-13):
- `const roles = ["kit", "bass"]; roles.map(r => tour[r])` → `tour[Pattern]` is `undefined` → the stack is **empty, no error**. Use accessor functions: `const roles = [p => p.kit, p => p.bass]`.
- `` const cell = "[g f]"; note(`<${cell}>`) `` interpolates a Pattern object → `[mini] parse error … but "\"" found`. Write the mini string in full (`!N` for repeats) instead of composing it from variables.
- It works only when the mapped value goes straight into `s()`/`note()`: `["gm_whistle", "gm_fiddle"].map(name => s(name))` is fine (a pattern is a valid argument).
- Rule: string literals only as **direct arguments** of Strudel calls; keys, lists and template pieces must be identifiers, functions or numbers. `check-track.py` warns on `[…"…"…].map(` and on `${` inside `note(`/`s(`/`chord(` templates.

## `arrange`
```js
arrange([cycles, pat], ...)  // pattern.mjs: section.fast(cycles) then stepcat(...).slow(total)
```
- Each section plays **its own pattern at native speed** for `cycles` cycles; an 8-entry `<...>` in an 8-cycle section plays each entry once. This does **not** freeze a shorter excerpt of a longer motif: a 2-cycle section using a 4-cycle motif can advance to the motif's second half on the next arrangement loop.
- When the intent is the same excerpt every time, freeze it explicitly: `arrange([2, motif.ribbon(0, 2)], [2, silence])`. Without `ribbon`, `motif = note("<c4 d4 e4 f4>")` yields C/D in cycles 0–2 and E/F in cycles 4–6; with it, both passages yield C/D. Apply the same window to related bass/chord lanes. Leave advancing material alone when that variation is intentional.
- Equal lane totals do not prove phrase repetition. For an altered intro/coda, query that window and the same window one full form later, e.g. `verify-track.py track.js --cycles 2 --loop 4` for the example above. No full audio render is required for this timing check.
- A ramp `saw.range(a,b).slow(n)` inside an `n`-cycle section covers **exactly** that section.
- All `$: arrange(...)` lanes must total the same number of cycles, or they drift at loop time. `check-track.py` verifies this.
- `every(n, f)` / `lastOf(n, f)` inside a section count the section's own cycles.
- Alternative: one `$: arrange([n, stack(...)], …)` where each section stacks its layers — readable per section; factor shared layers into constants and swap a layer for `silence` to mute it.
- **`struct()` fragments chords.** `note("[d4,a#4,g5]").struct("x [x x] x")` turns each chord into separate single-note haps; a following `.arp("1")` / `.arp("2")` then sees 1-note groups and returns the **first note only** — one chord voice out of three plays, silently (measured: 5 guitar events per cycle instead of 41). Write chord voices as separate lanes (`lo`, `mi`, `hi`, each with its own `struct`), or `arp` **before** `struct`. Count events per label to catch it.

## Gain, velocity, composition
- An outer `.gain(x)` **replaces** inner gains (`set` by default). To keep internal ratios inside a `stack`, use `.velocity(x)` on the inner layers: `gain *= velocity` (`superdough.mjs`).
- To multiply an existing velocity (accents): `.mul(velocity("[1 .8 .9]"))`. An outer `.velocity()` would overwrite.
- `add` on notes accepts names and numbers: `note("d5").add(note(12))`. `.transpose(n)` (semitones) is the documented form and also works on a `stack` of note patterns — transposing only the tonal layers while leaving drums outside is a key change with no percussion side effects.
- A single `.postgain(x)` on the whole `arrange(...)` is a uniform master trim (applied after effects): balance preserved, headroom gained.
- `.mul(velocity(sig))` / `.mul(gain(sig))` only act on haps that **already have** that key (`value.mjs unionWithObj`: common keys only; missing keys are copied, not multiplied — so a hap without `velocity` gets `velocity: sig` set rather than scaled, and a hap without `gain` gets `gain: sig`). For a cross-fade over heterogeneous layers, either guarantee the key in every timbre factory (set `.gain(x)` everywhere, then `mul(gain(saw…))`) or accept that `.velocity(sig)` overwrites inner accents.

## Orbits and global effects
- `room/size/roomfade/roomlp/roomdim` and `delay/delaytime/delayfeedback` feed **one bus per orbit** (`orbitBus.getReverb/getDelay`). Two patterns on the same orbit with different settings fight over one bus (docs: "unpredictable results"). One reverb = one orbit; group layers by "space".
- `roomsize/roomfade/roomlp/roomdim` rebuild the impulse response on change: never pattern them.
- `size`/`roomsize` is 0–10; values below 1 are nearly dry rooms.
- `dry(x)` = level of the direct signal (reverb unchanged) → lowering `dry` pushes a source "further away".

## Local effects are single-use per event
The signal chain has a fixed order (gain → lpf → hpf → bpf → vowel → coarse → crush → shape → distort → tremolo → compressor → pan → phaser → postgain → sends). Calling `.lpf(100).distort(2).lpf(800)` keeps only the last `lpf`; you cannot filter → distort → filter again on one event.

## Continuous signals are sampled per event
`sine`, `saw`, `tri`, `perlin`, `rand` are evaluated **once per triggered event**. `note("c3").s("sawtooth").lpf(sine.range(200, 2000).slow(4))` on a held note does not sweep — it picks one value at the onset. To hear a sweep, create more events (`.segment(16)`, `*16`) or use something truly continuous: ADSR, `penv`, `lpenv`, `vib`, `tremolo`, `phaser`, `duckorbit`.

## Absolute time vs cycles
- **Seconds**: `attack/decay/release`, `delaytime`, `roomfade`, `duckattack`, `lpattack/lpdecay`, `pattack/pdecay`.
- **Cycles**: `late/early`, `off`, `echo/echoWith`, `delaysync`, `slow/fast`, `swingBy`.
- Changing `setcpm` ⇒ re-scale the seconds by the tempo ratio (72→90: ×0.8). Prefer `delaysync(1/12)` (eighth-note triplet in 4/4) over `delaytime`.
- **Sustained sounds are one event per section, not one per cycle.** `droneOf(note("g2"))` in a 9-cycle section re-attacks every cycle: with `attack(.8).release(1.2)` on a 2.25 s cycle that pumps audibly. Use `note("g2").slow(9)` (one hap) with `clip(1.01)`. Measured: drone events at 2→4 and 4→13 after the fix, instead of 1 per cycle.
- Fading a single long event: `clip(.55).release(3)` — a `saw` on `velocity`/`gain` is sampled once at onset and does nothing on one hap.

## Soundfonts (`gm_*`)
- `.n(i)` picks the i-th file of the sound's list in `soundfonts/gm.mjs` (different ranges and timbres).
- Soundfonts honour `attack/decay/sustain/release`, `duration/clip`, `vib/vibmod`, pitch envelope; everything else goes through the shared effect chain.
- First trigger of a new sound loads it; a very first event may be late or missing. Not an error.

## Session / API facts
- Public session (no key): `/code`, `/play`, `/stop`, `/versions`, `/events` work; `GET /status` → `401 {"error":"API key required"}`. Read the current code with `hub.py peek` (SSE first event). You cannot see the red error bar — keep the track locally and ask the user to paste errors.
- Review mode (`agent_mode: review`): `POST /code` returns `status: "pending_review"`; nothing plays until the owner accepts in the browser. `hub.py push` exits 3. Check `hub.py info <id>` first.
- `/code` echoes the full code in its response: print only `status` and `version`.
- `/play` while already playing restarts the arrangement from cycle 0 — useful after a form change, intrusive during fine tuning (push without play for hot reload). [observed in sessions, not read in source]

## Misc
- Aliases: `hpf` ≡ `hcutoff`, `lpf` ≡ `cutoff`, `lpq` ≡ `resonance`, `legato` ≡ `clip`, `size` ≡ `roomsize`, `delaysync` ≡ `ds`, `tri` ≡ `triangle`, `saw` ≡ `sawtooth`, `sqr` ≡ `square`, `sin` ≡ `sine`.
- Sound names are matched **case-insensitively** (`getSound` lower-cases); bank aliases exist in lower case: `bank("tr909")`, `bank("linn")`, `bank("mpc60")` — `catalog.py banks` lists them.
- `coarse` is documented as working only in Chromium-based browsers; `crush` (bit depth 1–16) and `distort` work everywhere.
- `delayfeedback` is clamped to 0.995 (`feedbackdelay.mjs`); values ≥ 0.9 ring for a long time.
- `user` synth without `.partials([...])` silently falls back to `triangle` (logged, not an error).
- The `/learn/effects` page may come back empty on some fetches: the source is authoritative.
- `raw.githubusercontent.com/tidalcycles/strudel/...` returns 404 for `soundfonts/gm.mjs`; fetch from codeberg `uzu/strudel` at tag `@strudel/repl@1.3.0` (`raw/tag/@strudel/repl@1.3.0/packages/...`).
