# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-10-31

First standalone release. The same workflow has shipped vendored inside
conductor-okf since 1.3.0; this plugin carries it without conductor.

### Added
- `skills/handoff/` — owns `RUNBOOK.md` end to end: inline packets, durable
  writes, rolling checkpoints with recorded phase-boundary review verdicts, and
  `resume`.
- `skills/handoff/references/` — target rule, one-round grilling gate, rolling
  checkpoints, invocation weight ladder, and the prebaked-partition schema,
  shared by both skills.
- `skills/slice/` — conflict-free file partitions, wave plans derived from
  `depends_on`, and a pre-launch grilling gate.
- `/runbook:handoff` and `/runbook:passoff` commands.
- `scripts/build-plugin-zip.py` — vendors the workflow from its user-level
  source, rewrites paths and command names, validates, and packages a zip.
