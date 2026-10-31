# Durable mode — the runbook

**This skill owns `RUNBOOK.md` end to end.** No other command generates,
regenerates, or parses it, and nothing auto-loads it. `conductor-okf` ships no
runbook command; upstream `conductor` — which had one in marketplace source but
never in its installed build — was removed on 2026-08-15. Never reference
`/conductor:runbook`, and never assume something else will regenerate a section
for you.

## Target — the single authoritative rule

Everything else in this skill defers here.

1. **`conductor/` exists** → `conductor/RUNBOOK.md`. It belongs beside
   `product.md` / `tech-stack.md` / `workflow.md`, which are the context it
   summarizes.
2. **No `conductor/`** → create the directory and write
   `conductor/RUNBOOK.md` into it. That is a `mkdir` plus one file, nothing
   more.
3. **`.omc/RUNBOOK.md` exists** → migrate it into (1) and delete it. Legacy
   location.

**Never run `/conductor-okf:setup` to satisfy this.** That command is a
five-round interactive interview that writes ~8 files, spawns a planner agent,
and commits — catastrophic to trigger when someone asks for a handoff because
they are out of context and want to stop. Creating `conductor/` here means
creating the directory, not adopting conductor. When the bundle is absent, add
one line to your reply and move on:

> `conductor/` had no context bundle — `/conductor-okf:setup` will build one
> (product, tech-stack, workflow, styleguides) when you want it.

If the directory can't be created, write `.omc/RUNBOOK.md`, say it's a
fallback, and migrate later.

## Migration

1. Read both files.
2. **Concatenate session logs in date order.** Same format, so they merge with
   no rewrite. Never drop an entry.
3. Carry Decisions, Assumptions, and the review ledger across.
4. Delete `.omc/RUNBOOK.md`. A stub invites two runbooks that drift, which is
   worse than none.

## Format

This skill's own schema — not borrowed from anywhere. Omit empty sections.

```markdown
# <Project> — Runbook

**Last updated:** <YYYY-MM-DD HH:MM> · **Branch:** `<branch>` · **Last commit:** `<hash> <subject>`

## 1. Goal
## 2. State
### Review ledger
<phase · checkpoint · findings · verdict. A phase with no row is unreviewed.>
## 3. Decisions
<settled calls, one-line rationale each>
## 4. Assumptions
<`<assumption> · default taken: <x> · to reverse: <cost>`, highest cost first>
## 5. Environment & gotchas
<branch, uncommitted work, background processes, ports, where credential
values live — never the values>
## 6. Key files
## 7. Continuation plan
<ordered, numbered, imperative, self-contained>
## 8. Session log

### <YYYY-MM-DD HH:MM> — <title>
- Done:
- Reviewed:
- In flight:
- Blocked:
- Next: `<invocation>` — <reason>

## 9. Recommended invocations
<2–4, each with its trigger clause — see invocations.md>
```

One live §8 entry per session, amended as work rolls (rolling.md).

## Clipping — reading one section, not the whole file

The runbook grows; most reads want one section. Never read it whole to answer
"what's next".

**Resolve anchors at read time.** The numbered `## N.` headings are stable
anchors; line numbers are not — rolling mode edits this file constantly, so any
stored line number is stale almost immediately, and clipping the wrong range
yields *silently wrong content*, which is worse than no index at all.

```bash
grep -n '^## ' conductor/RUNBOOK.md     # one cheap call, always correct
```

Then `Read` with `offset`/`limit` between the target heading and the next. Or
in one step: `scrt "^## 7\." --in conductor/RUNBOOK.md --effort deep`.

**Cached hint (optional).** `metadata.json` may carry a hint to skip the grep:

```json
"runbook_index": {
  "total_lines": 214,
  "sections": {"1": 12, "2": 26, "4": 61, "7": 140, "8": 168}
}
```

It is a **hint, never truth**, and carries two guards:

1. **Line-count guard** — if `wc -l` ≠ `total_lines`, the hint is stale.
   Discard it and grep.
2. **Verify on clip** — the first line of every clip must be the expected
   heading. If it isn't, discard and grep.

Regenerate the hint whenever this skill writes the runbook. If a guard ever
fails, delete the hint rather than repairing it — a hint that failed once has
no credibility, and grep costs almost nothing.

## Coupling with conductor

The runbook is the summary; conductor's context files are the foundation
under it.

- **`conductor-okf:context-awareness`** loads `product.md`, `tech-stack.md`,
  `workflow.md`, `tracks.md`. Read the runbook first, descend where it points.
- **`conductor-okf:code-styleguides`** is loaded by every review checkpoint.
- **`product.md`** is the north star for phase-boundary review — see rolling.md.
- **Track markers and §1 must tell the same story.** When they disagree, record
  both and let the user reconcile. Report contradictions; don't fix them.

## Update semantics

- **Read before writing** — the session log is append-only.
- **Absolute dates**, converted at write time.
- **No secrets** — point at where a value lives.
- **Prune §8 entries older than 14 days** once §1 carries their substance.
- **Commit only if the user has been committing this session.**

## Resume

`/runbook:handoff resume`, or "where were we". Nothing auto-loads this file — reading
it is an explicit act.

1. Read `conductor/RUNBOOK.md` (else `.omc/RUNBOOK.md`).
2. **Verify before acting.** Check §1 in-flight claims against `git status` /
   `git log -3`. A three-day-old in-flight list is a hypothesis, not a fact.
   Report drift rather than trusting the file.
3. Read the review ledger before trusting any "done" — unreviewed work is
   in-flight however finished the code looks.
4. Read §4 Assumptions before building on anything; its top line is likeliest
   wrong.
5. Start at §7 step 1.
