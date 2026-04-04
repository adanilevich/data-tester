from src.dtos import TestCaseEntryDTO, LocationDTO, TestType, SpecType
from src.domain.specification.plugins.naming_conventions import (
    DefaultNamingConventions,
    NamingConventionsFactory,
)


class TestDefaultNamingConventions:
    """Test cases for DefaultNamingConventions class."""

    def test_match_schema(self):
        testcase = TestCaseEntryDTO(
            testobject="new_customers",
            testtype=TestType.SCHEMA,
            domain="test_domain",
            scenario="test_scenario",
        )
        file = LocationDTO("local://path/to/new_customers_spec_v1.xlsx")

        assert DefaultNamingConventions().match(testcase, file)

    def test_match_schema_invalid_extension(self):
        testcase = TestCaseEntryDTO(
            testobject="customers",
            testtype=TestType.SCHEMA,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/customers_spec.sql")

        match, spec_types = DefaultNamingConventions().match(testcase, file)

        assert not match
        assert not spec_types

    def test_match_schema_testcase_with_wrong_prefix(self):
        testcase = TestCaseEntryDTO(
            testobject="customers",
            testtype=TestType.SCHEMA,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/new_customers_spec_v1.xlsx")

        match, spec_types = DefaultNamingConventions().match(testcase, file)

        assert not match
        assert not spec_types

    def test_match_rowcount(self):
        testcase = TestCaseEntryDTO(
            testobject="transactions",
            testtype=TestType.ROWCOUNT,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/transactions_ROWCOUNT.sql")

        match, spec_types = DefaultNamingConventions().match(testcase, file)
        assert match
        assert spec_types == [SpecType.ROWCOUNT]

    def test_match_rowcount_invalid_extension(self):
        testcase = TestCaseEntryDTO(
            testobject="transactions",
            testtype=TestType.ROWCOUNT,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/transactions_ROWCOUNT.xlsx")

        match, spec_types = DefaultNamingConventions().match(testcase, file)
        assert not match
        assert not spec_types

    def test_match_rowcount_wrong_prefix(self):
        testcase = TestCaseEntryDTO(
            testobject="transactions",
            testtype=TestType.ROWCOUNT,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/customers_ROWCOUNT.sql")

        match, spec_types = DefaultNamingConventions().match(testcase, file)
        assert not match
        assert not spec_types

    def test_match_compare(self):
        testcase = TestCaseEntryDTO(
            testobject="orders",
            testtype=TestType.COMPARE,
            domain="test_domain",
        )
        file1 = LocationDTO("local://path/to/orders_COMPARE.sql")
        file2 = LocationDTO("local://path/to/orders_spec_v1.xlsx")

        match1, spec_types1 = DefaultNamingConventions().match(testcase, file1)
        match2, spec_types2 = DefaultNamingConventions().match(testcase, file2)
        assert match1
        assert match2
        assert spec_types1 == [SpecType.COMPARE]
        assert spec_types2 == [SpecType.SCHEMA]

    def test_match_compare_wrong_prefix(self):
        testcase = TestCaseEntryDTO(
            testobject="orders",
            testtype=TestType.COMPARE,
            domain="test_domain",
        )
        file = LocationDTO("local://path/to/customers_COMPARE.sql")

        match, spec_types = DefaultNamingConventions().match(testcase, file)
        assert not match
        assert not spec_types


class TestNamingConventionsFactory:
    """Test cases for NamingConventionsFactory class."""

    def test_create_returns_same_instance_for_different_domains(self):
        # Given different domain names
        factory = NamingConventionsFactory()
        domain1 = "domain1"
        domain2 = "domain2"

        # When creating naming conventions
        result1 = factory.create(domain1)
        result2 = factory.create(domain2)

        # Then the result is a DefaultNamingConventions instance
        assert isinstance(result1, DefaultNamingConventions)
        assert isinstance(result2, DefaultNamingConventions)
