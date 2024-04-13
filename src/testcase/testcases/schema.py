from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, asdict, field

from src.testcase.testcases import AbstractTestCase
from src.dtos.specifications import SchemaSpecificationDTO


@dataclass
class ColumnDiffEntryDTO:
    expected_column: Optional[str] = None
    expected_dtype: Optional[str] = None
    actual_column: Optional[str] = None
    actual_dtype: Optional[str] = None
    result_column: Optional[str] = None
    result_dtype: Optional[str] = None
    result_all: Optional[str] = None


@dataclass
class ColumnDiffDTO:
    diffs: List[ColumnDiffEntryDTO] = field(default_factory=lambda: [])

    def dict(self) -> Dict[str, List[Dict[str, str]]]:
        return {"diffs": [asdict(diff_entry) for diff_entry in self.diffs]}


class SchemaTestCase(AbstractTestCase):
    """
    Testcase compares specified schema vs what is actually implemented in database.
    Hereby, several comparisons take place -- depending on what is supported by db:
        - columns and datatypes are always compared
        - primary keys are compared if supported by backend (and specified)
        - partitioning columns are compared if supported by backend (and specified)
        - clustering columnsa are compared if supported by backend (and specified)
    """
    ttype = "SCHEMA"
    required_specs = ["schema"]
    preconditions = ["testobject_exists"]

    def _execute(self):

        actual_schema: SchemaSpecificationDTO = self._get_actual_schema()
        expected_schema: SchemaSpecificationDTO = self._get_expected_schema()
        if expected_schema is None:
            self.status = self.status.ABORTED
            self.result = self.result.NA
            return None
        else:
            self.add_fact({"Specification": expected_schema.location})

        # we start by comparing columns and datatypes
        columns_diff_dto, column_comparison_result = self._compare_columns(
            expected=expected_schema,
            actual=actual_schema,
            compare_datatypes=self.domain_config.schema_testcase_config.compare_datatypes
        )
        columns_diff_as_list = columns_diff_dto.dict()["diffs"]
        self.diff.update({"column_diff": columns_diff_as_list})
        self.add_detail({"Columns Comparison": str(columns_diff_as_list)})

        # next, we compare partitioning
        if self.backend.supports_partitions:
            partitioning_diff, partitioning_comparison_result = self._compare(
                expected=expected_schema,
                actual=actual_schema,
                compare_what="partitioning"
            )
            self.diff.update({"partitioning_diff": partitioning_diff})
            self.add_detail({"Partitioning Comparison": str(partitioning_diff)})
        else:
            partitioning_comparison_result = None

        # next, we compare clustering
        if self.backend.supports_clustering:
            clustering_diff, clustering_comparison_result = self._compare(
                expected=expected_schema,
                actual=actual_schema,
                compare_what="clustering"
            )
            self.diff.update({"clustering_diff": clustering_diff})
            self.add_detail({"Clustering Comparison": str(clustering_diff)})
        else:
            clustering_comparison_result = None

        # then, primary keys are compared vs specification
        if self.backend.supports_primary_keys:
            pk_diff, pk_comparison_result = self._compare(
                expected=expected_schema,
                actual=actual_schema,
                compare_what="primary_keys"
            )
            self.diff.update({"pk_diff": pk_diff})
            self.add_detail({"Primary Keys Comparison": str(pk_diff)})
        else:
            pk_comparison_result = None

        # finally, all results are evaluated to an overall test result
        self.result = self.result.OK
        self.summary = ""
        for result, name in [
            (column_comparison_result, "Column comparison"),
            (partitioning_comparison_result, "Partitioning comparison"),
            (clustering_comparison_result, "Clustering comparison"),
            (pk_comparison_result, "Primary key comparison"),
        ]:
            if result is True:
                self.summary += f" {name}: OK;"
            if result is False:
                self.summary += f" {name}: NOK;"
                self.result = self.result.NOK
            else:  # basically if result is None
                pass  # do not write anythnig to summary if comparison not supported

        if self.result == self.result.OK:
            self.summary = "Schema corresponds to specification:" + self.summary
        elif self.result == self.result.NOK:
            self.summary = "Schema deviates from specification:" + self.summary
        else:
            raise ValueError("Testresult is N/A, but this should not be possible.")

        return None

    def _get_actual_schema(self) -> SchemaSpecificationDTO:
        self.notify(f"Getting data object schema for testobject {self.testobject.name}")
        result_schema_raw = self.backend.get_schema(
            domain=self.testobject.domain,
            project=self.testobject.project,
            instance=self.testobject.instance,
            testobject=self.testobject.name
        )
        result_schema = self.backend.harmonize_schema(result_schema_raw)
        return result_schema

    def _get_expected_schema(self) -> Optional[SchemaSpecificationDTO]:
        """Gets expected schema specification from provided specs"""
        self.notify(f"Getting expected schema for testobject {self.testobject.name}")
        # unpack expected schema from provided specifications
        provided_schema_specs: List[SchemaSpecificationDTO] = []
        expected_schema: Optional[SchemaSpecificationDTO] = None
        for spec in self.specs:
            if isinstance(spec, SchemaSpecificationDTO):
                expected_schema = spec
                provided_schema_specs.append(expected_schema)

        # if more than one schema spec is provided, abort execution.
        # But: we don't check for 'no specs provided' since this is done by precon checks
        if len(provided_schema_specs) > 1:
            msg = "Testcase stopped: more than one schema spec provided!"
            self.update_summary(msg)
            self.add_detail({"Provided schema specs": str(provided_schema_specs)})
            self.notify(msg)
            return None
        else:
            return expected_schema

    @staticmethod
    def _compare_columns(expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
                         compare_datatypes: List[str]) -> Tuple[ColumnDiffDTO, bool]:
        """
        Returns the comparison result as a ComnDiffDTO object and overall OK/NOK result
        as boolean
        """

        diff = ColumnDiffDTO(diffs=[])
        result = True

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

        return diff, result

    @classmethod
    def _compare(cls, expected: SchemaSpecificationDTO, actual: SchemaSpecificationDTO,
                 compare_what: str) -> Tuple[Dict[str, List[str]], bool]:
        """
        Compares aspects between specified schema and actual schema.

        Args:
            expected: expected/specified schema object
            actual: actual schema_object
            compare_what: defines what to be compared. One of "partitioning",
                "clustering", "primary_keys"

        Returns:
            diff: Dict with "expected_..." and "actual_..." as keys, and lists as
                attributes, e.g. list of expected_primary_keys with column names
        """

        if compare_what == "partitioning":
            diff = {
                "expected_partitioning": expected.partition_columns or [],
                "actual_partitioning": actual.partition_columns or [],
            }
            l1, l2 = expected.partition_columns, actual.partition_columns
        elif compare_what == "clustering":
            diff = {
                "expected_clustering": expected.clustering_columns or [],
                "actual_clustering": actual.clustering_columns or [],
            }
            l1, l2 = expected.clustering_columns, actual.clustering_columns
        elif compare_what == "primary_keys":
            diff = {
                "expected_primary_keys": expected.primary_keys or [],
                "actual_primary_keys": actual.primary_keys or [],
            }
            l1, l2 = expected.primary_keys, actual.primary_keys
        else:
            raise ValueError(f"Comparison aspect {compare_what} unknown!")

        comparison_result = cls._compare_lists(l1, l2)

        return diff, comparison_result

    @staticmethod
    def _compare_lists(list_1: Optional[List[str]], list_2: Optional[List[str]]) -> bool:
        l1 = list_1 or []
        l2 = list_2 or []
        if set(sorted(l1)) == set(sorted(l2)):
            return True
        else:
            return False
