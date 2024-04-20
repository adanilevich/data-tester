from src.dtos import SchemaSpecificationDTO


def test_creating_schema_spec():
    spec = SchemaSpecificationDTO(location="this", columns={"a": "b"})
    assert spec.type == "schema"


def test_creating_schema_spec_from_dict():
    spec = SchemaSpecificationDTO.from_dict(spec_as_dict={
        "location": "this",
        "columns": {"a": "b"},
        "blub": "a"  # this should not play a role when constructing a schema spec
    })
    assert spec.type == "schema"
