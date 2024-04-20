import pytest

from src.dtos import SpecificationDTO, SchemaSpecificationDTO


def test_creating_spec_without_location():
    with pytest.raises(ValueError) as err:
        _ = SpecificationDTO()
    assert "Spec location not defined" in str(err)


def test_creating_spec_without_type():
    with pytest.raises(ValueError) as err:
        _ = SpecificationDTO(location="this")
    assert "Spec type not defined" in str(err)


def test_creating_schema_spec():
    spec = SchemaSpecificationDTO(location="this", columns={"a": "b"})
    assert spec.type == "schema"


def test_creating_schema_spec_without_columns():
    with pytest.raises(ValueError) as err:
        _ = SchemaSpecificationDTO(location="this")
    assert "Schema specification must have non-empty columns" in str(err)


def test_creating_schema_spec_from_dict():
    spec = SchemaSpecificationDTO.from_dict(spec_as_dict={
        "location": "this",
        "columns": {"a": "b"},
        "blub": "a"  # this should not play a role when constructing a schema spec
    })
    assert spec.type == "schema"
