---
name: slice
description: >
  Plans fine-grained sub-agent orchestration before spawning a swarm:
  slices a task into agent-sized units with pre-declared, conflict-free
  file boundaries, a per-slice model/effort assignment, a dependency-ordered
  wave plan (what runs in parallel vs. what must sequence), a verification
  lane, and a merge strategy — then runs a PRE-LAUNCH GRILLING SESSION that
  adversarially stress-tests the plan so tokens are only spent once the
  orchestration is sound. The parallel-orchestration sibling of `handoff`
  (which packages serial work). Use when the user wants to run a
  multi-agent / workflow / swarm job, "orchestrate this with subagents",
  "fan out agents", "run as much in parallel as possible", "define file
  boundaries ahead", or before launching any Workflow/Agent fan-out on a
  substantial task.
---

# slice — fine-grained sub-agent orchestration planner

Produce an **orchestration plan** for running a task across many sub-agents,
then **grill it** before spawning anything. Output the plan in chat; on
approval, launch. Where `handoff` packages a *serial* continuation for one
fresh agent, `slice` optimizes a *parallel* fan-out to many — and its last
section flips the handoff's "continuation plan" into an interrogation you must
pass first.

Two laws govern all parallel agent work, and every rule below serves them:
1. **Two agents that write the same file collide.** Make collisions
   impossible by construction, not by luck.
2. **Tokens go where they change the answer, nowhere else.** Right-size every
   slice's model; never fan out work a single context finishes cheaper.
3. **Slice agents sketch; the orchestrator inks.** Wave work is *sketch* work —
   agents edit, write tests, and self-review, but **never run builds, tests, or
   lint**, and never launch a background build with a poll loop. All compiling,
   testing, and linting is *review + line-pen* work that happens **once,
   serially, at the wave join**, run by the orchestrator. Concurrent self-builds
   deadlock on the build tool's shared lock or corrupt its shared cache (a
   compiler's build dir, a package manager's cache, a build daemon): the blocked
   agent stalls for the *other's entire build* and, if it built in the
   background, spins forever in a poll loop — the edits are fine on disk, but the
   swarm looks dead.

## Before writing: map ground truth, don't guess

You cannot partition files you haven't seen. Reconstruct from disk:

- **Check for a prebaked partition first.** `conductor/tracks/<id>/metadata.json`
  → `partitions`. `/conductor-okf:new-track` fills it from the planning
  analysis, so the boundary *reasoning* may already be done. Schema and the
  consumer contract: [../handoff/references/partitions.md](../handoff/references/partitions.md).
  - `confidence: "none"` or `unpartitioned` → nothing there; do the full recon.
  - `confidence: "planned"` → a **hypothesis, not a fact**. It describes the
    tree at `computed_at_commit`. If `HEAD` has moved, re-verify every `owns`
    list with a real grep before trusting it (that's grilling #1, which is
    mandatory either way). Then write it back as `"verified"`.
  - Files marked `status: "future"` don't exist yet — two slices declaring the
    same future path collide exactly like an existing file.
  Prebaking saves the thinking. It never saves the collision proof.
- `git status` / `git log -5 --oneline` — what's already in flight.
- **Fan out read-only mappers first** — one per subsystem the work touches,
  plus a dedicated **collision/invariant scout** whose only job is to find
  (a) every file more than one slice will *write* and (b) the sacred
  invariants (the tripwires a careless move breaks). This scout is the
  highest-value mapper; its output is the spine of the grilling. Recon is
  itself the first, cheapest fan-out — always read-only, always parallel.
  A structured schema (owned_files / shared_files / tripwires per phase →
  one synthesis agent) makes the partition executable literally.
- Any plan/spec/track on disk — link and obey; don't re-derive.
- The compile/build graph. In a single-crate refactor the real dependency
  spine is **file-write serialization**, not feature boundaries (see below).

## Output structure

Use these sections, in order. Omit any that would be empty — never pad.

**Objective** — one or two sentences: what "done" looks like, concretely.

**Slices** — the work cut into agent-sized units, one row each:
`id · one-line task · owned files · model/effort · depends-on`. Size so one
agent finishes in one context. Too big → split; merge-overhead > work → merge.

**File-boundary map** — the load-bearing section. Map every file that will be
*written* to the single slice that owns it, and prove no file appears twice in
one wave. Three rules that catch the partitions luck won't:
- **Own the file that physically holds the mutation, not the phase's nominal
  files.** A flag, compat shim, or toggle a slice must retire often lives in a
  *different* file than the slice's feature. Trace every flag/shim/toggle to
  its physical file and give that file to whoever mutates it. (Missing this is
  the classic boundary gap.)
