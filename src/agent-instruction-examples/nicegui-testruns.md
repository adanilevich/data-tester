# Task: nicegui-testruns
See `agent-artifacts/instructions/nicegui-testruns.md` for detailed instructions, then proceed.

---

## MANDATORY: Delegation to `nicegui-expert` agent

All technical work (analysis, code writing) must be delegated to the `nicegui-expert` agent. Do NOT perform analysis or write code yourself.

Orchestration steps (done by you, not the subagent):

1. Read all relevant files and pass their full contents to `nicegui-expert` in its prompt
2. Launch `nicegui-expert` for **analysis only** — ask it to assess the architecture per Motivation and Requirements below. Collect its output as findings.
3. Populate `findings.md` from `nicegui-expert` output, then invoke `planning-with-files:plan`.
4. Write the final plan according to Planning instructions in CLAUDE.md
5. Prompt me to review plan
6. After review launch `nicegui-expert` again for **implementation**, passing the full plan text and all relevant file contents.
7. After implementation, write summary according to Instruction in CLAUDE.md

## Motivation

We want to implement a testruns view in our NiceGUI ui to show users past and current testruns.

---

## Requirements
 As a user, when navigating to testruns, I want:
- all testruns of my domain to be listed
- filter by stage, instance, testrun result and free-search (live search) by testobject name
- testset list items are expandable, their headers show testset name, testrun status (colored by status),  stage of testrun, instance of testrun, number of testcases per status OK, NOK, NA and a report button/icon
- when expanded, show testcase results as matrix: testobjects as rows, testtypes as columns, matrix entries are OK, NOK, NA (green/red/yellow)
- when clicked on an icon, show a dialog which displays the testcase result in a well-readable manner and has buttons 'report', 'diff' (only not greyed out if both result NOK and testcase = COMPARE) and 'close' (to close the dialog)
- report buttons show notification "Reports not yet implemented"
- for list and matrix visualization see implementation of testset view - reuse components if reasonably possible

---

## Steps

1. Read all files listed above, then launch `nicegui-expert` for analysis (step 1-2 of orchestration).
2. Invoke `planning-with-files:plan` skill and write the plan (steps 3-4 of orchestration).
3. Prompt me to review plan (Step 5 or orchestration)
4. Launch `nicegui-expert` for implementation after plan is confirmed (step 6 of orchestration).
5. Write summary (step 7. of orchestration)
