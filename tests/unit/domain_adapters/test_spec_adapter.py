import io
from datetime import datetime
from uuid import uuid4

import polars as pl
import pytest
from src.domain.specification.plugins import NamingConventionsFactory, SpecParserFactory
from src.domain_adapters import SpecAdapter
from src.domain_ports import FindSpecsCommand
from src.dtos import (
    DomainConfigDTO,
    LocationDTO,
    RowcountSpecDTO,
    SchemaSpecDTO,
    SpecType,
    TestCaseEntryDTO,
    TestSetDTO,
    TestType,
)
from src.infrastructure.storage.user_storage import MemoryUserStorage


def _put(storage: MemoryUserStorage, path: str, data: bytes) -> None:
    """Write test data into MemoryUserStorage."""
    with storage.fs.open(path, mode="wb") as f:
        f.write(data)


class TestSpecAdapter:
    """Test suite for the SpecAdapter class"""

    @pytest.fixture
    def user_storage(self) -> MemoryUserStorage:
        """Create a MemoryUserStorage and populate with test data"""
        storage = MemoryUserStorage()

        # Add schema xlsx file for table1
        schema_data = self._create_test_xlsx_schema()
        _put(storage, "specs/table1_schema.xlsx", schema_data)
        _put(
            storage,
            "backup/table1_schema.xlsx",
            schema_data,
        )

        # Add rowcount SQL file for table1
        rowcount_sql = "SELECT COUNT(*) as __EXPECTED_ROWCOUNT__ FROM table1"
        _put(
            storage,
            "specs/table1_ROWCOUNT.sql",
            rowcount_sql.encode(),
        )

        # Add compare sample SQL and schema files for table2
        compare_sql = "SELECT id, name FROM table2 WHERE id = 1 -- __EXPECTED__"
        _put(
            storage,
            "specs/table2_COMPARE.sql",
            compare_sql.encode(),
        )
        _put(storage, "specs/table2_schema.xlsx", schema_data)

        return storage

    @pytest.fixture
    def naming_conventions_factory(
        self,
    ) -> NamingConventionsFactory:
        """Create a NamingConventionsFactory instance"""
        return NamingConventionsFactory()

    @pytest.fixture
    def formatter_factory(self) -> SpecParserFactory:
        """Create a SpecParserFactory instance"""
        return SpecParserFactory()

    @pytest.fixture
    def handler(
        self,
        user_storage: MemoryUserStorage,
        naming_conventions_factory: NamingConventionsFactory,
        formatter_factory: SpecParserFactory,
    ) -> SpecAdapter:
        """Create a SpecAdapter instance"""
        return SpecAdapter(
            naming_conventions_factory=naming_conventions_factory,
            user_storage=user_storage,
            formatter_factory=formatter_factory,
        )

    @pytest.fixture
    def domain_config_single_loc(self) -> DomainConfigDTO:
        return DomainConfigDTO(
            domain="test_domain",
            instances={"dev": ["primary"]},
            compare_datatypes=[],
            sample_size_default=100,
            spec_locations={"dev": ["memory://specs/"]},
            reports_location=LocationDTO("memory://reports/"),
        )

    @pytest.fixture
    def domain_config_multi_loc(self) -> DomainConfigDTO:
        return DomainConfigDTO(
            domain="test_domain",
            instances={"dev": ["primary"]},
            compare_datatypes=[],
            sample_size_default=100,
            spec_locations={"dev": ["memory://specs/", "memory://backup/"]},
            reports_location=LocationDTO("memory://reports/"),
        )

    @pytest.fixture
    def test_testset(self) -> TestSetDTO:
        """Create a test TestSetDTO with various test cases"""
        testcases = {
            "table1_SCHEMA": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.SCHEMA,
                domain="test_domain",
                comment="Schema test for table1",
            ),
            "table1_ROWCOUNT": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.ROWCOUNT,
                domain="test_domain",
                comment="Rowcount test for table1",
            ),
            "table2_COMPARE": TestCaseEntryDTO(
                testobject="table2",
                testtype=TestType.COMPARE,
                domain="test_domain",
                comment="Compare sample test for table2",
            ),
        }

        return TestSetDTO(
            testset_id=uuid4(),
            name="Test TestSet",
            description="A test set for unit testing",
            labels=["unit-test", "specification"],
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases=testcases,
            modified_at=datetime.now(),
        )

    def _create_test_xlsx_schema(self) -> bytes:
        """Create a test Excel file with schema data"""
        data = {
            "column": ["id", "name", "created_at"],
            "type": [
                "INTEGER",
                "VARCHAR(255)",
                "TIMESTAMP",
            ],
            "pk": ["x", "", ""],
            "partition": ["", "", "x"],
            "cluster": ["", "x", ""],
        }
        df = pl.DataFrame(data)

        buffer = io.BytesIO()
        df.write_excel(buffer, worksheet="schema")
        return buffer.getvalue()

    def test_init(self, handler: SpecAdapter):
        """Test that SpecAdapter initializes correctly"""
        assert handler.naming_conventions_factory is not None
        assert handler.user_storage is not None
        assert handler.formatter_factory is not None

    def test_list_specs_single_location_single_testcase(
        self,
        handler: SpecAdapter,
        test_testset: TestSetDTO,
        domain_config_single_loc: DomainConfigDTO,
    ):
        """Test find_specs with single location and single testcase"""
        single_testcase_testset = TestSetDTO(
            testset_id=test_testset.testset_id,
            name=test_testset.name,
            domain=test_testset.domain,
            default_stage=test_testset.default_stage,
            default_instance=test_testset.default_instance,
            testcases={"table1_SCHEMA": test_testset.testcases["table1_SCHEMA"]},
        )

        command = FindSpecsCommand(
            testset=single_testcase_testset,
            domain_config=domain_config_single_loc,
        )

        result = handler.find_specs(command)

        assert len(result.testcase_defs) == 1
        assert len(result.testcase_defs[0].specs) == 1
        assert isinstance(result.testcase_defs[0].specs[0], SchemaSpecDTO)
        assert result.testcase_defs[0].specs[0].testobject == "table1"

    def test_list_specs_multiple_locations(
        self,
        handler: SpecAdapter,
        test_testset: TestSetDTO,
        domain_config_multi_loc: DomainConfigDTO,
    ):
        """Test find_specs with multiple locations"""
        single_testcase_testset = TestSetDTO(
            testset_id=test_testset.testset_id,
            name=test_testset.name,
            domain=test_testset.domain,
            default_stage=test_testset.default_stage,
            default_instance=test_testset.default_instance,
            testcases={"table1_SCHEMA": test_testset.testcases["table1_SCHEMA"]},
        )

        command = FindSpecsCommand(
            testset=single_testcase_testset,
            domain_config=domain_config_multi_loc,
        )

        result = handler.find_specs(command)

        assert len(result.testcase_defs) == 1
        assert len(result.testcase_defs[0].specs) == 2
        assert all(
            isinstance(spec, SchemaSpecDTO) for spec in result.testcase_defs[0].specs
        )
        assert all(spec.testobject == "table1" for spec in result.testcase_defs[0].specs)

    def test_list_specs_multiple_testcases(
        self,
        handler: SpecAdapter,
        test_testset: TestSetDTO,
        domain_config_single_loc: DomainConfigDTO,
    ):
        """Test find_specs with multiple testcases"""
        command = FindSpecsCommand(
            testset=test_testset,
            domain_config=domain_config_single_loc,
        )

        result = handler.find_specs(command)

        assert len(result.testcase_defs) == 3

        # First testcase: table1_SCHEMA
        assert len(result.testcase_defs[0].specs) == 1
        assert isinstance(result.testcase_defs[0].specs[0], SchemaSpecDTO)
        assert result.testcase_defs[0].specs[0].testobject == "table1"

        # Second testcase: table1_ROWCOUNT
        assert len(result.testcase_defs[1].specs) == 1
        assert isinstance(result.testcase_defs[1].specs[0], RowcountSpecDTO)
        assert result.testcase_defs[1].specs[0].testobject == "table1"

        # Third testcase: table2_COMPARE
        assert len(result.testcase_defs[2].specs) == 2
        spec_types = [spec.spec_type for spec in result.testcase_defs[2].specs]
        assert SpecType.COMPARE in spec_types
        assert SpecType.SCHEMA in spec_types

    def test_list_specs_no_specs_found(
        self, handler: SpecAdapter, domain_config_single_loc: DomainConfigDTO
    ):
        """Test find_specs when no specifications are found"""
        testcase = TestCaseEntryDTO(
            testobject="nonexistent_table",
            testtype=TestType.SCHEMA,
            domain="test_domain",
            comment="Test for non-existent table",
        )

        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Empty Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases={"nonexistent_SCHEMA": testcase},
        )

        command = FindSpecsCommand(
            testset=testset,
            domain_config=domain_config_single_loc,
        )

        result = handler.find_specs(command)

        assert len(result.testcase_defs) == 1
        assert len(result.testcase_defs[0].specs) == 0

    def test_list_specs_preserves_testcase_order(
        self, handler: SpecAdapter, domain_config_single_loc: DomainConfigDTO
    ):
        """Test that find_specs preserves the order of testcases"""
        testcases = {
            "z_table": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.SCHEMA,
                domain="test_domain",
            ),
            "a_table": TestCaseEntryDTO(
                testobject="table2",
                testtype=TestType.SCHEMA,
                domain="test_domain",
            ),
            "m_table": TestCaseEntryDTO(
                testobject="table1",
                testtype=TestType.ROWCOUNT,
                domain="test_domain",
            ),
        }

        testset = TestSetDTO(
            testset_id=uuid4(),
            name="Ordered Test Set",
            domain="test_domain",
            default_stage="dev",
            default_instance="primary",
            testcases=testcases,
        )

        command = FindSpecsCommand(
            testset=testset,
            domain_config=domain_config_single_loc,
        )

        result = handler.find_specs(command)

        assert len(result.testcase_defs) == 3

        testcase_list = list(testset.testcases.values())
        for i, tcd in enumerate(result.testcase_defs):
            expected_testcase = testcase_list[i]
            if len(tcd.specs) > 0:
                assert all(
                    spec.testobject == expected_testcase.testobject for spec in tcd.specs
                )
