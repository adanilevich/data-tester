clear

echo ""
echo "RUNNING TYPE CHECKS"
mypy ../

echo ""
echo "RUNNING LINTING AND STYLE CHECKS"
flake8 ../ -v

echo ""
echo "RUNNING TESTS"
pytest