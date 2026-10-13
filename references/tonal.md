# Tonal: chord symbols, voicings, scales (verified in the `@strudel/repl@1.3.0` bundle)

Use this for covers and anything with a chord chart: a progression becomes one string instead of hand-written note stacks, and the voicing engine does voice-leading for you.

## Chord symbols → voicings
```js
chord("<C^7 A7b13 Dm7 G7>").voicing()            // one voiced chord per cycle
chord("<C^7 A7b13 Dm7 G7>*2").dict('ireal').voicing().s("gm_epiano1")
```
- `chord("…")` accepts root + symbol **from the voicing dictionary**. `ireal` (= `simple`, 62 symbols, + `ireal-ext`): `C` (major, `^`), `C^7`/`CM7` (maj7), `C^9`, `C6`, `C69`, `Cadd9`, `C-`/`Cm`, `C-7`/`Cm7`, `C-9`, `C-^7`, `C-6`, `C7`, `C9`, `C13`, `C7sus`, `C9sus`, `Csus`, `Ch7`/`Cm7b5` (half-dim), `Co`/`Co7` (dim), `C+`/`Caug`, `C7b9`, `C7#9`, `C7#11`, `C7b13`, `C7alt`, `C13b9`… Flats `b`, sharps `#`. **`Cmaj7`, `Cdim7`, `Csus4`, `Cmin7` are NOT recognised**: the chord logs `[voicing]: unknown chord` and plays **silence** — no red bar, so a missing chord is easy to miss. Slash-bass is not parsed — add the bass separately (`rootNotes` or a `note()` lane).
- Dictionaries (`dict`/`dictionary`): `ireal` (default), `ireal-ext` (same symbols, more voicings), `lefthand` (12 rootless jazz voicings: `m7 7 ^7 69 m7b5 7b9 7b13 o7 7#11 7#9 mM7 m6`), `triads` (`M m o aug`), `guidetones` (3rd + 7th), `legacy`.
- `anchor("a4")` / `mode("below" | "above" | "duck" | "root")`: where the voicing sits. `mode("below")` = top note ≤ anchor (default for ireal/lefthand); `mode("root:g2")` puts the root at the bottom ≥ g2 — the shorthand `mode("root:g2")` sets both.
- `offset(n)`: pick the n-th voicing up/down; `octaves(n)`: spread.
- `n("0 1 2 3").chord("<C Am F G>").voicing()`: `n` indexes the voicing's notes → arpeggios that follow the harmony with zero manual work.
- `.voicing()` output is a `note` pattern: everything downstream (`.s()`, `.add(note(12))`, `.transpose(3)`, `.struct(…)`, `.off(…)`) applies as usual.

Chords + bass from one chart (docs example, works in 1.3.0):
```js
chord("<C^7 A7b13 Dm7 G7>*2").dict('ireal').layer(
  x => x.struct("[~ x]*2").voicing().s("gm_epiano1"),
  x => n("0*4").set(x).mode("root:g2").voicing().s('sawtooth').lpf(800)
)
```
Root notes only: `"<C^7 A7b13 Dm7 G7>".rootNotes(2).note()` (octave 2).

## Scales
```js
n("0 2 4 6 4 2").scale("C:major")                 // degrees → notes; root defaults to octave 3
n("0 .. 7").scale("D:dorian")                      // mininotation range
n(run(8)).scale("<C:major F:lydian>/2")            // scale can be patterned
n("[0,7] 4 [-2,7] 4#").scale("C:minor")            // negative = below root; # / b = chromatic alteration
```
- Names must have **no spaces**: `C:major`, `Eb:minor:pentatonic`, `A:harmonic:minor`, `C:major:blues`, `F#:mixolydian`, `C:ritusen`, `D:whole:tone`. Any tonaljs scale type works (`major minor dorian phrygian lydian mixolydian aeolian locrian pentatonic blues harmonic:minor melodic:minor whole:tone diminished …`).
- `scaleTranspose(steps)` (alias `strans`): transpose **inside** the scale (`.scale("C:major").scaleTranspose("<0 2 4>")`) — diatonic sequences, modal mixture-free.
- `transpose(semitones)` (`trans`) works on note names and on `voicing()` output; `add(note(n))` is equivalent for control patterns.
- `transpose(n)` reads `hap.value.note` and keeps every other control (`s`, `gain`, `orbit`…), so it works on a fully timbred `stack(...)` — transpose one section's tonal layers after the factories, leave the kit outside. Spelling is tonal's (`B#4` for C5): cosmetic, the MIDI number is right.

