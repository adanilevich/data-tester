from typing import Dict, List, Any
import polars as pl

from src.testcase.testcases import AbstractTestCase
from src.dtos.specifications import CompareSampleSqlDTO, SchemaSpecificationDTO
from src.dtos.testcase import DBInstanceDTO


class CompareSampleTestCase(AbstractTestCase):
    """
    Testcase compares a sample of data from provided test sql vs the data in the test-
    object. All rows and columns which are defined in the test sql are compared.
    If provided backend supports execution pushdown, comparison is pushed to backend.
    """
    ttype = "COMPARE_SAMPLE"
    required_specs = ["compare_sample_sql", "schema"]
    preconditions = [
        "specs_are_unique", "primary_keys_are_specified", "testobject_exists",
        "testobject_not_empty",
    ]

    def _execute(self):
        sql: CompareSampleSqlDTO = self._get_spec(CompareSampleSqlDTO)
        schema: SchemaSpecificationDTO = self._get_spec(SchemaSpecificationDTO)

        sample_size = self._get_sample_size()
        self.notify(f"Starting execution with sample size {sample_size}")
        db = DBInstanceDTO.from_testobject(self.testobject)
        primary_keys = schema.primary_keys
        self.add_fact({"Primary keys": primary_keys})
        self.add_fact({"Schema specification": schema.location})
        self.add_fact({"Compare sample SQL": sql.location})

        if self.backend.supports_db_comparison is False:

            translated_query = self.backend.translate_query(sql.query, db)
            self.add_detail({"Original query": sql.query})
            self.add_detail({"Applied query": translated_query})
            try:
                sample_keys = self.backend.get_sample_keys(
                    query=translated_query,
                    primary_keys=primary_keys,
                    sample_size=sample_size,
                )
            except Exception as err:
                msg = "Error while sampling primary keys from test query: " + str(err)
                raise err.__class__(msg)

            try:
                expected = self.backend.get_sample_from_query(
                    query=translated_query,
                    primary_keys=primary_keys,
                    key_sample=sample_keys,
                )
                columns = list(expected.keys())
            except Exception as err:
                msg = "Error while sampling from test query: " + str(err)
                raise err.__class__(msg)

            try:
                actual = self.backend.get_sample_from_testobject(
                    testobject=self.testobject,
                    primary_keys=primary_keys,
                    key_sample=sample_keys,
                    columns=columns
                )
            except Exception as err:
                msg = "Error while sampling from testobject: " + str(err)
                raise err.__class__(msg)

            diff = self._get_diff(expected, actual)
        else:
            raise NotImplementedError("Using backend comparison not implemented")

        real_sample_size = len(list(expected.values())[0])

        if len(list(diff.values())[0]) == 0:
            self.result = self.result.OK
            self.summary = (f"Sample (of size {real_sample_size}) from testobject equals "
                            f"sample from test sql.")
        else:
            # trimm diff to ca. 500 examples to not blow up memory
            diff_example = {
                key: value[:500] for key, value in diff.items()
            }
            self.diff.update({"compare_sample_diff_example": diff_example})
            self.result = self.result.NOK
            diff_size = len(diff[list(diff.keys())[0]])
            msg = f"Testobject differs from test sql in {diff_size} sample row(s)."
            self.summary = msg

        return None

    def _get_sample_size(self) -> int:

        config = self.domain_config.compare_sample_testcase_config
        sample_size_per_testobject = config.sample_size_per_object or {}
        if self.testobject.name in sample_size_per_testobject:
            sample_size = sample_size_per_testobject[self.testobject.name]
        else:
            sample_size = config.sample_size

        return sample_size

    @staticmethod
    def _get_diff(expected: Dict[str, List[Any]], actual: Dict[str, List[Any]]) \
            -> Dict[str, List[Any]]:

        exp_df = pl.DataFrame(expected)
        act_df = pl.DataFrame(actual)

        try:
            schema = exp_df.schema
            act_df = act_df.cast(schema, strict=True)  # type: ignore
        except pl.ComputeError:
            act_df = act_df.cast(pl.String)
            exp_df = exp_df.cast(pl.String)

        def add_rowhash(df_: pl.DataFrame) -> pl.DataFrame:
            return df_.with_columns((df_.hash_rows()).alias("__rowhash__"))

        act_df = add_rowhash(act_df)
        exp_df = add_rowhash(exp_df)

        # Compare dataframes via an anti-join
        exp_not_act = exp_df.join(act_df, on="__rowhash__", how="anti")
        exp_not_act = exp_not_act.with_columns(pl.lit("testobject").alias("__source__"))

        act_not_exp = act_df.join(exp_df, on="__rowhash__", how="anti")
        act_not_exp = act_not_exp.with_columns(pl.lit("testquery").alias("__source__"))

        # merge results
        diff = (
            exp_not_act
            .extend(act_not_exp)
            .sort(by=["__rowhash__", "__source__"])
        )

        return diff.to_dict(as_series=False)
