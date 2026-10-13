# Sample banks and synths available in a StrudelHub session

Everything below is registered by the prebake of `@strudel/repl@1.3.0` (the bundle strudelhub.com loads) — no `samples()` call needed. Lists generated on 2026-10-13 from the sample maps the bundle fetches (`felixroos/dough-samples`, `tidalcycles/uzu-drumkit`, `todepond/samples` aliases); `python scripts/catalog.py update` refreshes `.catalog.json`; `catalog.py find <word>` / `info <name>` / `range <pitched_name>` query it; `catalog.py external github:user/repo` lists what a `samples()` call would add. `(n)` = number of variants, selectable with `.n(i)` or `name:i` (indexes wrap for samples).

Names are case-insensitive. Samples only load on first trigger: the very first hit of a new sound may be late or silent — not an error.

## Drum machines — `s("bd sd hh").bank("RolandTR909")`
`bank("X")` prepends `X_` to every name in `s()`. Standard hits: `bd sd rim cp hh oh cr rd ht mt lt sh cb tb perc misc fx`. Not every bank has every hit (table below; `check-track.py` flags a missing hit). Aliases are lower-case: `bank("tr909")` ≡ `bank("RolandTR909")`.

Without `bank()`, the bare names `bd sd hh oh cp cr rd ht mt lt rim sh cb tb misc brk` resolve to **uzu-drumkit** (`bd`(8) `sd`(5) `hh`(5) `oh`(4) `cp`(2) `cr`(2) `rim`(2) `misc`(5), others 1). `brk` is a **built-in 1-bar processed amen break** — `s("brk").fit()` or `.slice(8, "…")` works with no `samples()` call.