## Arpeggios and ornaments
- `.arp("0 1 2 3")` / `.arp("<0 [0,2] 1 [2,3]>")`: index into a chord `[c,e,g]` or a voicing, one chord per event → broken chords, Alberti bass (`arp("0 2 1 2")`), guitar strums.
- `.arpWith(xs => …)`: custom function on the chord's notes.
- `.off(1/16, x => x.add(note(12)).velocity(.4))`: octave echo; `.off(1/8, …)` three times for a strum.
- Humanised strum without `rolled` (absent in 1.3.0): `.layer(x => x.arp("0"), x => x.arp("1").late(1/32), x => x.arp("2").late(1/16))`.

## Cover workflow — usable source → extraction → arrangement
1. Match the promise: **inspiration** permits original material; a **recognizable cover** retains the theme while changing orchestration; a **faithful transcription** also requires accurate rhythm/form. Never replace a requested theme with generic stylistic material.
2. Start with the user's score/import, otherwise find one usable source with a complete thematic phrase, following this hierarchy: **1) MIDI/MusicXML** (machine-readable, exact rhythm) → **2) published/edited score** → **3) score image** → **4) tablature** (pitches only, never evidence for rhythm or form). Drop to a lower level only when the higher level is absent or incomplete on a named, specific point. Record the URL, stated arranger/author (or unknown), and whether it is official or a community transcription. A successful download proves availability, not authenticity; several mirrors may contain the same transcription.
3. Extract pitches **and onset/duration data**, meter, tempo and phrase length before arranging. MIDI: use a parser such as `mido` (optional dependency), inspect tempo/meter events and ticks-per-beat; do not infer key from an untrustworthy default key-signature tag. MusicXML: use the browser import and read its generated code with `hub.py peek`/`version`. Pitch-only tabs are not rhythmic evidence.
   - **Parsing ownership**: downloading and parsing a MIDI/MusicXML is factual extraction, not composition — the main model does it itself (or a research agent explicitly given shell/Python). Never assign it to a web/read-only scout; such a scout MUST state it cannot parse the binary instead of silently omitting or guessing its contents.
   - **Required deliverable**: a bar-by-bar table (pitch + duration, in one declared unit), separated per track/channel for MIDI, with tempo/meter taken from the file's metadata events, phrase lengths, and every contradiction listed together with the source that settles it under the step-2 hierarchy. "Unresolved" is acceptable only after the higher hierarchy levels are exhausted.
   - **Score images**: read at native resolution only. Any note re-read after an initial misreading stays low-confidence, marked `[INFERENCE]`, until a second source confirms it.
4. Stop researching once the material is sufficient for the requested fidelity. Consult another source only to settle a specific contradiction or missing phrase; do not demand proof of game-extracted data for a recognizable cover. Cite the source and mark remaining assumptions `[INFERENCE]`; never claim to have compared by ear when you cannot hear.
5. The main model composes the arrangement itself. Distinguish source facts from chosen tempo, voicings, form and timbres. `setcpm(BPM/4)` gives one 4/4 bar per cycle; preserve the theme's chromatic notes instead of forcing it into a scale.
6. For charts, define `const chart = "<C^7 A7b13 Dm7 G7>"`; derive `chord(chart).voicing()` and `chart.rootNotes(2).note()` where appropriate. Keep source inversions in a separate bass lane and exact melodic figures in `note()` strings. Shape sections with `arrange()`; freeze shorter excerpts with `ribbon()` when repetition is intended (see `strudel-gotchas.md`).
7. Lint before pushing; use a targeted runtime check only for unresolved execution/timing risk. Do not make exhaustive note comparisons or full-piece renders a prerequisite for every cover. No copyrighted lyrics/vocal samples.
