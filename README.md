# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                             |    Stmts |     Miss |   Cover |   Missing |
|--------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/apps/cli\_app.py                                                             |       19 |        0 |    100% |           |
| src/apps/cli\_di.py                                                              |       61 |        2 |     97% |    38, 49 |
| src/config/\_\_init\_\_.py                                                       |        2 |        0 |    100% |           |
| src/config/config.py                                                             |       19 |        1 |     95% |         9 |
| src/domain/\_\_init\_\_.py                                                       |        6 |        0 |    100% |           |
| src/domain/domain\_config/\_\_init\_\_.py                                        |        3 |        0 |    100% |           |
| src/domain/domain\_config/domain\_config.py                                      |       24 |        2 |     92% |     50-51 |
| src/domain/domain\_config/domain\_config\_adapter.py                             |       17 |        0 |    100% |           |
| src/domain/report/\_\_init\_\_.py                                                |        4 |        0 |    100% |           |
| src/domain/report/plugins/\_\_init\_\_.py                                        |        5 |        0 |    100% |           |
| src/domain/report/plugins/i\_report\_formatter.py                                |        5 |        0 |    100% |           |
| src/domain/report/plugins/txt\_testcase\_report.py                               |       24 |        3 |     88% |     52-54 |
| src/domain/report/plugins/xlsx\_testcase\_diff.py                                |       28 |        0 |    100% |           |
| src/domain/report/plugins/xlsx\_testrun\_report.py                               |       27 |        3 |     89% |     50-52 |
| src/domain/report/report.py                                                      |       73 |        7 |     90% |75, 84, 98, 100, 113, 139, 145 |
| src/domain/report/report\_adapter.py                                             |       35 |        0 |    100% |           |
| src/domain/specification/\_\_init\_\_.py                                         |        4 |        0 |    100% |           |
| src/domain/specification/plugins/\_\_init\_\_.py                                 |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_naming\_conventions.py                       |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_spec\_formatter.py                           |        7 |        0 |    100% |           |
| src/domain/specification/plugins/naming\_conventions.py                          |       35 |        3 |     91% | 27, 65-66 |
| src/domain/specification/plugins/spec\_formatter.py                              |       50 |        0 |    100% |           |
| src/domain/specification/specification.py                                        |       57 |        2 |     96% |   76, 122 |
| src/domain/specification/specification\_adapter.py                               |       24 |        0 |    100% |           |
| src/domain/testcase/\_\_init\_\_.py                                              |        2 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/\_\_init\_\_.py                         |        8 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/abstract\_check.py                      |       20 |        1 |     95% |        57 |
| src/domain/testcase/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/domain/testcase/precondition\_checks/check\_specs\_are\_unique.py            |       25 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/domain/testcase/precondition\_checks/precondition\_checker.py                |        9 |        0 |    100% |           |
| src/domain/testcase/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/domain/testcase/testcases/abstract\_testcase.py                              |      109 |        2 |     98% |   97, 108 |
| src/domain/testcase/testcases/compare.py                                         |      132 |       22 |     83% |121, 128, 134-135, 142-144, 177-178, 194-195, 206-209, 211-219 |
| src/domain/testcase/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/domain/testcase/testcases/rowcount.py                                        |       57 |        1 |     98% |        89 |
| src/domain/testcase/testcases/schema.py                                          |      132 |        3 |     98% |99, 110, 147 |
| src/domain/testcase/testrun.py                                                   |       74 |        1 |     99% |        50 |
| src/domain/testcase/testrun\_adapter.py                                          |       21 |        0 |    100% |           |
| src/domain/testset/\_\_init\_\_.py                                               |        2 |        0 |    100% |           |
| src/domain/testset/testset.py                                                    |       16 |        0 |    100% |           |
| src/domain/testset/testset\_adapter.py                                           |       14 |        0 |    100% |           |
| src/domain\_ports/\_\_init\_\_.py                                                |        6 |        0 |    100% |           |
| src/domain\_ports/i\_domain\_config.py                                           |        7 |        0 |    100% |           |
| src/domain\_ports/i\_report.py                                                   |       19 |        0 |    100% |           |
| src/domain\_ports/i\_specification.py                                            |        6 |        0 |    100% |           |
| src/domain\_ports/i\_testrun.py                                                  |        9 |        0 |    100% |           |
| src/domain\_ports/i\_testset.py                                                  |        8 |        0 |    100% |           |
| src/drivers/\_\_init\_\_.py                                                      |        6 |        0 |    100% |           |
| src/drivers/domain\_config\_driver.py                                            |       15 |        0 |    100% |           |
| src/drivers/report\_driver.py                                                    |       31 |       10 |     68% |33-34, 38-39, 43-44, 72-77, 83-86 |
| src/drivers/specification\_driver.py                                             |        9 |        0 |    100% |           |
| src/drivers/testrun\_driver.py                                                   |       18 |        4 |     78% |25-26, 30-31 |
| src/drivers/testset\_driver.py                                                   |       21 |        4 |     81% |36-37, 41-42 |
| src/dtos/\_\_init\_\_.py                                                         |        8 |        0 |    100% |           |
| src/dtos/domain\_config\_dtos.py                                                 |       27 |        1 |     96% |        51 |
| src/dtos/dto.py                                                                  |       17 |        0 |    100% |           |
| src/dtos/report\_dtos.py                                                         |       65 |        0 |    100% |           |
| src/dtos/specification\_dtos.py                                                  |       68 |        2 |     97% |   44, 101 |
| src/dtos/storage.py                                                              |       76 |        7 |     91% |43, 56, 67, 82, 85, 91, 98 |
| src/dtos/testcase\_dtos.py                                                       |      136 |        8 |     94% |146, 149, 197-200, 206, 231, 233 |
| src/dtos/testset\_dtos.py                                                        |       34 |        1 |     97% |        24 |
| src/infrastructure/backend/\_\_init\_\_.py                                       |        4 |        0 |    100% |           |
| src/infrastructure/backend/demo/\_\_init\_\_.py                                  |        3 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_backend.py                                 |      201 |       13 |     94% |139, 163-165, 185, 313, 317, 319, 323, 327, 430, 462, 468 |
| src/infrastructure/backend/demo/demo\_backend\_factory.py                        |       17 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_naming\_resolver.py                        |       67 |        3 |     96% |28, 112, 114 |
| src/infrastructure/backend/demo/demo\_query\_handler.py                          |       19 |        1 |     95% |        29 |
| src/infrastructure/backend/dummy/\_\_init\_\_.py                                 |        3 |        0 |    100% |           |
| src/infrastructure/backend/dummy/dummy\_backend.py                               |       29 |        9 |     69% |24, 27, 37, 45, 51, 56, 66, 77, 87 |
| src/infrastructure/backend/dummy/dummy\_backend\_factory.py                      |        6 |        0 |    100% |           |
| src/infrastructure/notifier/\_\_init\_\_.py                                      |        3 |        0 |    100% |           |
| src/infrastructure/notifier/in\_memory\_notifier.py                              |        7 |        0 |    100% |           |
| src/infrastructure/notifier/stdout\_notifier.py                                  |        4 |        0 |    100% |           |
| src/infrastructure/storage/\_\_init\_\_.py                                       |        6 |        0 |    100% |           |
| src/infrastructure/storage/dto\_storage\_factory.py                              |       19 |        1 |     95% |        39 |
| src/infrastructure/storage/dto\_storage\_file.py                                 |      154 |       22 |     86% |89-90, 163-164, 179-180, 192-193, 202-203, 214-215, 235, 237, 248-249, 258-259, 262, 292-294 |
| src/infrastructure/storage/user\_storage.py                                      |       67 |       13 |     81% |47-48, 55-56, 68-69, 79-80, 89-90, 107-111 |
| src/infrastructure/storage/user\_storage\_factory.py                             |       21 |        1 |     95% |        25 |
| src/infrastructure\_ports/\_\_init\_\_.py                                        |        9 |        0 |    100% |           |
| src/infrastructure\_ports/errors.py                                              |        7 |        0 |    100% |           |
| src/infrastructure\_ports/i\_backend.py                                          |        6 |        0 |    100% |           |
| src/infrastructure\_ports/i\_backend\_factory.py                                 |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage.py                                     |        5 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage\_factory.py                            |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_notifier.py                                         |        2 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage.py                                    |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage\_factory.py                           |        4 |        0 |    100% |           |
| **TOTAL**                                                                        | **2507** |  **155** | **94%** |           |

3 empty files skipped.


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