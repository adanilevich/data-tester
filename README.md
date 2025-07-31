# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                             |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/apps/cli/domain\_config\_di.py                                               |       19 |        0 |    100% |           |
| src/apps/cli/report\_di.py                                                       |       22 |        0 |    100% |           |
| src/apps/cli/specification\_di.py                                                |       15 |        0 |    100% |           |
| src/apps/cli/testcase\_di.py                                                     |       24 |        0 |    100% |           |
| src/apps/cli/testset\_di.py                                                      |       14 |        0 |    100% |           |
| src/config/\_\_init\_\_.py                                                       |        2 |        0 |    100% |           |
| src/config/config.py                                                             |       27 |        1 |     96% |         9 |
| src/domain/\_\_init\_\_.py                                                       |        6 |        0 |    100% |           |
| src/domain/domain\_config/\_\_init\_\_.py                                        |        3 |        0 |    100% |           |
| src/domain/domain\_config/domain\_config.py                                      |       28 |        4 |     86% |57-58, 68-73 |
| src/domain/domain\_config/domain\_config\_handler.py                             |       17 |        0 |    100% |           |
| src/domain/report/\_\_init\_\_.py                                                |        4 |        0 |    100% |           |
| src/domain/report/handle\_reports.py                                             |       57 |        1 |     98% |       146 |
| src/domain/report/plugins/\_\_init\_\_.py                                        |        5 |        0 |    100% |           |
| src/domain/report/plugins/i\_report\_formatter.py                                |        5 |        0 |    100% |           |
| src/domain/report/plugins/txt\_testcase\_report.py                               |       24 |        3 |     88% |     52-54 |
| src/domain/report/plugins/xlsx\_testcase\_diff.py                                |       28 |        0 |    100% |           |
| src/domain/report/plugins/xlsx\_testrun\_report.py                               |       27 |        3 |     89% |     51-53 |
| src/domain/report/report.py                                                      |       76 |        5 |     93% |113, 126-129, 191 |
| src/domain/specification/\_\_init\_\_.py                                         |        4 |        0 |    100% |           |
| src/domain/specification/handle\_specs.py                                        |       23 |        0 |    100% |           |
| src/domain/specification/plugins/\_\_init\_\_.py                                 |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_naming\_conventions.py                       |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_spec\_formatter.py                           |        9 |        0 |    100% |           |
| src/domain/specification/plugins/naming\_conventions.py                          |       33 |        2 |     94% |     62-63 |
| src/domain/specification/plugins/spec\_formatter.py                              |       44 |        0 |    100% |           |
| src/domain/specification/specification.py                                        |       67 |        4 |     94% |69, 110, 131-132 |
| src/domain/testcase/\_\_init\_\_.py                                              |        2 |        0 |    100% |           |
| src/domain/testcase/handle\_testruns.py                                          |       28 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/\_\_init\_\_.py                         |       10 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/abstract\_check.py                      |        6 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/domain/testcase/precondition\_checks/check\_specs\_are\_unique.py            |       24 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/i\_checkable.py                         |       11 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/i\_precondition\_checker.py             |        3 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/precondition\_checker.py                |       14 |        0 |    100% |           |
| src/domain/testcase/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/domain/testcase/testcases/abstract\_testcase.py                              |      104 |        0 |    100% |           |
| src/domain/testcase/testcases/compare.py                                         |      129 |       20 |     84% |117, 124, 130-131, 138-140, 173-174, 190-191, 202-210 |
| src/domain/testcase/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/rowcount.py                                        |       57 |        1 |     98% |        89 |
| src/domain/testcase/testcases/schema.py                                          |      131 |        3 |     98% |98, 109, 146 |
| src/domain/testcase/testrun.py                                                   |       64 |        3 |     95% |121, 127, 133 |
| src/domain/testset/\_\_init\_\_.py                                               |        2 |        0 |    100% |           |
| src/domain/testset/handle\_testsets.py                                           |       15 |        0 |    100% |           |
| src/domain/testset/testset.py                                                    |       28 |        2 |     93% |     54-55 |
| src/domain\_ports/\_\_init\_\_.py                                                |        6 |        0 |    100% |           |
| src/domain\_ports/domain\_config/\_\_init\_\_.py                                 |        2 |        0 |    100% |           |
| src/domain\_ports/domain\_config/i\_domain\_config\_handler.py                   |        9 |        0 |    100% |           |
| src/domain\_ports/report/\_\_init\_\_.py                                         |        2 |        0 |    100% |           |
| src/domain\_ports/report/i\_report\_handler.py                                   |       26 |        0 |    100% |           |
| src/domain\_ports/specification/\_\_init\_\_.py                                  |        2 |        0 |    100% |           |
| src/domain\_ports/specification/i\_spec\_handler.py                              |       10 |        0 |    100% |           |
| src/domain\_ports/testcase/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/domain\_ports/testcase/i\_testrun\_handler.py                                |       16 |        0 |    100% |           |
| src/domain\_ports/testset/\_\_init\_\_.py                                        |        2 |        0 |    100% |           |
| src/domain\_ports/testset/i\_testset\_handler.py                                 |       15 |        0 |    100% |           |
| src/drivers/cli/\_\_init\_\_.py                                                  |        6 |        0 |    100% |           |
| src/drivers/cli/domain\_config.py                                                |       11 |        0 |    100% |           |
| src/drivers/cli/report.py                                                        |       20 |        0 |    100% |           |
| src/drivers/cli/specification.py                                                 |        9 |        0 |    100% |           |
| src/drivers/cli/testcase.py                                                      |       13 |        2 |     85% |     31-37 |
| src/drivers/cli/testset.py                                                       |       16 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                         |        8 |        0 |    100% |           |
| src/dtos/domain\_config.py                                                       |       35 |        1 |     97% |        49 |
| src/dtos/dto.py                                                                  |       17 |        0 |    100% |           |
| src/dtos/location.py                                                             |       61 |        3 |     95% |60, 66, 68 |
| src/dtos/report.py                                                               |       62 |        0 |    100% |           |
| src/dtos/specification.py                                                        |       62 |        4 |     94% | 34-37, 95 |
| src/dtos/testcase.py                                                             |      112 |        2 |     98% |  154, 157 |
| src/dtos/testset.py                                                              |       34 |        1 |     97% |        24 |
| src/infrastructure/backend/\_\_init\_\_.py                                       |        5 |        0 |    100% |           |
| src/infrastructure/backend/demo/\_\_init\_\_.py                                  |        3 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_backend.py                                 |      171 |       16 |     91% |131, 148-150, 168, 288, 292, 294, 297-302, 402, 432, 438 |
| src/infrastructure/backend/demo/demo\_backend\_factory.py                        |       17 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_naming\_resolver.py                        |       50 |        5 |     90% | 28, 87-90 |
| src/infrastructure/backend/demo/demo\_query\_handler.py                          |       21 |        1 |     95% |        33 |
| src/infrastructure/backend/dummy/\_\_init\_\_.py                                 |        3 |        0 |    100% |           |
| src/infrastructure/backend/dummy/dummy\_backend.py                               |       26 |        9 |     65% |21, 24, 34, 42, 48, 53, 63, 74, 84 |
| src/infrastructure/backend/dummy/dummy\_backend\_factory.py                      |        6 |        0 |    100% |           |
| src/infrastructure/backend/map.py                                                |        8 |        2 |     75% |     7, 11 |
| src/infrastructure/notifier/\_\_init\_\_.py                                      |        5 |        0 |    100% |           |
| src/infrastructure/notifier/in\_memory\_notifier.py                              |        7 |        0 |    100% |           |
| src/infrastructure/notifier/map.py                                               |        8 |        1 |     88% |        11 |
| src/infrastructure/notifier/stdout\_notifier.py                                  |        4 |        0 |    100% |           |
| src/infrastructure/storage/\_\_init\_\_.py                                       |        5 |        0 |    100% |           |
| src/infrastructure/storage/dict\_storage.py                                      |       66 |        2 |     97% |   118-120 |
| src/infrastructure/storage/file\_storage.py                                      |      139 |       38 |     73% |59-66, 74-75, 82, 102-103, 122, 129-130, 146-147, 159, 162, 169-170, 184, 191-204, 223-227, 240, 246, 255-256 |
| src/infrastructure/storage/formatter\_factory.py                                 |       13 |        0 |    100% |           |
| src/infrastructure/storage/i\_formatter.py                                       |        7 |        0 |    100% |           |
| src/infrastructure/storage/i\_formatter\_factory.py                              |        4 |        0 |    100% |           |
| src/infrastructure/storage/json\_formatter.py                                    |       39 |        5 |     87% |46-48, 53-54 |
| src/infrastructure/storage/storage\_factory.py                                   |       19 |        0 |    100% |           |
| src/infrastructure\_ports/\_\_init\_\_.py                                        |        4 |        0 |    100% |           |
| src/infrastructure\_ports/backend/\_\_init\_\_.py                                |        3 |        0 |    100% |           |
| src/infrastructure\_ports/backend/i\_backend.py                                  |       10 |        0 |    100% |           |
| src/infrastructure\_ports/backend/i\_backend\_factory.py                         |        4 |        0 |    100% |           |
| src/infrastructure\_ports/notifier/\_\_init\_\_.py                               |        2 |        0 |    100% |           |
| src/infrastructure\_ports/notifier/i\_notifier.py                                |        2 |        0 |    100% |           |
| src/infrastructure\_ports/storage/\_\_init\_\_.py                                |        3 |        0 |    100% |           |
| src/infrastructure\_ports/storage/i\_storage.py                                  |        7 |        0 |    100% |           |
| src/infrastructure\_ports/storage/i\_storage\_factory.py                         |        4 |        0 |    100% |           |
|                                                                        **TOTAL** | **2530** |  **146** | **94%** |           |

9 empty files skipped.


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