- **Read-only files may be shared freely; only *writes* collide.**
- Resolve any genuinely shared write-target one of three ways: serialize the
  writers into different waves, give one slice sole ownership (others hand it
  patches), or split the file first. When agents must write in parallel and a
  shared file is unavoidable, `isolation:'worktree'` per agent + an explicit
  merge slice is the escape hatch — name it.

**Model & effort assignment** — per slice, the tier and why. Default map:
- read-only recon / mechanical bookkeeping / docs / retros → `haiku` (low).
- standard single-concern code, tests, mechanical UI/code moves → `sonnet`.
- hard multi-file arch, subtle-correctness cores (unwind safety, concurrency,
  the spine slice everything builds on), adversarial verify, the merge/
  synthesis slice → `opus` (high/xhigh).
Assign the tier to the *hardest sub-task in the slice*, not its average. A
mechanical move that carries many invariant tripwires earns a bump.

**Wave plan** — the dependency-ordered schedule as a DAG, not rigid rows.
- **The most-written file sets your minimum wave depth.** Find the file with
  the most distinct-phase writers; its writer count is the floor on sequential
  waves (they serialize through it), *regardless* of how shallow the logical
  compile deps are. This is usually the real bottleneck in a single-crate job.
- **Hide independent slices under the critical path.** A slice touching a
  disjoint directory doesn't belong in "wave 1" — it runs *beside the whole
  critical path* and joins before the final sweep. Same for a standalone
  module that only depends on the spine: it hides under the waves after the
  spine. Identify the critical path; everything else runs alongside it.
- Default to `pipeline()`; use a barrier only when the next wave needs *all*
  of the prior wave's results at once (dedup/merge/zero-count exit). Per-wave
  compile joins are legitimate barriers (the next wave needs the realized tree).
- **Leaf logic parallelizes; integration doesn't — plan an explicit integration
  wave.** Strict file-boundary slicing cleanly fans out the *leaf* logic
  (algorithms, pure fns, per-file bodies, unit tests) but structurally separates
  it from *integration* — the wiring that connects leaves into the running system
  (dispatch/registration, plugin/system wiring, call-site threading, cross-module
  glue, and any *newly-discovered* shared-vocabulary ops) lives in shared central
  files a single owner must serialize. So a well-formed plan ends with an
  **integration slice/wave** owned by one agent AFTER the parallel leaf wave;
  never mistake "the tracks compile together" for "the feature works end-to-end."
  The tell at merge time: leaf slices return `partial` with open-items that all
  name central/other-owner files (a materializer, a `plugin.rs`, a results
  handler, a not-yet-existing op) — that list *is* the integration wave's backlog.

**Verification lane** — check each slice in a pass *separate from the one that
wrote it* (never self-approve in the writing context). The orchestrator runs a
**compile-gate at each join**; correctness-critical slices also get an
adversarial/independent verify (a skeptic prompted to refute; kill on
majority-refute). Safety-critical infra (a panic guard, a lock) earns an inline
test-execution at its join even under a "one sweep at end" policy — that's the
sanctioned exception. The full test/lint/build sweep runs **once at the end on
the merged tree**.

**Merge & integration** — how parallel outputs recombine.
- **Shared working tree + disjoint files per wave + sequential waves = no git
  merge.** Each wave's edits land on disk before the next reads them; there is
  nothing to merge. Worktree isolation is only for genuinely-concurrent writes
  to a shared file — and it reintroduces a merge, so avoid it unless forced.
- **Concurrent builds are a hazard (law 3).** Two agents building one tree don't
  just race on shared build artifacts (stale caches, false cascades) — they
  serialize on the build tool's global lock, so the blocked one stalls for the
  *other's entire build* and, if it launched the build in the background, spins
  forever in its poll loop. Rule: same-wave agents **never** build/test/lint —
  put the ban *in every slice agent's brief*, not just the plan. At the join the
  orchestrator kills any stray build process (releases the lock), then runs ONE
  serial build → lint → test and dispatches a focused fix if red. Only a
  genuinely *solo* wave (one agent, nothing else building) may self-build.
- **Downstream slices re-locate against the realized tree.** Once the spine
  slice reshapes a file, every line number the recon captured is stale. Tell
  each downstream slice to re-read and re-find its splice points; never ship it
  raw recon line numbers to trust.
- **Thread cross-cutting constraints to every downstream slice.** A global
  ceiling the spine hits (a param-count limit, a public-API contract, a
  lint budget) lives in no single file — carry it forward in each later
  prompt or a slice will breach it blind.

