// Generic multi-section skeleton — neutral I–V–vi–IV progression in C major
// (C – G – Am – F, one chord per cycle, 4 cycles per pass).
// Everything stylistic (sounds, tempo, chords, rhythm) is a placeholder to replace.
//
// FORM — every lane totals 16 cycles (lanes with different totals drift when looping)
//
// | Lane    | 1-4 (intro) | 5-8 (A)        | 9-12 (B)   | 13-16 (outro) |
// |---------|-------------|----------------|------------|---------------|
// | chords  | chords      | chords         | chords     | chords (soft) |
// | layer   | —           | —              | layer      | layer (soft)  |
// | bass    | —           | bass (fade in) | bass       | bass          |
// | lead    | —           | arp            | arp        | —             |
//
// Actual splits: chords 4+4+4+4, layer 8+4+4, bass 4+4+8, lead 4+8+4.

// ---------- Instruments (replace according to intent) ----------
// The sounds below are PLACEHOLDERS: any synth (sine, sawtooth, square, triangle…),
// sample or gm_* fits any role. Pick by musical intent, not by this file.
// Only this block decides the timbre; the rest of the file does not change.
// gm_*: run `python scripts/check-track.py` (name exists?) and
//       `python scripts/sf-range.py <gm_xxx> [n]` (range) before pushing.
// Synth or sample: adapt/remove the `.n(0)` in the factories
//       (.n(i) picks an index in the soundfont/sample list, it is not a note).
const SND_CHORDS = "gm_string_ensemble_1" // placeholder — role: sustained harmony
const SND_LAYER  = "gm_pad_halo"          // placeholder — role: upper doubling layer
const SND_BASS   = "sine"                 // placeholder — role: low foundation
const SND_LEAD   = "triangle"             // placeholder — role: melodic line / arp

// Gotcha: setcpm = cycles per minute; 1 cycle = one 4/4 bar, hence BPM/4.
const BPM = 84
setcpm(BPM / 4)

// ---------- Space helpers (reverb per orbit) ----------
// Gotcha: reverb and delay are PER ORBIT (one shared bus) → one orbit per space,
//   never two different room/size settings on the same orbit.
// Parameter named `p` (never `m`, which shadows the mininotation global).
// Gotcha: do not name a constant after a Strudel control (`dry`, `room`, `size`…): it shadows it.
// Three spaces as starting values: adjust (or drop) according to intent.
const spaceNear = p => p.orbit(1).room(0.25).size(2).roomfade(1.5).roomlp(9000).roomdim(4000)
const spaceMid  = p => p.orbit(2).room(0.6).size(6).roomfade(3).roomlp(6000).roomdim(2500)
const spaceFar  = p => p.orbit(3).room(0.85).size(10).roomfade(5).roomlp(4000).roomdim(1800)

// ---------- Ramp ----------
// Gotcha: arrange() runs fast(nCycles) on each section, so slow(n) below
//   covers exactly one section of n cycles (n = length of the section it is used in).
// Signals are sampled once per event: ramps need several events per cycle to be heard.
const up = (a, b, n) => saw.range(a, b).slow(n)

// ---------- Factories xxxOf(pat) ----------
// A factory = one sound + its envelope + its space; the role does not depend on the timbre.
// attack/release and the orbit are starting values, to tune with the chosen sound.
// Gotcha: .velocity() OVERWRITES, .mul(velocity(x)) MULTIPLIES → internal ratios are set
//   with .mul(velocity(...)) without overwriting the base level set here.
const chordsOf = p => spaceMid(p.s(SND_CHORDS).n(0).velocity(1).attack(0.05).release(0.6))
const layerOf  = p => spaceFar(p.s(SND_LAYER).n(0).velocity(1).attack(0.3).release(1.2))
const bassOf   = p => spaceNear(p.s(SND_BASS).velocity(1).attack(0.02).release(0.4))
const leadOf   = p => spaceNear(p.s(SND_LEAD).velocity(1).attack(0.02).release(0.4))

// ---------- Musical material (original, neutral) ----------
// <a b c d> advances one entry per cycle. A shorter arrange section does not
// freeze the excerpt across loops: use pattern.ribbon(0, sectionCycles) when required.
const chords   = note("<[c3,e3,g3,c4] [g2,d3,g3,b3] [a2,e3,a3,c4] [f2,c3,f3,a3]>")
const chordsHi = note("<[c4,e4,g4,c5] [g3,d4,g4,b4] [a3,e4,a4,c5] [f3,c4,f4,a4]>") // same harmony, +1 octave
const bass   = note("<c2 g1 a1 f1>")
const mel    = note("<[e4 g4 c5 g4] [d4 g4 b4 g4] [c4 e4 a4 e4] [c4 f4 a4 f4]>")

// ---------- Master trim ----------
// Gotcha: lanes sum; one uniform postgain on every lane keeps the balance and adds headroom.
// Raise/lower this single number instead of touching each layer.
const MASTER = 0.6

// ---------- Lanes ----------
// Gotcha: each arrange([cycles, pattern], ...) must total 16; silence = empty section.
// Mute a lane for an A/B test by replacing its content with silence, not by deleting it.

// Chords: all along, filter opening over the intro (4-cycle ramp).
$: arrange(
  [4, chordsOf(chords).mul(velocity(0.6)).lpf(up(500, 4000, 4))],
  [4, chordsOf(chords).mul(velocity(0.8))],
  [4, chordsOf(chords).mul(velocity(0.9))],
  [4, chordsOf(chords).mul(velocity(0.5))]
).postgain(MASTER)

// Layer: enters on section B, backs off on the outro.
$: arrange(
  [8, silence],
  [4, layerOf(chordsHi).mul(velocity(0.7))],
  [4, layerOf(chordsHi).mul(velocity(0.4))]
).postgain(MASTER)

// Bass: 4-cycle fade in (gain and velocity multiply).
$: arrange(
  [4, silence],
  [4, bassOf(bass).mul(velocity(0.8)).gain(up(0.1, 1, 4))],
  [8, bassOf(bass).mul(velocity(0.9))]
).postgain(MASTER)

// Lead: arp on A and B, absent on intro and outro.
$: arrange(
  [4, silence],
  [8, leadOf(mel).mul(velocity(0.5))],
  [4, silence]
).postgain(MASTER)
