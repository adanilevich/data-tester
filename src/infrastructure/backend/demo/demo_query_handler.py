from __future__ import annotations

import re

from src.dtos import DBInstanceDTO, DomainConfigDTO


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


# Matches unqualified table names like stage_customers, core_account_payments,
# mart_customer_revenues_by_date — but not already-qualified ones (preceded by dot).
_TABLE_PATTERN = re.compile(r"(?<!\.)(?<!\w)\b((?:stage|core|mart)_\w+)\b")


class DefaultDemoTranslator:
    def __init__(self, domain_config: DomainConfigDTO):
        self.config: DomainConfigDTO = domain_config

    def translate(self, query: str, stage: str, instance: str) -> str:
        """Translate unqualified table names to fully-qualified DuckDB coordinates.

        Resolves e.g. ``stage_customers`` to ``sales_test.main.stage_customers``
        using the domain from config and the provided stage/instance.
        """
        if stage is None or instance is None:
            raise ValueError("Stage and instance must be provided")
        catalog = f"{self.config.domain}_{stage}"
        prefix = f"{catalog}.{instance}."

        def _qualify(match: re.Match[str]) -> str:
            return prefix + match.group(1)

        return _TABLE_PATTERN.sub(_qualify, query)
