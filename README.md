# Data Tester

[![Build](https://github.com/adanilevich/data-tester/actions/workflows/python-app.yml/badge.svg?kill_cache=1)](https://github.com/adanilevich/data-tester/actions/workflows/python-app.yml)
[![Coverage badge](https://raw.githubusercontent.com/adanilevich/data-tester/python-coverage-comment-action-data/badge.svg?kill_cache=1)](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

---

## Overview

**Data Tester** is a flexible framework designed to automate and standardize business validation tests for ETL (Extract, Transform, Load) pipelines. It enables data analysts, data platform owners, and engineers to define, execute, and report on business logic tests that ensure ETL processes produce correct and complete data.

The framework is built to:

- Validate business rules and transformations in ETL pipelines
- Automate regression and acceptance testing for data flows incl. test reporting
- Support rapid iteration and deployment of new ETL logic
- Be extensible to new data platform technologies, report and specification formats

## Project Goals

- **Support Business Validation:** Focus on verifying that ETL pipelines meet business requirements, not just technical data quality.
- **Accelerate ETL Development:** Enable fast feedback cycles for changes in business logic or data models.
- **Promote Collaboration:** Bridge the gap between business users and technical teams through transparent, understandable test results.
- **Enable Automation:** Integrate business tests into CI/CD pipelines for continuous validation of ETL processes.

## Key Features

- **Business Rule Testing:** Define and automate tests that check business logic, such as calculations, aggregations, mappings, and data transformations.
- **Automated Execution:** Due to built-in extensiblity, tests can be run via CLI or from UI or integrate with automation tools for scheduled or triggered runs.
- **Comprehensive Reporting:** Generate reports in multiple formats (json, txt, xlsx) - or extend the framework for your own format.
- **Adaptablity and Extensibility:** Due to the choices made in code architecture, this framework can be expanded to new data platforms and storage backends.

## Typical Workflow

1. **Define Business Test Cases:**
   - Define test specifications using SQL or custom specification formats.
2. **Execute Tests:**
   - Run business tests via the CLI or integrate with CI/CD tools to validate each ETL deployment.
3. **Review Results:**
   - Analyze generated reports to identify business rule violations or unexpected outcomes.
   - Share results with both technical and business teams for rapid feedback and resolution.
4. **Scale and manage:**
   - Organize tests in test sets depending on your stage (e.g. test, uat), test scenario or other requirements.
   - Schedule and execute test sets to ensure ETL result quality

---

For more details, see the source code and module-level documentation.
