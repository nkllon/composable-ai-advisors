.PHONY: help setup lint typecheck test markdown pre-commit-install ci run-backend

UV?=uv
PY?=python
VENV=.venv

help:
	@echo "Targets:"
	@echo "  setup               - create venv and install deps (runtime + dev)"
	@echo "  lint                - run ruff lint"
	@echo "  typecheck           - run mypy (non-failing like CI)"
	@echo "  test                - run pytest"
	@echo "  markdown            - run markdownlint with repo config"
	@echo "  pre-commit-install  - install pre-commit hooks"
	@echo "  ci                  - run lint, typecheck, test, markdown"
	@echo "  run-backend         - run FastAPI locally via uvicorn"

$(VENV)/bin/activate:
	$(UV) venv

setup: $(VENV)/bin/activate
	. $(VENV)/bin/activate; \
	$(UV) pip install -r backend/requirements.txt; \
	test -f backend/requirements-dev.txt && $(UV) pip install -r backend/requirements-dev.txt || true

lint: $(VENV)/bin/activate
	. $(VENV)/bin/activate; \
	$(UV)x ruff --version; \
	$(UV)x ruff check .

typecheck: $(VENV)/bin/activate
	. $(VENV)/bin/activate; \
	$(UV)x mypy --version; \
	$(UV)x mypy backend || true

test: $(VENV)/bin/activate
	. $(VENV)/bin/activate; \
	pytest -q

markdown:
	@command -v markdownlint >/dev/null 2>&1 || { echo "markdownlint not found. Install: npm i -g markdownlint-cli"; exit 1; }
	@markdownlint -c .markdownlint.yml $$(git ls-files "*.md")

pre-commit-install:
	@command -v pre-commit >/dev/null 2>&1 || { echo "pre-commit not found. Install: brew install pre-commit || pipx install pre-commit"; exit 1; }
	pre-commit install

ci: lint typecheck test markdown

run-backend: $(VENV)/bin/activate
	. $(VENV)/bin/activate; \
	$(PY) -m uvicorn backend.main:app --reload


