clear

echo "RUNNING TYPE CHECKS"
mypy

echo ""
echo "RUNNING LINTING AND STYLE CHECKS"
ruff check

echo ""
echo "RUNNING TESTS"
coverage run
coverage report