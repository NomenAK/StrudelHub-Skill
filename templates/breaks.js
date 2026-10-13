// Sample-based skeleton — drum machine + sliced break + bass + chords from a chord chart.
// Neutral material (Am7 – D7 – F^7 – E7, 92 BPM); everything stylistic is a placeholder.
// Works with the default sound map only (no samples() call): `brk` = built-in amen break,
// banks from tidal-drum-machines, `piano`/VCSL for keys. See references/samples.md.
//
// FORM — every lane totals 24 cycles
// | Lane   | 1-4 (intro) | 5-12 (A)        | 13-16 (break)   | 17-24 (B)          |
// |--------|-------------|-----------------|-----------------|--------------------|
// | drums  | hats only   | full kit        | sliced break    | full kit + break   |
// | bass   | —           | bass            | bass (filtered) | bass               |
// | keys   | chords soft | chords          | chords          | chords + arp       |
// Splits: drums 4+8+4+8, bass 4+8+4+8, keys 4+8+4+8.

const BPM = 92
setcpm(BPM / 4)

// ---------- Placeholders (swap by intent) ----------
const BANK  = "RolandTR808"   // any name from `catalog.py banks` (tr909, LinnDrum, EmuSP12, mpc60…)
const BREAK = "brk"           // built-in 1-bar amen; or samples('github:yaxu/clean-breaks/main') + "amen/4"
const KEYS  = "gm_epiano1"    // or "piano", "steinway", "vibraphone", "kawai" (VCSL, note-mapped)
const BASS  = "sawtooth"      // or "gm_electric_bass_finger", "gm_synth_bass_1"

// ---------- Harmony: one chart, every tonal lane derives from it ----------
// Gotcha: chord symbols need a root + symbol with no spaces; one chord per cycle here.
// ireal symbols: ^7 (maj7, also M7), m7 / -7, 7, m7b5 / h7, o7, sus, 7sus, 69, 7b9…
//   `maj7` and `dim7` are NOT in the dictionary → the chord is silently replaced by silence (log only).
const chart = "<Am7 D7 F^7 E7>"

// ---------- Spaces (one orbit per reverb) ----------
const dryKit  = p => p.orbit(1)
const roomMid = p => p.orbit(2).room(0.35).size(3).roomfade(1.2)
const roomFar = p => p.orbit(3).room(0.7).size(6).roomfade(2.5)

// ---------- Drums ----------
// Gotcha: not every bank has every hit; check-track.py flags missing ones. `cut(1)` chokes oh with hh.
const hats = s("hh*8").bank(BANK).n("<0 1>").velocity("[1 .55 .8 .5]*2").gain(0.6)
const kit  = stack(
  s("bd ~ [~ bd] ~, ~ sd ~ sd").bank(BANK).gain(0.9),
  s("[hh oh]*4").bank(BANK).cut(1).velocity("[1 .6]*4").gain(0.55),
).swingBy(1/8, 8)
// Sliced break: 8 slices, reordered every 4th cycle, fitted to the cycle.
// Gotcha: `fit()` matches the sample to the event; `/4` on a 4-bar break spreads it over 4 cycles.
const breakBeat = s(BREAK).fit().slice(8, "0 1 2 3 4 5 6 7".lastOf(4, x => x.rev()))
  .gain(0.75).hpf(120)
// Fill every 4th cycle on the snare position.
const fills = s("~ ~ ~ [sd sd:1 sd:2 sd:3]").bank(BANK).mask("<0 0 0 1>").gain(0.7)

// ---------- Bass: root notes of the chart ----------
// Gotcha: rootNotes(2) = octave 2; `.note()` turns the names into note events.
const bass = chart.rootNotes(2).note().struct("x ~ x [~ x] ~ x ~ ~").s(BASS)
  .lpf(500).lpenv(1.2).lpdecay(0.15).lpsustain(0.1).decay(0.18).sustain(0.4).release(0.08)
  .gain(0.45)

// ---------- Keys: voicings from the chart ----------
// Gotcha: voicing() outputs a note pattern; `.struct` gives it rhythm; `anchor` keeps the register.
const chords = chord(chart).dict('ireal').anchor("c5").voicing().struct("[~ x]*2").s(KEYS)
  .clip(0.9).gain(0.4)
const arp = n("0 2 1 3 2 0 3 1").chord(chart).voicing().s(KEYS).clip(0.5).gain(0.25)
  .off(1/16, x => x.add(note(12)).velocity(0.35))

// ---------- Master ----------
const MASTER = 0.7

$: arrange(
  [4,  dryKit(hats)],
  [8,  dryKit(stack(kit, fills))],
  [4,  roomMid(breakBeat)],
  [8,  dryKit(stack(kit, fills, breakBeat.gain(0.5)))]
).postgain(MASTER)

$: arrange(
  [4,  silence],
  [8,  roomMid(bass)],
  [4,  roomMid(bass.lpf(220))],
  [8,  roomMid(bass)]
).postgain(MASTER)

$: arrange(
  [4,  roomFar(chords.mul(velocity(0.6)).lpf(saw.range(600, 3000).slow(4)))],
  [8,  roomMid(chords)],
  [4,  roomFar(chords.mul(velocity(0.7)))],
  [8,  roomMid(stack(chords, arp))]
).postgain(MASTER)
