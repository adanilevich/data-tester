#!/bin/bash

echo "Running ruff checks..."
ruff check --fix
read -p "Press Enter to continue!"

echo "Running mypy checks..."
mypy
read -p "Press Enter to continue!"

echo "Running pytest..."
pytest
read -p "Press Enter to continue!"

echo "Running lint-imports..."
uv run lint-imports
read -p "Press Enter to continue!"

echo "Counting lines of code..."
pygount src --format=summary