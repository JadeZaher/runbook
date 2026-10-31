---
description: Package current work for the next session — durable by default
argument-hint: "[inline|save|rolling|resume] [topic]"
---

Invoke the `handoff` skill (`${CLAUDE_PLUGIN_ROOT}/skills/handoff/SKILL.md`) and follow it
exactly. Read `references/grilling.md` before writing the packet, and
`references/runbook.md` before writing or reading any file — **that file holds
the authoritative target rule; do not restate it from memory.**

Mode, from `$ARGUMENTS`:

- **`inline`** → print the packet as the chat response. Write nothing.
- **`resume`** → read the runbook back per `references/runbook.md` § Resume:
  read it, verify §1 in-flight claims against `git status` / `git log -3`,
  report drift, then start at §7 step 1. **Read-only — write nothing.**
- **`rolling`** → arm rolling mode per `references/rolling.md`: resolve the
  runbook target, open one live §8 entry, and **write the arming marker** so it
  survives compaction. Then keep it true at each of the three checkpoints,
  including the phase-boundary review whose verdict goes in the ledger. Use at
  the *start* of substantial work, not the end.
- **`save`, or no argument** → durable mode. An explicit slash invocation is
  almost always a session-end or milestone handoff, so persistence is the
  default.

Remaining words are the topic/title for the session-log entry. `inline`,
`save`, `rolling`, and `resume` are mode keywords — never treat them as a
topic. If no title is given, derive a short one; don't ask.

Run the one-round grilling gate first (not for `resume`). One
`AskUserQuestion` batch, at most four questions, ranked by blast radius →
reversal cost → whether only the user can answer. Then write regardless, with
unasked questions recorded as ranked assumptions.

End your reply with the path of every file written and a three-line summary of
what a fresh session should do first.
