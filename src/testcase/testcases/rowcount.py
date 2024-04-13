from typing import List, Optional, Tuple, Any

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
    preconditions = ["testobject_exists", "testobject_not_empty"]

    def _execute(self):

        rowcount_sql = self._get_rowcount_query()
        if rowcount_sql is None:
            self.status = self.status.ABORTED
            self.result = self.result.NA
            return None
        else:
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

    def _get_rowcount_query(self) -> Optional[RowCountSqlDTO]:

        provided_queries: List[RowCountSqlDTO] = []
        rowcount_query: Optional[RowCountSqlDTO] = None

        for spec in self.specs:
            if isinstance(spec, RowCountSqlDTO):
                provided_queries.append(spec)
                rowcount_query = spec

        # if more than one rowcount_sql is provided, abort execution.
        # But: we don't check for 'no specs provided' since this is done by precon checks
        if len(provided_queries) > 1:
            msg = "Testcase stopped: more than one rowcount query is provided!"
            self.update_summary(msg)
            self.add_detail({"Provided rowcount queries": str(provided_queries)})
            self.notify(msg)
            return None
        else:
            return rowcount_query

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
