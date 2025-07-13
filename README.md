# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                           |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/config/\_\_init\_\_.py                                                     |        1 |        0 |    100% |           |
| src/config/config.py                                                           |       16 |        1 |     94% |         9 |
| src/data\_platform/\_\_init\_\_.py                                             |        2 |        0 |    100% |           |
| src/data\_platform/demo/\_\_init\_\_.py                                        |        4 |        0 |    100% |           |
| src/data\_platform/demo/demo\_naming\_resolver.py                              |       47 |        4 |     91% |     82-85 |
| src/data\_platform/demo/demo\_platform.py                                      |      167 |       16 |     90% |113, 130-132, 152, 260, 264, 266, 269-274, 366, 392, 396 |
| src/data\_platform/demo/demo\_platform\_factory.py                             |       15 |        0 |    100% |           |
| src/data\_platform/demo/demo\_query\_handler.py                                |       21 |        1 |     95% |        36 |
| src/data\_platform/dependency\_injection.py                                    |       23 |        3 |     87% |     26-29 |
| src/data\_platform/dummy/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/data\_platform/dummy/dummy\_platform.py                                    |       26 |        9 |     65% |17, 20, 29, 37, 43, 47, 53, 60, 67 |
| src/data\_platform/dummy/dummy\_platform\_factory.py                           |        6 |        0 |    100% |           |
| src/domain\_config/\_\_init\_\_.py                                             |        1 |        0 |    100% |           |
| src/domain\_config/application/\_\_init\_\_.py                                 |        2 |        0 |    100% |           |
| src/domain\_config/application/fetch\_domain\_configs.py                       |       11 |        0 |    100% |           |
| src/domain\_config/application/save\_domain\_config.py                         |        8 |        0 |    100% |           |
| src/domain\_config/core/\_\_init\_\_.py                                        |        1 |        0 |    100% |           |
| src/domain\_config/core/domain\_config.py                                      |       65 |       11 |     83% |65-67, 70-72, 80-82, 120-122 |
| src/domain\_config/dependency\_injection.py                                    |       12 |        0 |    100% |           |
| src/domain\_config/drivers/\_\_init\_\_.py                                     |        1 |        0 |    100% |           |
| src/domain\_config/drivers/cli\_domain\_config\_manager.py                     |       22 |        0 |    100% |           |
| src/domain\_config/ports/\_\_init\_\_.py                                       |        3 |        0 |    100% |           |
| src/domain\_config/ports/drivers/i\_fetch\_domain\_configs.py                  |        9 |        0 |    100% |           |
| src/domain\_config/ports/drivers/i\_save\_domain\_config.py                    |        7 |        0 |    100% |           |
| src/domain\_config/ports/infrastructure/i\_storage.py                          |        4 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                       |        5 |        0 |    100% |           |
| src/dtos/domain\_config.py                                                     |       49 |        1 |     98% |        66 |
| src/dtos/dto.py                                                                |       12 |        1 |     92% |        18 |
| src/dtos/report.py                                                             |       50 |        0 |    100% |           |
| src/dtos/specification.py                                                      |       45 |        2 |     96% |    31, 69 |
| src/dtos/testcase.py                                                           |       87 |        5 |     94% |48, 58, 105, 122, 125 |
| src/notifier/\_\_init\_\_.py                                                   |        2 |        0 |    100% |           |
| src/notifier/in\_memory\_notifier.py                                           |        7 |        0 |    100% |           |
| src/notifier/stdout\_notifier.py                                               |        4 |        0 |    100% |           |
| src/report/\_\_init\_\_.py                                                     |        1 |        0 |    100% |           |
| src/report/adapters/\_\_init\_\_.py                                            |        1 |        0 |    100% |           |
| src/report/adapters/plugins/\_\_init\_\_.py                                    |        4 |        0 |    100% |           |
| src/report/adapters/plugins/json\_report.py                                    |       43 |        6 |     86% |50-52, 87-89 |
| src/report/adapters/plugins/txt\_testcase\_report.py                           |       24 |        3 |     88% |     47-49 |
| src/report/adapters/plugins/xlsx\_testcase\_diff.py                            |       28 |        0 |    100% |           |
| src/report/adapters/plugins/xlsx\_testrun\_report.py                           |       27 |        3 |     89% |     43-45 |
| src/report/application/\_\_init\_\_.py                                         |        1 |        0 |    100% |           |
| src/report/application/handle\_reports.py                                      |      104 |        9 |     91% |87, 111, 174, 186, 200-205, 226 |
| src/report/core/\_\_init\_\_.py                                                |        1 |        0 |    100% |           |
| src/report/core/report.py                                                      |       73 |        2 |     97% |     93-94 |
| src/report/drivers/\_\_init\_\_.py                                             |        1 |        1 |      0% |         2 |
| src/report/drivers/cli\_report\_manager.py                                     |       34 |       34 |      0% |      1-75 |
| src/report/ports/\_\_init\_\_.py                                               |        3 |        0 |    100% |           |
| src/report/ports/drivers/\_\_init\_\_.py                                       |        1 |        0 |    100% |           |
| src/report/ports/drivers/i\_report\_handler.py                                 |       24 |        0 |    100% |           |
| src/report/ports/infrastructure/\_\_init\_\_.py                                |        1 |        0 |    100% |           |
| src/report/ports/infrastructure/i\_storage.py                                  |        6 |        0 |    100% |           |
| src/report/ports/plugins/\_\_init\_\_.py                                       |        1 |        0 |    100% |           |
| src/report/ports/plugins/i\_report\_formatter.py                               |        5 |        0 |    100% |           |
| src/storage/\_\_init\_\_.py                                                    |        2 |        0 |    100% |           |
| src/storage/dict\_storage.py                                                   |       30 |        7 |     77% | 36, 52-57 |
| src/storage/file\_storage.py                                                   |       80 |       20 |     75% |54, 67-72, 79-81, 89, 94, 101-102, 120-122, 137-139, 146 |
| src/testcase/application/run\_testcases.py                                     |       21 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/\_\_init\_\_.py                         |       10 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/abstract\_check.py                      |        6 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/testcase/core/precondition\_checks/check\_specs\_are\_unique.py            |       24 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/i\_checkable.py                         |       11 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/i\_precondition\_checker.py             |        3 |        0 |    100% |           |
| src/testcase/core/precondition\_checks/precondition\_checker.py                |       14 |        0 |    100% |           |
| src/testcase/core/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/testcase/core/testcases/abstract\_testcase.py                              |       97 |        0 |    100% |           |
| src/testcase/core/testcases/compare\_sample.py                                 |      130 |       23 |     82% |93, 100, 106-108, 113-115, 149-151, 170-172, 186-194 |
| src/testcase/core/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/testcase/core/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/testcase/core/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/testcase/core/testcases/rowcount.py                                        |       56 |        1 |     98% |        70 |
| src/testcase/core/testcases/schema.py                                          |      130 |        3 |     98% |92, 101, 136 |
| src/testcase/core/testcases/testcase\_factory.py                               |       19 |        0 |    100% |           |
| src/testcase/drivers/cli\_testcase\_runner.py                                  |       13 |        0 |    100% |           |
| src/testcase/ports/\_\_init\_\_.py                                             |        5 |        0 |    100% |           |
| src/testcase/ports/drivers/i\_run\_testcases.py                                |       16 |        0 |    100% |           |
| src/testcase/ports/infrastructure/data\_platform/i\_data\_platform.py          |        9 |        0 |    100% |           |
| src/testcase/ports/infrastructure/data\_platform/i\_data\_platform\_factory.py |        4 |        0 |    100% |           |
| src/testcase/ports/infrastructure/notifier/i\_notifier.py                      |        2 |        0 |    100% |           |
|                                                                      **TOTAL** | **1888** |  **168** | **91%** |           |

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