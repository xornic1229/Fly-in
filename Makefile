PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

# Usage examples:
#   make run FILE=maps/easy/01_linear_path.txt
#   make debug FILE=maps/medium/03_priority_puzzle.txt

FILE ?= maps/easy/01_linear_path.txt

.PHONY: install run debug clean lint lint-strict

install:
	@$(PIP) install -U pip
	@# Dev tooling required by the subject
	@$(PIP) install -U flake8 mypy

run:
	@$(PYTHON) -m src $(FILE)

debug:
	@$(PYTHON) -m pdb -m src $(FILE)

clean:
	@find . -type d -name '__pycache__' -prune -exec rm -rf {} +
	@find . -type d -name '.mypy_cache' -prune -exec rm -rf {} +
	@find . -type d -name '.pytest_cache' -prune -exec rm -rf {} +
	@find . -type d -name '.ruff_cache' -prune -exec rm -rf {} +
	@find . -type f -name '*.pyc' -delete
	@find . -type f -name '*.pyo' -delete
	@find . -type f -name '*~' -delete

lint:
	@flake8 .
	@mypy . \
		--explicit-package-bases \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@flake8 .
	@mypy . --strict --explicit-package-bases