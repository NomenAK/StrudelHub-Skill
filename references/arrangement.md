# Arrangement, mix and iteration — devices, not rules

Everything here is a **starting point** taken from past sessions. Balance, pan, durations, harmony and timbre follow the user's intent and reference, never these numbers.

## Code layout (suggestion)
1. Header: title, key, progression, BPM, **form table with cycle counts**.
2. Material (mininotation strings): bass, chords, melodies, counter-lines, arps — one constant each, so the same line can be re-voiced by several instruments.
3. Spaces: one `orbit(n)` per reverb character (dry rhythm / medium / long), as helpers `space = p => p.orbit(2).room(0.5).size(4)` or inline per voice.
4. **Factories** `xxxOf(pat)` that fix a timbre; reuse them for special passages (pivot bar, break, outro) so the timbre does not jump.
5. Sections as `stack(...)` constants; one `$: arrange(...)` (or one lane per role, all with the same total). Mute a layer with `silence`, not by deleting it.
6. `.postgain(x)` once on the master.

## Form: creating a "moment"
Listeners remember contrasts, not layers. Devices that work in any style:
- **Subtractive break**: remove the rhythm section for 2–4 cycles, keep one melodic voice plus a textural one.
- **Riser into a gap**: one cycle of rising material (`n(run(16)).scale(...)`, `gain(saw.range(a,b))`, `lpf(saw.range(lo,hi))`, a `*16` roll), then `.mask("1 1 1 0")` — one beat of silence before the drop hits harder than any crescendo.
- **Key change for the last section**: `.transpose(3)` (or 1, 2, 5) on the `stack` of tonal layers only, drums outside. A pivot bar on the new dominant smooths it; a hard cut is also a valid choice.
- **Meter feel change**: 6 or 12 events per cycle for waltz/compound feel in one section, 8 or 16 in the next; `setcpm` unchanged.
- **Call and response**: two voices with `mask("<1 0>")` and `mask("<0 1>")`, or `off(1, fn)` so a voice answers itself one cycle later.
- **Motif, not note soup**: a 1–2 cycle idea, then the same idea sequenced up a step/third, then a descending answer. Repetition is what makes a melody a theme.
- **Outro**: `cat(finalChord, bed, bed).slow(1.5)` stretches time; or let one textural layer run alone for a cycle or two.

## Movement inside a section
Nothing should be identical two cycles in a row unless that is the point:
- `lastOf(4, x => x.ply(2))` on a snare/clap = fill; `sometimesBy(0.1–0.2, fn)` on hats = stray subdivisions.
- `degradeBy(0.3–0.6)` on a doubling layer = it comes and goes.
- `lpf("<900 1100 1400 1800>")` or `lpf(perlin.range(a,b).slow(8))` on a pad = slow breathing (sampled per event: works on patterns with several events per cycle).
- `pan(perlin.range(0.35, 0.65).slow(4))` = slow stereo drift.
- Ramps `saw.range(a,b).slow(n)` inside an `n`-cycle section cover exactly that section (gain fade-in, filter opening).

## Humanisation
- Timing: `.late(rand.range(0, 0.015))` (cycles) on plucked/keyboard layers; `.swingBy(1/6, 8)` for a light shuffle.
- Dynamics: `.velocity("[1 .6 .85 .5]*2")` accent patterns; `.mul(velocity(...))` to accent without overwriting an inner level.
- Pitch: slow shallow `vib` for tape/analog wobble; `penv` negative + short `pattack` for scooped wind/voice attacks.
- Layer doubling with an offset: `off(1/8, x => x.transpose(12).velocity(0.3))` — an octave shadow that is late by an eighth sounds like a second player.

## Stereo and depth
- `juxBy(0.5–0.8, rev)` on an arpeggio = the right channel plays it backwards; wide and hypnotic without a chorus.
- Register before volume: when two layers blur, move one an octave rather than raising its gain.
- `hpf(120–500)` on anything that is not the bass leaves the low end to the bass.
- `dry` lower + `room` higher = further away; `size` large + `roomlp` low = distant hall; `size` small + `room` low = close.
- Different orbits for different distances; the same orbit for sources that should sit in the same room.

## Mix hierarchy (one possible order)
Lead > chords > arp/ornaments > pads/texture. Tools: register, filters, pan, then gain. Softening **every** layer flattens the mix — adjust relative to neighbours. Finish with a single `postgain` on the master if the sum is hot.

## Transitions
- Compare end-of-section vs start-of-next for each layer (gain, filter): an unintended drop at a build is a transition bug; a deliberate cut is a device.
- A layer cut dead at the start of an outro reads as a cut; a fade (`gain(saw.range(1, 0.05).slow(n))`) is the alternative.
- A pivot bar (dominant of the next key, with the **same factories** as the layers it replaces, on **all** lanes) is one option before a key change.
- **Bridge on the source's own vamp**: when the piece has a two-chord vamp (Gm–F here), use it as the transition material between big sections — it belongs to the theme, so it never sounds like a device. Cross-fade only the roles that change (chords, bass, extras, kit) and let identical ones play through; add the next section's pickup, fading in, so the incoming lead is announced. Code pattern in `templates/long-form.js`.

## Iterating with the user
- Translate their words: "sharper" → shorter attack + more highs; "diffuse" → longer attack/release, lower lpf, more room/delay; "rounder" → slower attack + lpf + a sine doubling; "wider" → octave layers, `juxBy`, pad.
- Expect tiny steps ("remove X", "more Y"): keep the track as a local file, change one axis per request unless asked otherwise, report a before/after table with numbers.
- When they say "too much" after a change, propose a numeric middle.
- When they sense a problem without locating it: walk the section joins (levels, filters, harmony, real length of `@` motifs).
- To undo part of a change, diff against the previous version (`scripts/diff-versions.py`) rather than rebuild values from memory.
- A/B: swap the suspected layer for `silence`, push, ask. Every `stack` reference stays valid.
- **Ask "are you satisfied?" of yourself before delivering**: list the three most concrete doubts, then verify in the runtime the one that is binary (an event count per label, a note range, a bridge's gains). In practice each such pass found a real bug (a chord voice missing, a bass line two octaves too busy, bridges with no melody).
