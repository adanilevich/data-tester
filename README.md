# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                      |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/config/\_\_init\_\_.py                                                |        1 |        0 |    100% |           |
| src/config/config.py                                                      |       17 |        1 |     94% |        10 |
| src/domain\_config/\_\_init\_\_.py                                        |        1 |        0 |    100% |           |
| src/domain\_config/adapters/\_\_init\_\_.py                               |        2 |        0 |    100% |           |
| src/domain\_config/adapters/yaml\_formatter.py                            |       14 |        3 |     79% |     18-20 |
| src/domain\_config/adapters/yaml\_naming\_conventions.py                  |        6 |        0 |    100% |           |
| src/domain\_config/application/\_\_init\_\_.py                            |        2 |        0 |    100% |           |
| src/domain\_config/application/fetch\_domain\_configs.py                  |       13 |        0 |    100% |           |
| src/domain\_config/di/\_\_init\_\_.py                                     |        1 |        0 |    100% |           |
| src/domain\_config/di/di.py                                               |       10 |        0 |    100% |           |
| src/domain\_config/domain\_config.py                                      |       33 |        4 |     88% |53-57, 62-63 |
| src/domain\_config/drivers/\_\_init\_\_.py                                |        1 |        0 |    100% |           |
| src/domain\_config/drivers/domain\_config\_manager.py                     |       18 |        0 |    100% |           |
| src/domain\_config/ports/\_\_init\_\_.py                                  |        5 |        0 |    100% |           |
| src/domain\_config/ports/i\_domain\_config\_formatter.py                  |        3 |        0 |    100% |           |
| src/domain\_config/ports/i\_fetch\_domain\_configs.py                     |        6 |        0 |    100% |           |
| src/domain\_config/ports/i\_naming\_conventions.py                        |        2 |        0 |    100% |           |
| src/domain\_config/ports/i\_storage.py                                    |        5 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                  |        5 |        0 |    100% |           |
| src/dtos/configs.py                                                       |       50 |        1 |     98% |        67 |
| src/dtos/dto.py                                                           |       12 |        0 |    100% |           |
| src/dtos/reports.py                                                       |       57 |        2 |     96% |   76, 106 |
| src/dtos/specifications.py                                                |       40 |        2 |     95% |    25, 60 |
| src/dtos/testcase.py                                                      |       87 |        5 |     94% |48, 58, 105, 122, 125 |
| src/report/\_\_init\_\_.py                                                |        3 |        0 |    100% |           |
| src/report/application/\_\_init\_\_.py                                    |        3 |        3 |      0% |       2-4 |
| src/report/application/create\_testcase\_report.py                        |       10 |       10 |      0% |      1-24 |
| src/report/application/create\_testrun\_report.py                         |       10 |       10 |      0% |      1-24 |
| src/report/application/save\_report.py                                    |        7 |        7 |      0% |      1-13 |
| src/report/drivers/\_\_init\_\_.py                                        |        1 |        1 |      0% |         2 |
| src/report/drivers/cli\_report\_manager.py                                |       30 |       30 |      0% |      1-80 |
| src/report/plugins/\_\_init\_\_.py                                        |        1 |        0 |    100% |           |
| src/report/plugins/formatters/\_\_init\_\_.py                             |        1 |        0 |    100% |           |
| src/report/plugins/formatters/default/\_\_init\_\_.py                     |        8 |        0 |    100% |           |
| src/report/plugins/formatters/default/default\_formatter.py               |       33 |        1 |     97% |        92 |
| src/report/plugins/formatters/default/default\_naming\_conventions.py     |       23 |        7 |     70% |20, 35-38, 43-46 |
| src/report/plugins/formatters/default/i\_report\_artifact.py              |       16 |        0 |    100% |           |
| src/report/plugins/formatters/default/i\_report\_naming\_conventions.py   |        3 |        0 |    100% |           |
| src/report/plugins/formatters/default/json\_testcase\_report.py           |       15 |        1 |     93% |        26 |
| src/report/plugins/formatters/default/txt\_testcase\_report.py            |       16 |        1 |     94% |        27 |
| src/report/plugins/formatters/default/xlsx\_testcase\_diff.py             |       27 |       18 |     33% |     30-66 |
| src/report/plugins/formatters/default/xlsx\_testrun\_report.py            |       20 |       11 |     45% |     26-60 |
| src/report/ports/\_\_init\_\_.py                                          |        3 |        0 |    100% |           |
| src/report/ports/drivers/\_\_init\_\_.py                                  |        3 |        0 |    100% |           |
| src/report/ports/drivers/i\_create\_testcase\_report.py                   |        7 |        0 |    100% |           |
| src/report/ports/drivers/i\_create\_testrun\_report.py                    |        7 |        0 |    100% |           |
| src/report/ports/drivers/i\_save\_report.py                               |        8 |        0 |    100% |           |
| src/report/ports/infrastructure/\_\_init\_\_.py                           |        1 |        0 |    100% |           |
| src/report/ports/infrastructure/i\_storage.py                             |        3 |        0 |    100% |           |
| src/report/ports/plugins/\_\_init\_\_.py                                  |        1 |        0 |    100% |           |
| src/report/ports/plugins/i\_report\_formatter.py                          |        5 |        0 |    100% |           |
| src/report/report.py                                                      |       34 |        4 |     88% | 63, 68-71 |
| src/report/testcase\_report.py                                            |        9 |        0 |    100% |           |
| src/report/testrun\_report.py                                             |        9 |        0 |    100% |           |
| src/storage/\_\_init\_\_.py                                               |        1 |        0 |    100% |           |
| src/storage/file\_storage.py                                              |       74 |       18 |     76% |61-66, 73-75, 83, 88, 95-96, 114-116, 131-133 |
| src/testcase/adapters/data\_platforms/\_\_init\_\_.py                     |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/\_\_init\_\_.py                |        4 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_naming\_resolver.py      |       47 |        4 |     91% |     82-85 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform.py              |      167 |       16 |     90% |110, 127-129, 149, 255, 259, 261, 264-269, 361, 387, 391 |
| src/testcase/adapters/data\_platforms/demo/demo\_platform\_factory.py     |       16 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/demo/demo\_query\_handler.py        |       21 |        1 |     95% |        36 |
| src/testcase/adapters/data\_platforms/dummy/\_\_init\_\_.py               |        2 |        0 |    100% |           |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform.py            |       26 |        9 |     65% |15, 18, 26, 33, 39, 43, 49, 56, 63 |
| src/testcase/adapters/data\_platforms/dummy/dummy\_platform\_factory.py   |        6 |        0 |    100% |           |
| src/testcase/adapters/notifiers/\_\_init\_\_.py                           |        2 |        0 |    100% |           |
| src/testcase/adapters/notifiers/in\_memory\_notifier.py                   |        7 |        0 |    100% |           |
| src/testcase/adapters/notifiers/stdout\_notifier.py                       |        4 |        0 |    100% |           |
| src/testcase/application/run\_testcases.py                                |       21 |        0 |    100% |           |
| src/testcase/di/di.py                                                     |       23 |        3 |     87% |     26-29 |
| src/testcase/drivers/cli\_testcase\_runner.py                             |       13 |        0 |    100% |           |
| src/testcase/ports/\_\_init\_\_.py                                        |        4 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform.py                                   |        9 |        0 |    100% |           |
| src/testcase/ports/i\_data\_platform\_factory.py                          |        4 |        0 |    100% |           |
| src/testcase/ports/i\_notifier.py                                         |        2 |        0 |    100% |           |
| src/testcase/ports/i\_run\_testcases.py                                   |       16 |        0 |    100% |           |
| src/testcase/precondition\_checks/\_\_init\_\_.py                         |       10 |        0 |    100% |           |
| src/testcase/precondition\_checks/abstract\_check.py                      |        6 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/testcase/precondition\_checks/check\_specs\_are\_unique.py            |       23 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/testcase/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_checkable.py                         |       11 |        0 |    100% |           |
| src/testcase/precondition\_checks/i\_precondition\_checker.py             |        3 |        0 |    100% |           |
| src/testcase/precondition\_checks/precondition\_checker.py                |       14 |        0 |    100% |           |
| src/testcase/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/testcase/testcases/abstract\_testcase.py                              |       97 |        0 |    100% |           |
| src/testcase/testcases/compare\_sample.py                                 |      130 |       23 |     82% |93, 100, 106-108, 113-115, 149-151, 170-172, 186-194 |
| src/testcase/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/testcase/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/testcase/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/testcase/testcases/rowcount.py                                        |       56 |        1 |     98% |        70 |
| src/testcase/testcases/schema.py                                          |      130 |        3 |     98% |92, 101, 136 |
| src/testcase/testcases/testcase\_factory.py                               |       19 |        0 |    100% |           |
|                                                                 **TOTAL** | **1764** |  **202** | **89%** |           |

8 empty files skipped.


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