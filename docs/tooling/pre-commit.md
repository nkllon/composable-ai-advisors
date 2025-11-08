### Pre-commit (local checks)

This repository includes a pre-commit hook to run Markdown lint locally before you commit, so CI won’t surprise you.

Setup
1) Install pre-commit:
   - macOS (Homebrew): `brew install pre-commit`
   - Python: `pipx install pre-commit` (or `pip install pre-commit`)
2) Install markdownlint CLI:
   - Node: `npm i -g markdownlint-cli`
3) Enable hooks in this repo:
   - `pre-commit install`

Usage
- On every `git commit`, staged `.md` files are linted via:
  - `markdownlint -c .markdownlint.yml`
- Run on all files:
  - `pre-commit run --all-files`

Notes
- The hook assumes `markdownlint` is in your PATH.
- CI still enforces the markdown check; this just catches issues earlier.


