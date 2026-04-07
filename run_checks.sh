#!/bin/bash

echo "Running ruff checks..."
uv run ruff check --fix
[ $? -ne 0 ] && read -p "Ruff failed. Press Enter to continue!"

echo "Running typechecks ..."
uv run ty check
[ $? -ne 0 ] && read -p "Typechecks failed. Press Enter to continue!"

echo "Running lint-imports..."
uv run lint-imports
[ $? -ne 0 ] && read -p "Lint-imports failed. Press Enter to continue!"

echo "Running tests ..."
uv run coverage run
[ $? -ne 0 ] && read -p "Tests failed. Press Enter to continue!"

echo "Printing coverage report..."
uv run coverage report

echo "Generating badges..."
uv run python badges/generate.py
