#!/usr/bin/env python3
"""
Deterministic Markdown syntax checker for this repo.

Checks:
- Balanced fenced code blocks (``` ... ```)
- Mermaid blocks:
  - No HTML <br>, <br/>, <br /> inside
  - Must contain a known diagram directive (flowchart|graph|sequenceDiagram|classDiagram|stateDiagram|erDiagram|journey|gantt|pie)
- Headings must have a space after '#' (e.g., '# Title', not '#Title')

Exit codes:
  0 = OK
  1 = Violations found
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple


FENCE_OPEN_RE = re.compile(r"^```(\w+)?\s*$")
FENCE_CLOSE_RE = re.compile(r"^```\s*$")
MERMAID_FENCE_RE = re.compile(r"^```mermaid\s*$", re.IGNORECASE)
HTML_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)
MERMAID_DIRECTIVE_RE = re.compile(
    r"^\s*(flowchart|graph|sequenceDiagram|classDiagram|stateDiagram-v2|stateDiagram|erDiagram|journey|gantt|pie)\b",
    re.IGNORECASE,
)
BAD_HEADING_RE = re.compile(r"^(#{1,6})(\S)")  # '#' immediately followed by non-space


def list_markdown_files(root: Path) -> List[Path]:
    return [p for p in root.rglob("*.md") if ".git" not in p.parts]


def check_fences(lines: List[str], path: Path) -> List[str]:
    violations: List[str] = []
    stack: List[Tuple[str, int]] = []  # (lang, start_line)
    for i, line in enumerate(lines, start=1):
        if FENCE_OPEN_RE.match(line):
            m = FENCE_OPEN_RE.match(line)
            lang = (m.group(1) or "").lower() if m else ""
            stack.append((lang, i))
            continue
        if FENCE_CLOSE_RE.match(line):
            if not stack:
                violations.append(f"{path}:{i}: closing code fence without opening fence")
            else:
                stack.pop()
    if stack:
        # report all unclosed fences
        for lang, start in stack:
            label = lang or "plain"
            violations.append(f"{path}:{start}: unclosed code fence (```{label})")
    return violations


def check_mermaid(lines: List[str], path: Path) -> List[str]:
    violations: List[str] = []
    in_mermaid = False
    mermaid_start = 0
    seen_directive = False
    for i, line in enumerate(lines, start=1):
        if not in_mermaid:
            if MERMAID_FENCE_RE.match(line):
                in_mermaid = True
                mermaid_start = i
                seen_directive = False
            continue
        # inside mermaid until closing fence
        if FENCE_CLOSE_RE.match(line):
            if not seen_directive:
                violations.append(f"{path}:{mermaid_start}: mermaid block missing directive (e.g., 'flowchart TD')")
            in_mermaid = False
            continue
        if HTML_BR_RE.search(line):
            violations.append(f"{path}:{i}: HTML <br> not allowed inside mermaid code block")
        if MERMAID_DIRECTIVE_RE.match(line):
            seen_directive = True
    # if file ends while in mermaid, fences checker will report it
    return violations


def check_headings(lines: List[str], path: Path) -> List[str]:
    violations: List[str] = []
    for i, line in enumerate(lines, start=1):
        if BAD_HEADING_RE.match(line):
            violations.append(f"{path}:{i}: heading must have a space after '#', e.g., '# Title'")
    return violations


def check_file(path: Path) -> List[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    violations: List[str] = []
    violations += check_fences(lines, path)
    violations += check_mermaid(lines, path)
    violations += check_headings(lines, path)
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    md_files = list_markdown_files(root)
    all_violations: List[str] = []
    for p in md_files:
        all_violations.extend(check_file(p))
    if all_violations:
        print("Markdown syntax check failed:", file=sys.stderr)
        for v in all_violations:
            print(v, file=sys.stderr)
        return 1
    print("Markdown syntax check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

