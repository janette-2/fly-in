NAME = fly-in

RUN = python3 main.py
FLAKE = flake8
MYPY = mypy
PDB = python3 -m pdb

# ?=  means "use this default, but let the user override it".
# Example:  make run MAP=mi_mapa.txt
# If you don't pass MAP, it uses the map below.
MAP ?= maps/medium/03_priority_puzzle.txt

# Default target. Runs lint when you just type `make`.
all: lint

install:
# --quiet = hide progress bars and download messages.
	uv tool install --force flake8 --quiet
	uv tool install --force mypy --quiet

run:
	$(RUN) $(MAP)

debug:
	$(PDB) main.py $(MAP)

clean:
# Remove cache directories created by Python and mypy
	rm -rf __pycache__ .mypy_cache .pytest_cache
# .pyc files = compiled Python code that Python auto-generates when
# you import a module. They are safe to delete.
	find . -type f -name '*.pyc' -delete
	find . -type d -name '__pycache__' -empty -delete

lint:
# @ = run the command silently (don't print it, just show the output).
	@echo "=== flake8 ==="
	$(FLAKE) .
	@echo
	@echo "=== mypy ==="
# --warn-return-any     warns when a function returns Any (untyped)
# --warn-unused-ignores warns about "# type: ignore" comments that are no longer needed
# --ignore-missing-imports  skips errors for missing type stubs in third-party libs
# --disallow-untyped-defs   errors if a function has no type annotations
# --check-untyped-defs      partially checks the body of untyped functions
	$(MYPY) . --warn-return-any --warn-unused-ignores \
		--ignore-missing-imports --disallow-untyped-defs \
		--check-untyped-defs

lint-strict:
	@echo "=== flake8 ==="
	$(FLAKE) .
	@echo
	@echo "=== mypy --strict ==="
	$(MYPY) . --strict

# .PHONY = tells Make "these are NOT files, always run them".
# Normally Make thinks every target is a filename.
# If a file named "clean" existed, Make would skip it.
# .PHONY stops that — the recipe runs every time.
.PHONY: all install run debug clean lint lint-strict
