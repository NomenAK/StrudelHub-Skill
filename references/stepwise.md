# Stepwise patterning (experimental in 1.3.0, present in the StrudelHub bundle)

Default Strudel reasons in **cycles**: `fastcat("a b c", "d e")` squashes each argument into half a cycle. Stepwise functions reason in **steps** so patterns of different length line up by step count. Names may change in later Strudel versions; these exist in `@strudel/repl@1.3.0`.

| Function | Effect | Use |
|---|---|---|
| `stepcat(a, b, …)` (`timecat`) | concatenate by steps: `stepcat("bd sd cp", "hh hh")` ≡ `"bd sd cp hh hh"`; `[len, pat]` pairs ≡ `"e3@3 g3"` | phrases of unequal length; `arrange` uses it internally |
| `pace(n)` | play at `n` steps per cycle (`"bd sd cp".pace(4)` ≡ `"<bd sd cp>*4"`) | fix the pulse after `stepcat`/`expand`/`take` |
| `polymeter("c eb g", "c2 g2")` (`pm`) | repeat each until all fit the LCM of steps (≡ `"{c eb g, c2 g2}%6"`) | polymeters, 3-against-4 |
| `take("2")` / `take("-2")` | first / last n steps; patterned `take("1 2 3")` grows | progressive fills, partial phrases |
| `drop("1")` / `drop("-1")` | drop n steps from start / end | |
| `expand(f)` / `contract(f)` | multiply / divide step size (needs `stepcat` or `pace` to hear it) | stretch one phrase against another |
| `extend(n)` | like `fast` but also multiplies the step count: `stepcat("a b".extend(2), "c d")` ≡ `"a b a b c d"` | |
| `grow("1")` / `shrink("1")` | progressively grow / shrink by n steps per repetition (`"1 -1"` from both ends) | risers, breakdowns from a drum phrase |
| `tour(…)` | insert a pattern walking through a list of patterns | |
| `"a [^b c] d"` | `^` makes a sub-pattern count as separate steps | |

Recipes:
- Breakdown fill: `s("bd sd hh cp").shrink("1").pace(4)` — the phrase loses a hit each repetition.
- 7/8 against 4/4: `polymeter("bd ~ sd ~ hh hh sd", "oh ~ ~ ~").pace(8)` — without `pace`, the LCM of 7 and 4 (28 steps) lands in one cycle.
- Odd phrase lengths in an arrangement: `stepcat([3, phraseA], [1, turnaround]).pace(4)` keeps a 4-beat pulse with a 3+1 bar structure.
