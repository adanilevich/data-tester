from typing import Dict, Any, List

import pytest
import random
import numpy as np
from string import ascii_lowercase, digits
import time
import polars as pl

from src.testcase.testcases import CompareSampleTestCase
from src.dtos.specifications import SchemaSpecificationDTO, CompareSampleSqlDTO


# noinspection PyUnusedLocal
class TestCompareSampleTestCase:

    schema = SchemaSpecificationDTO(
        location="this_location",
        columns={"a": "int", "b": "string", "c": "bool"},
        primary_keys=["a", "b"]
    )

    sql = CompareSampleSqlDTO(
        location="this_location",
        query="this_will_be_changed",
    )

    data = pl.DataFrame({
        "a": [1, 2, 3],
        "b": ["this", "that", "other"],
        "c": [True, False, True],
        "__concat_key__": ["1|this", "2|that", "3|other"]
    })

    @pytest.fixture
    def testcase(self, testcase_creator) -> CompareSampleTestCase:

        testcase_ = testcase_creator.create(ttype="COMPARE_SAMPLE")

        def get_sample_keys_(query, *args, **kwargs) -> List[str]:
            if "exception" in query:
                raise NotImplementedError("This is a simulated exception.")
            else:
                return self.data.select("__concat_key__").to_series().to_list()

        testcase_.backend.get_sample_keys = get_sample_keys_

        def get_sample_from_query_(
                primary_keys: List[str], *args, **kwargs) -> pl.DataFrame:
            if "exception" in primary_keys:
                raise NotImplementedError("This is a simulated exception.")
            if "bad" in primary_keys:
                return self.data[:-1]
            else:
                return self.data

        testcase_.backend.get_sample_from_query = get_sample_from_query_

        def get_sample_from_testobject_(*args, **kwargs) -> pl.DataFrame:
            return get_sample_from_query_(primary_keys=[])

        testcase_.backend.get_sample_from_testobject = get_sample_from_testobject_

        testcase_.specs = [self.schema, self.sql]

        # noinspection PyTypeChecker
        return testcase_

    def test_default_sample_size_is_used_if_specific_not_specified(self, testcase):
        testcase.domain_config.compare_sample_testcase_config.sample_size_per_object = {}
        testcase.domain_config.compare_sample_testcase_config.sample_size = 1

        assert testcase._get_sample_size() == 1

    def test_specific_sample_size_is_used_if_specified(self, testcase):
        sample_sizes = {testcase.testobject.name: 100}
        testcase.domain_config.compare_sample_testcase_config.sample_size_per_object = \
            sample_sizes
        testcase.domain_config.compare_sample_testcase_config.sample_size = 1

        assert testcase._get_sample_size() == 100

    def test_execution_stops_for_pushdown_computation(self, testcase):
        testcase.backend.supports_db_comparison = True

        with pytest.raises(NotImplementedError) as err:
            testcase._execute()

        assert "Using backend comparison not implemented" in str(err)

    def test_key_sampling_exception_is_caught(self, testcase):
        sql = CompareSampleSqlDTO.from_dict(self.sql.dict())
        sql.query = "exception"
        testcase.specs = [sql, self.schema]

        with pytest.raises(NotImplementedError) as err:
            testcase._execute()

        assert "Error while sampling primary keys" in str(err)
        assert "simulated exception" in str(err)

    def test_query_sampling_exception_is_caught(self, testcase):
        schema = SchemaSpecificationDTO.from_dict(self.schema.dict())
        schema.primary_keys = ["exception"]
        testcase.specs = [self.sql, schema]

        with pytest.raises(NotImplementedError) as err:
            testcase._execute()

        assert "Error while sampling from test query" in str(err)
        assert "simulated exception" in str(err)

    def test_happy_path(self, testcase):

        testcase._execute()

        assert testcase.result == testcase.result.OK
        assert "from testobject equals sample from test sql" in testcase.summary

    def test_that_diff_is_treated_correctly(self, testcase):
        schema = SchemaSpecificationDTO.from_dict(self.schema.dict())
        schema.primary_keys = ["bad"]
        testcase.specs = [self.sql, schema]

        testcase._execute()

        assert testcase.result == testcase.result.NOK
        assert "compare_sample_diff_example" in testcase.diff
        assert testcase.summary == "Testobject differs from test sql in 1 sample row(s)."

    # skip performance test, only execute if needed
    @pytest.mark.skip_test
    def test_comparison_performance(self, testcase):

        print("\nStarting performance tests for compare_sample ...")
        num_cols = 50  # times four

        def prepare_data(num_rows_: int, num_cols_: int):

            start_ = time.time()
            data = dict()
            other_data = dict()

            ints = np.random.randint(1, 1_000_000_000, (num_cols_, num_rows_)).tolist()
            floats = np.random.uniform(0.0, 1_000_000_000_000_000.0, (num_cols_, num_rows_)).tolist()
            chars = ascii_lowercase + digits
            base_strings = [''.join(random.choice(chars) for _ in range(20)) for _ in range(num_rows_)]
            strings = [np.random.choice(base_strings, num_rows_) for _ in range(num_cols_)]

            for idx, _ in enumerate(ints):
                data.update({str(idx) + "_int": ints[idx]})
                data.update({str(idx) + "_float": floats[idx]})
                data.update({str(idx) + "_int": strings[idx]})
                other_data.update({str(idx) + "_int": ints[idx][:-1]})
                other_data.update({str(idx) + "_float": floats[idx][:-1]})
                other_data.update({str(idx) + "_int": strings[idx][:-1]})

            end_ = time.time()
            data_preparation_time = (end_ - start_)
            print(f"\nData preparation time for {num_rows_} rows: ", data_preparation_time)
            return pl.DataFrame(data), pl.DataFrame(other_data)

        def compare_data(data_, other_data_):
            start_ = time.time()
            diff_ = testcase._get_diff(data_, other_data_)
            end_ = time.time()
            comparison_time = (end_ - start_)
            print("\nData comparison time: ", comparison_time)
            return diff_

        for num_rows in [1_000, 10_000, 100_000, 1_000_000]:
            _data, _other_data = prepare_data(num_rows, num_cols)
            diff = compare_data(_data, _other_data)
