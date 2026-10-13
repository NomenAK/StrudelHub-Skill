# Verified controls and functions (`@strudel/repl@1.3.0` bundle — the version strudelhub.com loads — and docs strudel.cc/learn)

Row = name (aliases) — unit / semantics — notes. Every entry here was either found in the 1.3.0 bundle / `controls.mjs` / `pattern.mjs` / `signal.mjs` at that tag or exercised in a live session. Samples and `bank()` are in `samples.md`; chords/scales in `tonal.md`; step-based functions in `stepwise.md`.

## Sound sources (besides samples / `gm_*`)
| Sound | Notes |
|---|---|
| `sine` `sawtooth` `square` `triangle` | basic oscillators; `triangle` is the default when `note` has no `s` |
| `supersaw` | thick detuned saw (`synth.mjs`); `detune`, `unison`, `spread` |
| `white` `pink` `brown` | noise, hardest to softest; percussive with `decay(.03).sustain(0)`; textural beds with `att/rel` + filters |
| `crackle` + `density(x)` | built-in crackle generator; uniform, mechanical character — layered filtered noise sounds more organic |
| `user` + `partials([...])` | additive waveform |
| `fm` / `fmh` / `fmattack` / `fmdecay` / `fmsustain` / `fmenv` | FM on any oscillator; non-integer `fmh` ⇒ metallic |
| `noise(x)` | add pink noise to any oscillator |

## Pitch / envelope
| Control | Semantics | Notes |
|---|---|---|
| `note`, `n`, `freq` | pitch; `n` = sound index for soundfonts/samples | `controls.mjs` |
| `attack (att)` `decay (dec)` `sustain (sus)` `release (rel)` / `adsr("a:d:s:r")` | seconds / level 0–1 | default release 0.01; `adsr(".1:.1:.5:.2")` sets all four |
| `clip (legato)` / `duration` | fraction of event duration / cycles | also truncates soundfonts and samples |
| `velocity (vel)` | multiplies `gain` | |
| `vib (vibrato, v)` / `vibmod` | Hz / depth in **semitones** | slow+shallow (`vib(0.4).vibmod(0.08)`) = tape wow/flutter; `vib(5).vibmod(0.15)` = expressive vibrato; `vib(5.5).vibmod(0.04)` = subtle shimmer |
| `penv` `pattack` `pdecay` `prelease` `pcurve` `panchor` | pitch envelope in semitones / seconds | negative `penv` with a short `pattack` = scooped attack (`penv(-0.5).pattack(0.03)` on a wind sound); large positive + `pdecay` on `sine` = kick |

## Filters
| Control | Semantics |
|---|---|
| `lpf (cutoff, ctf, lp)` / `lpq (resonance)` | low-pass Hz / Q 0–50; mininotation `lpf("800:10")` sets Q too |
| `hpf (hcutoff, hp)` / `hpq` | high-pass; `hpf("200:5")` |
| `bpf (bandf, bp)` / `bpq (bandq)` | band-pass |
| `lpenv (lpe)` · `hpenv (hpe)` · `bpenv (bpe)` | filter-envelope depth in **octaves**; >0 opens from cutoff, <0 starts high and falls |
| `lpattack lpdecay lpsustain lprelease` (`lpa lpd lps lpr`; same with `hp*`, `bp*`) | filter ADSR (s / level); envelope is active as soon as one value is set |
| `fanchor` | 0–1, where the envelope sits around the cutoff (0 = cutoff is the floor) |
| `ftype` | `12db` (0), `ladder` (1), `24db` (2); `ftype("ladder")` is the aggressive one |
| `vowel` | formant filter: `a e i o u ae aa oe ue y uh un en an on` |

Example: `lpf(1500).lpenv(1.2).lpattack(0.01).lpdecay(0.8).lpsustain(0.25)` = opens fast, falls back.

## Space (per orbit)
| Control | Semantics |
|---|---|
| `orbit (o)` | bus with its own reverb + delay |
| `room` | reverb send 0–1 |
| `size (roomsize, sz, rsize)` | 0–10, tail length — small rooms < 2, halls 4–6, cathedrals 8–10 |
| `roomfade (rfade)` | tail fade time (s) |
| `roomlp (rlp)` / `roomdim (rdim)` | tail low-pass at start / at −60 dB |
| `ir (iresponse)` | sample as impulse response (needs `samples()`) |
| `dry` | direct level (bypasses `post`) |
| `delay` / `delaytime (dt)` (s) / `delaysync (ds)` (cycles) / `delayfeedback (dfb)` (clamped 0.995) | per-orbit delay; mininotation shorthand `delay("0.3:0.385:0.35")` |
| `postgain` | gain after all effects — on the whole `arrange(...)` it is a uniform master trim |

