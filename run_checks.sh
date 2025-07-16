#!/bin/bash

echo "Running ruff checks..."
ruff check --fix
read -p "Press Enter to continue!"

echo "Running mypy checks..."
mypy
read -p "Press Enter to continue!"

echo "Running pytest..."
pytest