from typing import cast

from src.config import Config
from src.dtos import TestRunDTO, TestRunReportDTO
from src.apps.cli_di import CliDependencyInjector


class CliApp:
    def __init__(self, config: Config):
        self.config = config
        self.di = CliDependencyInjector(config)

    def run_tests(self, domain: str, testset_name: str):

        # fetch domain config
        domain_config_manager = (
            self.di.domain_config_driver()
        )
        domain_configs = (
            domain_config_manager.list_domain_configs()
        )
        domain_config = domain_configs.get(domain)
        if domain_config is None:
            raise ValueError(
                f"Domain {domain} not found in domain configs"
            )

        # fetch testset
        testset_manager = self.di.testset_driver()
        testset = testset_manager.load_domain_testset_by_name(
            domain=domain, name=testset_name
        )

        # fetch specifications
        spec_manager = self.di.specification_driver()
        specs = spec_manager.find_specifications(
            testset=testset,
            locations=domain_config.specifications_locations_by_instance(
                stage=testset.stage or testset.default_stage,
                instance=testset.instance
                or testset.default_instance,
            ),
        )

        # execute testrun
        testrun_manager = self.di.testrun_driver()
        testrun = TestRunDTO.from_testset(
            testset=testset,
            spec_list=specs,
            domain_config=domain_config,
        )
        testrun = testrun_manager.execute_testrun(testrun)

        # generate report
        report_manager = self.di.report_driver()
        report = report_manager.create_report(testrun)
        report = cast(TestRunReportDTO, report)

        # update testrun with report ids and save testrun
        testrun_manager.set_report_ids(
            testrun=testrun, report=report
        )

        # save report
        report_manager.save_report(report)
