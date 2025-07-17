# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                           |    Stmts |     Miss |   Cover |   Missing |
|------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/config/\_\_init\_\_.py                                                     |        1 |        0 |    100% |           |
| src/config/config.py                                                           |       22 |        1 |     95% |        10 |
| src/data\_platform/\_\_init\_\_.py                                             |        3 |        0 |    100% |           |
| src/data\_platform/demo/\_\_init\_\_.py                                        |        3 |        0 |    100% |           |
| src/data\_platform/demo/demo\_naming\_resolver.py                              |       47 |        4 |     91% |     82-85 |
| src/data\_platform/demo/demo\_platform.py                                      |      168 |       16 |     90% |115, 132-134, 154, 262, 266, 268, 271-276, 368, 394, 398 |
| src/data\_platform/demo/demo\_platform\_factory.py                             |       17 |        0 |    100% |           |
| src/data\_platform/demo/demo\_query\_handler.py                                |       21 |        1 |     95% |        36 |
| src/data\_platform/dummy/\_\_init\_\_.py                                       |        3 |        0 |    100% |           |
| src/data\_platform/dummy/dummy\_platform.py                                    |       26 |        9 |     65% |17, 20, 29, 37, 43, 47, 53, 60, 67 |
| src/data\_platform/dummy/dummy\_platform\_factory.py                           |        6 |        0 |    100% |           |
| src/domain\_config/\_\_init\_\_.py                                             |        2 |        0 |    100% |           |
| src/domain\_config/application/\_\_init\_\_.py                                 |        1 |        0 |    100% |           |
| src/domain\_config/application/domain\_config\_handler.py                      |       15 |        0 |    100% |           |
| src/domain\_config/core/\_\_init\_\_.py                                        |        1 |        0 |    100% |           |
| src/domain\_config/core/domain\_config.py                                      |       63 |       13 |     79% |52-53, 65-67, 70-72, 80-82, 117-119 |
| src/domain\_config/dependency\_injection.py                                    |       22 |        2 |     91% |    21, 27 |
| src/domain\_config/drivers/\_\_init\_\_.py                                     |        2 |        0 |    100% |           |
| src/domain\_config/drivers/cli\_domain\_config\_manager.py                     |       23 |        0 |    100% |           |
| src/domain\_config/ports/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/domain\_config/ports/drivers/\_\_init\_\_.py                               |        2 |        0 |    100% |           |
| src/domain\_config/ports/drivers/i\_domain\_config\_handler.py                 |        9 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                       |        8 |        0 |    100% |           |
| src/dtos/domain\_config.py                                                     |       35 |        1 |     97% |        52 |
| src/dtos/dto.py                                                                |       15 |        0 |    100% |           |
| src/dtos/location.py                                                           |       45 |        2 |     96% |    41, 47 |
| src/dtos/report.py                                                             |       56 |        0 |    100% |           |
| src/dtos/specification.py                                                      |       45 |        2 |     96% |    31, 69 |
| src/dtos/testcase.py                                                           |      107 |        2 |     98% |  150, 153 |
| src/dtos/testset.py                                                            |       27 |        0 |    100% |           |
| src/notifier/\_\_init\_\_.py                                                   |        3 |        0 |    100% |           |
| src/notifier/in\_memory\_notifier.py                                           |        7 |        0 |    100% |           |
| src/notifier/stdout\_notifier.py                                               |        4 |        0 |    100% |           |
| src/report/\_\_init\_\_.py                                                     |        2 |        0 |    100% |           |
| src/report/adapters/\_\_init\_\_.py                                            |        2 |        0 |    100% |           |
| src/report/adapters/plugins/\_\_init\_\_.py                                    |        4 |        0 |    100% |           |
| src/report/adapters/plugins/json\_report.py                                    |       43 |        6 |     86% |50-52, 87-89 |
| src/report/adapters/plugins/txt\_testcase\_report.py                           |       24 |        3 |     88% |     47-49 |
| src/report/adapters/plugins/xlsx\_testcase\_diff.py                            |       28 |        0 |    100% |           |
| src/report/adapters/plugins/xlsx\_testrun\_report.py                           |       27 |        3 |     89% |     44-46 |
| src/report/application/\_\_init\_\_.py                                         |        2 |        0 |    100% |           |
| src/report/application/handle\_reports.py                                      |       61 |        1 |     98% |       143 |
| src/report/core/\_\_init\_\_.py                                                |        2 |        0 |    100% |           |
| src/report/core/report.py                                                      |       78 |        2 |     97% |   105-106 |
| src/report/dependency\_injection.py                                            |       45 |        7 |     84% |36-40, 47, 51, 53 |
| src/report/drivers/\_\_init\_\_.py                                             |        2 |        0 |    100% |           |
| src/report/drivers/cli\_report\_manager.py                                     |       33 |        5 |     85% |41, 45, 49, 65, 70 |
| src/report/ports/\_\_init\_\_.py                                               |        3 |        0 |    100% |           |
| src/report/ports/drivers/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/report/ports/drivers/i\_report\_handler.py                                 |       24 |        0 |    100% |           |
| src/report/ports/plugins/\_\_init\_\_.py                                       |        1 |        0 |    100% |           |
| src/report/ports/plugins/i\_report\_formatter.py                               |        5 |        0 |    100% |           |
| src/storage/\_\_init\_\_.py                                                    |        4 |        0 |    100% |           |
| src/storage/dict\_storage.py                                                   |       28 |        0 |    100% |           |
| src/storage/file\_storage.py                                                   |       82 |        6 |     93% |48-50, 67, 100-101 |
| src/storage/i\_storage.py                                                      |        7 |        0 |    100% |           |
| src/testcase/\_\_init\_\_.py                                                   |        2 |        0 |    100% |           |
| src/testcase/application/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/testcase/application/handle\_testruns.py                                   |       34 |        0 |    100% |           |
| src/testcase/core/\_\_init\_\_.py                                              |        2 |        0 |    100% |           |
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
| src/testcase/core/testcases/abstract\_testcase.py                              |       99 |        0 |    100% |           |
| src/testcase/core/testcases/compare\_sample.py                                 |      130 |       23 |     82% |93, 100, 106-108, 113-115, 149-151, 170-172, 186-194 |
| src/testcase/core/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/testcase/core/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/testcase/core/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/testcase/core/testcases/rowcount.py                                        |       56 |        1 |     98% |        70 |
| src/testcase/core/testcases/schema.py                                          |      130 |        3 |     98% |92, 101, 136 |
| src/testcase/core/testrun/\_\_init\_\_.py                                      |        2 |        0 |    100% |           |
| src/testcase/core/testrun/testrun.py                                           |       62 |        1 |     98% |       161 |
| src/testcase/dependency\_injection.py                                          |       35 |       10 |     71% |22, 30, 35, 38-43, 49-50 |
| src/testcase/drivers/\_\_init\_\_.py                                           |        1 |        0 |    100% |           |
| src/testcase/drivers/cli\_testrun\_manager.py                                  |       18 |        3 |     83% | 21, 39-45 |
| src/testcase/ports/\_\_init\_\_.py                                             |        3 |        0 |    100% |           |
| src/testcase/ports/drivers/\_\_init\_\_.py                                     |        2 |        0 |    100% |           |
| src/testcase/ports/drivers/i\_testrun\_handler.py                              |       16 |        0 |    100% |           |
| src/testcase/ports/infrastructure/\_\_init\_\_.py                              |        3 |        0 |    100% |           |
| src/testcase/ports/infrastructure/data\_platform/\_\_init\_\_.py               |        3 |        0 |    100% |           |
| src/testcase/ports/infrastructure/data\_platform/i\_data\_platform.py          |        9 |        0 |    100% |           |
| src/testcase/ports/infrastructure/data\_platform/i\_data\_platform\_factory.py |        4 |        0 |    100% |           |
| src/testcase/ports/infrastructure/notifier/\_\_init\_\_.py                     |        2 |        0 |    100% |           |
| src/testcase/ports/infrastructure/notifier/i\_notifier.py                      |        2 |        0 |    100% |           |
| src/testset/\_\_init\_\_.py                                                    |        1 |        0 |    100% |           |
| src/testset/application/\_\_init\_\_.py                                        |        1 |        0 |    100% |           |
| src/testset/application/handle\_testsets.py                                    |       15 |        0 |    100% |           |
| src/testset/core/\_\_init\_\_.py                                               |        1 |        0 |    100% |           |
| src/testset/core/testset.py                                                    |       32 |        2 |     94% |     54-55 |
| src/testset/dependency\_injection.py                                           |       25 |        0 |    100% |           |
| src/testset/drivers/\_\_init\_\_.py                                            |        1 |        0 |    100% |           |
| src/testset/drivers/cli\_testset\_manager.py                                   |       14 |        0 |    100% |           |
| src/testset/ports/\_\_init\_\_.py                                              |        2 |        0 |    100% |           |
| src/testset/ports/drivers/\_\_init\_\_.py                                      |        2 |        0 |    100% |           |
| src/testset/ports/drivers/i\_testset\_handler.py                               |       15 |        0 |    100% |           |
|                                                                      **TOTAL** | **2200** |  **131** | **94%** |           |

2 empty files skipped.


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