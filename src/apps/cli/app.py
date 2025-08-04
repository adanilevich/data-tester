from typing import cast

from src.config import Config
from src.dtos import TestRunDTO, TestRunReportDTO
from .domain_config_di import DomainConfigDependencyInjector
from .testcase_di import TestCaseDependencyInjector
from .report_di import ReportDependencyInjector
from .specification_di import SpecDependencyInjector
from .testset_di import TestSetDependencyInjector


class CliApp:
    def __init__(self, config: Config):
        self.config = config
        self.domain_config_di = DomainConfigDependencyInjector(config)
        self.testcase_di = TestCaseDependencyInjector(config)
        self.report_di = ReportDependencyInjector(config)
        self.specification_di = SpecDependencyInjector(config)
        self.testset_di = TestSetDependencyInjector(config)

    def run_tests(self, domain: str, testset_name: str):

        # fetch domain config
        domain_config_manager = self.domain_config_di.cli_domain_config_manager()
        domain_configs = domain_config_manager.fetch_domain_configs()
        domain_config = domain_configs.get(domain)
        if domain_config is None:
            raise ValueError(f"Domain {domain} not found in domain configs")

        # fetch testset
        testset_manager = self.testset_di.cli_testset_manager()
        testset = testset_manager.load_domain_testset_by_name(
            domain=domain,
            name=testset_name
        )

        # fetch specifications
        spec_manager = self.specification_di.cli_spec_manager()
        specs = spec_manager.find_specifications(
            testset=testset,
            locations=domain_config.specifications_locations_by_instance(
                stage=testset.stage or testset.default_stage,
                instance=testset.instance or testset.default_instance
            )
        )

        # execute testrun
        testrun_manager = self.testcase_di.cli_testrun_manager()
        testrun = TestRunDTO.from_testset(
            testset=testset,
            spec_list=specs,
            domain_config=domain_config
        )
        testrun = testrun_manager.execute_testrun(testrun)

        # generate report
        report_manager = self.report_di.cli_report_manager(domain_config=domain_config)
        report = report_manager.create_report(testrun)
        report = cast(TestRunReportDTO, report)

        # update testrun with report ids and save testrun
        testrun_manager.set_report_ids(testrun=testrun, report=report)

        # save report
        report_manager.save_report_artifacts_for_users(report)
        report_manager.save_report_in_internal_storage(report)
