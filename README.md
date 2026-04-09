# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/apps/cli/app.py                                                             |       16 |        0 |    100% |           |
| src/apps/cli/di.py                                                              |       64 |        2 |     97% |    43, 60 |
| src/apps/cli/main\_cli.py                                                       |       13 |       13 |      0% |      7-24 |
| src/apps/http/app.py                                                            |       20 |        0 |    100% |           |
| src/apps/http/di.py                                                             |       62 |        0 |    100% |           |
| src/apps/http/main\_http.py                                                     |       30 |       30 |      0% |     10-64 |
| src/apps/http/routers/domain\_config.py                                         |       16 |        1 |     94% |        13 |
| src/apps/http/routers/platform.py                                               |       10 |        0 |    100% |           |
| src/apps/http/routers/reports.py                                                |       17 |        0 |    100% |           |
| src/apps/http/routers/specifications.py                                         |        8 |        0 |    100% |           |
| src/apps/http/routers/testcases.py                                              |       12 |        2 |     83% |     20-21 |
| src/apps/http/routers/testruns.py                                               |       23 |        1 |     96% |        19 |
| src/apps/http/routers/testsets.py                                               |       15 |        0 |    100% |           |
| src/client\_interface/\_\_init\_\_.py                                           |        1 |        0 |    100% |           |
| src/client\_interface/requests.py                                               |       11 |        1 |     91% |        27 |
| src/config/\_\_init\_\_.py                                                      |        2 |        0 |    100% |           |
| src/config/config.py                                                            |       22 |        1 |     95% |         9 |
| src/domain/\_\_init\_\_.py                                                      |        2 |        0 |    100% |           |
| src/domain/domain\_config/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/domain/domain\_config/domain\_config.py                                     |       24 |        2 |     92% |     50-51 |
| src/domain/report/\_\_init\_\_.py                                               |        3 |        0 |    100% |           |
| src/domain/report/plugins/\_\_init\_\_.py                                       |        5 |        0 |    100% |           |
| src/domain/report/plugins/i\_report\_formatter.py                               |        6 |        0 |    100% |           |
| src/domain/report/plugins/txt\_testcase\_report.py                              |       41 |        3 |     93% |     62-64 |
| src/domain/report/plugins/xlsx\_testcase\_diff.py                               |       23 |        0 |    100% |           |
| src/domain/report/plugins/xlsx\_testrun\_report.py                              |       18 |        3 |     83% |     43-45 |
| src/domain/report/report.py                                                     |       33 |        0 |    100% |           |
| src/domain/specification/\_\_init\_\_.py                                        |        2 |        0 |    100% |           |
| src/domain/specification/plugins/\_\_init\_\_.py                                |        4 |        0 |    100% |           |
| src/domain/specification/plugins/i\_naming\_conventions.py                      |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_spec\_parser.py                             |       10 |        3 |     70% |     33-35 |
| src/domain/specification/plugins/naming\_conventions.py                         |       39 |        3 |     92% | 28, 74-75 |
| src/domain/specification/plugins/spec\_parser.py                                |       75 |       12 |     84% |95-98, 123-125, 134-135, 147-149 |
| src/domain/specification/specification.py                                       |       43 |        1 |     98% |        78 |
| src/domain/testrun/\_\_init\_\_.py                                              |        1 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/\_\_init\_\_.py                         |        9 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/abstract\_check.py                      |       20 |        1 |     95% |        56 |
| src/domain/testrun/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     23-24 |
| src/domain/testrun/precondition\_checks/check\_specs\_are\_unique.py            |       25 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_specs\_not\_empty.py             |       16 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_testobject\_exists.py            |       12 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/precondition\_checker.py                |        9 |        0 |    100% |           |
| src/domain/testrun/testcases/\_\_init\_\_.py                                    |        9 |        0 |    100% |           |
| src/domain/testrun/testcases/abstract\_testcase.py                              |      139 |        1 |     99% |       127 |
| src/domain/testrun/testcases/compare.py                                         |      135 |       11 |     92% |126, 133, 217-225 |
| src/domain/testrun/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/rowcount.py                                        |       61 |        1 |     98% |        97 |
| src/domain/testrun/testcases/schema.py                                          |      133 |        3 |     98% |105, 116, 155 |
| src/domain/testrun/testcases/stagecount.py                                      |       51 |        0 |    100% |           |
| src/domain/testrun/testrun.py                                                   |       81 |        1 |     99% |        48 |
| src/domain/testset/\_\_init\_\_.py                                              |        1 |        0 |    100% |           |
| src/domain/testset/testset.py                                                   |       16 |        0 |    100% |           |
| src/domain\_adapters/\_\_init\_\_.py                                            |        7 |        0 |    100% |           |
| src/domain\_adapters/domain\_config\_adapter.py                                 |       17 |        0 |    100% |           |
| src/domain\_adapters/platform\_adapter.py                                       |       10 |        0 |    100% |           |
| src/domain\_adapters/report\_adapter.py                                         |       12 |        0 |    100% |           |
| src/domain\_adapters/specification\_adapter.py                                  |       26 |        0 |    100% |           |
| src/domain\_adapters/testrun\_adapter.py                                        |       24 |        0 |    100% |           |
| src/domain\_adapters/testset\_adapter.py                                        |       14 |        0 |    100% |           |
| src/domain\_ports/\_\_init\_\_.py                                               |        7 |        0 |    100% |           |
| src/domain\_ports/i\_domain\_config.py                                          |        7 |        0 |    100% |           |
| src/domain\_ports/i\_platform.py                                                |        5 |        0 |    100% |           |
| src/domain\_ports/i\_report.py                                                  |        6 |        0 |    100% |           |
| src/domain\_ports/i\_specification.py                                           |        5 |        0 |    100% |           |
| src/domain\_ports/i\_testrun.py                                                 |       13 |        0 |    100% |           |
| src/domain\_ports/i\_testset.py                                                 |        8 |        0 |    100% |           |
| src/drivers/\_\_init\_\_.py                                                     |        7 |        0 |    100% |           |
| src/drivers/domain\_config\_driver.py                                           |       15 |        0 |    100% |           |
| src/drivers/platform\_driver.py                                                 |        9 |        0 |    100% |           |
| src/drivers/report\_driver.py                                                   |       12 |        0 |    100% |           |
| src/drivers/specification\_driver.py                                            |        8 |        0 |    100% |           |
| src/drivers/testrun\_driver.py                                                  |       23 |        2 |     91% |     33-34 |
| src/drivers/testset\_driver.py                                                  |       24 |        0 |    100% |           |
| src/dtos/\_\_init\_\_.py                                                        |        8 |        0 |    100% |           |
| src/dtos/domain\_config\_dtos.py                                                |       14 |        0 |    100% |           |
| src/dtos/dto.py                                                                 |       16 |        0 |    100% |           |
| src/dtos/notification\_dtos.py                                                  |       22 |        0 |    100% |           |
| src/dtos/report\_dtos.py                                                        |        7 |        0 |    100% |           |
| src/dtos/specification\_dtos.py                                                 |       97 |       11 |     89% |42, 54, 63, 66-69, 72, 82, 124, 139, 142 |
| src/dtos/storage\_dtos.py                                                       |       74 |        5 |     93% |47, 71, 86, 89, 102 |
| src/dtos/testrun\_dtos.py                                                       |      131 |        2 |     98% |  114, 117 |
| src/dtos/testset\_dtos.py                                                       |       33 |        1 |     97% |        24 |
| src/infrastructure/backend/\_\_init\_\_.py                                      |        4 |        0 |    100% |           |
| src/infrastructure/backend/demo/\_\_init\_\_.py                                 |        3 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_backend.py                                |      229 |       11 |     95% |113-114, 226, 251-253, 267, 274-275, 403, 538 |
| src/infrastructure/backend/demo/demo\_backend\_factory.py                       |       16 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_naming\_resolver.py                       |       42 |        4 |     90% |58, 62, 64, 68 |
| src/infrastructure/backend/demo/demo\_query\_handler.py                         |       25 |        1 |     96% |        41 |
| src/infrastructure/demo\_latency.py                                             |       27 |        2 |     93% |     25-26 |
| src/infrastructure/notifier/\_\_init\_\_.py                                     |        3 |        0 |    100% |           |
| src/infrastructure/notifier/log\_notifier.py                                    |       24 |        0 |    100% |           |
| src/infrastructure/storage/\_\_init\_\_.py                                      |        6 |        0 |    100% |           |
| src/infrastructure/storage/dto\_storage\_factory.py                             |       19 |        1 |     95% |        40 |
| src/infrastructure/storage/dto\_storage\_file.py                                |      159 |       32 |     80% |88-89, 151-153, 158-162, 175-178, 191-192, 201-202, 213-214, 236, 238, 240, 247-248, 257-263, 266, 296-298 |
| src/infrastructure/storage/user\_storage.py                                     |       69 |       13 |     81% |49-50, 55-56, 66-67, 75-76, 83-84, 101-103 |
| src/infrastructure/storage/user\_storage\_factory.py                            |       21 |        1 |     95% |        26 |
| src/infrastructure\_ports/\_\_init\_\_.py                                       |        9 |        0 |    100% |           |
| src/infrastructure\_ports/errors.py                                             |        7 |        0 |    100% |           |
| src/infrastructure\_ports/i\_backend.py                                         |       17 |        2 |     88% |   147-148 |
| src/infrastructure\_ports/i\_backend\_factory.py                                |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage.py                                    |        5 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage\_factory.py                           |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_notifier.py                                        |        3 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage.py                                   |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage\_factory.py                          |        4 |        0 |    100% |           |
| src/ui/app.py                                                                   |        8 |        8 |      0% |      3-14 |
| src/ui/client/\_\_init\_\_.py                                                   |        1 |        1 |      0% |         2 |
| src/ui/client/client.py                                                         |       43 |       43 |      0% |      6-82 |
| src/ui/common.py                                                                |        6 |        6 |      0% |       1-8 |
| src/ui/components/\_\_init\_\_.py                                               |        2 |        2 |      0% |       2-3 |
| src/ui/components/example\_reusable.py                                          |       21 |       21 |      0% |      1-46 |
| src/ui/components/navbar.py                                                     |       24 |       24 |      0% |      3-58 |
| src/ui/components/statusbar.py                                                  |       34 |       34 |      0% |      3-71 |
| src/ui/config.py                                                                |        8 |        8 |      0% |      3-36 |
| src/ui/controller/\_\_init\_\_.py                                               |        2 |        2 |      0% |       2-3 |
| src/ui/controller/controller.py                                                 |      164 |      164 |      0% |     1-256 |
| src/ui/controller/state.py                                                      |       97 |       97 |      0% |     1-292 |
| src/ui/main\_ui.py                                                              |       14 |       14 |      0% |     30-71 |
| src/ui/pages/domain\_home.py                                                    |       12 |       12 |      0% |      3-25 |
| src/ui/pages/domain\_selection.py                                               |       29 |       29 |      0% |      7-66 |
| **TOTAL**                                                                       | **3292** |  **651** | **80%** |           |

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