**Pre-launch grilling session** — the gate. These eight are *self*-interrogation:
answer them from the recon yourself, and don't spawn until you can. This is the
handoff's continuation plan turned adversarial — don't trust the plan, attack
it. One line each; an unanswerable one means the plan isn't ready. Only the few
that genuinely need the operator get escalated (see after #8).

1. **Collision proof.** Name any file written by two slices in the same wave —
   *including* the file that physically holds each retired flag/shim. If the
   answer isn't "none," the wave is wrong. **Verify the disjointness claim with
   a real grep** (e.g. the two module-registration sites are actually different
   files) — don't trust the recon's assertion.
2. **Dependency honesty.** For each sequenced wave, what *exact* symbol, type,
   or realized-tree edit from the prior wave does it need? If you can't name it
   — and it's not a pure file-serialization dep — the waves should merge.
3. **Right-sized model.** Which slice is over-tiered (cheaper model gets it)?
   Which is under-tiered (correctness rides on it, weak tier)? Move both.
4. **The merge is planned, not hoped.** Is it shared-tree-sequential (no merge)
   or does something reconcile worktrees? What's the first thing that breaks at
   the seam — and did every downstream slice get told to re-locate against the
   realized tree, not stale line numbers?
5. **Verification is independent.** Is anything approved by the context that
   produced it? Add a separate verify pass. Is any safety-critical slice
   trusting a self-report instead of an executed test at its join?
6. **Barrier justified.** Every barrier: does the next wave truly need ALL
   prior results, or just some? If just some, it's a pipeline.
7. **Failure blast radius.** If the highest-risk slice returns garbage or dies,
   what's corrupted and what still stands? The spine slice poisons everything
   downstream — gate and review it before its dependents launch.
8. **Cheaper serial path.** Once merge + grilling + per-join overhead is
   counted, would one context be faster? If yes, don't fan out. Parallelism
   that loses to serial is theater — and a single-crate job whose critical path
   is one serialized file is often mostly-serial with a few slices hidden
   beside it; be honest about how much parallelism there actually is.

**When a grilling question needs the user, not you.** The eight above are
*self*-interrogation — you answer them from the recon. A few can't be settled
without the operator: whether the fan-out is worth its cost at all (#8), which
of two valid partitions matches their priority, a scope or budget ceiling, a
risk they'd rather not take on the spine slice. Escalate exactly those through
the one-round gate in [../handoff/references/grilling.md](../handoff/references/grilling.md):
rank by blast radius → reversal cost → who can answer, batch at most four in a
single `AskUserQuestion` with recommended options, then proceed. Anything
unasked becomes a stated assumption in the plan, ordered by reversal cost — the
orchestrator's own challenge list at the first join. Never open a second round,
and never stall a sound plan on a question you can answer yourself.

**Persist the verified partition.** Once the collision proof passes, write the
plan back to `conductor/tracks/<id>/metadata.json` → `partitions` with
`confidence: "verified"` and the current `computed_at_commit`, per
[../handoff/references/partitions.md](../handoff/references/partitions.md). The
next fan-out on this track then starts from proven boundaries instead of
re-deriving them. If a wave is later voided by a collision, set that partition
back to `"none"` rather than leaving a partition that looks verified and isn't.

Only after all eight pass: launch (Workflow for deterministic fan-out/loops,
Agent for one-off units), then **watch and report** (below), verify at each
join, checkpoint-commit compile-green waves, sweep once at the end.

## Live visibility & steering — the orchestrator's standing duty

Launching is **not fire-and-forget.** A backgrounded wave is invisible unless
the orchestrator (the poller) makes it visible — and an invisible swarm that has
hung looks identical to one that's working (the edits sit fine on disk while the
run is dead). So while any wave runs, the poller surfaces to the user,
**unprompted**, a tight digest:
- **Edits so far** — which files each slice has written/created (a status /
  diff-stat digest), so the user watches the change take shape.
- **Traces** — what each agent is *doing now*: a compact per-agent line pulled
  from its run transcript (reads → edits → the command it's on), not a raw dump.
- **Health** — progressing or stalled? Call the tells: no new edits for a while,
  an agent stuck in a build/poll loop, a transcript that stopped growing, a build
  process pinned at zero CPU.

Cadence: **at every wave barrier** (the natural steering point), plus a mid-wave
check on long slices. Keep each report a tight digest — files touched, one line
per agent, any risk — and hand the user the intervention handles (what's running,
how to stop it) so they can **steer or abort mid-flight** rather than discover a
dead swarm an hour later. Visibility is the orchestrator's job, not something the
user should have to go digging through transcripts for.

## Calibration

Match plan weight to the job. A three-slice one-wave fan-out earns a half-page;
a multi-phase refactor with a serialized critical path earns the full structure
and a hard grilling. The grilling's job #8 exists to kill fan-outs that lose to
serial. Tight and sleek: dense rows, no narrative, every line load-bearing.
