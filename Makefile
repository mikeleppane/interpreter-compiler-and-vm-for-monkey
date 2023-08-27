SRC_DIR = ./src/

.PHONY: check fix schema run

check:
	poetry run mypy --version
	poetry run mypy $(SRC_DIR) repl.py
	poetry run black --version
	poetry run black --check --line-length=100 $(SRC_DIR) repl.py
	poetry run isort --version
	poetry run isort --check-only $(SRC_DIR) repl.py
	poetry run ruff --version
	poetry run ruff check $(SRC_DIR) repl.py

fix:
	poetry run black --line-length=100 $(SRC_DIR) repl.py
	poetry run isort $(SRC_DIR) repl.py
	poetry run ruff check --fix $(SRC_DIR) repl.py

test:
	poetry run pytest -v tests/

test-unit:
	poetry run pytest -v tests/unit

cov:
	poetry run pytest -v --cov="."