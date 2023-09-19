SOURCES = ./src/ repl.py

.PHONY: check fix schema run

check:
	poetry run mypy --version
	poetry run mypy $(SOURCES)
	poetry run ruff --version
	poetry run ruff check $(SOURCES)
	poetry run black --version
	poetry run black --check --line-length=100 $(SOURCES)
	poetry run isort --version
	poetry run isort --check-only $(SOURCES)

fix:
	poetry run black --line-length=100 $(SOURCES)
	poetry run isort $(SOURCES)
	poetry run ruff check --fix $(SOURCES)

test:
	poetry run pytest -v tests/

test-unit:
	poetry run pytest -v tests/unit

test-integration:
	poetry run pytest -v tests/unit

cov:
	poetry run pytest -v --cov="./src"