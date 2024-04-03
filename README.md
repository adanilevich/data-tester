# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                              |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------ | -------: | -------: | ------: | --------: |
| src/testcase/application/run\_testcases.py                        |       24 |        0 |    100% |           |
| src/testcase/di/di.py                                             |       24 |        1 |     96% |        28 |
| src/testcase/driven\_adapters/backends/dummy\_backend.py          |        5 |        1 |     80% |        10 |
| src/testcase/driven\_adapters/backends/dummy\_backend\_factory.py |        6 |        0 |    100% |           |
| src/testcase/driven\_adapters/backends/local\_backend.py          |      125 |      125 |      0% |     1-299 |
| src/testcase/driven\_adapters/notifiers/in\_memory\_notifier.py   |        7 |        0 |    100% |           |
| src/testcase/driven\_adapters/notifiers/stdout\_notifier.py       |        4 |        0 |    100% |           |
| src/testcase/driven\_ports/i\_backend.py                          |        6 |        0 |    100% |           |
| src/testcase/driven\_ports/i\_backend\_factory.py                 |        6 |        0 |    100% |           |
| src/testcase/driven\_ports/i\_notifier.py                         |        4 |        0 |    100% |           |
| src/testcase/driver\_adapters/cli\_testcase\_runner.py            |       13 |        0 |    100% |           |
| src/testcase/driver\_ports/i\_run\_testcases.py                   |       18 |        0 |    100% |           |
| src/testcase/dtos.py                                              |       69 |        0 |    100% |           |
| src/testcase/precondition\_checks/abstract\_check.py              |        8 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_nok.py           |        6 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_ok.py            |        6 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_exists.py    |       10 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_checkable.py                 |       15 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_precondition\_checker.py     |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/precondition\_checker.py        |       18 |        0 |    100% |           |
| src/testcase/testcases/dummy\_exception\_testcase.py              |       10 |        0 |    100% |           |
| src/testcase/testcases/dummy\_nok\_testcase.py                    |       11 |        0 |    100% |           |
| src/testcase/testcases/dummy\_ok\_testcase.py                     |       11 |        0 |    100% |           |
| src/testcase/testcases/testcase.py                                |       86 |        1 |     99% |        91 |
| src/testcase/testcases/testcase\_factory.py                       |       19 |        0 |    100% |           |
|                                                         **TOTAL** |  **516** |  **128** | **75%** |           |

12 empty files skipped.


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/adanilevich/data-tester/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/adanilevich/data-tester/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fadanilevich%2Fdata-tester%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.