from __future__ import annotations

from src.dtos import DTO
from typing import List, Dict, Optional, Any


class SchemaTestCaseConfigDTO(DTO):
    compare_datatypes: List[str]

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, List[str]]) -> SchemaTestCaseConfigDTO:
        return super().from_dict(config_as_dict)


class CompareSampleTestCaseConfigDTO(DTO):
    sample_size: int
    sample_size_per_object: Dict[str, int] = dict()

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]) -> CompareSampleTestCaseConfigDTO:
        return super().from_dict(config_as_dict)


class TestCasesConfigDTO(DTO):
    schema: SchemaTestCaseConfigDTO  # type: ignore
    compare_sample: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]) -> TestCasesConfigDTO:
        schema = config_as_dict["schema"]
        compare_sample = config_as_dict["compare_sample"]
        return cls(
            schema=SchemaTestCaseConfigDTO.from_dict(schema),
            compare_sample=CompareSampleTestCaseConfigDTO.from_dict(compare_sample)
        )


class DomainConfigDTO(DTO):
    """
    This serves as a generic fixtures container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    instances: Dict[str, List[str]]  # dict {stage: [instance1, instance2], ...}
    testreports_locations: List[str]
    specifications_locations: List[str]
    testcases: TestCasesConfigDTO
    platform_specific: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, config_as_dict: dict) -> DomainConfigDTO:
        return cls(
            domain=config_as_dict["domain"],
            instances=config_as_dict["instances"],
            testreports_locations=config_as_dict["testreports_locations"],
            specifications_locations=config_as_dict["specifications_locations"],
            testcases=TestCasesConfigDTO.from_dict(config_as_dict["testcases"]),
            platform_specific=config_as_dict.get("platform_specific")
        )
