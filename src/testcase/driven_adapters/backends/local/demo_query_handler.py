from __future__ import annotations

from src.testcase.dtos import DomainConfigDTO


class DemoQueryHandler:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, domain: str, project, instance: str) -> str:

        translator = self._fetch_translator(domain=domain)
        translated_query = translator.translate(query, project, instance)
        return translated_query

    def _fetch_translator(self, domain: str):
        #  include any domain-specific fetching of translators here
        if domain in ["payments", "sales"]:
            return DefaultDemoTranslator(domain_config=self.config)
        else:
            raise NotImplementedError(f"Unknown translation domain f{domain}")


class DefaultDemoTranslator:

    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, project: str, instance: str) -> str:
        if self.config:
            return query + f"\n--{project}" + f"\n--{instance}"
        else:
            return query
