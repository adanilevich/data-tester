from typing import Dict, Any, List

import pytest

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

    data = {
        "a": [1, 2, 3],
        "b": ["this", "that", "other"],
        "c": [True, False, True],
        "__concat_key__": ["1|this", "2|that", "3|other"]
    }

    @pytest.fixture
    def testcase(self, testcase_creator) -> CompareSampleTestCase:

        testcase_ = testcase_creator.create(ttype="COMPARE_SAMPLE")

        def get_sample_keys_(query, *args, **kwargs) -> List[str]:
            if "exception" in query:
                raise NotImplementedError("This is a simulated exception.")
            else:
                return self.data["__concat_key__"]

        testcase_.backend.get_sample_keys = get_sample_keys_

        def get_sample_from_query_(
                primary_keys: List[str], *args, **kwargs
        ) -> Dict[str, List[Any]]:
            if "exception" in primary_keys:
                raise NotImplementedError("This is a simulated exception.")
            if "bad" in primary_keys:
                return {k: v[:-1] for k, v in self.data.items()}
            else:
                return self.data

        testcase_.backend.get_sample_from_query = get_sample_from_query_

        def get_sample_from_testobject_(*args, **kwargs) -> Dict[str, List[Any]]:
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
