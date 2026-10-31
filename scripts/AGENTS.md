# `scripts/` — build machinery

Not shipped. `build-plugin-zip.py` excludes `scripts/` and `dist/` from the
archive, so what lands on another machine is only the plugin itself.

## Why the skills are vendored rather than authored here

`handoff`, `slice`, and the `handoff`/`passoff` commands are maintained at the
**user level** (`~/.claude/skills/`, `~/.claude/commands/`) and copied into this
plugin at build time. On the authoring machine they must work as plain `/handoff`
and `/passoff` — without a plugin install, without the `/runbook:` namespace —
and `handoff` inline mode is the most-invoked path. So the canonical copy stays
where it is edited and where the `~/.claude` repo tracks it; this repo is its
published form. The direction is one-way and the build is the only writer.

conductor-okf vendors the same four sources with the same script (only
`PLUGIN_NAME` differs), so the two plugins never disagree about the workflow.

## What the build rewrites

| Source form | Vendored form | Why |
|---|---|---|
| `~/.claude/skills/…` | `${CLAUDE_PLUGIN_ROOT}/skills/…` | The user-level tree may not exist |
| `~/.claude/commands/…` | `${CLAUDE_PLUGIN_ROOT}/commands/…` | Same |
| `/handoff`, `/passoff`, `/slice` | `/runbook:<name>` | Plugin commands are namespaced |

The command rewrite uses a lookbehind (`(?<![\w/.\-])`) so path segments such as
`skills/handoff/SKILL.md` and `../handoff/references/partitions.md` survive
untouched. Other plugins' commands (`/code-review`, `/codex:rescue`, …) are left
alone — renaming them into this namespace would invent commands that do not
exist.

## Usage

```bash
python scripts/build-plugin-zip.py                    # vendor + validate + package
python scripts/build-plugin-zip.py --strict           # fail on validator warnings
python scripts/build-plugin-zip.py --skip-vendor      # package the tree as-is
python scripts/build-plugin-zip.py --claude-home DIR  # vendor from a different source
```

Writes `dist/runbook-<version>.zip`, versioned from `.claude-plugin/plugin.json`.
