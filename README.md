# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                        |    Stmts |     Miss |  Cover |   Missing |
|------------------------------------------------------------ | -------: | -------: | -----: | --------: |
| src/\_\_init\_\_.py                                         |        0 |        0 |   100% |           |
| src/testcase/\_\_init\_\_.py                                |        0 |        0 |   100% |           |
| src/testcase/application/\_\_init\_\_.py                    |        0 |        0 |   100% |           |
| src/testcase/driven\_adapters/\_\_init\_\_.py               |        0 |        0 |   100% |           |
| src/testcase/driven\_adapters/backends/\_\_init\_\_.py      |        0 |        0 |   100% |           |
| src/testcase/driven\_adapters/notifiers/\_\_init\_\_.py     |        0 |        0 |   100% |           |
| src/testcase/driven\_adapters/notifiers/stdout\_notifier.py |        4 |        4 |     0% |       1-6 |
| src/testcase/driven\_ports/\_\_init\_\_.py                  |        0 |        0 |   100% |           |
| src/testcase/driven\_ports/backend\_interface.py            |        6 |        6 |     0% |       1-9 |
| src/testcase/driven\_ports/notifier\_interface.py           |        5 |        5 |     0% |      1-15 |
| src/testcase/driver\_adapters/\_\_init\_\_.py               |        0 |        0 |   100% |           |
| src/testcase/driver\_ports/\_\_init\_\_.py                  |        0 |        0 |   100% |           |
| src/testcase/dtos.py                                        |       47 |       47 |     0% |      1-64 |
| src/testcase/precondition\_checkers/\_\_init\_\_.py         |        0 |        0 |   100% |           |
| src/testcase/precondition\_checkers/abstract\_checker.py    |       15 |       15 |     0% |      1-33 |
| src/testcase/precondition\_checkers/checkable.py            |       16 |       16 |     0% |      1-30 |
| src/testcase/precondition\_checkers/checker\_interface.py   |       17 |       17 |     0% |      1-51 |
| src/testcase/precondition\_checkers/testobject\_exists.py   |       11 |       11 |     0% |      1-25 |
| src/testcase/testcases/\_\_init\_\_.py                      |        0 |        0 |   100% |           |
| src/testcase/testcases/testcase.py                          |       97 |       97 |     0% |     1-159 |
|                                                   **TOTAL** |  **218** |  **218** | **0%** |           |


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