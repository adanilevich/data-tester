clear

echo "RUNNING TYPE CHECKS"
mypy src/

echo ""
echo "RUNNING LINTING AND STYLE CHECKS"
flake8 src/ -v --max-line-length 90

echo ""
echo "RUNNING TESTS"
coverage run --rcfile=.coveragerc -m pytest -m "not skip_test and not infrastructure" tests/
coverage report --rcfile=.coveragerc