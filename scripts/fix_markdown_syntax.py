#!/usr/bin/env python3
"""
Deterministic fixer for Markdown syntax issues:
- Add missing space after heading hashes outside code fences.
- Close unclosed fenced code blocks by inserting closing ``` before a new fence and/or EOF.

This tool is conservative: it does NOT modify content inside code fences.
"""
from __future__ import annotations

import re
from pathlib import Path

FENCE_OPEN_RE = re.compile(r"^```([A-Za-z0-9_\-]+)?\s*$")
FENCE_CLOSE_RE = re.compile(r"^```\s*$")
BAD_HEADING_RE = re.compile(r"^(#{1,6})(?!\s)")


def list_markdown_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.md") if ".git" not in p.parts]


def fix_file(path: Path) -> bool:
    original = path.read_text(encoding="utf-8", errors="replace").splitlines(keepends=True)
    fixed_lines: list[str] = []
    in_fence = False
    modified = False
    for idx, line in enumerate(original):
        if FENCE_OPEN_RE.match(line.rstrip("\n\r")):
            # if already in a fence, close it before opening a new one
            if in_fence:
                fixed_lines.append("```\n")
                modified = True
            in_fence = True
            fixed_lines.append(line)
            continue
        if FENCE_CLOSE_RE.match(line.rstrip("\n\r")):
            in_fence = False
            fixed_lines.append(line)
            continue
        if not in_fence and BAD_HEADING_RE.match(line):
            # insert a single space after the run of '#'
            fixed_line = re.sub(r"^(#{1,6})(?!\s)", r"\1 ", line)
            if fixed_line != line:
                modified = True
            fixed_lines.append(fixed_line)
        else:
            fixed_lines.append(line)
    # close fence at EOF if left open
    if in_fence:
        fixed_lines.append("```\n")
        modified = True
    if modified:
        path.write_text("".join(fixed_lines), encoding="utf-8")
    return modified


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    md_files = list_markdown_files(root)
    changed = 0
    for p in md_files:
        if fix_file(p):
            changed += 1
    print(f"Markdown fixer updated {changed} files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

