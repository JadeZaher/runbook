---
name: handoff
description: >
  Packages current work so a fresh session or subagent can resume it without
  re-discovery — state, decisions, gotchas, key files, and an executable
  continuation plan — grilling the user in one round on the questions that
  would otherwise be re-litigated. Prints inline by default; writes or rolls a
  durable RUNBOOK.md on request. Use for "handoff", "passoff", "save a
  handoff", "runbook", "roll the runbook", "where were we", "resume", or moving
  this conversation to a new session without losing context.
---

# handoff — session state, packaged for whoever picks it up next

| Mode | Trigger | Lands |
|---|---|---|
| **inline** (default) | "handoff", "passoff", "continuation prompt" | chat response, pasteable into a new session |
| **durable** | `/runbook:handoff`, "save a handoff", "capture this session" | `RUNBOOK.md` — target rule in [references/runbook.md](references/runbook.md) |
| **rolling** | `/runbook:handoff rolling`, "roll the runbook" | incremental checkpoint writes during execution — [references/rolling.md](references/rolling.md) |
| **resume** | `/runbook:handoff resume`, "where were we" | reads the runbook back and verifies it — [references/runbook.md](references/runbook.md) § Resume |

Inline mode writes nothing — no file, no Artifact, no memory — unless asked in
the same request. Durable mode writes the runbook and names it in the reply;
rolling mode may also touch track markers and directory `AGENTS.md`, and names
every file it wrote.

`handoff` is the *serial* sibling of `slice`: this packages state for one agent
continuing the work, `slice` partitions work across many agents at once. They
share three references — the grilling gate
([grilling.md](references/grilling.md)), the partition schema
([partitions.md](references/partitions.md)), and the invocation ladder
([invocations.md](references/invocations.md)) — so each concept is defined once.

## Before writing: gather, don't guess

Reconstruct from ground truth, not recollection — your recollection may itself
be a compaction summary:

- `git status`, `git diff --stat`, `git log -5 --oneline`.
- Active TaskList/todo state — done, in-flight, pending.
- **The conductor layer.** `RUNBOOK.md` is the summary;
  `conductor-okf:context-awareness` loads the foundation under it — `product.md`
  (what this is *for*), `tech-stack.md`, `workflow.md`, `tracks.md`. Read the
  runbook, descend only where it points. Other plans on disk get linked, not
  re-derived.
- Background processes, servers, and agents started this session — what they're
  doing and where output lands.
- The conversation, for what is **not** recoverable from code or git: why an
  approach was rejected, a preference stated, a fact from an external system.

Where you aren't confident of the true state — whether a fix was actually
verified — say so. A wrong "done" costs the next session more than an honest
"unverified".

## The grilling gate

Run the one-round gate in [references/grilling.md](references/grilling.md)
before writing.

Short form: everything unresolved gets the flip test (name what changes if the
answer flips, or cut it); cut the discoverable, already-decided, premature, and
cosmetic; rank survivors by blast radius → reversal cost → whether only the
user can answer; top four into **one** `AskUserQuestion` with recommended
options. Answers become Decisions, unasked become Assumptions. Then write
regardless. Skip the gate when nothing is genuinely unresolved.

## Output structure

In this order; omit any section that would be empty rather than writing "N/A".

**Goal** — what's being accomplished and why, including stated constraints.
Enough to know what "done" looks like.

**State** — complete / in-flight / blocked. Distinguish verified from
believed-correct: "code written" and "confirmed working" are different claims,
and the gap is where the next session loses time. Include commit hashes and the
**review ledger** — which phases have a recorded verdict. Unreviewed work is
in-flight however finished the code looks.

**Key context** — the non-obvious material a fresh read of code and git log
would *not* surface: approaches tried and rejected and why, constraints,
surprises, external facts. Highest-value section; prioritize density here.

**Decisions** — settled calls, one line of rationale each ("chose X over Y
because Z"). What a fresh session would otherwise re-litigate.

**Assumptions** — what the gate didn't ask: `<assumption> · default taken: <x>
· to reverse: <cost>`, highest cost first. The top line is what to confirm
before building on it.

**Relevant files** — `path:line` for files that matter, one clause each on why.
The files to open first, not a listing.

**Environment** — what a fresh session can't discover: branch, uncommitted or
stashed work, running processes, ports, tools configured this session, open
worktrees. Name where credential *values* live; never include them.

**Continuation plan** — ordered, numbered instructions to the new agent, not a
status recap. Each names the file, the change, and the reason. Order by
dependency, not discovery order. Optimize so step 1 is executable with no
further investigation.

**Open questions** — only what's genuinely undecided: deferred questions with
the trigger that makes each live. Omit if none.

## The continuation prompt

Every inline packet ends with a fenced block the user can paste as a new
session's opening message — the *instruction* that starts work, not a summary.

````markdown
```
Resume work on <goal, one line>.

[if a runbook exists:]
Read `<path>` first — state, decisions, assumptions, review ledger. Verify its
in-flight claims against `git status` before acting. Start at §7 step 1.

[otherwise:]
First action: <concrete step — file, change, reason>.
Look at: <path:line> · <path:line>

Watch out for: <the single most expensive gotcha>

Suggested: `<invocation>` — <trigger clause>
```
````

When a runbook exists the prompt stays tight and points at it — a duplicate
that drifts is worse than a pointer.

Pick invocations with [references/invocations.md](references/invocations.md),
working its weight ladder **from the bottom**: inline → one skill → one agent →
`/runbook:slice` fan-out → ultra tier. Take the lowest rung that does the job. **2–4
maximum, each with the clause from this packet that selected it** — "three
disjoint store files, no shared edits → ultrapilot". A recommendation without a
trigger is a guess the next session re-derives. When the next step is just
"edit these two files", say that.

Include the review checkpoint the next phase needs, so it's planned rather than
remembered — `/security-review` when the next step touches an auth path.

## Calibration

Match density to what happened: a ten-minute task earns a few lines, a
multi-hour effort the full structure. Convert every relative date to an absolute
one at write time.
