lint:
	uv run ruff check src/ tests/
	uv run isort --check-only src/ tests/
	uv run black --check src/ tests/

lint-fix:
	uv run isort src/ tests/
	uv run ruff check --fix src/ tests/
	uv run black src/ tests/
	uv run ruff check src/ tests/