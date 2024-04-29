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
        print("SDFGdfDSFGdfgdfgdfgggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggggfggggg")

        return cls(
            schema=SchemaTestCaseConfigDTO.from_dict(schema),
            compare_sample=CompareSampleTestCaseConfigDTO.from_dict(compare_sample),
        )

class DomainConfigDTO(DTO):
    """
    This serves as a generic fixtures container for business-related configurations.
    The required attributes are defined by configuration needs of implemented Testcases,
    e.g., the testcase compare_sample requires a sample size definition.
    """
    domain: str
    instances: Dict[str, List[str]]  # dict {stage: [instance1, instance2], ...}
    # Specifications can be stored in one location or several locations,
    # e.g. separated by type (sql, excel) or by layer of tested object in DWH.
    # Alternatively, they are stored on one or several locations per stage and
    # and instance - e.g. if different versions are relevant for TEST and UAT
    specifications_locations: str | List[str] | Dict[str, str] | Dict[str, List[str]]
    testmatrices_locations: str | Dict[str, str]  # testmatrix is stored in one location
    # or one location per stage and instance, e.g. as dict(stage.instace: location)
    testreports_locations: str | List[str]
    testcases: TestCasesConfigDTO
    platform_specific: Optional[Dict[str, Any]] = None

    @classmethod
    def from_dict(cls, dict_: dict) -> Self:
        return cls(
            domain=dict_["domain"],
            instances=dict_["instances"],
            specifications_locations=dict_["specifications_locations"],
            testmatrices_locations=dict_["testmatrices_locations"],
            testreports_locations=dict_["testreports_locations"],
            testcases=TestCasesConfigDTO.from_dict(dict_["testcases"]),
            platform_specific=dict_.get("platform_specific"),
        )

    def _item_as_list(self, input: str | List[str]) -> List[str]:
        if isinstance(input, str):
            return [input]
        elif isinstance(input, list):
            return input
        else:
            raise ValueError("Input must be string or list of strings.")

    def testmatrix_location_by_instance(self, stage: str, instance: str) -> str:
        """
        Returns testmatrix location relevant for given stage and instance. If only one
        global testmatrix location is defined, that is returned.
        """

        if isinstance(self.testmatrices_locations, str):
            return self.testmatrices_locations
        else:
            try:
                return self.testmatrices_locations[f"{stage}.{instance}"]
            except KeyError as err:
                msg = "Testmatrices lolcations undefined " \
                    f"for stage.instance={stage}.{instance}"
                raise KeyError(msg) from err

    def specifications_locations_by_instance(
            self, stage: str, instance: str) -> List[str]:

        if isinstance(self.specifications_locations, (str, list)):
            return self._item_as_list(self.specifications_locations)
        else:
            try:
                result = self.specifications_locations[f"{stage}.{instance}"]
                return self._item_as_list(result)
            except KeyError as err:
                msg = "Specifications locations undefined for stage.instance=" \
                    f"{stage}.{instance}"
                raise KeyError(msg) from err
