# Recommended invocations — matching work shape to this install

Feeds the **continuation prompt** at the end of an inline packet and **§9** of
the runbook.

## The weight ladder — pick the lowest rung that does the job

Orchestration is a cost, not a virtue. Escalate on evidence, never in
anticipation.

| Rung | Use when | Shape |
|---|---|---|
| **0 · inline** | The work is known and small — a few files, no discovery | No invocation. Say "edit X, then Y." |
| **1 · one skill** | One bounded concern: a review, a build fix, a doc pass | A single `/command` |
| **2 · one agent** | One bounded job worth offloading for context, not speed | One `Agent` call, cheapest tier that works. An opus agent or a research run is a rung-2 *shape* at rung-4 *cost* — sanity-check the spend first |
| **3 · `/runbook:slice` fan-out** | 3+ files that can be partitioned with no shared writes | Plan boundaries first, then launch |
| **4 · ultra tier** | Sustained multi-phase work — build, verify, fix, repeat | `ultrawork` / `ultrapilot` / `ultraqa` / `autopilot` |

Two rules that keep this honest:

- **A rung-4 recommendation must name the phases it will run.** If you can't,
  it's rung 1 or 2 wearing a costume.
- **Never recommend a rung above the work.** Routing a ten-minute edit through
  an orchestrator loses to doing it — that's `slice`'s grilling question #8,
  applied to the recommendation itself.

## Rules for the block itself

- **2–4 recommendations, never a catalogue.** Twelve options is zero decisions.
- **Every line carries its trigger** — the clause from *this* packet that
  selected it: "three disjoint store files, no shared edits → ultrapilot".
  Without it, the next session re-derives the choice from scratch.
- **Top line is executable as step 1** of the continuation plan.
- **Verify before naming.** Plugin rosters change; if you haven't confirmed a
  command exists, describe the action in plain words instead.
- **Include the next review checkpoint**, so it's planned rather than
  remembered — `/security-review` when the next step touches an auth path.

## Rung 0–1 · single concern

| Work shape | Invocation |
|---|---|
| Resume: read the runbook back, verify against `git status` | `/runbook:handoff resume` — nothing auto-loads it |
| Load project foundation (product, tech-stack, workflow, tracks) | `conductor-okf:context-awareness` — the layer under the runbook |
| Question about the code, no changes | `/ask:ask` |
| Broad search, many hits, findings must survive compaction | `scrt "pat" --in . --effort scan --mp-stash <slug>` |
| Review the current diff | `/code-review` (`high` when correctness-critical; `--fix` applies) |
| Quality only, no bug hunt | `/simplify` |
| Auth / payments / crypto / user input / secrets touched | `/security-review` — non-negotiable |
| Build or type errors blocking | `/oh-my-claudecode:build-fix` |
| Completed work needs durable docs | `/write-docs:write-docs "..." --update` |
| Rationale for a module just landed | Edit that directory's `AGENTS.md` |
| Conductor track ready to run | `/conductor-okf:implement` |
| New feature/bug needing spec + tasks | `/conductor-okf:new-track` |

## Rung 2 · one offloaded job

| Work shape | Agent |
|---|---|
| Contested design or a plan worth attacking | `oh-my-claudecode:critic` (opus) |
| Deep review of a correctness-critical diff | `oh-my-claudecode:code-reviewer` (opus) |
| Independent second opinion when stuck | `/codex:rescue` |
| Test coverage in doubt | `oh-my-claudecode:qa-tester` |
| "Why is X broken" | `/oh-my-claudecode:analyze` |
| Find code across a large tree | `/oh-my-claudecode:deepsearch` |
| External research, cited | `/deep-research:deep-research` |

## Rung 3 · planned fan-out

| Work shape | Invocation |
|---|---|
| Parallel work needing conflict-free boundaries planned first | `/runbook:slice` — waves, model tiers, merge strategy, pre-launch grilling |
| Boundaries already proven disjoint | `/oh-my-claudecode:ultrapilot` or `:swarm` |

`/runbook:slice` before a fan-out is nearly always worth it: it costs one planning pass
and its grilling regularly kills fan-outs that lose to serial.

## Rung 4 · ultra tier

Reach here when work spans phases and will outlive one context.

| Work shape | Invocation |
|---|---|
| Sustained high-throughput push across many tasks | `/oh-my-claudecode:ultrawork` |
| Idea → working code with a verifier pass | `/oh-my-claudecode:autopilot` |
| Test → fix → verify until a goal is met | `/oh-my-claudecode:ultraqa` |
| Loop until done, architect-verified | `/oh-my-claudecode:ralph` |
| Plan contested, needs consensus | `/oh-my-claudecode:ralplan` |
| Token-tight but still parallel | `/oh-my-claudecode:ecomode` |
| Hardest reasoning on one problem | `ultrathink` keyword |

## Domain-specific

When the work is squarely in a vendor's domain, name that vendor's skill and
let it load its own guidance — Cloudflare (`cloudflare`, `wrangler`,
`workers-best-practices`, `durable-objects`, `agents-sdk`, `sandbox-sdk`),
Railway, Figma, Penpot, Stripe, Airflow (`astronomer-data:*`), Terraform,
Telegram, `pi-bridge:*`. `fde` covers onboarding onto an unfamiliar repo.
