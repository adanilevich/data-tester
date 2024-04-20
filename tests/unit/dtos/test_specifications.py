from src.dtos import SchemaSpecificationDTO, SpecFactory


def test_creating_spec_from_dict():
    spec = SchemaSpecificationDTO.from_dict(
        {
            "location": "this",
            "testobject": "doesnt matter",
            "columns": {"a": "b"},
            "blub": "a"  # this should not play a role when constructing a schema spec
        }
    )
    assert spec.type == "schema"
    assert isinstance(spec, SchemaSpecificationDTO)


class TestSpecFactory:

    def test_that_known_spec_type_is_created(self):
        dict_ = {
            "type": "schema",
            "location": "this",
            "testobject": "doesnt matter",
            "columns": {"a": "b"},
        }

        spec = SpecFactory().create_from_dict(dict_)
        assert isinstance(spec, SchemaSpecificationDTO)
