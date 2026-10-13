// LONG-FORM SKELETON — one short form replayed as "tours" (placeholder material: A minor, 4/4, 96 BPM).
// Model:
//  - A TOUR is a role object {pick, leadA, chordsA, bassA, kit…}: one full pass of the FORM below.
//    Every role holds a pattern or is missing/silence. Build tour N+1 as {...tourN, role: newPattern}.
//  - At most 2 major changes per tour (timbre swap, texture thinning, transposition…): listeners
//    follow density in waves; everything else stays identical to the previous tour.
//  - BRIDGES sit between tours on the vamp. Per role listed in `roles`: same pattern OBJECT in both
//    tours (===) → it plays through; different → outgoing fades out, incoming fades in.
//  - freeze: each arrange section is ribbon(0, n) so `<a b>` alternations restart in every section.
//  - PRIMER: a silent early hit of every sound used only later, so soundfonts are loaded in advance.
//  - 3 FIXED ORBITS (reverb/delay are per orbit): near / far / wash. Never two settings per orbit.
// Total = tours x 12 + bridges x 4 = 3 x 12 + 3 x 4 = 48 cycles (3 tours + 2 bridges + closing fade).
setcpm(96 / 4)

// ======================= MATERIAL (placeholders: replace) =======================
const pickA = note("<~ [~@3 e5]>") // pickup, 2 cycles, last beat of the vamp (announces the lead)
const melA = note("<[a4 c5 e5 c5] [b4 d5 e5 ~]>")                // 2-cycle melody
const loA = note("<a3 g3>"), miA = note("<c4 b3>"), hiA = note("<e4 d4>") // chords: 3 voice lanes (Am | G)
const loV = note("<a3 f3>"), miV = note("<c4 a3>"), hiV = note("<e4 c4>") // vamp (Am | F)
const rootsA = note("<a2 g2>"), rootsV = note("<a2 f2>")
const bassA = note("<[a1 ~ e2 ~] [g1 ~ d2 ~]>"), bassV = note("<[a1 ~ e2 ~] [f1 ~ c2 ~]>")
// A plain "…" is already a mini-notation Pattern, which is exactly what struct() wants.
const strumRhythm = "x [x x] x x"
const pulseRhythm = "x ~ x ~"

// ======================= SPACES (3 fixed orbits) =======================
const near = pat => pat.orbit(1).room(.14).size(1.8)
const far = pat => pat.orbit(2).room(.4).size(4.2)
const wash = pat => pat.orbit(3).room(.6).size(7).roomlp(2400)

// ======================= TIMBRES (every factory sets its own .gain) =======================
const leadA_Of = pat => far(pat.s("gm_pan_flute").n(0).attack(.02).release(.18).clip(.95)
  .vib(5.2).vibmod(.12).hpf(300).lpf(6500).pan(.5).gain(.46))
const leadB_Of = pat => wash(pat.transpose(-12).s("gm_epiano1").n(0).attack(.005).decay(.5).sustain(.35).release(.6)
  .clip(.95).hpf(240).lpf(3800).pan(.5).gain(.4))
// 3 voice lanes, slightly staggered like a strum
const chordsOf = (lo, mi, hi, rhythm = strumRhythm) => near(stack(
  lo.struct(rhythm), mi.struct(rhythm).late(1/192).pan(.42), hi.struct(rhythm).late(1/96).pan(.58)
).s("gm_acoustic_guitar_nylon").n(0).attack(.002).decay(.3).sustain(.4).release(.15).clip(.8)
  .hpf(180).lpf(4400).gain(.3))
// snd goes straight to s() as a Pattern: piano roots in tour 1, then gm_acoustic_bass in tour 2
const bassOf = (pat, snd = "gm_acoustic_bass") => near(pat.s(snd).n(0).attack(.004).release(.15).clip(.9)
  .lpf(1200).pan(.5).gain(.5))

// ======================= KITS =======================
const kitA = near(s("woodblock").n(3).struct("x ~ x x").velocity("1 .6 .8 .7").hpf(600).pan(.4).gain(.26)).label("kitA")
const kitB = near(stack(
  s("framedrum").n(2).struct("x ~ ~ x ~ x ~ ~").velocity("1 .6 .8").lpf(3000).pan(.44).gain(.38),
  s("tambourine").n(2).struct("~ x ~ x").velocity(.7).hpf(2200).pan(.66).gain(.16)
)).label("kitB")

