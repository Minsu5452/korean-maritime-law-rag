.PHONY: up down test lint collect index eval smoke

up:
	docker compose up -d
down:
	docker compose down
test:
	uv run pytest
lint:
	uv run ruff check .
collect:
	uv run python scripts/collect.py
index:
	uv run python scripts/build_index.py
eval:
	uv run python scripts/evaluate.py
smoke:
	uv run python scripts/smoke.py
