# runbook

Session handoff and parallel fan-out planning for Claude Code.

Two skills that keep long-horizon work from dying with the context window:

- **`handoff`** packages the current session so a fresh one resumes without
  re-discovery: state, settled decisions, stated assumptions, a review ledger,
  and an executable continuation plan, written to a durable `RUNBOOK.md`.
- **`slice`** is its parallel sibling: it cuts a task into agent-sized units
  with pre-declared, conflict-free file boundaries, assigns a model tier per
  slice, derives waves from `depends_on`, and grills the plan before any agent
  is spawned.

Works on its own. Inside a [conductor-okf](https://github.com/JadeZaher/conductor-okf)
project it also reads the prebaked file partitions that `/conductor-okf:new-track`
writes into each track — conductor-okf ships its own vendored copy of these
skills, so install one or the other, not both.

## Installation

### From GitHub

```
/plugin install runbook --marketplace JadeZaher/runbook
```

### From a local directory

```bash
claude --plugin-dir /path/to/runbook     # one session
claude plugin validate /path/to/runbook  # check the manifest first
```

For a permanent install, add the directory that contains `runbook/` as a
marketplace (it needs a `.claude-plugin/marketplace.json` listing
`"source": "./runbook"`), then:

```bash
/plugin marketplace add /path/to/marketplace
/plugin install runbook@<marketplace-name>
```

### From a zip

```bash
python scripts/build-plugin-zip.py --skip-vendor   # package the tree as-is
claude --plugin-dir dist/runbook-1.0.0.zip         # one session
```

The archive has the plugin root at the archive root — Claude Code extracts it
and treats the extracted directory as the plugin.

### Verify

Type `/runbook:` in a session with the plugin loaded. You should see the
`handoff` and `passoff` commands and the `slice` skill.

## `handoff` — serial continuation

Nothing auto-loads the runbook; reading and writing it are always explicit acts.

| Mode | Invocation | Lands |
|---|---|---|
| **inline** | "handoff", "passoff", "where were we" | A pasteable packet in chat. Writes nothing. |
| **durable** | `/runbook:handoff` | `conductor/RUNBOOK.md` |
| **rolling** | `/runbook:handoff rolling` | Incremental checkpoints *during* execution |
| **resume** | `/runbook:handoff resume` | Reads the runbook back and verifies it against `git status` |

`/runbook:passoff` is an alias — same skill, same behavior.

**Target rule** (`skills/handoff/references/runbook.md` is authoritative):
`conductor/` exists → `conductor/RUNBOOK.md`; no `conductor/` → create the
directory and write it there; a legacy `.omc/RUNBOOK.md` → migrate and delete.

Before writing, `handoff` runs a **one-round grilling gate**: it cuts every
question that is discoverable, already decided, premature, or cosmetic, ranks
the rest by blast radius and reversal cost, and asks at most four. Answers
become Decisions; everything unasked becomes a stated Assumption with its
default and reversal cost.

## `slice` — parallel fan-out

For work that goes *wide* instead of *forward*. Two laws it enforces:

1. Two agents writing one file collide — so make collisions impossible by
   construction, with `owns` lists declared before launch.
2. Slice agents *sketch*, the orchestrator *inks* — building, testing, and
   linting happen once, serially, at the wave join.

A partition is a **hypothesis stamped with a commit**, never a fact: if `HEAD`
has moved, every `owns` list is re-verified with a real grep, and
`confidence: "none"` always beats a guess.

## The review ledger

Every phase boundary gets an **adversarial review whose verdict is recorded**
in runbook §2 — run in a context separate from the one that wrote the code, and
prompted to refute rather than confirm. A phase with no verdict is
*unreviewed*, not done. Verdicts are `PASS`, `PASS-with-deferred`, or
`BLOCKED`.

## Shared references

Both skills read from `skills/handoff/references/`, so each concept is defined
once:

| Reference | Defines |
|---|---|
| [`runbook.md`](skills/handoff/references/runbook.md) | Target rule, file format, clipping, resume protocol |
| [`grilling.md`](skills/handoff/references/grilling.md) | The one-round question gate |
| [`rolling.md`](skills/handoff/references/rolling.md) | Checkpoints, phase-boundary review verdicts, track markers |
| [`invocations.md`](skills/handoff/references/invocations.md) | The weight ladder: inline → skill → agent → fan-out → ultra |
| [`partitions.md`](skills/handoff/references/partitions.md) | Partition schema and the consumer contract |

The skills name other plugins' commands where they fit (`/code-review`,
`/security-review`, `/simplify`, `/codex:rescue`, …). Those are optional —
`invocations.md` tells the agent to verify a command exists before naming it.

## Maintaining this repo

The skills are authored at the user level (`~/.claude/skills/handoff`,
`~/.claude/skills/slice`, `~/.claude/commands/handoff.md`,
`~/.claude/commands/passoff.md`) and **vendored** into this plugin by the build,
which rewrites user-level paths to `${CLAUDE_PLUGIN_ROOT}` and bare slash
commands to `/runbook:*`:

```bash
python scripts/build-plugin-zip.py           # vendor + validate + package
python scripts/build-plugin-zip.py --strict  # fail on validator warnings
```

Hand-edits to `skills/` or `commands/` here are overwritten by the next build.
See [`scripts/AGENTS.md`](scripts/AGENTS.md) for why.

## License

Apache-2.0
