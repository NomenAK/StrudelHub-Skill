# StrudelHub-Skill

Agent skill for composing, pushing and iterating live [Strudel](https://strudel.cc) music on [StrudelHub](https://strudelhub.com) sessions, pinned to `@strudel/repl@1.3.0`.

Entry point: [`SKILL.md`](SKILL.md). Everything else is referenced from there.

| Path | Content |
|---|---|
| `SKILL.md` | Workflow, verification policy, golden rules |
| `references/` | API facts, Strudel gotchas (verified against the pinned tag), effects, samples, soundfonts, tonal, stepwise, arrangement devices, long-form pieces |
| `scripts/hub.py` | Session client (`new`, `push`, `play`, `peek`, `versions`, `revert`, `explore`…) — Python stdlib only |
| `scripts/check-track.py` | Offline lint: sound/bank names and indices, broken samples, shadowed globals, lane totals, mininotation and transpiler traps |
| `scripts/verify-track.py` | Targeted runtime check in an isolated recorder page (Playwright): events, sound registry, loop comparison, label counts, pitch ranges, per-tour sweep, silent render |
| `scripts/catalog.py`, `sf-range.py`, `diff-versions.py` | Sound catalogue search, GM MIDI ranges, version diffs |
| `templates/` | Skeletons: multi-section, breaks, techno, long-form (tours + bridges) |

## Install

Copy or clone the folder into your agent's skills directory (e.g. `~/.agents/skills/strudelhub`). Scripts need Python 3; the optional runtime verifier needs `python -m pip install playwright && python -m playwright install chromium`. The API key is read only from the `STRUDELHUB_API_KEY` environment variable and is never written by the scripts.

## Licence

MIT.
