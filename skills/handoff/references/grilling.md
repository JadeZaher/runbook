# The grilling gate — one round, then commit to assumptions

Shared by `handoff` (open questions in a packet) and `slice` (a plan question
only the user can settle).

**One batch per gate invocation; at most one gate per phase boundary; never a
second round on the same gate.** Never a block.

`AskUserQuestion` caps at 4, so this is a **ranking function**, not a question
bank. Choosing the right four is the whole skill — everything unasked becomes a
stated assumption, which is a fine outcome as long as it's *stated*.

## The flip test — the entry requirement

For every candidate question, say what changes if the answer flips. If you
cannot name a concrete change to the continuation plan, cut it, however
interesting it is.

Write the flip next to the question when you ask it, and next to the answer
when you record it. A question whose flip you can't articulate is a question
you're asking to look thorough.

## Cut before you rank

Most "open questions" aren't questions. Remove these first:

- **Discoverable** — the answer is in the code, the git log, a doc, or one
  command. Answer it yourself right now and put the answer in Key context.
  Never spend the round on something a grep would settle.
- **Already decided, merely unrecorded** — a recall task, not a question. Write
  it into Decisions with its rationale.
- **Premature** — it only matters after an earlier decision lands. Record it as
  a downstream open question and name the trigger that makes it live.
- **Cosmetic** — naming, formatting, ordering, anything the next session can
  change in a minute without rework.
- **Approval-seeking** — "should I proceed?", "does this look right?", "is the
  plan good?". Not decisions. Cut on sight.

## Rank the survivors, take the top four

Score on three axes, in this order:

1. **Blast radius.** Does the answer reorder, add, or delete continuation
   steps? That's top tier. Does it change how one step is implemented? Second
   tier. Does it change only wording? Already cut above.
2. **Reversal cost.** How expensive is the wrong default to undo *after* the
   next session has built on top of it? Schema shape, API or data contract,
   file layout, dependency choice, anything downstream work will assume as
   given. High reversal cost promotes a question even at moderate blast radius
   — this is the axis people under-weight.
3. **Who can answer.** Prefer what only the user knows — priority between two
   valid paths, taste, budget, an external commitment, what the thing is
   actually *for* — over anything the next session could discover for itself.

Ties break toward the question that unblocks step 1 of the continuation plan.
A question about step 9 can wait for the session that reaches step 9.

## Asking

One `AskUserQuestion` call, all questions batched.

- **Concrete options, never an open prompt.** The user picks in seconds; they
  compose prose in minutes. 2–4 options each.
- **Lead with the option you'd take,** labelled `(Recommended)`, and say why.
  You have the context; make the default easy to accept.
- **Put the flip in the description** — what this choice changes downstream, in
  a clause. That's what makes the choice answerable by someone who has stopped
  thinking about the task.
- **Options must be genuinely distinct.** Two options that produce the same
  work are one option.

## Recording — the part that makes the packet clean

**Answered** → into **Decisions**, phrased as settled fact with its rationale
("chose X over Y because Z"). Never leave an answered question sitting in Open
questions; that invites the next session to re-litigate a call already made.

**Unasked** → into **Assumptions**, one line each, three fields:

```
<assumption> · default taken: <what you did> · to reverse: <what it costs>
```

Order by reversal cost, highest first. That ordering *is* the next session's
challenge list — line one is the thing to confirm before building anything on
top of it. This block is why one round is enough: the questions you didn't get
to are still visible, still ranked, and still cheap to raise later.

An honest Assumptions block beats a packet that hides uncertainty behind
confident prose. Never silently take a default and present it as settled.

## Don't

If the answers open new questions, they become assumptions or downstream open
items — not a second round. And when nothing is genuinely unresolved, skip the
gate silently; don't announce that you skipped it.
