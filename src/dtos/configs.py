from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Optional, Any


@dataclass
class SchemaTestCaseConfigDTO:
    compare_datatypes: List[str]

    @classmethod
    def from_dict(cls, config_as_dicf: Dict[str, List[str]]):
        return cls(compare_datatypes=config_as_dicf["compare_data_types"])


@dataclass
class CompareSampleTestCaseConfigDTO:
    sample_size: int
    sample_size_per_object: Dict[str, int]

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]) -> CompareSampleTestCaseConfigDTO:
        sample_size_per_object = config_as_dict.get(
            "sample_size_per_object", dict())
        return cls(
            sample_size=config_as_dict["sample_size"],
            sample_size_per_object=sample_size_per_object
        )


@dataclass
class TestCasesConfigDTO:
    schema: SchemaTestCaseConfigDTO
    compare_sample: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]) -> TestCasesConfigDTO:
        return cls(
            schema=config_as_dict["schema"],
            compare_sample=config_as_dict["compare_sample"]
        )


@dataclass
class DomainConfigDTO:
    """
    This serves as a generic data container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    instances: Dict[str, List[str]]  # stage: [instance1, instance2]
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
