from __future__ import annotations

from dataclasses import dataclass, field
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
    sample_size_per_object: Optional[Dict[str, int]] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, config_as_dict: Dict[str, Any]):
        specified_sample_size_per_object: Optional[Dict] = config_as_dict.get(
            "sample_size_per_object", None)
        if specified_sample_size_per_object is None:
            sample_size_per_object: dict = dict()
        elif len(specified_sample_size_per_object) == 0:
            sample_size_per_object = dict()
        else:
            sample_size_per_object = specified_sample_size_per_object

        return cls(
            sample_size=config_as_dict["sample_size"],
            sample_size_per_object=sample_size_per_object
        )


@dataclass
class DomainConfigDTO:
    """
    This serves as a generic data container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    schema_testcase_config: SchemaTestCaseConfigDTO
    compare_sample_testcase_config: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, domain_config_dict: dict) -> DomainConfigDTO:
        return cls(
            domain=domain_config_dict["domain"],
            schema_testcase_config=SchemaTestCaseConfigDTO.from_dict(
                domain_config_dict["schema_testcase_config"]),
            compare_sample_testcase_config=CompareSampleTestCaseConfigDTO.from_dict(
                domain_config_dict["compare_sample_testcase_config"]
            )
        )
