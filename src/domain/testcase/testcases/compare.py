from typing import List, Tuple

import polars as pl

from . import (
    AbstractTestCase,
    time_it,
    TestCaseError,
    SpecNotFoundError,
)
from src.dtos import (
    CompareSqlDTO,
    SchemaSpecificationDTO,
    DBInstanceDTO,
    TestResult,
    TestType,
)


class CompareTestCaseError(TestCaseError):
    """
    Exception raised when a compare testcase operation fails.
    """


class PrimaryKeysMissingError(CompareTestCaseError):
    """
    Exception raised when primary keys are missing in the query
    """


class QueryExecutionError(CompareTestCaseError):
    """
    Exception raised when a query execution fails
    """


class CompareTestCase(AbstractTestCase):
    """
    Testcase compares a sample of data from provided test sql vs the data in the test-
    object. All rows and columns which are defined in the test sql are compared.
    If provided backend supports execution pushdown, comparison is pushed to backend.
    """

    ttype = TestType.COMPARE
    required_specs = ["compare_sql", "schema"]
    preconditions = [
        "specs_are_unique",
        "primary_keys_are_specified",
        "testobject_exists",
        "testobject_not_empty",
    ]

    def _execute(self):
        self.db = DBInstanceDTO.from_testobject(self.testobject)
        self.translated_query = self.backend.translate_query(self.sql.query, self.db)

        self.add_fact({"Primary keys": ",".join(self.schema.primary_keys or [])})
        self.add_fact({"Schema specification": self.schema.location.path})
        self.add_fact({"Compare SQL": self.sql.location.path})
        self.add_detail({"Original query": self.sql.query})
        self.add_detail({"Applied query": self.translated_query})

        # get schema defined by testquery
        schema_of_testquery = self._get_schema_from_query()

        # sample primary keys from query
        sample_keys = self._sample_keys_from_query(schema=schema_of_testquery)

        # sample fixtures which matches the pk sample from query
        expected = self._sample_data_from_query(
            sample_keys=sample_keys, schema=schema_of_testquery
        )
        self.add_fact({"Actual sample size": expected.shape[0]})

        # sample fixtures which matches the pk sample from testobject
        actual = self._sample_data_from_testobject(
            sample_keys=sample_keys, columns=expected.columns, schema=schema_of_testquery
        )

        # compare both samples
        diff = self._compare(expected, actual)

        if diff.shape[0] == 0:
            self.result = TestResult.OK
            self.summary = "Sample from testobject equals sample from test sql."
        else:
            self.result = TestResult.NOK
            self.summary = f"Testobject differs from SQL in {diff.shape[0]} row(s)."
            # trimm diff to ca. 500 examples to not blow up Excel memory
            diff_example = diff.head(500).to_dict(as_series=False)
            self.diff.update({"compare_diff": diff_example})

        return None

    @property
    def sample_size(self) -> int:
        config = self.domain_config.testcases.compare
        sample_size = config.sample_size_per_object.get(self.testobject.name)
        if sample_size is None:
            sample_size = config.sample_size
            self.notify("Using default sample size for comparison")
        else:
            self.notify("Using object specific sample size for comparison")

        detail = {"Specified sample size": sample_size}
        if detail not in self.details:
            self.add_detail(detail)

        return sample_size

    @property
    def sql(self) -> CompareSqlDTO:
        for spec in self.specs:
            if isinstance(spec, CompareSqlDTO):
                return spec
        raise SpecNotFoundError("Compare sql not found")

    @property
    def schema(self) -> SchemaSpecificationDTO:
        for spec in self.specs:
            if isinstance(spec, SchemaSpecificationDTO):
                return spec
        raise SpecNotFoundError("Schema spec not found")

    @time_it(step_name="getting schema of test query")
    def _get_schema_from_query(self) -> SchemaSpecificationDTO:
        try:
            schema = self.backend.get_schema_from_query(self.translated_query, self.db)
        except Exception as err:
            raise QueryExecutionError(
                "Error while obtaining schema from test query"
            ) from err

        pks = self.schema.primary_keys or []
        missing_pks = [pk for pk in pks if pk not in schema.columns]
        if not len(missing_pks) == 0:
            missing = ", ".join(missing_pks)
            self.add_fact({"Primary keys missing in query": missing})
            raise PrimaryKeysMissingError(f"Primary keys are missing in query: {missing}")

        return schema

    @time_it(step_name="sampling primary keys from query")
    def _sample_keys_from_query(self, schema: SchemaSpecificationDTO) -> List[str]:
        try:
            sample_keys = self.backend.get_sample_keys(
                query=self.translated_query,
                primary_keys=self.schema.primary_keys,  # type: ignore
                sample_size=self.sample_size,
                db=self.db,
                cast_to=schema,
            )
        except Exception as err:
            raise QueryExecutionError(
                "Error while sampling primary keys from test query"
            ) from err

        return sample_keys

    @time_it(step_name="sampling fixtures from query")
    def _sample_data_from_query(
        self, sample_keys: List[str], schema: SchemaSpecificationDTO
    ) -> pl.DataFrame:
        try:
            expected = self.backend.get_sample_from_query(
                query=self.translated_query,
                primary_keys=self.schema.primary_keys,  # type: ignore
                key_sample=sample_keys,
                db=self.db,
                cast_to=schema,
            )
        except Exception as err:
            raise QueryExecutionError("Error while sampling from test query") from err

        return expected

    @time_it(step_name="sampling fixtures from testobject")
    def _sample_data_from_testobject(
        self, sample_keys: List[str], columns: List[str], schema: SchemaSpecificationDTO
    ) -> pl.DataFrame:
        try:
            actual = self.backend.get_sample_from_testobject(
                testobject=self.testobject,
                primary_keys=self.schema.primary_keys,  # type: ignore
                key_sample=sample_keys,
                columns=columns,
                cast_to=schema,
            )
        except Exception as err:
            raise QueryExecutionError("Error while sampling from testobject") from err

        return actual

    # noinspection PyMethodMayBeStatic
    @time_it(step_name="harmonizing schemas")
    def _harmonize_schemas(
        self, expected: pl.DataFrame, actual: pl.DataFrame
    ) -> Tuple[pl.DataFrame, pl.DataFrame]:
        # try to same-cast to expected schema or to string - this is slow!
        if expected.schema != actual.schema:
            self.notify("Schemas of query sample and testobject are different.")
            self.add_fact({"Warning": "Schema differs between query and testobject"})
            for col, dtype in expected.schema.items():
                if expected.schema[col] != actual.schema[col]:
                    try:
                        actual = actual.cast({col: dtype})
                    except pl.PolarsError:
                        actual = actual.cast({col: pl.String})
                        expected = expected.cast({col: pl.String})
        else:
            self.notify("Testobject and query have same schema.")
            self.add_fact({"Schema info": "Testobject and query have same schema!"})

        return expected, actual

    @time_it(step_name="calculating rowhashes")
    def _calculate_rowhash(
        self, expected: pl.DataFrame, actual: pl.DataFrame
    ) -> Tuple[pl.DataFrame, pl.DataFrame]:
        def add_rowhash(df_: pl.DataFrame) -> pl.DataFrame:
            return df_.with_columns((df_.hash_rows()).alias("__rowhash__"))

        actual = add_rowhash(actual)
        expected = add_rowhash(expected)

        return expected, actual

    @time_it(step_name="calculating diff")
    def _calculate_diff(
        self, expected: pl.DataFrame, actual: pl.DataFrame
    ) -> pl.DataFrame:
        # Evaluate diff using an anti-join
        exp_not_act = expected.join(actual, on="__rowhash__", how="anti").with_columns(
            pl.lit("testobject").alias("__source__")
        )
        act_not_exp = actual.join(expected, on="__rowhash__", how="anti").with_columns(
            pl.lit("testquery").alias("__source__")
        )
        diff = exp_not_act.extend(act_not_exp)  # extend appends to dataframe

        return diff

    @time_it(step_name="comparing expected vs actual sample")
    def _compare(self, expected: pl.DataFrame, actual: pl.DataFrame) -> pl.DataFrame:
        expected, actual = self._harmonize_schemas(expected, actual)
        expected, actual = self._calculate_rowhash(expected, actual)
        diff = self._calculate_diff(expected, actual)

        sort_by = None
        if "__concat_key__" in diff.columns:
            sort_by = ["__concat_key__", "__source__"]

        diff = diff.sort(by=sort_by or diff.columns[0])

        return diff
