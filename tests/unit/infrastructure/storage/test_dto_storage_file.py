from typing import cast
from uuid import uuid4

import pytest
from fsspec.implementations.memory import MemoryFileSystem
from src.dtos import (
    DTO,
    DomainConfigDTO,
    LocationDTO,
    ObjectType,
    TestCaseDTO,
    TestCaseEntryDTO,
    TestSetDTO,
    TestType,
)
from src.infrastructure.storage.dto_storage_file import (
    DtoStorageFileError,
    JsonSerializer,
    MemoryDtoStorage,
)
from src.infrastructure_ports import ObjectNotFoundError


def _make_domain_config(domain: str = "payments") -> DomainConfigDTO:
    return DomainConfigDTO(
        domain=domain,
        instances={"test": ["alpha"]},
        spec_locations={"test": ["memory://specs/"]},
        reports_location=LocationDTO("memory://reports/"),
        compare_datatypes=["int", "string"],
        sample_size_default=100,
        sample_size_per_object={},
    )


def _make_testset(domain: str = "payments", name: str = "my_testset") -> TestSetDTO:
    return TestSetDTO(
        name=name,
        domain=domain,
        default_stage="test",
        default_instance="alpha",
        testcases={
            "obj_schema": TestCaseEntryDTO(
                testobject="obj",
                testtype=TestType.SCHEMA,
                domain="test_domain",
            ),
        },
    )


