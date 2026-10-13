// Four-on-the-floor skeleton — 909 kit, sidechained bass/pad, acid line, riser + drop.
// Neutral material (F minor, 128 BPM); every sound/number is a placeholder.
// Default sound map only (no samples() call). See references/samples.md, effects-cheatsheet.md.
//
// FORM — every lane totals 32 cycles
// | Lane   | 1-8 (intro)       | 9-16 (groove)    | 17-20 (break) | 21-24 (build)     | 25-32 (drop)     |
// |--------|-------------------|------------------|---------------|-------------------|------------------|
// | drums  | kick + hats       | full kit         | —             | kick + riser roll | full kit + fills |
// | bass   | —                 | bass             | bass filtered | bass filtered up  | bass             |
// | acid   | —                 | —                | acid, open    | acid              | acid             |
// | pad    | pad (ducked)      | pad              | pad           | pad + riser       | pad              |
// Splits: 8+8+4+4+8 on every lane.

const BPM = 128
setcpm(BPM / 4)

// ---------- Placeholders ----------
const BANK = "RolandTR909"     // tr808, tr707, LinnDrum, EmuSP12, mpc60… (`catalog.py banks`)
const BASS = "sawtooth"        // gm_synth_bass_2, square, supersaw
const ACID = "sawtooth"        // square for a softer line
const PAD  = "supersaw"        // gm_pad_warm, gm_pad_halo, "white" noise bed

// ---------- Harmony (material) ----------
const root  = note("<f1 f1 ab1 c2>")                        // one bass note per cycle
const acidP = note("<[f2 f2 f3 ab2] [f2 c3 eb3 f2] [f2 f2 ab2 f3] [c3 f2 eb2 f2]>")
const padCh = note("<[f3,ab3,c4,eb4] [f3,ab3,c4,eb4] [ab3,c4,eb4,g4] [c3,eb3,g3,bb3]>")

// ---------- Spaces (one orbit per reverb; orbit 3 = everything the kick ducks) ----------
const dryKit = p => p.orbit(1)                                     // not `dry`: that is a Strudel control
const ducked = p => p.orbit(3).room(0.25).size(4).roomfade(1.5)   // bass + pad: pumped by the kick
const wide   = p => p.orbit(2).room(0.4).size(5).delay(0.25).delaysync(3/16).delayfeedback(0.4)

// ---------- Drums ----------
// Gotcha: duckorbit lives on the *carrier* (the kick): every kick dips orbit 3 for `duckattack` seconds.
// Gotcha: an orbit exists only once something has played on it. If the first kick fires before any
//   orbit-3 event, the browser logs `duck target orbit 3 does not exist` (red bar, harmless after cycle 0).
//   Fix: the ducked lanes start on cycle 0 (pad below), or add a silent primer on orbit 3 — see `primer`.
const primer = s("sine").gain(0).orbit(3)   // 1 silent event per cycle on orbit 3; only the first matters
const kick = s("bd*4").bank(BANK).gain(1).duckorbit(3).duckattack(0.12).duckdepth(0.6).late(0.001)
const hats = stack(
  s("[~ hh]*4").bank(BANK).n("<0 1>").velocity("[.9 .6]*4").gain(0.5),
  s("[~ ~ ~ oh]*2").bank(BANK).cut(1).gain(0.35),
)
const clap = s("~ cp ~ cp").bank(BANK).gain(0.6).room(0.2).size(2)
const ride = s("rd*8").bank(BANK).velocity("[.7 .4]*4").gain(0.25).hpf(4000)
const fill = s("sd*16").bank(BANK).mask("<0 0 0 1>").velocity(saw.range(0.3, 1)).gain(0.6)
const kit  = stack(kick, hats, clap, fill)
// Riser roll: 1 cycle of accelerating snare (ply grows), filter opening, into the drop.
const roll = s("sd*8").bank(BANK).ply("<1 1 2 4>").velocity(saw.range(0.3, 1).slow(4))
  .lpf(saw.range(600, 8000).slow(4)).gain(0.5)

// ---------- Bass: filtered saw, sidechained via orbit 3 ----------
const bass = root.struct("[x ~]*8").s(BASS).clip(0.6).lpf(380).lpq(4).lpenv(1.5).lpdecay(0.12).lpsustain(0)
  .decay(0.2).sustain(0.3).release(0.05).gain(0.5)

// ---------- Acid: 303-style — accents + slides via penv, resonance, distortion ----------
// Gotcha: signals are sampled per event; 16 events per cycle make the saw sweep audible.
const acid = acidP.struct("x*16").s(ACID).clip("[.5 .9]*8")
  .lpf(sine.range(300, 1800).slow(8)).lpq(14).lpenv(2.5).lpdecay(0.14).lpsustain(0.05)
  .penv("[0 0 0 -2]*4").pattack(0.02)
  .velocity("[1 .6 .8 .6]*4").distort("0.4:0.7").gain(0.3)

// ---------- Pad ----------
const pad = padCh.s(PAD).unison(5).detune(0.25).spread(0.8).attack(0.6).release(1.2)
  .lpf(1400).hpf(200).gain(0.18)
const riserPad = padCh.s("white").attack(0.01).release(0.3)
  .lpf(saw.range(400, 9000).slow(4)).gain(saw.range(0.02, 0.18).slow(4)).hpf(300)

// ---------- Master ----------
const MASTER = 0.65

$: arrange(
  [8,  dryKit(stack(primer, kick, hats))],
  [8,  dryKit(kit)],
  [4,  silence],
  [4,  dryKit(stack(primer, kick, roll))],
  [8,  dryKit(stack(kit, ride))]
).postgain(MASTER)

$: arrange(
  [8,  silence],
  [8,  ducked(bass)],
  [4,  ducked(bass.lpf(160))],
  [4,  ducked(bass.lpf(saw.range(160, 380).slow(4)))],
  [8,  ducked(bass)]
).postgain(MASTER)

$: arrange(
  [8,  silence],
  [8,  silence],
  [4,  wide(acid.lpq(6))],
  [4,  wide(acid)],
  [8,  wide(acid)]
).postgain(MASTER)

$: arrange(
  [8,  ducked(pad.gain(saw.range(0.05, 0.18).slow(8)))],
  [8,  ducked(pad)],
  [4,  ducked(pad.lpf(900))],
  [4,  ducked(stack(pad, riserPad))],
  [8,  ducked(pad)]
).postgain(MASTER)