| Bank | alias | hits (×n = variants via `.n(i)`) |
|---|---|---|
| `AJKPercusyn` | percysyn | bd cb×2 ht sd |
| `AkaiLinn` | linn | bd cb cp cr hh ht lt mt oh rd sd sh tb |
| `AkaiMPC60` | mpc60 | bd×2 cp cr hh ht lt misc×2 mt oh perc×5 rd rim sd×3 |
| `AkaiXR10` | xr10 | bd×10 cb cp cr×3 hh×2 ht lt×2 misc×4 mt×2 oh perc×15 rd rim×2 sd×10 sh tb |
| `AlesisHR16` | hr16 | bd cp hh ht lt oh perc×8 rim sd sh×3 |
| `AlesisSR16` | sr16 | bd×13 cb cp cr×2 hh×3 misc×3 oh×4 perc×7 rd×3 rim sd×12 sh tb |
| `BossDR110` | dr110 | bd cp cr hh oh rd sd |
| `BossDR220` | dr220 | bd cp cr hh ht lt mt oh perc rd sd |
| `BossDR55` | dr55 | bd×2 hh×2 rim sd×8 |
| `BossDR550` | dr550 | bd×5 cb×2 cp cr hh×2 ht×3 lt×3 misc×3 mt×2 oh×2 perc×11 rd×2 rim sd×6 sh×2 tb |
| `CasioRZ1` | rz1 | bd cb cp cr hh ht lt mt rd×2 rim sd |
| `CasioSK1` | sk1 | bd hh ht mt oh sd |
| `CasioVL1` | vl1 | bd hh sd |
| `DoepferMS404` | ms404 | bd×2 hh lt oh sd |
| `EmuDrumulator` | drumulator | bd cb cp cr hh ht lt mt oh perc rim sd |
| `EmuModular` |  | bd×2 misc perc×2 |
| `EmuSP12` | sp12 | bd×14 cb cp cr hh×2 ht×6 lt×6 misc×7 mt×4 oh perc rd rim×2 sd×21 |
| `KorgDDM110` | ddm110 | bd cp cr hh ht×2 lt×2 oh rim sd |
| `KorgKPR77` | kpr77 | bd cp hh oh sd |
| `KorgKR55` | kr55 | bd cb cr hh ht oh perc×2 rim sd |
| `KorgKRZ` | krz | bd cr fx×2 hh ht lt misc oh rd sd×2 |
| `KorgM1` | m1 | bd×3 cb cp cr hh×2 ht×2 misc×16 mt oh×2 perc×7 rd rim sd×4 sh tb |
| `KorgMinipops` | minipops | bd×7 hh×4 misc×4 oh×4 sd×13 |
| `KorgPoly800` | poly800 | bd×4 |
| `KorgT3` | t3 | bd×5 cp hh×2 misc×4 oh×2 perc×4 rim sd×5 sh×3 |
| `Linn9000` | 9000 | bd cb×2 cr×2 hh ht×2 lt×2 mt oh perc×3 rd×2 rim sd tb |
| `LinnDrum` |  | bd cb cp cr hh×3 ht×2 lt×2 mt oh perc×6 rd rim×3 sd×3 sh tb |
| `LinnLM1` | lm1 | bd×4 cb cp hh ht lt oh perc×3 rim sd sh tb |
| `LinnLM2` | lm2 | bd×4 cb cp cr hh×2 ht lt mt oh×2 rd rim×2 sd×4 sh tb |
| `MFB512` |  | bd cp cr hh ht lt mt oh sd |
| `MPC1000` |  | bd×5 cp hh×4 oh perc sd×4 sh |
| `MoogConcertMateMG1` | concertmatemg1 | bd×3 sd×2 |
| `OberheimDMX` | dmx | ×3 bd×3 cp cr hh ht lt mt oh rd rim sd×3 sh tb |
| `RhodesPolaris` | polaris | bd×4 misc×4 sd×4 |
| `RhythmAce` | ace | bd×3 hh ht lt oh perc×6 sd×3 |
| `RolandCompurhythm1000` | compurhythm1000 | bd cb cp cr hh ht lt mt oh perc×3 rd rim sd |
| `RolandCompurhythm78` | compurhythm78 | bd cb hh×2 misc×4 oh×2 perc×8 sd tb |
| `RolandCompurhythm8000` | compurhythm8000 | bd cb cp cr hh ht lt mt oh perc×2 rim sd |
| `RolandD110` | d110 | bd cb×2 cr hh lt oh×2 perc×3 rd rim sd×3 sh tb |
| `RolandD70` | d70 | bd×4 cb cp cr hh lt mt oh perc rd rim sd×5 sh |
| `RolandDDR30` | ddr30 | bd×8 ht×4 lt×4 sd×8 |
| `RolandJD990` | jd990 | bd×10 cb cp cr hh×4 ht lt×5 misc×12 mt×2 oh×2 perc×6 rd sd×15 tb |
| `RolandMC202` | mc202 | bd×5 ht×3 perc |
| `RolandMC303` | mc303 | bd×16 cb×2 cp×8 fx×2 hh×6 ht×5 lt×5 misc×8 mt×6 oh×5 perc×39 rd×2 rim×6 sd×26 sh×7 tb×5 |
| `RolandMT32` | mt32 | bd cb cp cr hh ht lt mt oh×2 perc×13 rd rim sd×2 sh×2 tb |
| `RolandR8` | r8 | bd×7 cb cp cr hh×2 ht×4 lt×4 mt×4 oh perc×8 rd×2 rim×2 sd×12 sh×2 tb |
| `RolandS50` | s50 | bd×4 cb cp cr×2 ht lt×2 misc×6 mt oh perc×14 rd sd×3 sh×4 tb×2 |
| `RolandSH09` | sh09 | bd×43 |
| `RolandSystem100` | system100 | bd×15 hh×2 misc×2 oh×3 perc×19 sd×21 |
| `RolandTR505` | tr505 | bd cb×2 cp cr hh ht lt mt oh perc×3 rd rim sd |
| `RolandTR606` | tr606 | bd cr hh ht lt oh sd |
| `RolandTR626` | tr626 | bd×2 cb cp cr×2 hh ht×2 lt×2 mt×2 oh perc×8 rd×2 rim sd×3 sh tb |
| `RolandTR707` | tr707 | bd×2 cb cp cr hh ht lt mt oh rim sd×2 tb |
| `RolandTR727` | tr727 | perc×10 sh×2 |
| `RolandTR808` | tr808 | bd×25 cb×2 cp×5 cr×25 hh ht×5 lt×5 mt×5 oh×5 perc×16 rim sd×25 sh×2 |
| `RolandTR909` | tr909 | bd×4 cp×5 cr×5 hh×4 ht×9 lt×9 mt×9 oh×5 rd×5 rim×3 sd×16 |
| `SakataDPM48` | dpm48 | bd×3 cp cr hh×2 ht lt×2 mt oh perc×2 rd rim sd×2 sh×2 |
| `SequentialCircuitsDrumtracks` | circuitsdrumtracks | bd cb cp cr hh ht oh rd rim sd sh tb |
| `SequentialCircuitsTom` | circuitstom | bd cp cr hh ht×2 oh sd |
| `SergeModular` | serge | bd misc perc×5 |
| `SimmonsSDS400` | sds400 | ht×3 lt×6 mt×8 sd×3 |
| `SimmonsSDS5` | sds5 | bd×12 hh×5 ht×3 lt×8 mt×6 oh×2 rim×7 sd×21 |
| `SoundmastersR88` | r88 | bd cr hh oh sd×2 |
| `UnivoxMicroRhythmer12` | microrhythmer12 | bd hh oh sd |
| `ViscoSpaceDrum` | spacedrum | bd×11 cb hh×6 ht×7 lt×2 misc×2 mt×2 oh×3 perc×2 rim sd×3 |
| `XdrumLM8953` | lm8953 | bd×3 cr hh×2 ht×2 lt×2 mt×2 oh rd rim×2 sd×5 tb |
| `YamahaRM50` | rm50 | bd×103 cb×6 cp×2 cr×22 hh×18 ht×25 lt×49 misc×28 mt×34 oh×12 perc×56 rd×13 sd×108 sh×6 tb×3 |
| `YamahaRX21` | rx21 | bd cp cr hh ht lt mt oh sd |
| `YamahaRX5` | rx5 | bd×2 cb fx hh lt oh rim sd×3 sh tb |
| `YamahaRY30` | ry30 | bd×13 cb×2 cp cr×2 hh×4 ht×3 lt×3 misc×8 mt×2 oh×4 perc×13 rd×3 rim×2 sd×21 sh×2 tb |
| `YamahaTG33` | tg33 | bd×4 cb×3 cp cr×3 fx ht×2 lt×2 misc×10 mt×2 oh perc×12 rd×2 rim sd×5 sh tb |

