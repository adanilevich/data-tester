clear

echo ""
echo "RUNNING TYPE CHECKS"
mypy ../

echo ""
echo "RUNNING LINTING AND STYLE CHECKS"
flake8 ../ -v --max-line-length 90

echo ""
echo "RUNNING TESTS"
coverage run --rcfile=tests/coverage.ini -m pytest tests/
coverage report --rcfile=tests/coverage.ini