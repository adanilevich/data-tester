from typing import List, Optional, Dict

from src.testcase.core.testcases import AbstractTestCase
from src.dtos import SchemaSpecificationDTO, TestResult, DTO, TestType


class ColumnDiffEntryDTO(DTO):
    expected_column: Optional[str] = None
    expected_dtype: Optional[str] = None
    actual_column: Optional[str] = None
    actual_dtype: Optional[str] = None
    result_column: Optional[str] = None
    result_dtype: Optional[str] = None
    result_all: Optional[str] = None


class ColumnDiffDTO(DTO):
    diffs: List[ColumnDiffEntryDTO] = []


class SchemaTestCase(AbstractTestCase):
    """
    Testcase compares specified schema vs what is actually implemented in database.
    Hereby, several comparisons take place -- depending on what is supported by db:
        - columns and datatypes are always compared
        - primary keys are compared if supported by backend (and specified)
        - partitioning columns are compared if supported by backend (and specified)
        - clustering columnsa are compared if supported by backend (and specified)
    """
    ttype = TestType.SCHEMA
    required_specs = ["schema"]
    preconditions = ["specs_are_unique", "testobject_exists"]

    def _execute(self):

        self.column_comparison_result: Optional[bool] = None
        self.partitioning_comparison_result: Optional[bool] = None
        self.clustering_comparison_result: Optional[bool] = None
        self.pk_comparison_result: Optional[bool] = None

        expected = self.schema
        actual = self._get_actual_schema()

        self.add_fact({"Specification": expected.location})

        # we start by comparing columns and datatypes
        columns_diff_dto = self._compare_columns(expected, actual)
        columns_diff_as_list = columns_diff_dto.to_dict()["diffs"]
        self.diff.update({"column_diff": columns_diff_as_list})
        self.add_detail({"Columns Comparison": str(columns_diff_as_list)})

        # next, we compare partitioning
        partitioning_diff = self._compare_partitioning(expected, actual)
        if partitioning_diff is not None:
            self.diff.update({"partitioning_diff": partitioning_diff})
            self.add_detail({"Partitioning Comparison": str(partitioning_diff)})

        # next, we compare clustering
        clustering_diff = self._compare_clustering(expected, actual)
        if clustering_diff is not None:
            self.diff.update({"clustering_diff": clustering_diff})
            self.add_detail({"Clustering Comparison": str(clustering_diff)})

        # then, primary keys are compared vs specification
        pk_diff = self._compare_primary_keys(expected, actual)
        if pk_diff is not None:
            self.diff.update({"pk_diff": pk_diff})
            self.add_detail({"Primary Keys Comparison": str(pk_diff)})

        # finally, all results are evaluated to an overall test result
        self.result = TestResult.OK
        self.summary = ""
        for result, description in [
            (self.column_comparison_result, "Column comparison"),
            (self.partitioning_comparison_result, "Partitioning comparison"),
            (self.clustering_comparison_result, "Clustering comparison"),
            (self.pk_comparison_result, "Primary key comparison"),
        ]:
            if result is True:
                self.summary += f" {description}: OK;"
            if result is False:
                self.summary += f" {description}: NOK;"
                self.result = self.result.NOK
            else:  # basically if result is None, e.g. comparison not supported
                pass

        if self.result == self.result.OK:
            self.summary = "Schema corresponds to specification:" + self.summary
        elif self.result == self.result.NOK:
            self.summary = "Schema deviates from specification:" + self.summary
        else:
            raise ValueError("Testresult is N/A, but this should not be possible.")

        return None

    @property
    def schema(self) -> SchemaSpecificationDTO:
        for spec in self.specs:
            if isinstance(spec, SchemaSpecificationDTO):
                return spec
        raise ValueError("Schema specification not found")

    def _get_actual_schema(self) -> SchemaSpecificationDTO:
        self.notify(f"Getting data object schema for testobject {self.testobject.name}")
        result_schema_raw = self.backend.get_schema(self.testobject)
        result_schema = self.backend.harmonize_schema(result_schema_raw)
        return result_schema

    def _compare_columns(
            self, expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
    ) -> ColumnDiffDTO:
        """
        Returns the comparison result as a ComnDiffDTO object and overall OK/NOK result
        as boolean
        """

        diff = ColumnDiffDTO(diffs=[])
        result = True
        compare_datatypes = self.domain_config.testcases.schema.compare_datatypes

        for expected_col, expected_dtype in expected.columns.items():
            diff_entry = ColumnDiffEntryDTO()
            diff_entry.expected_column = expected_col
            diff_entry.expected_dtype = expected_dtype
            if expected_col in actual.columns:
                diff_entry.actual_column = expected_col
                diff_entry.actual_dtype = actual.columns[expected_col]
                diff_entry.result_column = "OK"
                if diff_entry.actual_dtype == diff_entry.expected_dtype:
                    diff_entry.result_dtype = "OK"
                else:
                    # proceed only if exected dtype is configured for comparison
                    if diff_entry.expected_dtype in compare_datatypes:
                        diff_entry.result_dtype = "NOK"
            else:
                diff_entry.result_column = "NOK"

            if diff_entry.result_dtype == "NOK" or diff_entry.result_column == "NOK":
                diff_entry.result_all = "NOK"
            else:
                diff_entry.result_all = "OK"
            diff.diffs.append(diff_entry)

        for actual_col, actual_dtype in actual.columns.items():
            if actual_col in expected.columns:
                pass
            else:
                diff_entry = ColumnDiffEntryDTO()
                diff_entry.actual_column = actual_col
                diff_entry.actual_dtype = actual_dtype
                diff_entry.result_column = "NOK"
                diff_entry.result_all = "NOK"
                diff.diffs.append(diff_entry)

        # if any of the column comparison is NOK, overall result is False/NOK
        for diff_entry in diff.diffs:
            if diff_entry.result_all == "NOK":
                result = False

        self.column_comparison_result = result
        return diff

    def _compare_partitioning(
            self, expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
    ) -> Optional[Dict[str, List[str]]]:

        if self.backend.supports_partitions:
            diff = {
                "expected_partitioning": expected.partition_columns or [],
                "actual_partitioning": actual.partition_columns or [],
            }
            l1, l2 = expected.partition_columns, actual.partition_columns

            self.partitioning_comparison_result = self._compare_lists(l1, l2)
        else:
            diff = None

        return diff

    def _compare_clustering(
            self, expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
    ) -> Optional[Dict[str, List[str]]]:

        if self.backend.supports_clustering:
            diff = {
                "expected_clustering": expected.clustering_columns or [],
                "actual_clustering": actual.clustering_columns or [],
            }
            l1, l2 = expected.clustering_columns, actual.clustering_columns
            self.clustering_comparison_result = self._compare_lists(l1, l2)
        else:
            diff = None

        return diff

    def _compare_primary_keys(
            self, expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
    ) -> Optional[Dict[str, List[str]]]:

        if self.backend.supports_primary_keys:
            diff = {
                "expected_primary_keys": expected.primary_keys or [],
                "actual_primary_keys": actual.primary_keys or [],
            }
            l1, l2 = expected.primary_keys, actual.primary_keys
            self.pk_comparison_result = self._compare_lists(l1, l2)
        else:
            diff = None

        return diff

    @staticmethod
    def _compare_lists(list_1: Optional[List[str]], list_2: Optional[List[str]]) -> bool:
        l1 = list_1 or []
        l2 = list_2 or []
        if set(sorted(l1)) == set(sorted(l2)):
            return True
        else:
            return False