Idiom starting points (verify by ear with the user): TR808 (hip-hop, trap, electro), TR909 (house, techno), TR707/TR727 (80s pop, latin), LinnDrum/LinnLM1 (80s pop, Prince), AkaiMPC60/EmuSP12 (boom-bap, lo-fi), OberheimDMX (80s electro), CasioRZ1/SK1 (lo-fi, chiptune), YamahaRM50/RY30 (90s), KorgMinipops/RhythmAce (organ-combo vintage), RolandCompurhythm78 (CR-78, 70s pop).

## VCSL (Versilian Community Sample Library) — orchestral, keyboard, world, percussion
Real multisampled instruments; often better than `gm_*` for mallets, keys, winds and percussion. Pitched ones are keyed by note: `note("c4 e4").s("vibraphone")` picks the nearest sample (so the range below is where it sounds natural; outside it the sampler pitch-shifts the nearest file, which gets thin or muddy). Unpitched ones: `s("conga:3")` selects a variant.

### Pitched (name · variants · sampled range)
| Sound | n | range |
|---|---|---|
| `balafon` | 6 | c#3–f5 |
| `balafon_hard` | 6 | c#3–f5 |
| `balafon_soft` | 6 | c#3–f5 |
| `belltree` | 6 | c5–a#5 |
| `clavisynth` | 19 | c0–c6 |
| `dantranh` | 17 | b1–b4 |
| `dantranh_tremolo` | 16 | b1–b4 |
| `dantranh_vibrato` | 16 | b1–b4 |
| `fmpiano` | 22 | c0–c7 |
| `folkharp` | 29 | c1–g#5 |
| `glockenspiel` | 7 | g4–c7 |
| `handchimes` | 19 | c3–c6 |
| `harmonica` | 9 | c3–c6 |
| `harmonica_soft` | 10 | c3–c6 |
| `harmonica_vib` | 10 | c3–c6 |
| `harp` | 23 | e1–f7 |
| `kalimba` | 11 | b2–b4 |
| `kalimba2` | 25 | g1–c#6 |
| `kalimba3` | 22 | a#1–a4 |
| `kalimba4` | 22 | a#1–c#5 |
| `kalimba5` | 14 | f2–f4 |
| `kawai` | 37 | c0–c7 |
| `marimba` | 10 | f1–c6 |
| `ocarina` | 11 | a3–c#5 |
| `ocarina_small` | 10 | a#4–b5 |
| `ocarina_small_stacc` | 13 | a4–c6 |
| `ocarina_vib` | 10 | a3–c5 |
| `organ_4inch` | 27 | c1–e5 |
| `organ_8inch` | 27 | c1–e5 |
| `organ_full` | 27 | c1–e5 |
| `piano1` | 22 | c0–c7 |
| `pipeorgan_loud` | 21 | c1–c6 |
| `pipeorgan_loud_pedal` | 11 | c1–f#3 |
| `pipeorgan_quiet` | 21 | c1–c6 |
| `pipeorgan_quiet_pedal` | 11 | c1–f#3 |
| `psaltery_bow` | 11 | a#3–f#5 |
| `psaltery_pluck` | 11 | a#3–f#5 |
| `psaltery_spiccato` | 11 | a#3–f#5 |
| `recorder_alto_stacc` | 12 | f#3–e5 |
| `recorder_alto_sus` | 12 | f3–e5 |
| `recorder_alto_vib` | 12 | f3–e5 |
| `recorder_bass_stacc` | 15 | f2–f4 |
| `recorder_bass_sus` | 12 | f#2–e4 |
| `recorder_bass_vib` | 14 | f2–e4 |
| `recorder_soprano_stacc` | 12 | c4–a#5 |
| `recorder_soprano_sus` | 13 | c4–c6 |
| `recorder_tenor_stacc` | 12 | c3–b4 |
| `recorder_tenor_sus` | 13 | c3–c5 |
| `recorder_tenor_vib` | 14 | c3–b4 |
| `sax` | 23 | g#1–e5 |
| `sax_stacc` | 23 | g#1–e5 |
| `sax_vib` | 19 | a#1–d5 |
| `saxello` | 8 | a#2–e5 |
| `saxello_stacc` | 8 | a#2–d5 |
| `saxello_vib` | 8 | a#2–d#5 |
| `steinway` | 42 | a#0–g#7 |
| `strumstick` | 19 | d2–a4 |
| `super64` | 13 | c2–c6 |
| `super64_acc` | 13 | c2–c6 |
| `super64_vib` | 13 | c2–c6 |
| `tubularbells` | 9 | c3–e4 |
| `tubularbells2` | 11 | c4–f5 |
| `vibraphone` | 11 | f2–e5 |
| `vibraphone_bowed` | 6 | a2–e5 |
| `vibraphone_soft` | 11 | f2–e5 |
| `wineglass` | 4 | d#4–d5 |
| `wineglass_slow` | 4 | d#4–d5 |
| `xylophone_hard_ff` | 8 | g3–c7 |
| `xylophone_hard_pp` | 8 | g3–c7 |
| `xylophone_medium_ff` | 8 | g3–c7 |
| `xylophone_medium_pp` | 8 | g3–c7 |
| `xylophone_soft_ff` | 8 | g3–c7 |
| `xylophone_soft_pp` | 8 | g3–c7 |

