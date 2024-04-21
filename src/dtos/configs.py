from typing import List, Dict, Optional, Any, Self

from src.dtos import DTO


class SchemaTestCaseConfigDTO(DTO):
    compare_datatypes: List[str]


class CompareSampleTestCaseConfigDTO(DTO):
    sample_size: int
    sample_size_per_object: Dict[str, int] = dict()


class TestCasesConfigDTO(DTO):
    schema: SchemaTestCaseConfigDTO  # type: ignore
    compare_sample: CompareSampleTestCaseConfigDTO

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        schema = dict_["schema"]
        compare_sample = dict_["compare_sample"]
        return cls(
            schema=SchemaTestCaseConfigDTO.from_dict(schema),
            compare_sample=CompareSampleTestCaseConfigDTO.from_dict(compare_sample)
        )


# TODO: specifications_locations should be a dict by stage and instance
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
    storage_location: Optional[str] = None  # location where config is (to be) stored

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        return cls(
            domain=dict_["domain"],
            instances=dict_["instances"],
            testreports_locations=dict_["testreports_locations"],
            specifications_locations=dict_["specifications_locations"],
            testcases=TestCasesConfigDTO.from_dict(dict_["testcases"]),
            platform_specific=dict_.get("platform_specific"),
            storage_location=dict_.get("storage_location"),
        )
