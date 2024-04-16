# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                      |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/dtos/configs.py                                                       |       35 |        3 |     91% | 13, 23-25 |
| src/dtos/specifications.py                                                |       45 |        2 |     96% |    54, 65 |
| src/dtos/testcase.py                                                      |       65 |        2 |     97% |    40, 51 |
| src/testcase/adapters/data\_platforms/\_\_init\_\_.py                     |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/\_\_init\_\_.py                |        4 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_naming\_resolver.py      |       49 |        5 |     90% | 24, 84-87 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform.py              |      170 |       16 |     91% |116, 133-135, 155, 259, 263, 265, 268-273, 365, 391, 395 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform\_factory.py     |       16 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_query\_handler.py        |       23 |        2 |     91% |    23, 37 |
| src/testcase/adapters/data\_platforms/dummy/\_\_init\_\_.py               |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform.py            |       27 |        9 |     67% |16, 19, 23, 26, 32, 36, 42, 49, 56 |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform\_factory.py   |        6 |        0 |    100% |           |
| src/testcase/adapters/notifiers/\_\_init\_\_.py                           |        2 |        0 |    100% |           |
| src/testcase/adapters/notifiers/in\_memory\_notifier.py                   |        7 |        0 |    100% |           |
| src/testcase/adapters/notifiers/stdout\_notifier.py                       |        4 |        0 |    100% |           |
| src/testcase/application/run\_testcases.py                                |       23 |        0 |    100% |           |
| src/testcase/di/di.py                                                     |       21 |        1 |     95% |        25 |
| src/testcase/drivers/cli\_testcase\_runner.py                             |       13 |        0 |    100% |           |
| src/testcase/ports/\_\_init\_\_.py                                        |        4 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform.py                                   |       30 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform\_factory.py                          |        6 |        0 |    100% |           |
| src/testcase/ports/i\_notifier.py                                         |        4 |        0 |    100% |           |
| src/testcase/ports/i\_run\_testcases.py                                   |       20 |        0 |    100% |           |
| src/testcase/precondition\_checks/\_\_init\_\_.py                         |       10 |        0 |    100% |           |
| src/testcase/precondition\_checks/abstract\_check.py                      |        8 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/testcase/precondition\_checks/check\_specs\_are\_unique.py            |       23 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_checkable.py                         |       18 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_precondition\_checker.py             |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/precondition\_checker.py                |       15 |        0 |    100% |           |
| src/testcase/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/testcase/testcases/abstract\_testcase.py                              |      104 |        1 |     99% |       106 |
| src/testcase/testcases/compare\_sample.py                                 |      131 |       23 |     82% |92, 99, 105-107, 112-114, 148-150, 169-171, 185-193 |
| src/testcase/testcases/dummy\_exception.py                                |       10 |        0 |    100% |           |
| src/testcase/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/testcase/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/testcase/testcases/rowcount.py                                        |       57 |        1 |     98% |        71 |
| src/testcase/testcases/schema.py                                          |      135 |        3 |     98% |98, 107, 142 |
| src/testcase/testcases/testcase\_factory.py                               |       21 |        0 |    100% |           |
|                                                                 **TOTAL** | **1190** |   **70** | **94%** |           |

7 empty files skipped.


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