### Unpitched (variants via `.n(i)`)
`agogo`(5), `anvil`(9), `ballwhistle`(2), `bassdrum1`(8), `bassdrum2`(30), `bongo`(28), `brakedrum`(17), `cabasa`(6)
`cajon`(18), `clap`(10), `clash`(10), `clash2`(5), `clave`(6), `conga`(34), `cowbell`(13), `darbuka`(20)
`didgeridoo`(12), `fingercymbal`, `flexatone`(8), `framedrum`(18), `gong`(7), `gong2`(6), `guiro`(5), `handbells`(3)
`hihat`(15), `marktrees`(6), `oceandrum`(3), `ratchet`(8), `shaker_large`(6), `shaker_small`(16), `siren`(5), `slapstick`(5)
`sleighbells`(6), `slitdrum`(6), `snare_hi`(8), `snare_low`(20), `snare_modern`(72), `snare_rim`(4), `sus_cymbal`(25), `sus_cymbal2`(23)
`tambourine`(7), `tambourine2`(7), `timpani`(30), `timpani2`(204), `timpani_roll`(10), `tom2_mallet`(8), `tom2_rim`(6), `tom2_stick`(8)
`tom_mallet`(8), `tom_rim`(6), `tom_stick`(8), `trainwhistle`(6), `triangles`(37), `vibraslap`(4), `woodblock`(10)

Notes: `snare_modern`(72) and `timpani2`(204) are big velocity/variant sets — `.n(irand(72))` for natural variation. `pipeorgan_*` / `organ_*` are real pipe/reed organs; `organ_4inch` = quiet flute stop, `organ_full` = full registration. `super64` = Super 64 accordion. `dantranh` = Vietnamese zither. `psaltery_bow` = bowed psaltery, sustained.

**Broken in Chromium (2026-10-13): `shaker_small` and `shaker_large`.** Their GitHub paths contain `%2C` (`Shaker, Small/`), and raw.githubusercontent.com answers with two `Content-Disposition` headers → `net::ERR_RESPONSE_HEADERS_MULTIPLE_CONTENT_DISPOSITION`; every variant fails, silently for the listener (the verifier reports it under `diagnostics`). Substitute: `s("tambourine").n("<5 6>").hpf(4000)` reads as a shaker. `check-track.py` errors on both names; `catalog.py` marks them `(broken: …)`.

