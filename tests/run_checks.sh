clear

echo "RUNNING TYPE CHECKS"
mypy

echo ""
echo "RUNNING LINTING AND STYLE CHECKS"
flake8

echo ""
echo "RUNNING TESTS"
coverage run
coverage report