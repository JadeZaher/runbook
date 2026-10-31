# Rolling mode — keeping the runbook true during execution

**What rolling buys, honestly:** durability against crash and compaction, and
evidence recorded while it is still on screen. It does **not** save tokens — it
spends them to make the record survive. A session-end handoff is cheaper and
fine for short work. Roll when the work is long enough that losing the thread
is the real risk.

## Arming

Rolling does not activate from a state. It activates from an explicit act:
`/runbook:handoff rolling`, "roll the runbook", or a user request.

On arming, write a marker so it survives compaction — the event rolling exists
to protect against:

```
notepad_write_priority  (or .omc/state/rolling.json)
  runbook: <path> · live entry: <### heading> · armed: <YYYY-MM-DD HH:MM>
```

Without the marker, "for the rest of the session" is an assertion that dies at
the first compaction. Re-read the marker after any compaction to recover the
live entry heading — that heading is what `Edit` needs to match.

## Checkpoints

Three, deliberately. More triggers than this and the write cost outruns the
value:

| Trigger | What lands |
|---|---|
| **A phase completes** | Review checkpoint (below), markers, retro lines |
| **A blocker is hit** | The blocker and what would unblock it |
| **Approaching a delegation boundary** (~30–40% context) | Full live-entry refresh before handing off |

Commits, decisions, and disproven assumptions fold into the next checkpoint
rather than triggering their own write. If nothing on this list has happened,
write nothing — rolling is checkpoint-driven, never periodic.

## Cost discipline

- **Edit the live entry; never rewrite the file.** `Edit` needs an exact
  `old_string` — that's what the arming marker's heading is for.
- **2–5 lines per checkpoint.** A checkpoint is a fact, not a summary.
- **`In flight` and `Next` are edited in place** so they're never stale;
  `Done` and `Reviewed` append.
- **Reviews are the dominant cost, not the writing** — budget them below.

## Review checkpoints

**Every phase boundary gets an adversarial review whose verdict is recorded.**
Phase boundaries only — not every task. A phase with no verdict is unreviewed,
not done.

**Adversarial and never self-approving.** The review runs in a pass separate
from the one that wrote the code — a different agent or fresh context. Prompt
the reviewer to **refute**, not confirm. A writing context reviewing its own
output confirms its own assumptions; that is not a review.

**Budget: 1 reviewer per phase.** Escalate to 3 independent reviewers with
majority-refute-kills only for correctness-critical changes — concurrency,
auth, data migration, anything whose failure is silent. Three reviewers on a
routine phase is theater.

**Skip list.** These record `Reviewed: n/a — <reason>` and the marker still
flips: docs and comments, formatting, generated files, dependency version
bumps, single-line fixes, and any change with no runtime behavior.

Match the reviewer to what changed — one, not the catalogue:

| What the phase touched | Checkpoint |
|---|---|
| Any non-trivial diff | `/code-review` (`high` when correctness-critical) |
| Auth, payments, crypto, user input, secrets | `/security-review` — non-negotiable |
| Broad or messy diff, quality only | `/simplify` |
| Contested design | `oh-my-claudecode:critic` (opus) |
| A correctness claim you can't falsify yourself | `/codex:rescue` |
| Test coverage in doubt | `oh-my-claudecode:qa-tester` |

Every code checkpoint loads **`conductor-okf:code-styleguides`** plus
`conductor/workflow.md` and the project's `CLAUDE.md`/`AGENTS.md`. Review
against the conventions this project holds, not generic taste: a finding that
contradicts house style is noise, and a violation the guide names is real even
when the code works. Name the guide in the verdict so a disputed finding traces
to its rule.

### `product.md` as north star

A phase-boundary review also asks: **does this still serve what the product is
for?** Compare `conductor/product.md` to what the phase delivered.

| Drift | Response |
|---|---|
| None, or something the doc doesn't speak to | Nothing. Don't manufacture a finding. |
| Small but still serving the stated goal | One retro line. |
| Large, **work right / doc stale** | *Propose* the `product.md` edit — show the diff, get a yes. Never rewrite the north star unilaterally; the user approved it section by section. |
| Large, **doc right / work wandered** | A finding. Continuing is a decision that needs stating. |
| Large, **unclear which** | Grill — one round, per grilling.md. |

Silent drift compounds: each phase built on a wandered foundation costs more to
correct than the last. Never resolve large drift by quietly picking a side.

### Recording

```
- Reviewed: <phase> · /code-review high + styleguides · product: aligned ·
  2 findings (1 fixed, 1 deferred → Assumptions) · PASS
```

Verdict is `PASS` / `PASS-with-deferred` / `BLOCKED`. `product:` is `aligned` /
`drift-noted` / `product.md edit proposed` / `GRILLED → <decision>`. Deferred
findings go to Assumptions with reversal cost.

**Interaction with the one-sweep test rule.** Checkpoints are *review*, not
test runs — they read the diff and report, and their fixes batch into the
single end sweep. Two sanctioned exceptions execute inline: safety-critical
infrastructure (a panic guard, a lock, an auth path), and a `slice` wave-join
compile gate where the next wave needs a realized tree.

## Track markers

- `[ ]` → `[~]` on start.
- `[~]` → `[x]` after a non-`BLOCKED` verdict, or a skip-list `n/a`.
- **`[x] (unreviewed)`** is legal when no reviewer is available or the user
  declines. A runbook where nothing is ever `[x]` reads as a stalled project —
  worse than an honest unreviewed marker.
- `/conductor-okf:implement` flips markers on its own terms and knows nothing
  about verdicts. Don't fight it; record the verdict in the ledger regardless.
- `metadata.json` stays the machine source of truth. New `conductor/` files get
  OKF frontmatter (`type` required); existing files get it lazily when touched.

## Retros

At each phase boundary, capture what the diff cannot show — one line each:

- A dead end and why it failed. This is what stops the next session repeating it.
- An assumption that turned out false, and what replaced it.
- A surprise about the codebase, environment, or an external system.

No retro for a phase that went as planned; "went fine" is noise.

## Doc updates

- **Rationale for a module** → that directory's `AGENTS.md`, one-line pointer
  from the code.
- **Completed work worth durable history** → `/write-docs:write-docs "..."
  --update`.
- **A convention that emerged** → the project's `CLAUDE.md`/`AGENTS.md`, not the
  runbook.

If it will still be true in a month, it belongs in docs. The runbook holds
current state and should shrink as work completes.