// ======================= FORM HELPERS =======================
const up = x => (x === undefined ? silence : x)
// TRAP 1: the transpiler turns EVERY "…" literal into a mini-notation Pattern, even outside Strudel
// calls. So roles are named by ACCESSORS, never by string keys: ["leadA"].map(k => p[k]) indexes with a
// Pattern (undefined → silence, no error). Same trap: `${x}` interpolating a Pattern into a template.
const R = {
  pick: p => p.pick, leadA: p => p.leadA, leadB: p => p.leadB,
  chordsV: p => p.chordsV, chordsA: p => p.chordsA, chordsB: p => p.chordsB,
  bassV: p => p.bassV, bassA: p => p.bassA, bassB: p => p.bassB, extrasV: p => p.extrasV, kit: p => p.kit,
}
// The form is declared once: [cycles, roles playing in that section]. 12 cycles per tour.
const vamp = [R.pick, R.chordsV, R.bassV, R.extrasV, R.kit]
const FORM = [
  [2, vamp], [4, [R.leadA, R.chordsA, R.bassA, R.kit]],
  [2, vamp], [4, [R.leadB, R.chordsB, R.bassB, R.kit]],
]
const tourOf = p => FORM.map(([n, rs]) => [n, stack(...rs.map(get => up(get(p))))])
// Bridge fades: mul(gain(saw…)) scales each layer's own .gain (velocity ratios kept).
const fadeOut = pat => pat.mul(gain(saw.range(1, .08).slow(4)))
const fadeIn = pat => pat.mul(gain(saw.range(.1, 1).slow(4)))
const freeze = sections => sections.map(([n, pat]) => [n, pat.ribbon(0, n)])

// ======================= BRIDGES (4 cycles on the vamp) =======================
// Roles compared by identity through accessors, again no string keys (TRAP 1).
const roles = [p => p.chordsV, p => p.bassV, p => p.extrasV, p => p.kit]
const br = (a, c, constant = silence) => [4, stack(
  constant,
  ...roles.map(get => get(a) === get(c) ? up(get(a)) : stack(fadeOut(up(get(a))), fadeIn(up(get(c)))))
)]
// the bridge also carries the incoming tour's pickup, fading in, so the next lead is announced
const brTo = (a, c, constant = silence) => br(a, c, stack(constant, fadeIn(up(c.pick))))

// ======================= TOURS =======================
// primer.mask("<1 0>"): sounds only needed later, first hit silent (gain 0). `name` is a Pattern here
// (TRAP 1 again) and s(Pattern) is what we want: the mapped value goes straight to s().
const primer = stack(
  ...["gm_acoustic_bass", "gm_epiano1", "framedrum", "tambourine"]
    .map(name => s(name).note("c4").struct("x").gain(0).clip(.1))
).label("primer")
// 1 — plain: flute, nylon trio, piano roots, light kit. B reuses the A material (replace with a real B)
const t1 = {
  pick: leadA_Of(pickA), leadA: leadA_Of(melA), leadB: leadA_Of(melA),
  chordsV: chordsOf(loV, miV, hiV), chordsA: chordsOf(loA, miA, hiA), chordsB: chordsOf(loA, miA, hiA),
  bassV: bassOf(rootsV.struct(pulseRhythm), "piano"), bassA: bassOf(rootsA.struct(pulseRhythm), "piano"),
  bassB: bassOf(rootsA.struct(pulseRhythm), "piano"), extrasV: primer.mask("<1 0>"), kit: kitA,
}
// 2 — (a) spread override, 2 changes: framedrum kit + acoustic bass line (pick, leads, chords unchanged)
const t2 = {
  ...t1, kit: kitB, bassV: bassOf(bassV), bassA: bassOf(bassA), bassB: bassOf(bassA),
  extrasV: silence, // the primer was only needed once
}
// 3 — (b) fragments: Rhodes plays the head of A only, chords and bass of A are silent roles
//     (c) B transposed up a tone: lead, the three chord lanes AND the bass together
const t3 = {
  ...t2, leadA: leadB_Of(melA.mask("<1 0>")), chordsA: silence, bassA: silence,
  leadB: leadB_Of(melA.transpose(2)), chordsB: chordsOf(loA.transpose(2), miA.transpose(2), hiA.transpose(2)),
  bassB: bassOf(bassA.transpose(2)),
}

// Master. Every section is frozen; the last bridge fades t3 out into nothing (c = empty tour).
$: arrange(
  ...freeze(tourOf(t1)), ...freeze([brTo(t1, t2)]),
  ...freeze(tourOf(t2)), ...freeze([brTo(t2, t3)]),
  ...freeze(tourOf(t3)), ...freeze([br(t3, {})])
).postgain(1)
