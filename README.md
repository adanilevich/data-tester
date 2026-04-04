# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/adanilevich/data-tester/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                                            |    Stmts |     Miss |   Cover |   Missing |
|-------------------------------------------------------------------------------- | -------: | -------: | ------: | --------: |
| src/apps/cli\_app.py                                                            |       19 |        0 |    100% |           |
| src/apps/cli\_di.py                                                             |       63 |        2 |     97% |    42, 59 |
| src/config/\_\_init\_\_.py                                                      |        2 |        0 |    100% |           |
| src/config/config.py                                                            |       18 |        1 |     94% |         9 |
| src/domain/\_\_init\_\_.py                                                      |        2 |        0 |    100% |           |
| src/domain/domain\_config/\_\_init\_\_.py                                       |        2 |        0 |    100% |           |
| src/domain/domain\_config/domain\_config.py                                     |       24 |        2 |     92% |     50-51 |
| src/domain/report/\_\_init\_\_.py                                               |        3 |        0 |    100% |           |
| src/domain/report/plugins/\_\_init\_\_.py                                       |        5 |        0 |    100% |           |
| src/domain/report/plugins/i\_report\_formatter.py                               |        5 |        0 |    100% |           |
| src/domain/report/plugins/txt\_testcase\_report.py                              |       42 |        3 |     93% |     69-71 |
| src/domain/report/plugins/xlsx\_testcase\_diff.py                               |       28 |        0 |    100% |           |
| src/domain/report/plugins/xlsx\_testrun\_report.py                              |       32 |        4 |     88% | 58, 63-65 |
| src/domain/report/report.py                                                     |       83 |        7 |     92% |99, 108, 122, 124, 137, 163, 169 |
| src/domain/specification/\_\_init\_\_.py                                        |        2 |        0 |    100% |           |
| src/domain/specification/plugins/\_\_init\_\_.py                                |        4 |        0 |    100% |           |
| src/domain/specification/plugins/i\_naming\_conventions.py                      |        5 |        0 |    100% |           |
| src/domain/specification/plugins/i\_spec\_parser.py                             |       10 |        0 |    100% |           |
| src/domain/specification/plugins/naming\_conventions.py                         |       35 |        3 |     91% | 27, 65-66 |
| src/domain/specification/plugins/spec\_parser.py                                |       59 |        9 |     85% |89-92, 116-118, 127-128 |
| src/domain/specification/specification.py                                       |       44 |        1 |     98% |        78 |
| src/domain/testrun/\_\_init\_\_.py                                              |        1 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/\_\_init\_\_.py                         |        9 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/abstract\_check.py                      |       20 |        1 |     95% |        57 |
| src/domain/testrun/precondition\_checks/check\_always\_nok.py                   |        5 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_always\_ok.py                    |        5 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_primary\_keys\_are\_specified.py |       15 |        2 |     87% |     22-23 |
| src/domain/testrun/precondition\_checks/check\_specs\_are\_unique.py            |       25 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_specs\_not\_empty.py             |       16 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_testobject\_exists.py            |       11 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/check\_testobject\_not\_empty.py        |        9 |        0 |    100% |           |
| src/domain/testrun/precondition\_checks/precondition\_checker.py                |        9 |        0 |    100% |           |
| src/domain/testrun/testcases/\_\_init\_\_.py                                    |        8 |        0 |    100% |           |
| src/domain/testrun/testcases/abstract\_testcase.py                              |      110 |        2 |     98% |  108, 119 |
| src/domain/testrun/testcases/compare.py                                         |      136 |       11 |     92% |125, 132, 216-224 |
| src/domain/testrun/testcases/dummy\_exception.py                                |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/dummy\_nok.py                                      |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/dummy\_ok.py                                       |       11 |        0 |    100% |           |
| src/domain/testrun/testcases/rowcount.py                                        |       61 |        1 |     98% |        94 |
| src/domain/testrun/testcases/schema.py                                          |      133 |        3 |     98% |101, 112, 151 |
| src/domain/testrun/testrun.py                                                   |       83 |        1 |     99% |        53 |
| src/domain/testset/\_\_init\_\_.py                                              |        1 |        0 |    100% |           |
| src/domain/testset/testset.py                                                   |       16 |        0 |    100% |           |
| src/domain\_adapters/\_\_init\_\_.py                                            |        6 |        0 |    100% |           |
| src/domain\_adapters/domain\_config\_adapter.py                                 |       17 |        0 |    100% |           |
| src/domain\_adapters/report\_adapter.py                                         |       35 |        0 |    100% |           |
| src/domain\_adapters/specification\_adapter.py                                  |       22 |        0 |    100% |           |
| src/domain\_adapters/testrun\_adapter.py                                        |       21 |        0 |    100% |           |
| src/domain\_adapters/testset\_adapter.py                                        |       14 |        0 |    100% |           |
| src/domain\_ports/\_\_init\_\_.py                                               |        6 |        0 |    100% |           |
| src/domain\_ports/i\_domain\_config.py                                          |        7 |        0 |    100% |           |
| src/domain\_ports/i\_report.py                                                  |       19 |        0 |    100% |           |
| src/domain\_ports/i\_specification.py                                           |        5 |        0 |    100% |           |
| src/domain\_ports/i\_testrun.py                                                 |        9 |        0 |    100% |           |
| src/domain\_ports/i\_testset.py                                                 |        8 |        0 |    100% |           |
| src/drivers/\_\_init\_\_.py                                                     |        6 |        0 |    100% |           |
| src/drivers/domain\_config\_driver.py                                           |       15 |        0 |    100% |           |
| src/drivers/report\_driver.py                                                   |       37 |       14 |     62% |35-36, 40-41, 45-46, 50-51, 55-56, 84-89, 95-98 |
| src/drivers/specification\_driver.py                                            |        9 |        0 |    100% |           |
| src/drivers/testrun\_driver.py                                                  |       18 |        4 |     78% |25-26, 30-31 |
| src/drivers/testset\_driver.py                                                  |       21 |        4 |     81% |36-37, 41-42 |
| src/dtos/\_\_init\_\_.py                                                        |        9 |        0 |    100% |           |
| src/dtos/domain\_config\_dtos.py                                                |       27 |        1 |     96% |        51 |
| src/dtos/dto.py                                                                 |       17 |        0 |    100% |           |
| src/dtos/notification\_dtos.py                                                  |       22 |        0 |    100% |           |
| src/dtos/report\_dtos.py                                                        |       65 |        0 |    100% |           |
| src/dtos/specification\_dtos.py                                                 |       73 |        4 |     95% |38, 50, 96, 107 |
| src/dtos/storage\_dtos.py                                                       |       79 |        5 |     94% |47, 71, 86, 89, 102 |
| src/dtos/testrun\_dtos.py                                                       |      136 |        8 |     94% |146, 149, 197-200, 206, 231, 233 |
| src/dtos/testset\_dtos.py                                                       |       34 |        1 |     97% |        25 |
| src/infrastructure/backend/\_\_init\_\_.py                                      |        4 |        0 |    100% |           |
| src/infrastructure/backend/demo/\_\_init\_\_.py                                 |        3 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_backend.py                                |      203 |       14 |     93% |93, 153, 177-179, 196, 317, 321, 323, 327, 331, 434, 463, 469 |
| src/infrastructure/backend/demo/demo\_backend\_factory.py                       |       17 |        0 |    100% |           |
| src/infrastructure/backend/demo/demo\_naming\_resolver.py                       |       67 |        3 |     96% |28, 112, 114 |
| src/infrastructure/backend/demo/demo\_query\_handler.py                         |       19 |        1 |     95% |        29 |
| src/infrastructure/notifier/\_\_init\_\_.py                                     |        3 |        0 |    100% |           |
| src/infrastructure/notifier/log\_notifier.py                                    |       24 |        0 |    100% |           |
| src/infrastructure/storage/\_\_init\_\_.py                                      |        6 |        0 |    100% |           |
| src/infrastructure/storage/dto\_storage\_factory.py                             |       19 |        1 |     95% |        39 |
| src/infrastructure/storage/dto\_storage\_file.py                                |      173 |       37 |     79% |90-91, 153-155, 162-164, 171-173, 177-181, 196-199, 211-212, 221-222, 233-234, 254, 256, 267-268, 277-281, 284, 314-316 |
| src/infrastructure/storage/user\_storage.py                                     |       67 |       13 |     81% |47-48, 53-54, 64-65, 73-74, 81-82, 99-101 |
| src/infrastructure/storage/user\_storage\_factory.py                            |       21 |        1 |     95% |        25 |
| src/infrastructure\_ports/\_\_init\_\_.py                                       |        9 |        0 |    100% |           |
| src/infrastructure\_ports/errors.py                                             |        7 |        0 |    100% |           |
| src/infrastructure\_ports/i\_backend.py                                         |        6 |        0 |    100% |           |
| src/infrastructure\_ports/i\_backend\_factory.py                                |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage.py                                    |        5 |        0 |    100% |           |
| src/infrastructure\_ports/i\_dto\_storage\_factory.py                           |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_notifier.py                                        |        3 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage.py                                   |        4 |        0 |    100% |           |
| src/infrastructure\_ports/i\_user\_storage\_factory.py                          |        4 |        0 |    100% |           |
| **TOTAL**                                                                       | **2602** |  **164** | **94%** |           |

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