.PHONY: install run lint test build check

install:
	uv sync

run:
	uv run database

lint:
	uv run ruff check .

test:
	uv run python -m unittest discover -s tests -v

build:
	uv build

check:
	uvx twine check dist/*
