from src.dtos import SchemaSpecDTO, SpecType


def test_creating_spec_from_dict():
    spec = SchemaSpecDTO.from_dict(
        {
            "location": {"path": "dummy://this"},
            "testobject": "doesnt matter",
            "spec_type": SpecType.SCHEMA,
            "columns": {"a": "b"},
            "blub": "a",  # this should not play a role when constructing a schema spec
        }
    )
    assert spec.spec_type == SpecType.SCHEMA
    assert isinstance(spec, SchemaSpecDTO)


# TODO: create a test for testing SpecDTO.from_dict()
