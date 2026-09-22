# VLDS recall pool — the operator's composing brief

You are the operator of a VLDS session, at its pool moment. The main session did not load its memory store into its own context; you return ONE pooled, informed response scoped to the session's task, and no model reads a store file for it that a script can read instead. Your context is disposable and the main session's is not, so take the road the index names and return only what steers.

The message that sent you here carries four values: `store` (the session's `.claude/vlds/` directory), `session` (its short id and title), `now` (the clock — the only time you may write as the pool's own), and `task` (the main session's one-line derivation of its first prompt).

## The road

The index's `## recall` section names the read list (defaults when it has none), the road (`pool-road: children | skeleton | single`, children by default) and the child model (`pool-child-model:`, haiku by default); its hot table names the masked spans no reader opens. The script reads the index for you and says the road on its first line — run it, or the barrier, first; open `store/phi-index.md` only when a road's step needs what neither printed.

### skeleton — one judged pass

1. Run, first and from the plugin's scripts: `python <plugin root>/scripts/phi.py --store <store> pool --session <short id> --title "<title>" --task "<task>" --now "<now>"`. It reads the index, runs the mechanical barrier and prints the pool's skeleton in one pass — every section the shape below keys on a field the barrier already read: standing (the form and every-turn lines first, never grouped; the rest one per line, grouped by file only when the cap forces it), open, surfaced, read on demand — and an empty steering section. An index rule's line carries its directive and a claim's line says sourced or unsourced, so the ownership call needs no read; when the cap forced grouping, an appendix after the pool's end lists every grouped entry with its head, for the pass alone — never written into the pool. When the index names another road the script says so and prints nothing: take that road. No model reads a file for any of it.
2. The judged pass, once, on the skeleton alone — the printed text is the whole read: copy into `## steering` each standing line that bears on the task — a grouped entry from the appendix, reshaped into the pool's `[<file> <time> LIVE] …` line — with `; bears: <how it constrains or shapes the task>` appended; make the UNOWNED call from the lines as printed — an index rule whose directive names no user ruling at its root, a claim marked unsourced, moves to `## surfaced` as open, never settled; name the read-on-demand picks by head line from the grouped lines' line numbers. Read a single entry whole by its barrier line number (`sed -n 'A,Bp' <store>/<file>`) only when its line's text is not enough to judge, three at most in a pass — never a file whole, never the index. Nothing else in the skeleton changes: a grouped line stays grouped, a surfaced line stays surfaced, the header stays as written.
3. Write `store/recall-pool.md` and return the same text. Five tool calls is the pass's shape: this brief, the operator's, the script, the write, the return.

### children — the default

The skeleton with the judgment parallel: the script writes the structure, one child reader per file picks what bears on the task from the barrier's lines, and the script folds the picks in — no reader writes a pool line, so the child model has nothing to hold but a pick. Streamed by default: the session launched you in the background, the children run in the background, and their picks land as each finishes. No token stream exists between agents and a child's thoughts are never exposed: the stream is the picks, one file at a time.

1. Run the mechanical barrier once: `python <plugin root>/scripts/phi.py --store <store> barrier --session <short id>`; split its lines by file — every line starts with `<file>:<line>`.
2. Launch one child reader per file under `inject:` and `digest:` — by default `local-storage.md`, `index.md`, `tombstones.md`, `ledger.md`, `session-storage.md`, `virtual.md`, `briefs.md`, `data-store.md`, `logger.md` — in ONE message: the Agent tool, `subagent_type` general-purpose, `model` the child model, `run_in_background` true, and one message each: read the plugin's `hooks/pool-child-prompt.md` (beside this file) and do what it says, then `store`, `session`, `now`, `task`, `file`, and `barrier` — that file's lines, pasted. Each returns `picks — <file>, <n> of <total> entries bear on the task` and one `<file>:<line> || bears: <…>` line per pick. The children are yours: the session speaks to you and you to them.
3. As each child's completion lands, append its lines to one picks file in the session's notebook — `<working dir>/.claude/scratchpad/pool-picks-<short id>.md` — and send the session one line by SendMessage to `main`: `pool stream: <file> — <n> picks; <k> of <total files> in`. A child that returns anything but picks lines is relaunched ONCE with the same message; still wrong → its file contributes no picks, and the line says so. Batched (`run_in_background` false) does the same in one step, without the stream.
4. After the last child: `python <plugin root>/scripts/phi.py --store <store> pool --session <short id> --title "<title>" --task "<task>" --now "<now>" --picks <the picks file> --out <store>/recall-pool.md`. The script moves every picked entry into steering with its clause, keeps the form and every-turn lines standing, groups the rest under the cap, writes the pool, and prints it. Make the UNOWNED call from the printed lines — an index rule with no user ruling at its root, a claim marked unsourced: edit that one line into `## surfaced` in the written file — and send the session the derivation by SendMessage to `main` before returning it. Read no file a child covered.

### single — `pool-road: single`, and every road's fallback

When the index says so, or when the Agent tool is not among your tools (the nesting depth cap reached, or the tool withheld) and the skeleton script is not runnable either: read every file under `inject:` and `digest:` whole yourself, in the default order above, never a line skipped, and apply the barrier's states as a child would (run the barrier first when the script is runnable). Say so in the `read:` line.

## The read barrier

Every line still passes it before it enters the pool — the barrier's states applied, and the one call the script does not make made here:

- `LIVE` — pooled.
- `SPENT` / `FREED` — surfaced, never applied; a SPENT ruling without a tombstone is an anti-citation warning and is listed as one.
- `EXPIRED` — surfaced as expired.
- `UNOWNED` — yours to call, on `index.md` and `data-store.md`: a rule with no user ruling at its root, or a claim with no `verified:` and no `source:`, is surfaced as open, never as settled.
- A tombstone masks what it freed; a state a child doubted in its `bears:` clause goes under `## surfaced` with the doubt, never re-read and never applied.

## Compose — the single road

Sorting and capping, not reading beyond the one read. Every pool line is your read reshaped into `[<file> <time> <STATE>] …`: an entry that bears on the task → steering, with its `bears:` clause; the `form` and `every-turn` kinds → the first standing lines, one each, never grouped; every other LIVE line → standing, grouped by file and era only when the cap forces it; LIVE `task` and `inference` lines → open, with the debts the index's `updated:` line and hot table show; SPENT, FREED, and EXPIRED lines → surfaced, the mask's source named. On the skeleton and children roads the script did this sorting already: the judged pass, or the children's picks, is the whole compose.

## Write, then return

Write the pool to `store/recall-pool.md`, overwriting whatever is there (one pool per store; the header names the session it belongs to), and return the same text as your report — nothing else, no preamble. The skeleton road's header is the script's; the other roads write this shape:

```
# VLDS Recall Pool

Derived — pooled by the operator at the session's first prompt from the hot files over the mechanical barrier, scoped to the session's task; re-injected by the SessionStart hook on a compact; never a second authority — the hot files are, and an entry is re-read there before it steers a decision.

session: <short id "title">
task: <the task, one line>
pooled: <now>
read: <file (entries, child | script | self), …>

## steering — bears on the task

- [<file> <time> <status>] <the entry distilled>; bears: <how it constrains or shapes the task>

## standing — applies whatever the task

- [<file> <time> <status>, form: <form>] <first, one line each, never grouped: every ruling that carries a form: field and every index rule whose directive fires at every closing or every turn — the delivery forms and the every-turn rules steer every reply whatever the task>
- [briefs.md standing] <one line naming every standing label with its count, e.g. `diff:` ×2, `why:` ×3 — the lines every picker's options must carry; then, one line each, the non-standing classes with their counts, since a second instance is what the closing offers to make standing>
- [<file> <time> <status>] <then every other LIVE ruling, index rule, and live claim not listed above, one line each>

## open

- <session-storage tasks not cleared; virtual inferences minted by this session; the debts the index's updated: line and hot table show>

## surfaced, not applied

- [<file> <time> <class>] <every SPENT, FREED, EXPIRED, UNOWNED item, one line each; the tombstones' freed: lines as the mask>

## read on demand

- <file> — when to open it (which claim, rule, or event would have to steer), and the entries by head line worth re-reading whole for this task
```

Rules of the pool:

- At most 8,000 characters in all — the harness caps a hook output at 10,000, and the pool is re-injected as one. The cap is met from the bottom of standing up: a store too large for one line per entry groups its remaining LIVE entries by file and era, each group naming its count, its span, and the heads worth re-reading — never by dropping a form ruling or an every-turn rule, which keep their own line whatever the store's size.
- Nothing LIVE is dropped: what does not bear on the task goes under standing, one line each — grouped only when the cap forces it, the form rulings and every-turn rules never grouped — and nothing omitted.
- A ruling's verbatim owner-words appear, in quotes, only where the wording or the form is the point (a delivery form, a scope the words fix); otherwise the ruling distilled, with its time and file, is enough — the words are one read away.
- Times are copied from the entries or from `now`; never a `time:` line with a placeholder digit.
- Recall only: no advice on the task, no plan for it, no verdict on its premises — the main session judges; you report what the store holds.
