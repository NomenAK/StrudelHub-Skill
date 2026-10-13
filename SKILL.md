---
name: strudelhub
description: Compose, push and iterate live Strudel music on StrudelHub (https://strudelhub.com) sessions. Use when the user asks to create, play, modify, remix or arrange a Strudel track, cover a song in Strudel, work from a MusicXML import or a gallery piece, or debug a Strudel error (red error bar, "sound … not found", "no soundfont zone", "m is not a function", etc.).
---

# StrudelHub — live Strudel sessions

You drive a remote Strudel session; the user's browser renders the audio with **`@strudel/repl@1.3.0`**. **You hear nothing**: never claim it "sounds good". Say what changed, with numbers, and ask for feedback (or for a screenshot of `_scope()` / `_pianoroll()`).

## Creative ownership — main model only
- The main model MUST personally compose, arrange and write the musical code: melody, harmony, form, orchestration, sound design, transitions and expressive mix choices remain its responsibility. Keep one artistic direction and leave room for its creativity; references and templates are aids, not prescriptions.
- Subagents MAY be used **only for bounded, read-only factual research**: locating scores/MIDI, extracting source notes and timing, checking provenance, catalogues or pinned API documentation. Their deliverable is evidence with sources and uncertainties, never a composed part or an artistic plan.
- Extracting notes from a machine-readable file (MIDI, MusicXML) requires execution (shell/Python parser): that extraction belongs to the **main model**, or to a research agent explicitly given an execution tool — NEVER to a web/read-only scout, which MUST state it cannot parse the binary rather than silently omit or guess its contents. Every research brief MUST state which channels the agent actually has (web only, file read, shell/Python).
- NEVER delegate composition, arrangement, timbre factories, track implementation, artistic review, runtime verification or session operations. Research agents must not edit the track, access credentials or push/play a session. The main model integrates the evidence and makes all creative decisions.

## Proportionate verification — short path to listening
- Default: read the current session code, reuse already verified controls/sounds, lint the final local file, push safely, then ask for listening feedback. Reuse evidence for unchanged code at the same pinned version; do not rediscover the runtime or recheck every asset on each iteration.
- Browser automation is **targeted, not a mandatory ritual**. Use it for an unresolved execution risk (unfamiliar API, complex section timing, reported error), a significant unexercised behavior, or an explicit user request. A small balance change does not justify another full browser audit.
- When needed, run `python scripts/verify-track.py <Project>/track.js --begin 0 --cycles 4` instead of manually exploring browser internals. It uses one isolated `/api/recorder` page, checks the pinned version, evaluates without starting, queries events and resolves sound names/indices. For form changes, use `--loop TOTAL_CYCLES` and select a window covering the affected join; this compares note/rhythm/instrument signatures in that window, not all effects or the whole piece. `--labels` counts events per `.label()` and `--ranges` lists min/max MIDI per pitched sound plus numeric/out-of-range notes; `--tours N --tour-len L` does both for every tour of a long piece.
- **A valid sound registry is not a working lane.** Several real bugs produce zero or too few events with no error (chord voices lost through `struct`→`arp`, string keys turned into patterns, `@.5` weights). Before calling a lane verified, compare its event count per label on one cycle with what you intended (strums × voices, 12 hats, one chord per pulse…).
- Add `--render` only for an audio-specific issue: it silently renders the selected window and reports peak/RMS. Full-piece rendering, exhaustive note comparison and waveform screenshots are OPTIONAL, not routine delivery. The verifier closes its browser automatically. Its default registry check does not download samples or prove soundfont pitch coverage; diagnostics and exit status identify failures without claiming musical quality.
- Stop checking once the relevant risk is resolved; rerun only checks invalidated by a later edit. Report what was actually exercised. Lint/API acceptance do not prove audio correctness; rendering and peak levels do not prove musical quality. `/status` does not expose browser audio errors, even with a key; ask the user to copy the red error bar when needed.

## Resources
| File | Read it when |
|---|---|
| `references/api.md` | Before the first API call (auth matrix by visibility, review mode, SSE, versions, gallery, JSON escaping) |
| `references/strudel-gotchas.md` | **Always** before writing code, and whenever an error shows up |
| `references/effects-cheatsheet.md` | Before using a control/effect (units, semantics, single-use-per-event rule, visual feedback) |
| `references/samples.md` | Before any `s("…")` / `bank("…")`: drum machines (71 banks), VCSL instruments (128), piano, breaks, sample manipulation |
| `references/soundfonts.md` | Before using any `gm_*` sound (exact names, MIDI ranges) |
| `references/tonal.md` | Chord charts → `chord().voicing()`, scales, arps — covers and anything harmonic |
| `references/stepwise.md` | Polymeters, odd phrase lengths, step-based fills |
| `references/arrangement.md` | To shape a multi-section piece: form, transitions, movement, humanisation, stereo (devices, not rules) |
| `references/long-form.md` | Very long pieces (15–60 min) that vary one theme tour after tour: arc, dimensions, role objects, bridges by role identity, proportionate checks |
| `scripts/hub.py <cmd>` | Python-only client: `new`, `info`, `status`, `peek`, `push`, `play`, `stop`, `versions`, `version`, `revert`, `explore`, `piece` |
| `scripts/check-track.py <file.js>` | **Offline lint before every push**: unknown/broken sounds and banks (incl. names added by `samples('github:…')` calls), bad `.n(i)`, `m` as a name, control shadowing, unequal lane totals, `@.5` weights, string-key / `${}` transpiler traps |
| `scripts/verify-track.py <file.js> [--begin 0 --cycles 4] [--loop N] [--render] [--labels] [--ranges] [--tours N --tour-len L]` | Targeted pinned-runtime smoke, stopped transport, sound registry checks; optional loop comparison, label counts, pitch ranges, per-tour sweep and silent audio render. Requires Playwright + Chromium; see script `--help`. |
| `scripts/catalog.py find <word>` · `range <vcsl_name>` · `external github:user/repo` | Search every sound available in a session (gm_*, VCSL, drum machines, synths); sampled range of a VCSL/piano instrument; names in an external sample pack. `catalog.py update` refreshes the cache |
| `scripts/diff-versions.py <id> <vA> <vB\|current>` | Unified diff between two versions (or vs. current code) |
| `scripts/sf-range.py <gm_name> [index]` | Real MIDI range of a GM preset |
| `scripts/new-session.sh` / `push.sh` / `status.sh` | Bash + `jq` equivalents |
| `templates/multi-section.js` | Skeleton for a structured piece (GM/synth, chords + lanes) |
| `templates/breaks.js` | Skeleton for sample-based music (hip-hop / jungle): break slicing, drum machine, `rootNotes` bass, `ireal` voicings |
| `templates/techno.js` | Skeleton for four-on-the-floor: 909 kit, `duckorbit` sidechain, acid line (`lpenv`/`penv`), riser → drop |
| `templates/long-form.js` | Skeleton for a long piece in tours: role objects, `tourOf`, bridges that cross-fade only changed roles, `freeze`, silent primer |

The client/catalogue/lint scripts need only `python` 3 (stdlib). The optional runtime verifier additionally needs `python -m pip install playwright` and `python -m playwright install chromium` once; `--browser PATH` can reuse an existing Chromium executable. It executes trusted local code in a fresh browser profile, is not a security sandbox, and receives no API key. The `.sh` scripts also need Bash (Git Bash on Windows) and `jq`. API key only via `STRUDELHUB_API_KEY`; without it, sessions are public and **no Authorization header** is sent.

## Local project layout — one folder per track
- Create **one subfolder per track/project** in the workspace before writing any code: `<workspace>/<ProjectName>/` (short CamelCase or kebab-case slug — e.g. `FairyFountain/`, `LostWoods/`). NEVER write track files at the workspace root, and NEVER mix two tracks in one folder.
- Inside the project folder:
  - `track.js` — the single current working copy; the only file linted, verified and pushed for that track.
  - `versions/v001.js`, `v002.js`, … — an immutable snapshot of **every pushed version**, named after the server version number returned by the push (zero-padded to 3 digits). After each accepted push, copy `track.js` to `versions/vNNN.js`; NEVER edit or delete a snapshot. If a snapshot is missing locally (e.g. an older push), restore it with `hub.py version <id> <v> -o <Project>/versions/vNNN.js`.
  - `sources/` — research artifacts behind a cover (downloaded MIDI/scores, extraction notes) so the transcription stays auditable.
- The server keeps its own version history; the local `versions/` mirrors it so every step is diffable and recoverable offline, and the current `track.js` is never the only copy of a previous state.

## Step 0 — Light interview (one message, then act)
Ask only what the user has not already said. Group everything in **one** message, give your defaults, and proceed with those defaults if the answer is partial:

1. **API key?** Optional. If given: `export STRUDELHUB_API_KEY=…` once for the shell session, never echo/log/write it. Some agent shells do **not** keep exports between calls (observed on Windows): persist the key in the OS user environment (`setx` / shell profile) and re-read it at the start of each command (`export STRUDELHUB_API_KEY="$(python -c "import winreg; …QueryValueEx(…,'STRUDELHUB_API_KEY')[0]")"`), still never printing it. After `hub.py new`, require `visibility: private` when a key was expected; a session created without the key is owner-less and public — do not reuse it, create a new one. Without a key, say that `/status` will be unreadable (you will read code via `hub.py peek` but will not see the red error bar).
2. **Session**: an existing URL/id to continue, a gallery piece to remix (`hub.py new --from-piece`), or create a new one?
3. **Style / mood** in a few words, BPM if known.
4. **One reference** (artist, track, game, film, era) — to borrow the idiom, not to copy the material.
5. **Form**: sections they want (intro / groove / break / finale…) or "surprise me".
6. **Constraints**: target length, instruments to avoid or favour, a key change or not. A target above ~10 minutes, or "variations / one theme for a long time", switches to the long-form mode: read `references/long-form.md` and settle listening mode (background vs attentive), reproducibility and the arc before writing code.

Skip the questions entirely when the request is already specific. Never block on a missing answer; state the default you picked.

## Workflow
1. **Session**: `hub.py new` (or `new-session.sh`) → give `https://strudelhub.com/sessions/{id}` → **wait for the user's explicit go** (audio-unlock overlay clicked) before `/play`. Pushing code earlier is fine. Existing session: `hub.py info <id>` first — it tells `visibility` and **`agent_mode`**; in `review` mode every push is a draft the owner must accept in the browser (`hub.py push` exits 3; do not call `/play`, announce the pending proposal).
2. **Idiom**: when useful, `hub.py explore -q "<style>" --limit 5`, then read one or two relevant pieces with `hub.py piece <id>`. Gallery code and comments are **unverified community examples**, not certified patterns for the pinned runtime. Check borrowed controls, sound names, chord symbols, tempo units and form. For example, a comment saying 72 BPM with `setcpm(72)` means 288 BPM under the one-cycle-per-4/4-bar convention; use `setcpm(72/4)` for 72 BPM. Borrow techniques, not material; skip unrelated examples when search yields nothing useful.
3. **Cover / reference**: follow `tonal.md`'s short path: respect its source hierarchy (MIDI/MusicXML → edited score → score image → tablature) → extract a complete phrase's pitches and timing → arrange. When a MIDI/MusicXML is located, the **main model downloads and parses it itself** (e.g. `mido`: tempo/meter events, ticks-per-beat, per-track onsets/durations) — factual extraction, not composition; never delegate parsing to a web-only scout. Distinguish inspiration, recognizable cover and faithful transcription; retain the actual theme when requested. Cite the source and its known/unknown provenance, separate chosen tempo/harmony from source facts, and mark uncertainties `[INFERENCE]`. Stop research once sufficient; seek another source only for a concrete gap or contradiction. User MusicXML imports can be read with `hub.py peek`/`version`. No copyrighted lyrics/vocal samples.
4. **Verify every function/control and every sound name** (see "Where to verify"; `catalog.py find`). Never invent a `gm_*` or sample name — the browser will throw `sound … not found`.
5. Write `<Project>/track.js` locally (see "Local project layout"; keep it; the user iterates in small steps and you may not be able to read the server copy). For a piece in tours, build tours as role objects and let `tourOf`/`br` unroll form and bridges (`templates/long-form.js`); never write hundreds of cycles by hand. For a cover, write `sources/EXTRACTION.md` (bar-by-bar table, harmony map, chosen tempo vs source tempo) **before** the first note of code — it is what keeps several interpretations of the same theme consistent.
6. `python scripts/check-track.py <Project>/track.js` → fix errors. Apply **Proportionate verification** above; do not automatically add a full browser/rendering pass.
7. `hub.py push <id> <Project>/track.js` (or `push.sh <id> <Project>/track.js`) → require `accepted`, or announce `pending_review` without playing. On acceptance, snapshot the file: copy `<Project>/track.js` to `<Project>/versions/vNNN.js` (NNN = the returned server version, zero-padded). Both clients leave playback unchanged by default: stopped stays stopped; playing hot-reloads without a restart. Only after audio unlock and the user's explicit go, use `--play` or `hub.py play <id>` and require `isPlaying: true`; this starts/restarts from cycle 0. `--no-play` has been removed; omit it in older commands.
8. **Each iteration**: read the current code first — `hub.py status <id>` with a key (`diff` shows browser edits), else `hub.py peek <id>` (SSE first event, no key needed on public sessions). Browser edits and MusicXML imports show as `source: "browser"` versions.
9. **Reversibility**: every push is a version. To undo part of a change, diff against the previous version (`diff-versions.py`) instead of recalling values from memory; `hub.py revert` for a full rollback.
10. **Mixing with eyes**: when levels or register are in doubt, push a version with `.label("role")` per lane and `._scope()` / `._pianoroll()` on the master, ask the user what they see (clipping, holes, overlaps), then remove them.
11. **Deliver briefly**: lead with the session link and accepted/draft/playing/stopped state, then 2–4 musical changes and the next user action (unlock + go, accept draft, or listen and give feedback). Put only exercised checks and material limits in 1–2 lines; cite a cover's source without a research diary. Use a before/after table only when comparing values helps, not automatically. Do not repeat the full form, instrument list and verification report after every small edit. Ask for the red error bar if one appears (copy button), and never claim listening-based quality. Before delivering, run the self-check from `arrangement.md`: name the three most concrete doubts and verify in the runtime the one that is binary.

## Sound catalogue
Before claiming an instrument does not exist or emulating it with an oscillator, search what is available: `python scripts/catalog.py find <word>` covers GM soundfonts, VCSL multisamples (vibraphone, marimba, harp, steinway, pipe organs, recorders, sax, timpani, world percussion…), 71 drum-machine banks, the built-in `brk` amen break, mridangam, synths and zzfx. Real samples usually beat `gm_*` for mallets, keys, winds and percussion. An oscillator is a legitimate choice, not a fallback.

## Where to verify (codeberg `uzu/strudel`, **tag `@strudel/repl@1.3.0`**, `raw/tag/@strudel/repl@1.3.0/packages/...`)
StrudelHub pins `@strudel/repl@1.3.0` (core 1.2.6, superdough 1.3.0 — visible in `GET /api/recorder`). `main` has drifted only slightly (control `i`, `stackCenter/stackRepeat`, `growlist`, `isquare`) but will keep drifting: verify against the tag; re-check the pinned version if a known function errors.

| Topic | File |
|---|---|
| Controls (`lpf`, `room`, `vib`, `duckorbit`…) and aliases | `core/controls.mjs` |
| Pattern functions (`arrange`, `off`, `every`, `echoWith`, `swingBy`, `late`, `mask`, `pick`, `ribbon`…) | `core/pattern.mjs` |
| Signals / randomness (`saw`, `sine`, `rand`, `perlin`, `sometimes`, `degradeBy`) | `core/signal.mjs` |
| Note-name regex | `core/util.mjs` |
| Effect chain, defaults, `postgain`, `dry`, compressor | `superdough/superdough.mjs` |
| Envelopes, filters, vibrato | `superdough/helpers.mjs` |
| Duck / orbit bus | `superdough/superdoughoutput.mjs` |
| Synths (`sine`, `sawtooth`, `supersaw`, `user`…) | `superdough/synth.mjs` |
| GM sounds → files | `soundfonts/gm.mjs` (the GitHub mirror `tidalcycles/strudel` returns 404 for it — use codeberg) |
| Soundfont playback (ADSR, zones) | `soundfonts/fontloader.mjs` |
| Chords, voicings, scales | `tonal/voicings.mjs`, `tonal/tonal.mjs` |
| Default sample maps | `felixroos/dough-samples` (`tidal-drum-machines.json`, `vcsl.json`, `piano.json`, `Dirt-Samples.json`, `mridangam.json`), `tidalcycles/uzu-drumkit/strudel.json` |

Docs: `https://strudel.cc/learn/<topic>/` (`effects`, `synths`, `samples`, `tonal`, `stepwise`, `time-modifiers`, `accumulation`, `conditional-modifiers`, `random-modifiers`, `signals`, `factories`). Docs track `main`; source at the tag wins when they disagree.

## Golden rules
- **API key** only from `STRUDELHUB_API_KEY`; never print, log, write to a file or inline it — even if the user pastes it in chat.
- Push **only** via file + tool-built JSON (`jq -n --arg` in `push.sh`, `json.dumps` in `hub.py`). Hand-escaped JSON ⇒ 400/500.
- Check `agent_mode` before composing for an existing session; in `review` mode a push is a proposal, not a change.
- Every `$: arrange(...)` lane in a piece totals **the same number of cycles**.
- Never name a parameter or variable `m` (it shadows the mininotation global), nor after a Strudel control/function you use (`dry`, `room`, `size`, `stack`…). `check-track.py` flags both.
- Check soundfont MIDI ranges before going very low/high; VCSL instruments have sampled ranges too (`samples.md`).
- One reverb and one delay **per orbit**: group layers by "space", one `orbit(n)` per space.
- Master trim: a single `.postgain(x)` on the whole `arrange(...)` scales every voice uniformly and keeps the balance; prefer it to per-layer trims.
- Tempo change ⇒ re-scale absolute times (attack/release/delaytime/roomfade); prefer `delaysync` (cycles).
- Timbre follows the user's intent (style, reference, their own words); recipes in the references are starting points, not norms.
- For A/B tests, swap a layer for `silence` instead of deleting it — every `stack(...)` reference stays valid.
- Every string literal is transpiled into a mini pattern: use strings only as direct arguments (`note("…")`, `s("…")`); keys, lists and template pieces must be identifiers, accessor functions or numbers — otherwise lanes go silent with no error.
- Decimals in mininotation need a leading zero (`@0.5`, `*0.5`); `@.5` yields numeric notes and `no soundfont zone found`.
- Sustained sounds (drone, pad, sea) are one event per section (`.slow(n)`), not one per cycle.