## Dynamics / modulation / stereo
| Control | Semantics |
|---|---|
| `compressor("thr:ratio:knee:att:rel")` | DynamicsCompressor **per event** (not a master bus) |
| `duckorbit (duck)` `duckdepth` `duckattack` `duckonset` | sidechain: the carrying event dips the gain of the target orbit; e.g. kick `.duckorbit(3).duckattack(0.3).duckdepth(0.45)` makes orbit 3 pump; `duckorbit("2:3")` for several. **The target orbit must already have played** (lazily created) or the browser logs `duck target orbit 3 does not exist`: start the ducked lane on cycle 0 or add `s("sine").gain(0).orbit(3)` next to the kick |
| `tremolo (trem)` / `tremolosync (tremsync)` / `tremolodepth` / `tremoloskew` / `tremolophase` / `tremoloshape` | amplitude modulation (Hz / cycles); shape `tri square sine saw ramp` |
| `phaser (ph)` `phaserdepth` `phasercenter` `phasersweep` `phaserrate` | phaser |
| `shape` `distort (dist)` `crush` `coarse` | saturation / lo-fi; `distort("amount:postgain:type")` gets loud fast — compensate with the 2nd field (`"0.6:0.8"`); `crush` 16 (clean) → 1 (destroyed); `coarse` Chromium-only |
| `pan` / `pansplay` / `panwidth` / `panorient` | 0 left – 1 right; `pan(perlin.range(0.35, 0.65).slow(4))` = slow drift (sampled per event); `pansplay` spreads chord notes across the field |
| `jux(fn)` / `juxBy(width, fn)` | apply `fn` to the right channel only: `juxBy(0.7, rev)` = mirrored arpeggio, wide stereo |
| `xfade(a, pos, b)` | cross-fade two patterns, `pos` 0–1 patternable (`xfade(a, "<0 .25 .5 .75 1>", b)`) — transitions between sections without `arrange` |

## Pattern functions
| Function | Effect |
|---|---|
| `arrange([n, pat], …)` | form in sections (see gotchas) |
| `stack(a, b, …)` / `cat(a, b)` / `seq(a, b)` | layer / one per cycle / crammed in one cycle |
| `silence` | empty section; also the cleanest way to mute a layer for A/B |
| `late(t)` / `early(t)` | shift in cycles; `late(rand.range(0, 0.015))` = micro-timing humanisation; a value pattern = per-bar rubato |
| `off(t, fn)` | `stack(pat, fn(pat.late(t)))`: `off(1/8, x => x.transpose(12).gain(0.2))` octave shadow; `off(1, x => x.transpose(-7))` canon a fifth below one cycle later |
| `superimpose(fn)` / `layer(fn…)` | add transformed copy / replace with transformed copies |
| `echo(n, t, fb)` / `echoWith(n, t, (p,i) => …)` | rhythmic echoes, with velocity decay or custom transform |
| `swingBy(x, n)` / `swing(n)` | swing; `swingBy(1/6, 8)` = light swing on eighths |
| `every(n, fn)` (`firstOf`), `lastOf(n, fn)` | periodic variation; `lastOf(4, x => x.ply(2))` = fill every 4th cycle |
| `sometimesBy(p, fn)`, `sometimes/often/rarely/almostNever`, `degradeBy(p)`, `undegradeBy(p)` | random variation / thinning |
| `mask("1 1 1 0")` / `struct("x ~ [~ x] ~")` | silence by boolean pattern / impose rhythm; `mask("<1 0>")` + `mask("<0 1>")` on two voices = call and response |
| `ply(n)`, `rev`, `palindrome`, `iter(n)`, `iterBack`, `linger(f)`, `chunk(n, fn)`, `fastChunk`, `inside/outside`, `bite(n, "…")`, `squeeze`, `zoom(a, b)`, `compress(a, b)`, `ribbon(offset, len)` | structural transforms; `ribbon(3, 2)` = loop cycles 3–4 of a longer/random pattern (freeze a good random take) |
| `segment(n)` (`seg`) | sample a continuous signal n times per cycle → turns `saw`/`perlin` into audible sweeps |
| `euclid(k, n)` / `euclidRot(k, n, r)` / `"x(3,8,2)"` | euclidean rhythms (`s("bd(3,8)")`, `note("c3(5,8,2)")`) |
| `press` / `pressBy(x)` | shift every event by half (x) its duration → off-beat/syncopated version |
| `hurry(x)` | `fast` + `speed` for samples |
| `brak` | breakbeat-style squash every other cycle |
| `when(bool, fn)` / `whenKey` | conditional transform |
| `pick([a, b], "0 1")` / `pickRestart` / `inhabit` / `squeeze` | choose sub-patterns by index (song-section switching without `arrange`) |
| `chooseCycles(a, b)` (`randcat`), `wrandcat([a, w], …)`, `chooseWith(sig, [...])`, `irand(n)`, `brand`/`brandBy(p)` | random choice per cycle / weighted / signal-driven; `irand(8)` integer 0–7 |
| `n(run(16)).scale("C4:lydian")` | scale run (risers, fills); scale details in `tonal.md` |
| `saw/sine/tri/square/perlin/rand.range(a,b).slow(n)` | parameter ramps and LFOs (sampled per event) |
| `transpose(n)`, `add(note(n))`, `mul(velocity(x))` | transposition / control arithmetic |
| `slow(x)` on a `cat(...)` outro | ritardando-like stretch (`slow(1.5)`) |
| `setcpm(bpm/4)` | tempo; 1 cycle = one 4/4 bar |

## Visual feedback (the user sees what you cannot hear)
| Function | Effect |
|---|---|
| `._pianoroll()` on a lane (or `.pianoroll()` on the whole) | scrolling piano roll in the editor; shows gaps, register collisions, lane totals |
| `._scope()` / `._spectrum()` | oscilloscope / spectrum of that lane — clipping and mud are visible |
| `._punchcard()` | event grid |
| `.label("bass")` / `.color("#f80")` | names and colours in the highlight — ask the user "which label is too loud?" instead of guessing |

While mixing, push a version with `_scope()` on the master and `label()` per role, ask for a screenshot or a description, then remove them.
