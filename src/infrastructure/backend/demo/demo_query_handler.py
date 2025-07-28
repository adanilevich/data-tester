from __future__ import annotations

from src.dtos import DomainConfigDTO, DBInstanceDTO


class DemoQueryHandler:
    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, db: DBInstanceDTO) -> str:
        translator = self._fetch_translator(domain=db.domain)
        translated_query = translator.translate(query, db.stage, db.instance)
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

    def translate(self, query: str, stage: str, instance: str) -> str:
        assert stage is not None
        assert instance is not None
        if self.config:
            return query
        else:
            return query
