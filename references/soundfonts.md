# GM soundfonts (`gm_*`)

Names: `packages/soundfonts/gm.mjs` at tag `@strudel/repl@1.3.0` (list of files per sound; `//`-commented entries are ignored). Fetch from codeberg — the GitHub mirror 404s on this file. **Sample banks (drum machines, VCSL orchestral/percussion, mridangam, piano) are in `samples.md`** — check there first for mallets, keys, winds and percussion: real samples usually beat the GM soundfont.
Data: `https://felixroos.github.io/webaudiofontdata/sound/<file>.js` (default URL in `fontloader.mjs`).
`.n(i)` selects the i-th file of the list (default 0); an index beyond the list is an error for soundfonts (`check-track.py` flags it). A note outside `keyRangeLow..keyRangeHigh` ⇒ `no soundfont zone found for preset`.

## List before you guess
```bash
python scripts/catalog.py find organ        # gm_*, VCSL and drum-machine names containing "organ"
python scripts/catalog.py list gm            # all 125 gm_* names with their file counts
```
`scripts/check-track.py track.js` validates every `s("…")`, `bank("…")` and `gm_*:i` index in a file and suggests close names.

**Names are Strudel's, not the official GM table.** Traps seen in sessions:

| Wrong guess | Real name |
|---|---|
| `gm_electric_piano_1` | `gm_epiano1` (also `gm_epiano2`) |
| `gm_acoustic_grand_piano` | `gm_piano` |
| `gm_organ` | `gm_church_organ`, `gm_reed_organ`, `gm_drawbar_organ`, `gm_percussive_organ`, `gm_rock_organ` |
| `gm_strings` | `gm_string_ensemble_1`, `gm_string_ensemble_2`, `gm_tremolo_strings`, `gm_pizzicato_strings` |
| `gm_choir` | `gm_choir_aahs`, `gm_voice_oohs`, `gm_synth_choir`, `gm_pad_choir` |
| `gm_bell` | `gm_tubular_bells`, `gm_tinkle_bell`, `gm_glockenspiel`, `gm_celesta`, `gm_music_box` |

Families available (≈125 names): pianos/epianos/clav/harpsichord · organs · guitars (nylon, steel, jazz, clean, muted, overdriven, distortion, harmonics) · basses (acoustic, finger, pick, fretless, slap, synth) · strings/harp/timpani · ensembles/choirs · brass · reeds (sax, oboe, english_horn, bassoon, clarinet) · pipes (piccolo, flute, recorder, pan_flute, blown_bottle, shakuhachi, whistle, ocarina) · `gm_lead_1_square` … `gm_lead_8_bass` · `gm_pad_*` · `gm_fx_*` · ethnic (sitar, banjo, shamisen, koto, kalimba, bagpipe, fiddle, shanai) · percussive (tinkle_bell, agogo, steel_drums, woodblock, taiko_drum, melodic_tom, synth_drum, reverse_cymbal) · fx (guitar_fret_noise, breath_noise, seashore, bird_tweet, telephone, helicopter, applause, gunshot).

## Sample banks loaded by default
See `samples.md` (drum machines with `bank()`, VCSL instruments, mridangam, `piano`, Dirt subset, uzu-drumkit defaults, synths and zzfx). No vinyl/crackle sample in the defaults: build textures from `white/pink/brown` noise with `att/rel` and filters, or `s("crackle").density(x)`. Any other bank: `samples('github:user/repo')` at the top of the code, then `s("name")`.

## Measured MIDI ranges (sample; 60 = c4)
| Sound | idx | File | Range | Notes |
|---|---|---|---|---|
| `gm_church_organ` | 0 | 0190_JCLive | 33–101 (a1–f7) | g1 (31) **errors** |
| `gm_church_organ` | 1 | 0190_Aspirin | 0–127 | very low 16' pedal |
| `gm_drawbar_organ` | 0 | 0160_JCLive | 21–108 | |
| `gm_percussive_organ` | 0 | 0170_JCLive | 0–108 | sharp attack |
| `gm_reed_organ` | 0 | 0200_JCLive | 0–108 | |
| `gm_tubular_bells` | 0 | 0140_JCLive | 27–95 | |
| `gm_timpani` | 0 | 0470_Aspirin | 0–127 | |
| `gm_string_ensemble_1` | 0 | 0480_Aspirin | 0–127 | |
| `gm_choir_aahs` | 0 | 0520_Aspirin | 0–127 | |
| `gm_voice_oohs` | 0 | 0530_Aspirin | 0–127 | |
| `gm_flute` | 0 | 0730_JCLive | 24–113 | |
| `gm_pad_halo` | 0 | 0940_Chaos | 0–108 | |

Measured 2026-10-13 with `python scripts/sf-range.py <name> [idx]`; remote files can change — re-check when in doubt. Sounds not listed here have not been measured: run the script before writing below c2 or above c7.

## Timbre notes (starting points, any style)
- GM sounds are fairly loud; `gain(0.2–0.5)` is a sane start. Several `gm_*` layers plus drums sum well above 1.0 — trim on the master.
- Sustained GM sounds (organs, strings, choirs, pads) take `attack`/`release`; plucked ones (harp, guitars, epianos, mallets) respond to `clip` for staccato.
- Doubling a GM sound with a `sine` at unison, `velocity(0.2–0.35)`, adds body without changing character.
- Wind/voice leads: `vib(4–6).vibmod(0.1–0.2)` plus a small negative `penv` for the attack.
- Keyboard/plucked: slow `vib(0.3–0.5).vibmod(0.05–0.1)` reads as tape or analog drift.
- Distance: `attack 0.5–0.9`, `hpf(300–400)`, `dry(0.4–0.5)`, large orbit.
- Noise beds: `s("brown*2").att(0.4).rel(0.6).lpf(2800).hpf(300)` (hiss), `s("brown").lpf(90)` (rumble), `s("white*16").degradeBy(0.6).dec(0.025).sus(0).bpf(2500)` (dust) — mix to taste or drop any of them.
