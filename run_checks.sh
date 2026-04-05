#!/bin/bash

echo "Running ruff checks..."
uv run ruff check --fix

read -p "Next: typechecks. Press Enter to continue!"
echo "Running typechecks ..."
uv run ty check

read -p "Next: lint-imports. Press Enter to continue!"
echo "Running lint-imports..."
uv run lint-imports

read -p "Next: tests. Press Enter to continue!"
echo "Running tests ..."
uv run coverage run

#read -p "Next: coverage report. Press Enter to continue!"
#echo "Printing coverage report..."
#uv run coverage report
#read -p "Next: code line count. Press Enter to continue!"

#echo "Running code line count..."
#uv run pygount src --format=summary

echo "Generating badges..."
uv run python badges/generate.py