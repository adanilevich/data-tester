from src.apps.cli_di import CliDependencyInjector
from src.config import Config


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
        testrun_def = spec_driver.find_specs(testset=testset, domain_config=domain_config)

        # execute testrun
        testrun_driver = self.di.testrun_driver()
        testrun = testrun_driver.execute_testrun(testrun_def)

        return testrun
