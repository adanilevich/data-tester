# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/config/\_\_init\_\_.py                                                      |        1 |        0 |    100% |           |
| src/config/config.py                                                            |        9 |        1 |     89% |         8 |
| src/domain\_config/\_\_init\_\_.py                                              |        1 |        0 |    100% |           |
| src/domain\_config/adapters/\_\_init\_\_.py                                     |        2 |        0 |    100% |           |
| src/domain\_config/adapters/yaml\_formatter.py                                  |       23 |        5 |     78% |24-26, 37-38 |
| src/domain\_config/adapters/yaml\_naming\_conventions.py                        |        6 |        0 |    100% |           |
| src/domain\_config/application/\_\_init\_\_.py                                  |        2 |        0 |    100% |           |
| src/domain\_config/application/fetch\_domain\_configs.py                        |       13 |        0 |    100% |           |
| src/domain\_config/di/\_\_init\_\_.py                                           |        1 |        0 |    100% |           |
| src/domain\_config/di/di.py                                                     |       10 |        0 |    100% |           |
| src/domain\_config/domain\_config.py                                            |       33 |        4 |     88% |57-61, 66-67 |
| src/domain\_config/drivers/\_\_init\_\_.py                                      |        1 |        0 |    100% |           |
| src/domain\_config/drivers/domain\_config\_manager.py                           |       18 |        0 |    100% |           |
| src/domain\_config/ports/\_\_init\_\_.py                                        |        5 |        0 |    100% |           |
| src/domain\_config/ports/i\_domain\_config\_formatter.py                        |       10 |        0 |    100% |           |
| src/domain\_config/ports/i\_fetch\_domain\_configs.py                           |        6 |        0 |    100% |           |
| src/domain\_config/ports/i\_naming\_conventions.py                              |        2 |        0 |    100% |           |
| src/domain\_config/ports/i\_storage.py                                          |        5 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                        |        5 |        0 |    100% |           |
| src/dtos/configs.py                                                             |       50 |        1 |     98% |        67 |
| src/dtos/dto.py                                                                 |       12 |        1 |     92% |        15 |
| src/dtos/reports.py                                                             |       32 |        0 |    100% |           |
| src/dtos/specifications.py                                                      |       40 |        2 |     95% |    25, 62 |
| src/dtos/testcase.py                                                            |       71 |        0 |    100% |           |
| src/report/\_\_init\_\_.py                                                      |        3 |        0 |    100% |           |
| src/report/abstract\_report.py                                                  |       30 |        8 |     73% |14-19, 35, 38 |
| src/report/adapters/naming\_conventions/default\_report\_naming\_conventions.py |        9 |        9 |      0% |      1-18 |
| src/report/application/\_\_init\_\_.py                                          |        3 |        3 |      0% |       2-4 |
| src/report/application/create\_testcase\_report.py                              |       12 |       12 |      0% |      1-28 |
| src/report/application/create\_testrun\_report.py                               |       12 |       12 |      0% |      1-28 |
| src/report/application/save\_report.py                                          |       15 |       15 |      0% |      1-37 |
| src/report/drivers/\_\_init\_\_.py                                              |        1 |        1 |      0% |         2 |
| src/report/drivers/simple\_report\_manager.py                                   |       19 |       19 |      0% |      1-58 |
| src/report/ports/\_\_init\_\_.py                                                |        7 |        0 |    100% |           |
| src/report/ports/i\_create\_testcase\_report.py                                 |        6 |        0 |    100% |           |
| src/report/ports/i\_create\_testrun\_report.py                                  |        6 |        0 |    100% |           |
| src/report/ports/i\_formattable.py                                              |        7 |        0 |    100% |           |
| src/report/ports/i\_report\_formatter.py                                        |        3 |        0 |    100% |           |
| src/report/ports/i\_report\_naming\_conventions.py                              |        3 |        0 |    100% |           |
| src/report/ports/i\_save\_report.py                                             |        9 |        0 |    100% |           |
| src/report/ports/i\_storage.py                                                  |        4 |        0 |    100% |           |
| src/report/testcase\_report.py                                                  |       49 |        8 |     84% |48, 110-117 |
| src/report/testrun\_report.py                                                   |       25 |        1 |     96% |        39 |
| src/storage/\_\_init\_\_.py                                                     |        1 |        0 |    100% |           |
| src/storage/file\_storage.py                                                    |       73 |       15 |     79% |73, 83, 87-89, 97, 102, 109-110, 119, 122, 129, 134-136 |
| src/testcase/adapters/data\_platforms/\_\_init\_\_.py                           |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/\_\_init\_\_.py                      |        4 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_naming\_resolver.py            |       47 |        4 |     91% |     82-85 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform.py                    |      167 |       16 |     90% |110, 127-129, 149, 255, 259, 261, 264-269, 361, 387, 391 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform\_factory.py           |       16 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_query\_handler.py              |       21 |        1 |     95% |        36 |
| src/testcase/adapters/data\_platforms/dummy/\_\_init\_\_.py                     |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform.py                  |       26 |        9 |     65% |15, 18, 26, 33, 39, 43, 49, 56, 63 |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform\_factory.py         |        6 |        0 |    100% |           |
| src/testcase/adapters/notifiers/\_\_init\_\_.py                                 |        2 |        0 |    100% |           |
| src/testcase/adapters/notifiers/in\_memory\_notifier.py                         |        7 |        0 |    100% |           |
| src/testcase/adapters/notifiers/stdout\_notifier.py                             |        4 |        0 |    100% |           |
| src/testcase/application/run\_testcases.py                                      |       20 |        0 |    100% |           |
| src/testcase/di/di.py                                                           |       23 |        3 |     87% |     26-29 |
| src/testcase/drivers/cli\_testcase\_runner.py                                   |       13 |        0 |    100% |           |
| src/testcase/ports/\_\_init\_\_.py                                              |        4 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform.py                                         |        9 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform\_factory.py                                |        4 |        0 |    100% |           |
| src/testcase/ports/i\_notifier.py                                               |        2 |        0 |    100% |           |
| src/testcase/ports/i\_run\_testcases.py                                         |       16 |        0 |    100% |           |
| src/testcase/precondition\_checks/\_\_init\_\_.py                               |       10 |        0 |    100% |           |
| src/testcase/precondition\_checks/abstract\_check.py                            |        6 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_nok.py                         |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_ok.py                          |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_primary\_keys\_are\_specified.py       |       15 |        2 |     87% |     22-23 |
| src/testcase/precondition\_checks/check\_specs\_are\_unique.py                  |       23 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_exists.py                  |       11 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_not\_empty.py              |        9 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_checkable.py                               |       11 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_precondition\_checker.py                   |        3 |        0 |    100% |           |
| src/testcase/precondition\_checks/precondition\_checker.py                      |       14 |        0 |    100% |           |
| src/testcase/testcases/\_\_init\_\_.py                                          |        8 |        0 |    100% |           |
| src/testcase/testcases/abstract\_testcase.py                                    |       99 |        0 |    100% |           |
| src/testcase/testcases/compare\_sample.py                                       |      130 |       23 |     82% |93, 100, 106-108, 113-115, 149-151, 170-172, 186-194 |
| src/testcase/testcases/dummy\_exception.py                                      |       10 |        0 |    100% |           |
| src/testcase/testcases/dummy\_nok.py                                            |       11 |        0 |    100% |           |
| src/testcase/testcases/dummy\_ok.py                                             |       11 |        0 |    100% |           |
| src/testcase/testcases/rowcount.py                                              |       56 |        1 |     98% |        70 |
| src/testcase/testcases/schema.py                                                |      132 |        3 |     98% |95, 104, 139 |
| src/testcase/testcases/testcase\_factory.py                                     |       18 |        0 |    100% |           |
|                                                                       **TOTAL** | **1637** |  **179** | **89%** |           |

11 empty files skipped.


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