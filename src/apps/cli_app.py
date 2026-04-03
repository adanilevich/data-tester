from src.config import Config
from src.dtos import TestRunDTO
from src.apps.cli_di import CliDependencyInjector


class CliApp:
    def __init__(self, config: Config):
        self.config = config
        self.di = CliDependencyInjector(config)

    def run_tests(self, domain: str, testset_name: str):
        # fetch domain config
        domain_config_driver = self.di.domain_config_driver()
        domain_config = domain_config_driver.load_domain_config(domain=domain)

        # fetch testset
        testset_driver = self.di.testset_driver()
        testset = testset_driver.load_domain_testset_by_name(
            domain=domain, name=testset_name
        )

        # fetch specifications
        spec_driver = self.di.specification_driver()
        specs = spec_driver.find_specifications(
            testset=testset,
            locations=domain_config.specifications_locations_by_instance(
                stage=testset.stage or testset.default_stage,
                instance=testset.instance or testset.default_instance,
            ),
        )

        # execute testrun
        testrun_driver = self.di.testrun_driver()
        testrun = TestRunDTO.from_testset(
            testset=testset,
            spec_list=specs,
            domain_config=domain_config,
        )
        testrun = testrun_driver.execute_testrun(testrun)

        # generate and save all reports
        report_driver = self.di.report_driver()
        report_driver.create_and_save_all_reports(testrun)