class TestMemoryDtoStorage:
    @pytest.fixture
    def storage(self) -> MemoryDtoStorage:
        s = MemoryDtoStorage(
            serializer=JsonSerializer(),
            storage_location=LocationDTO("memory://data/"),
        )
        cast(MemoryFileSystem, s.fs).store.clear()
        return s

    # --- write_dto / read_dto roundtrip ---

    def test_write_read_domain_config(self, storage: MemoryDtoStorage):
        config = _make_domain_config("payments")
        storage.write_dto(config)

        result = storage.read_dto(ObjectType.DOMAIN_CONFIG, config.id)
        result = cast(DomainConfigDTO, result)
        assert result.domain == "payments"

    def test_write_read_testset(self, storage: MemoryDtoStorage):
        testset = _make_testset("payments", "my_testset")
        storage.write_dto(testset)

        result = storage.read_dto(ObjectType.TESTSET, testset.id)
        result = cast(TestSetDTO, result)
        assert result.name == "my_testset"
        assert result.domain == "payments"

    # --- read_dto not found ---

    def test_read_dto_not_found_raises(self, storage: MemoryDtoStorage):
        with pytest.raises(ObjectNotFoundError):
            storage.read_dto(ObjectType.TESTSET, str(uuid4()))

    # --- subfolder structure ---

    def test_domain_config_stored_in_folder(self, storage: MemoryDtoStorage):
        config = _make_domain_config("payments")
        storage.write_dto(config)

        expected = f"data/domain_configs/{config.id}.json"
        assert storage.fs.exists(expected)

    def test_testset_stored_in_subfolder(self, storage: MemoryDtoStorage):
        testset = _make_testset("payments")
        storage.write_dto(testset)

        expected = f"data/testsets/payments/{testset.id}.json"
        assert storage.fs.exists(expected)

    def test_write_read_testcase(
        self, storage: MemoryDtoStorage, testcase_result: TestCaseDTO
    ):
        storage.write_dto(testcase_result)

        result = cast(
            TestCaseDTO,
            storage.read_dto(ObjectType.TESTCASE, str(testcase_result.id)),
        )
        assert result.id == testcase_result.id
        assert result.testtype == testcase_result.testtype
        assert result.result == testcase_result.result
        assert result.testobject.name == testcase_result.testobject.name
        assert result.testrun_id == testcase_result.testrun_id

    def test_testcase_stored_in_flat_folder(
        self, storage: MemoryDtoStorage, testcase_result: TestCaseDTO
    ):
        storage.write_dto(testcase_result)

        expected = f"data/testcases/{testcase_result.id}.json"
        assert storage.fs.exists(expected)

    def test_testcase_read_not_found(self, storage: MemoryDtoStorage):
        with pytest.raises(ObjectNotFoundError):
            storage.read_dto(ObjectType.TESTCASE, str(uuid4()))

    # --- list_dtos ---

    def test_list_dtos_domain_configs(self, storage: MemoryDtoStorage):
        c1 = _make_domain_config("payments")
        c2 = _make_domain_config("sales")
        storage.write_dto(c1)
        storage.write_dto(c2)

        result = storage.list_dtos(ObjectType.DOMAIN_CONFIG)
        assert len(result) == 2
        domains = {cast(DomainConfigDTO, r).domain for r in result}
        assert domains == {"payments", "sales"}

    def test_list_dtos_testsets_with_domain_filter(self, storage: MemoryDtoStorage):
        ts1 = _make_testset("payments", "ts1")
        ts2 = _make_testset("sales", "ts2")
        storage.write_dto(ts1)
        storage.write_dto(ts2)

        result = storage.list_dtos(ObjectType.TESTSET, filters={"domain": "payments"})
        assert len(result) == 1
        assert cast(TestSetDTO, result[0]).name == "ts1"

    def test_list_dtos_empty(self, storage: MemoryDtoStorage):
        result = storage.list_dtos(ObjectType.TESTSET)
        assert result == []

    # --- order_by ---

    def test_list_dtos_invalid_order_by_raises(self, storage: MemoryDtoStorage):
        with pytest.raises(ValueError, match="Unsupported order_by"):
            storage.list_dtos(ObjectType.TESTSET, order_by="name")

    # --- write_dto infers object_type ---

    def test_write_dto_unknown_type_raises(self, storage: MemoryDtoStorage):
        class UnknownDTO(DTO):
            value: str = "test"

        with pytest.raises(DtoStorageFileError, match="Cannot infer"):
            storage.write_dto(UnknownDTO())

    # --- duplicate detection ---

    def test_read_dto_multiple_matches_raises(self, storage: MemoryDtoStorage):
        config = _make_domain_config("sales")
        serializer = JsonSerializer()
        content = serializer.serialize(config)
        with storage.fs.open(f"data/domain_configs/{config.id}.json", "wb") as f:
            f.write(content)
        with storage.fs.open(f"data/domain_configs/sub/{config.id}.json", "wb") as f:
            f.write(content)

        with pytest.raises(DtoStorageFileError, match="Multiple"):
            storage.read_dto(ObjectType.DOMAIN_CONFIG, str(config.id))

    # --- delete_dto ---

    def test_delete_dto_removes_file(self, storage: MemoryDtoStorage):
        testset = _make_testset("payments", "to_delete")
        storage.write_dto(testset)
        expected = f"data/testsets/payments/{testset.id}.json"
        assert storage.fs.exists(expected)

        storage.delete_dto(ObjectType.TESTSET, str(testset.id))

        assert not storage.fs.exists(expected)

    def test_delete_dto_not_found_raises(self, storage: MemoryDtoStorage):
        with pytest.raises(ObjectNotFoundError):
            storage.delete_dto(ObjectType.TESTSET, str(uuid4()))

    def test_delete_dto_multiple_matches_raises(self, storage: MemoryDtoStorage):
        testset = _make_testset("payments", "dup")
        serializer = JsonSerializer()
        content = serializer.serialize(testset)
        with storage.fs.open(f"data/testsets/{testset.id}.json", "wb") as f:
            f.write(content)
        with storage.fs.open(f"data/testsets/sub/{testset.id}.json", "wb") as f:
            f.write(content)

        with pytest.raises(DtoStorageFileError, match="Multiple"):
            storage.delete_dto(ObjectType.TESTSET, str(testset.id))
