#!/usr/bin/env python3
"""
Deterministic check for Mermaid code blocks in Markdown files.
Rules enforced:
- No HTML line breaks (<br>, <br/>, <br />) inside ```mermaid code fences.

Exit codes:
0 = OK
1 = Violations found
"""
from __future__ import annotations

import sys
import re
from pathlib import Path

MERMAID_FENCE_RE = re.compile(r"^```mermaid\s*$", re.IGNORECASE)
FENCE_CLOSE_RE = re.compile(r"^```\s*$")
HTML_BR_RE = re.compile(r"<br\s*/?>", re.IGNORECASE)


def find_markdown_files(root: Path) -> list[Path]:
    return [p for p in root.rglob("*.md") if ".git" not in p.parts]


def check_file(path: Path) -> list[str]:
    violations: list[str] = []
    in_mermaid = False
    with path.open("r", encoding="utf-8") as fh:
        for idx, line in enumerate(fh, start=1):
            if not in_mermaid and MERMAID_FENCE_RE.match(line):
                in_mermaid = True
                continue
            if in_mermaid and FENCE_CLOSE_RE.match(line):
                in_mermaid = False
                continue
            if in_mermaid:
                if HTML_BR_RE.search(line):
                    violations.append(f"{path}:{idx}: HTML <br> found inside mermaid block")
    return violations


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    all_md = find_markdown_files(root)
    all_violations: list[str] = []
    for md in all_md:
        all_violations.extend(check_file(md))
    if all_violations:
        print("Mermaid Markdown check failed:\n", file=sys.stderr)
        for v in all_violations:
            print(v, file=sys.stderr)
        return 1
    print("Mermaid Markdown check passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

