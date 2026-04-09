from typing import Annotated

from fastapi import Depends, Request

from src.apps.cli.di import (
    get_backend_factory,
    get_dto_storage,
    get_notifiers,
    get_user_storage,
)
from src.config import Config
from src.domain.report.plugins import (
    ITestCaseFormatter,
    ITestRunFormatter,
    TxtTestCaseReportFormatter,
    XlsxTestCaseDiffFormatter,
    XlsxTestRunReportFormatter,
)
from src.domain.specification import NamingConventionsFactory, SpecParserFactory
from src.domain_adapters import (
    DomainConfigAdapter,
    PlatformAdapter,
    ReportAdapter,
    SpecAdapter,
    TestRunAdapter,
    TestSetAdapter,
)
from src.drivers import (
    DomainConfigDriver,
    PlatformDriver,
    ReportDriver,
    SpecDriver,
    TestRunDriver,
    TestSetDriver,
)
from src.infrastructure_ports import IDtoStorage, INotifier, IUserStorage


class HttpDependencyInjector:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.dto_storage: IDtoStorage = get_dto_storage(config)
        self.user_storage: IUserStorage = get_user_storage(config)
        self.testcase_formatters: list[ITestCaseFormatter] = [
            TxtTestCaseReportFormatter(),
            XlsxTestCaseDiffFormatter(),
        ]
        self.testrun_formatters: list[ITestRunFormatter] = [
            XlsxTestRunReportFormatter(),
        ]
        self.notifiers: list[INotifier] = get_notifiers(config)
        self.backend_factory = get_backend_factory(config)
        self.spec_naming_conventions_factory = NamingConventionsFactory()
        self.spec_formatter_factory = SpecParserFactory()

    def domain_config_driver(self) -> DomainConfigDriver:
        handler = DomainConfigAdapter(dto_storage=self.dto_storage)
        return DomainConfigDriver(domain_config_adapter=handler)

    def platform_driver(self) -> PlatformDriver:
        handler = PlatformAdapter(backend_factory=self.backend_factory)
        return PlatformDriver(platform_adapter=handler)

    def testset_driver(self) -> TestSetDriver:
        handler = TestSetAdapter(dto_storage=self.dto_storage)
        return TestSetDriver(testset_adapter=handler)

    def spec_driver(self) -> SpecDriver:
        handler = SpecAdapter(
            user_storage=self.user_storage,
            naming_conventions_factory=self.spec_naming_conventions_factory,
            formatter_factory=self.spec_formatter_factory,
            notifiers=self.notifiers,
        )
        return SpecDriver(spec_adapter=handler)

    def testrun_driver(self) -> TestRunDriver:
        handler = TestRunAdapter(
            backend_factory=self.backend_factory,
            notifiers=self.notifiers,
            dto_storage=self.dto_storage,
            max_testrun_threads=self.config.DATATESTER_MAX_TESTRUN_THREADS,
        )
        return TestRunDriver(testrun_adapter=handler)

    def report_driver(self) -> ReportDriver:
        handler = ReportAdapter(
            testcase_formatters=self.testcase_formatters,
            testrun_formatters=self.testrun_formatters,
            dto_storage=self.dto_storage,
        )
        return ReportDriver(report_adapter=handler)


# --- FastAPI dependency provider functions ---


def get_domain_config_driver(request: Request) -> DomainConfigDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.domain_config_driver()


def get_testset_driver(request: Request) -> TestSetDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.testset_driver()


def get_spec_driver(request: Request) -> SpecDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.spec_driver()


def get_testrun_driver(request: Request) -> TestRunDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.testrun_driver()


def get_report_driver(request: Request) -> ReportDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.report_driver()


def get_platform_driver(request: Request) -> PlatformDriver:
    di: HttpDependencyInjector = request.app.state.di
    return di.platform_driver()


DomainConfigDriverDep = Annotated[DomainConfigDriver, Depends(get_domain_config_driver)]
PlatformDriverDep = Annotated[PlatformDriver, Depends(get_platform_driver)]
TestSetDriverDep = Annotated[TestSetDriver, Depends(get_testset_driver)]
SpecDriverDep = Annotated[SpecDriver, Depends(get_spec_driver)]
TestRunDriverDep = Annotated[TestRunDriver, Depends(get_testrun_driver)]
ReportDriverDep = Annotated[ReportDriver, Depends(get_report_driver)]
