install:
	uv sync

run:
	uv run python -m src

debug:
	uv run python -m pdb -m src

clean:
	rm -rf __pycache__ src/__pycache__ .mypy_cache

lint:
	uv run flake8 .
	uv run mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	uv run flake8 .
	uv run mypy . --strict

help:
	@echo "make install      install dependencies (uv sync)"
	@echo "make run          run with the default files"
	@echo "make debug        run with pdb"
	@echo "make clean        remove caches"
	@echo "make lint         flake8 + mypy"
	@echo "make lint-strict  flake8 + mypy --strict"

.PHONY: help install run debug clean lint lint-strict
