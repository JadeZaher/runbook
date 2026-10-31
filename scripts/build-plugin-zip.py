#!/usr/bin/env python3
"""Vendor the runbook workflow from ~/.claude into this plugin, validate it, and write a distributable .zip.

The canonical, hand-edited copies of the runbook workflow live at the user level
(~/.claude/skills/handoff, ~/.claude/skills/slice, ~/.claude/commands/handoff.md,
~/.claude/commands/passoff.md). This plugin ships a *vendored* copy so a single zip
carries the whole workflow to another machine. Run this script after editing the
canonical copies; never hand-edit the vendored ones. See scripts/AGENTS.md.
"""

import argparse
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

PLUGIN_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_NAME = "runbook"

# (source, destination relative to the plugin root) — the workflow's four canonical pieces.
VENDORED_SOURCES = [
    ("skills/handoff", "skills/handoff"),
    ("skills/slice", "skills/slice"),
    ("commands/handoff.md", "commands/handoff.md"),
    ("commands/passoff.md", "commands/passoff.md"),
]

# Applied in order to every vendored markdown file. User-level absolute paths become
# plugin-relative ones, and bare slash commands become namespaced ones, because neither
# `~/.claude/skills/handoff/SKILL.md` nor `/handoff` exists on a machine that only
# installed this plugin. The lookbehind keeps path segments like `skills/handoff` and
# `../handoff/references/` from being mistaken for command invocations.
PATH_REWRITES = [
    (re.compile(re.escape("~/.claude/skills/")), "${CLAUDE_PLUGIN_ROOT}/skills/"),
    (re.compile(re.escape("~/.claude/commands/")), "${CLAUDE_PLUGIN_ROOT}/commands/"),
    (re.compile(r"(?<![\w/.\-])/handoff\b"), "/" + PLUGIN_NAME + ":handoff"),
    (re.compile(r"(?<![\w/.\-])/passoff\b"), "/" + PLUGIN_NAME + ":passoff"),
    (re.compile(r"(?<![\w/.\-])/slice\b"), "/" + PLUGIN_NAME + ":slice"),
]

# Never shipped: build machinery, build output, and OS/editor droppings.
EXCLUDED_FROM_ZIP = {"dist", "scripts", ".git", "node_modules", "__pycache__"}
EXCLUDED_FILE_SUFFIXES = (".pyc", ".tmp", ".log")
EXCLUDED_FILE_NAMES = {".DS_Store", "Thumbs.db"}


def read_plugin_version():
    manifest = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
    import json

    return json.loads(manifest.read_text(encoding="utf-8"))["version"]


def rewrite_markdown(text):
    for pattern, replacement in PATH_REWRITES:
        text = pattern.sub(replacement, text)
    return text


def vendor_runbook_workflow(claude_home):
    """Copy the canonical workflow into the plugin, rewriting paths as it goes."""
    rewritten_files = 0
    for source_relative, destination_relative in VENDORED_SOURCES:
        source = claude_home / source_relative
        destination = PLUGIN_ROOT / destination_relative
        if not source.exists():
            sys.exit("missing canonical source: %s" % source)

        if source.is_dir():
            shutil.rmtree(destination, ignore_errors=True)
            shutil.copytree(source, destination)
            copied = sorted(destination.rglob("*.md"))
        else:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            copied = [destination]

        for markdown_file in copied:
            original = markdown_file.read_text(encoding="utf-8")
            rewritten = rewrite_markdown(original)
            if rewritten != original:
                markdown_file.write_text(rewritten, encoding="utf-8", newline="\n")
                rewritten_files += 1
        print("  vendored %-22s -> %s" % (source_relative, destination_relative))
    print("  rewrote paths in %d file(s)" % rewritten_files)


def validate_plugin(strict):
    command = ["claude", "plugin", "validate", str(PLUGIN_ROOT)]
    if strict:
        command.append("--strict")
    # The validator prints UTF-8 glyphs; the Windows default codec (cp1252) cannot decode them.
    result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace")
    sys.stdout.write(result.stdout)
    sys.stderr.write(result.stderr)
    if result.returncode != 0:
        sys.exit("validation failed (exit %d)" % result.returncode)


def is_shipped(path):
    relative = path.relative_to(PLUGIN_ROOT)
    if EXCLUDED_FROM_ZIP.intersection(relative.parts):
        return False
    return path.name not in EXCLUDED_FILE_NAMES and not path.name.endswith(EXCLUDED_FILE_SUFFIXES)


def package_plugin_zip(version):
    """Write dist/<name>-<version>.zip with the plugin root at the zip root.

    Claude Code extracts the archive and treats the extracted directory as the plugin
    root, so `.claude-plugin/plugin.json` must sit at the top level — no wrapper folder.
    """
    distribution_directory = PLUGIN_ROOT / "dist"
    distribution_directory.mkdir(exist_ok=True)
    archive_path = distribution_directory / ("%s-%s.zip" % (PLUGIN_NAME, version))

    shipped = sorted(p for p in PLUGIN_ROOT.rglob("*") if p.is_file() and is_shipped(p))
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in shipped:
            archive.write(path, path.relative_to(PLUGIN_ROOT).as_posix())

    print("  %d file(s) -> %s (%.1f KB)" % (len(shipped), archive_path, archive_path.stat().st_size / 1024))
    return archive_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claude-home", default=str(Path.home() / ".claude"),
                        help="where the canonical skills/ and commands/ live")
    parser.add_argument("--skip-vendor", action="store_true", help="package what is already in the tree")
    parser.add_argument("--skip-validate", action="store_true", help="skip `claude plugin validate`")
    parser.add_argument("--strict", action="store_true", help="fail the build on validator warnings")
    arguments = parser.parse_args()

    version = read_plugin_version()
    print("building %s v%s" % (PLUGIN_NAME, version))

    if not arguments.skip_vendor:
        print("vendor:")
        vendor_runbook_workflow(Path(arguments.claude_home))
    if not arguments.skip_validate:
        print("validate:")
        validate_plugin(arguments.strict)
    print("package:")
    package_plugin_zip(version)


if __name__ == "__main__":
    main()
