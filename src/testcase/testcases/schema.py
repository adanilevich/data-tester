from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass, asdict, field

from src.testcase.testcases.abstract_testcase import AbstractTestCase
from src.testcase.driven_ports.i_backend import SchemaDTO


@dataclass
class ColumnDiffEntryDTO:
    expected_col: Optional[str] = None
    expected_dtype: Optional[str] = None
    actual_col: Optional[str] = None
    actual_dtype: Optional[str] = None
    result_col: Optional[str] = None
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

        actual_schema: SchemaDTO = self._get_actual_schema()
        expected_schema: SchemaDTO = self._get_expected_schema()
        if expected_schema is None:
            self.status = self.status.ABORTED
            self.result = self.result.NA
            return None

        # we start by comparing columns and datatypes
        column_diff_dto: ColumnDiffDTO
        column_comparison_result: bool

        column_diff_dto, column_comparison_result = self._compare_columns(
            expected_schema, actual_schema)
        column_diffs: List[Dict[str, str]] = column_diff_dto.dict()["diffs"]
        self.diff.update({"column_diff": column_diffs})
        if column_comparison_result is not True:
            self.add_detail({"Columns diff": str(column_diffs)})

        # next, we compare partitioning
        partitioning_comparison_result: Optional[bool]  # default OK for later evaluation
        if self.backend.supports_partitions:
            partitioning_diff, partitioning_comparison_result = self._compare_partitions(
                expected_schema, actual_schema
            )
            self.diff.update({"partitioning_diff": partitioning_diff})
            if partitioning_comparison_result is not True:
                self.add_detail({"Partitioning diff": str(partitioning_diff)})
        else:
            partitioning_comparison_result = None

        # next, we compare clustering
        if self.backend.supports_clustering:
            clustering_diff, clustering_comparison_result = self._compare_clustering(
                expected_schema, actual_schema
            )
            self.diff.update({"clustering_diff": clustering_diff})
            if column_comparison_result is not True:
                self.add_detail({"Clustering diff": str(clustering_diff)})
        else:
            clustering_comparison_result = None

        # then, primary keys are compared vs specification
        if self.backend.supports_primary_keys:
            pk_diff, pk_comparison_result = self._compare_primary_keys(
                expected_schema, actual_schema
            )
            self.diff.update({"pk_diff": pk_diff})
            if pk_comparison_result is not True:
                self.add_detail({"Clustering diff": str(pk_diff)})
        else:
            pk_comparison_result = None

        # finally, all results are evaluated to an overall test result
        self.result = self.result.OK
        for result, name in [
            (column_comparison_result, "Column comparison"),
            (partitioning_comparison_result, "Partitioning comparison"),
            (clustering_comparison_result, "Clustering comparison"),
            (pk_comparison_result, "Primary key comparison"),
        ]:
            if result is True:
                self.summary += f"{name}: OK; "
            if result is None:
                pass  # do not write anythnig to summary if comarison not supported
            else:
                self.summary += f"{name}: OK; "
                self.result = self.result.NOK

        if self.result == self.result.OK:
            self.summary = "Testobject schema corresponds to specification: "
        elif self.result == self.result.NOK:
            self.summary = "Testobject schema does NOT correspond to specification. "
        else:
            raise ValueError("Testresult is N/A, but this should not be possible.")

        return None

    def _get_actual_schema(self) -> SchemaDTO:
        self.notify(f"Getting data object schema for {self.testobject.name}")
        result_schema_raw = self.backend.get_schema(
            domain=self.testobject.domain,
            project=self.testobject.project,
            instance=self.testobject.instance,
            testobject=self.testobject.name
        )
        result_schema = self.backend.harmonize_schema(result_schema_raw)
        return result_schema

    def _get_expected_schema(self) -> Optional[SchemaDTO]:
        self.notify(f"Getting expected schema for {self.testobject.name}")
        # unpack expected schema from provided specifications
        provided_schema_specs: List[SchemaDTO] = []
        expected_schema: Optional[SchemaDTO] = None  # will hold the specified schema
        for spec in self.specs:
            if spec.type == "schema":
                # TODO: rework this later when spec datatypes are adapted
                if isinstance(spec.content, dict):
                    expected_schema = SchemaDTO(columns=spec.content)
                    provided_schema_specs.append(expected_schema)

        # if more than one schema spec is provided, abort execution.
        # But: we don't check for 'no specs provided' since this is done by precon checks
        if len(provided_schema_specs) > 1:
            msg = "Testcase stopped: more than one schema spec provided!"
            self.update_summary(msg)
            self.add_detail({"Provided schema specs": str(provided_schema_specs)})
            self.notify(msg)
            return None

        return expected_schema

    @staticmethod
    def _compare_columns(exp: SchemaDTO, act: SchemaDTO) -> Tuple[ColumnDiffDTO, bool]:
        """
        Returns the comparison result as a ComnDiffDTO object and overall OK/NOK result
        as boolean
        """

        diff = ColumnDiffDTO(diffs=[])
        result = True

        for expected_col, expected_dtype in exp.columns.items():
            diff_entry = ColumnDiffEntryDTO()
            diff_entry.expected_col = expected_col
            diff_entry.expected_dtype = expected_dtype
            if expected_col in act.columns:
                diff_entry.actual_col = expected_col
                diff_entry.actual_dtype = act.columns[expected_col]
                diff_entry.result_col = "OK"
                if diff_entry.actual_dtype == expected_dtype:
                    diff_entry.result_dtype = "OK"
                else:
                    diff_entry.result_dtype = "NOK"
            else:
                diff_entry.result_col = "NOK"

            if diff_entry.result_dtype == "NOK" or diff_entry.result_col == "NOK":
                diff_entry.result_all = "NOK"
            diff.diffs.append(diff_entry)

        for actual_col, actual_dtype in act.columns.items():
            if actual_col in exp.columns:
                pass
            else:
                diff_entry = ColumnDiffEntryDTO()
                diff_entry.actual_col, diff_entry.actual_dtype = actual_col, actual_dtype
                diff_entry.expected_col, diff_entry.actual_dtype = None, None
                diff_entry.result_col = "NOK"
                diff_entry.result_dtype = "N/A"
                diff_entry.result_all = "NOK"

                diff.diffs.append(diff_entry)

        for diff_entry in diff.diffs:
            if diff_entry.result_all == "NOK":
                result = False

        return diff, result

    @staticmethod
    def _compare_partitions(exp: SchemaDTO, act: SchemaDTO) \
            -> Tuple[Dict[str, List[str]], bool]:

        exp.partition_columns = exp.partition_columns or []
        act.partition_columns = act.partition_columns or []

        diff = {
            "expected_partitioning_columns": exp.partition_columns,
            "actual_partitioning_columns": act.partition_columns,
        }

        if set(sorted(exp.partition_columns)) == set(sorted(act.partition_columns)):
            comparison_result = True
        else:
            comparison_result = False

        return diff, comparison_result

    @staticmethod
    def _compare_clustering(exp: SchemaDTO, act: SchemaDTO) \
            -> Tuple[Dict[str, List[str]], bool]:

        exp.clustering_columns = exp.clustering_columns or []
        act.clustering_columns = act.clustering_columns or []

        diff = {
            "expected_clustering_columns": exp.clustering_columns,
            "actual_clustering_columns": act.clustering_columns,
        }

        if set(sorted(exp.clustering_columns)) == set(sorted(act.clustering_columns)):
            comparison_result = True
        else:
            comparison_result = False

        return diff, comparison_result

    @staticmethod
    def _compare_primary_keys(exp: SchemaDTO, act: SchemaDTO) \
            -> Tuple[Dict[str, List[str]], bool]:

        exp.primary_keys = exp.primary_keys or []
        act.primary_keys = act.primary_keys or []

        diff = {
            "expected_primary_keys": exp.primary_keys,
            "actual_primary_keys": act.primary_keys,
        }

        if set(sorted(exp.primary_keys)) == set(sorted(act.primary_keys)):
            comparison_result = True
        else:
            comparison_result = False

        return diff, comparison_result
