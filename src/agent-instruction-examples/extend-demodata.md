# Task: extend-demodata
See `agent-artifacts/instructions/extend-demodata.md` for detailed instructions.

## Context and Motivation
For demonstation purposes, we need more testsets and according user specifications. Lets extend the scripts prepare_demo_data and prepare_demo_artifacts.

## Requirements
- Applicable testcases: for stage_ testobjects STAGECOUNT and SCHEMA, for all other testobjects ROWCOUNT, SCHEMA, COMPARE
- For domain payments:
    - if not already done, extend domain_config for payments with spec_locations for both stages test and UAT
    - rename current testset 'payments_full' to 'Payments Partial'
    - create a new testset 'Payments Full' in stage 'test', instance 'alpha' which covers all testobjects (stage_, core_, and mart_) with all applicable testcases. Create all required user specifications for this testset if not already exist
    - create a new testset 'Payments UAT' which covers all existing testobjects in payments_uat. create all user specifications for that and make all specifications stored in stage-specific locations, e.g. 'user/uat' and 'user/test'. Important: make the schema specification for core_account_payments faulty - such that testcase returns NOK - but only for UAT! Leave out schema specification for UAT stage_accounts such that testcase returns N/A
- For domain sales:
    - Rename testset 'sales_validation' to 'Sales Validation'
    - Add testset 'Sales Full' which tests all applicable testcases for all four testobjects in stage test, instance main
- For all domains and testsets: Add comment to each testset which specifies which testcases are expected to fail and why. Format such that string is easily user-readable

## Steps
1. Throughly analyze the provided context and the requirements
2. Analyze the codebase and identify side effects, esp. on integration tests, but also on unittests. If any side effects, make a suggestion how to adapt without reducing test coverage
3. Make a plan and implement

## Before prompting for implementation verify
- [ ] Final plan persisted to `agent-artifacts/plans/plan-{task-title}.md`
- [ ] Intermediate files updated in `agent-artifacts/plans/intermediate/{task-title}/` 