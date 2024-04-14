from typing import List, Tuple, Any

from src.testcase.testcases import AbstractTestCase
from src.dtos.specifications import RowCountSqlDTO


class RowCountTestCase(AbstractTestCase):
    """
    Testcase compares specified schema vs what is actually implemented in database.
    Hereby, several comparisons take place -- depending on what is supported by db:
        - columns and datatypes are always compared
        - primary keys are compared if supported by backend (and specified)
        - partitioning columns are compared if supported by backend (and specified)
        - clustering columnsa are compared if supported by backend (and specified)
    """
    ttype = "ROWCOUNT"
    required_specs = ["rowcount_sql"]
    preconditions = ["specs_are_unique", "testobject_exists", "testobject_not_empty"]

    def _execute(self):

        # we rely on precondition checks that unique rowcount sql is provided
        rowcount_sql = self._get_rowcount_sql()
        self.add_fact({"Rowcount Query": rowcount_sql.location})

        query = rowcount_sql.query + """
            SELECT *, 'expected' AS __source__ FROM __expected_count__
            UNION ALL
            SELECT *, 'actual' AS __source__ FROM __actual_count__
        """

        try:
            query_result = self.backend.run_query(
                query=query,
                domain=self.testobject.domain,
                stage=self.testobject.stage,
                instance=self.testobject.instance
            )
        except Exception as err:
            error_message = f"Error during rowcount query execution: {str(err)}"
            raise err.__class__(error_message)

        count_column_name = "cnt"
        for column_name in query_result:
            if column_name != "__source__":
                count_column_name = column_name

        counts_as_tuples = list(zip(
            query_result[count_column_name],
            query_result["__source__"]
        ))
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

    def _get_rowcount_sql(self) -> RowCountSqlDTO:

        provided_sqls: List[RowCountSqlDTO] = []

        for spec in self.specs:
            if isinstance(spec, RowCountSqlDTO):
                provided_sqls.append(spec)

        if len(provided_sqls) > 1:
            raise ValueError("Non-unique rowcound sqls provided. Prechecks failed.")

        return provided_sqls[0]

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
            summary = (f"Actual rowcount ({actual_count}) deviates from "
                       f"expected rowcount ({expected_count})!")
            self.summary = summary

        self.diff.update({"rowcount_diff": {
            "expected_count": expected_count,
            "actual_count": actual_count,
        }})
