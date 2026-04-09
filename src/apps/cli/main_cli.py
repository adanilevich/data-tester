"""CLI entry point for Data Tester.

Usage:
    uv run python -m src.apps.cli.main_cli <domain> <testset_name>
"""

import argparse

from src.apps.cli.app import CliApp
from src.config import Config


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Data Tester CLI")
    parser.add_argument("domain", help="Domain name")
    parser.add_argument("testset_name", help="Testset name")
    args = parser.parse_args()
    config = Config()
    app = CliApp(config)
    app.run_tests(domain=args.domain, testset_name=args.testset_name)


if __name__ == "__main__":
    main()
