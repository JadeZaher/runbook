# Prebaked file partitions

Shared by `slice` (which computes and consumes them) and `handoff` (which
records and rolls them). Lives in `conductor/tracks/<id>/metadata.json` under
`partitions`.

The point: the expensive part of orchestration recon is *reasoning about
boundaries* — which files group together, which are shared, what breaks if you
move them. That reasoning is already done when a track is planned. Storing it
means a later fan-out starts from a hypothesis instead of a blank page.

## The one rule that keeps this safe

**A prebaked partition is a hypothesis, never a fact.** It describes the tree as
of the commit it was computed at. Code moves; files split; a flag migrates to
another file.

Before any launch, re-verify — this is `slice` grilling question #1 and it is
not optional:

- `git rev-parse HEAD` vs `computed_at_commit`. Equal → trust the shape, still
  confirm files exist. Different → re-verify every `owns` list with a real grep
  before spawning anything.
- Any `owns` entry that no longer exists, or now appears in two slices, voids
  the wave. Recompute that wave.

Prebaking saves the thinking. It never saves the collision proof.

## Schema

Canonical shape — an object:

```json
"partitions": {
  "computed_at": "2026-08-15T09:58:00Z",
  "computed_at_commit": "a1b2c3d",
  "confidence": "planned",
  "slices": [
    {
      "id": "s1",
      "task": "Extract the quest store",
      "owns": ["src/stores/quest.ts", {"path": "src/stores/quest.test.ts", "status": "future"}],
      "model": "sonnet",
      "depends_on": []
    }
  ],
  "shared_writes": [
    {"path": "src/registry.ts", "owner": "s3", "reason": "all three register here; s3 serializes"}
  ],
  "tripwires": ["save-format version must stay in lockstep with the migration table"],
  "integration_slice": "s9"
}
```

`confidence`:
- `none` — the stub. Nothing computed; the next consumer fills it.
- `planned` — derived from planning analysis, never verified against the tree.
- `verified` — collision proof run against `computed_at_commit`.

**Shorthand.** A bare array is accepted and normalizes to the canonical object
with `confidence: "none"` and every other field empty:

```json
"partitions": [
  {"id": "s1", "task": "...", "owns": ["src/a.ts"]}
]
```

Two shapes, one normalization rule. Don't add a third — every accepted shape is
a parser every consumer has to implement.

**File entries** are a string (shorthand for `{path, status: "existing"}`) or an
object:

```json
{"path": "src/thing.ts", "status": "existing|future", "note": "why this slice owns it"}
```

`status: "future"` declares a file the slice will *create*. This is what makes
partitioning a greenfield track meaningful — a file that doesn't exist yet can
still be owned, and two slices both declaring the same future path is a
collision exactly like two slices writing an existing one.

## The unpartitioned fallback

When boundaries can't be determined — the work is exploratory, the files don't
exist and can't be predicted, or the planner simply didn't have enough — emit
the stub rather than guessing:

```json
"partitions": {"confidence": "none", "unpartitioned": "<one line on why>"}
```

A wrong partition is worse than none: it looks authoritative and sends two
agents at the same file. `confidence: "none"` tells the next consumer to do the
recon itself. **Never fabricate a partition to avoid an empty field.**

## Who writes it, when

| Moment | Action |
|---|---|
| `/conductor-okf:new-track` | Self-fill from the planning analysis already done — no extra recon pass. Anything uncertain → `unpartitioned`. |
| `/runbook:slice` planning a fan-out | Read it. `none` → compute from scratch. `planned` → verify, then upgrade to `verified`. Write the result back. |
| `handoff` rolling, at a wave join | Record which slices landed; mark a voided wave `confidence: "none"` so the next run recomputes rather than trusting it. |

**Never spend a separate recon fan-out at track creation.** The planner has
already read the codebase to write the spec; partitions come out of that
analysis or they come out `unpartitioned`. Spawning mappers when the user asked
for a track is the same overreach as running a setup wizard when they asked for
a handoff.

## Mapping to slice's plan

The schema is `slice`'s output structure, persisted — not a parallel invention:

| `slice` section | Field |
|---|---|
| Slices (`id · task · owned files · model · depends-on`) | `slices[]` |
| File-boundary map | `owns` per slice, plus `shared_writes` |
| Resolved shared write-target | `shared_writes[].owner` |
| Wave plan | derived from `depends_on` — the DAG, not a stored wave number |
| Collision/invariant scout output | `tripwires` |
| Integration wave | `integration_slice` |

Waves are **derived from `depends_on`, never stored.** A stored wave number goes
stale the moment a dependency changes, and then it silently disagrees with the
DAG that generated it.
