PYTHON ?= python3

.PHONY: run clean

run:
	$(PYTHON) -m src $(FILE)

clean:
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +
