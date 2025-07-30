from typing import List, Tuple, Any

from . import AbstractTestCase, TestCaseError, BackendError, SpecNotFoundError
from src.dtos import RowCountSqlDTO, DBInstanceDTO, TestType


class RowCountTestCaseError(TestCaseError):
    """
    Exception raised when a rowcount testcase operation fails.
    """


class RowCountQueryExecutionError(RowCountTestCaseError, BackendError):
    """
    Exception raised when a rowcount query execution fails
    """


class RowCountTestCase(AbstractTestCase):
    """
    Testcase compares specified schema vs what is actually implemented in database.
    Hereby, several comparisons take place -- depending on what is supported by db:
        - columns and datatypes are always compared
        - primary keys are compared if supported by backend (and specified)
        - partitioning columns are compared if supported by backend (and specified)
        - clustering columnsa are compared if supported by backend (and specified)
    """

    ttype = TestType.ROWCOUNT
    required_specs = ["rowcount_sql"]
    preconditions = ["specs_are_unique", "testobject_exists", "testobject_not_empty"]

    def _execute(self):
        self.add_fact({"Rowcount Query": self.sql.location.path})
        db = DBInstanceDTO.from_testobject(self.testobject)

        query = (
            self.sql.query
            + """
            SELECT *, 'expected' AS __source__ FROM __expected_count__
            UNION ALL
            SELECT *, 'actual' AS __source__ FROM __actual_count__
        """
        )
        translated_query = self.backend.translate_query(query, db)
        self.add_detail({"Original query": query})
        self.add_detail({"Applied query": translated_query})

        try:
            query_result = self.backend.run_query(translated_query, db)
        except Exception as err:
            raise RowCountQueryExecutionError(
                "Error during rowcount query execution"
            ) from err

        count_column_name = "cnt"
        for column_name in query_result.columns:
            if column_name != "__source__":
                count_column_name = column_name

        counts_as_tuples = list(
            zip(
                query_result.to_dict(as_series=False)[count_column_name],
                query_result.to_dict(as_series=False)["__source__"],
                strict=False,
            )
        )
        if self._validate_counts(counts_as_tuples) is False:
            return None

        expected_count: int = 0
        actual_count: int = 0

        for count, source in counts_as_tuples:
            if source == "expected":
                expected_count = count
            else:
                actual_count = count

        self._evaluate_results(expected_count, actual_count)

        return None

    @property
    def sql(self) -> RowCountSqlDTO:
        for spec in self.specs:
            if isinstance(spec, RowCountSqlDTO):
                return spec
        raise SpecNotFoundError("Rowcount SQL not found.")

    def _validate_counts(self, counts_as_tuples: List[Tuple[str, Any]]) -> bool:
        if len(counts_as_tuples) != 2:
            self.result = self.result.NA  # type: ignore[assignment]
            self.status = self.status.ABORTED  # type: ignore[assignment]
            summary = "Rowcount validation failed: Counts defined in SQL must be unique."
            self.summary = summary
            return False
        else:
            return True

    def _evaluate_results(self, expected_count: int, actual_count: int):
        if expected_count == actual_count:
            self.result = self.result.OK  # type: ignore[assignment]
            self.summary = f"Actual rowcount ({actual_count}) matches expected rowcount."
        else:
            self.result = self.result.NOK  # type: ignore[assignment]
            summary = (
                f"Actual rowcount ({actual_count}) deviates from "
                f"expected rowcount ({expected_count})!"
            )
            self.summary = summary

        self.diff.update(
            {
                "rowcount_diff": {
                    "expected_count": expected_count,
                    "actual_count": actual_count,
                }
            }
        )