## Other default maps
- **`piano`**(29): Salamander-type multisample keyed A0–C8 — `note("c4").s("piano")`. Good neutral acoustic piano; `steinway`/`kawai` (VCSL) are alternatives with different colour.
- **Dirt-Samples subset**: `casio`(3) `crow`(4) `east`(9) `insect`(3) `jazz`(8) `metal`(10) `numbers`(9) `space`(18) `wind`(10). `numbers` = spoken digits; `space`/`wind` = long textures (use `loop(1)`, `loopAt`, `chop`).
- **mridangam** (South-Indian drum strokes, bank-less names): `ardha`(20) `chaapu`(13) `dhi`(7) `dhin`(8) `dhum`(7) `gumki`(14) `ka`(12) `ki`(7) `na`(12) `nam`(8) `ta`(9) `tha`(7) `thom`(7). The docs' `.bank("mridangam")` examples are **not** needed here — the names are top-level.
- **Synth sources**: `sine sawtooth square triangle` (+ aliases `sin saw sqr tri`), `pulse` (+ `pw`), `supersaw` (`detune unison spread`), `user` (+ `partials([...])`, else falls back to triangle), noise `white pink brown`, `crackle` (+ `density`), `bytebeat`.
- **zzfx** (chiptune one-shots): `z_sine z_sawtooth z_square z_triangle z_tan z_noise` with `zrand curve slide deltaSlide pitchJump pitchJumpTime znoise zmod zcrush zdelay`. Good for 8-bit blips, lasers, hits.

## Loading more
`samples('github:<user>/<repo>[/<branch>]')` at the top of the code (expects a `strudel.json` at the repo root), e.g. `samples('github:tidalcycles/dirt-samples')` (218 names: `breaks125 breaks152 breaks157 breaks165 amencutup(32) …`), `samples('github:yaxu/clean-breaks/main')` (32 classic breaks: `amen apache funkydrummer think kool impeach sesame …`), `samples('github:switchangel/pad')`. Or an inline map: `samples({kick: 'bd/BT0AADA.wav'}, 'https://raw.githubusercontent.com/tidalcycles/Dirt-Samples/master/')`. Pitched custom samples: `{moog: {g2: 'file.wav', g3: '…'}}`. Browser caching of `strudel.json` is aggressive: append `?v=2` to force a refetch.

## Sample manipulation controls (all verified in the 1.3.0 bundle)
| Control | Semantics |
|---|---|
| `n(i)` / `name:i` | variant index (wraps for samples; errors for `gm_*`) |
| `speed(x)` | playback rate; negative = reverse; cheap pitch change (`speed(2)` = +1 octave) |
| `begin(0–1)` / `end(0–1)` | start / stop point as a fraction of the file |
| `cut(group)` | choke group: a new hit in the group stops the previous one (`s("[oh hh]*4").cut(1)`) |
| `clip(x)` (`legato`) | multiply event duration; truncates the sample at the end |
| `loop(1)` + `loopBegin`/`loopEnd` | loop a region; not tempo-synced |
| `loopAt(n)` | stretch the sample to `n` cycles by changing speed (breaks, loops) |
| `fit()` | fit the sample to its event duration (`s("amen/4").fit()`) |
| `chop(n)` | cut into `n` grains played in order (`.chop(8).rev()` reverses the chunks) |
| `striate(n)` | `n` parts, one part per repetition |
| `slice(n, "0 1 2 3")` / `slice([0,.25,.5,.75], …)` | play numbered slices in a pattern (breakbeat rearrangement) |
| `splice(n, "…")` | like `slice` but each slice is re-pitched to fit its step (tempo-locked) |
| `scrub("0.25:1.5 …")` | position (0–1) `:` speed, tape-style |
| `stretch(x)` | phase-vocoder time stretch (expensive) |
| `fmh/fmi` | FM also works on samples |

Break recipe (any genre): `s("brk").fit().slice(8, "0 1 2 3 4 5 6 7".every(4, x => x.rev()))` with the built-in break, or `samples('github:yaxu/clean-breaks/main'); s("amen/4").fit().slice(8, …)` — `/4` because that break is 4 bars long; `slice` indices then reorder it. `splice` instead of `slice` keeps slices tempo-locked when the step lengths vary.
