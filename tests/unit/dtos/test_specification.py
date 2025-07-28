from src.dtos import SchemaSpecificationDTO, SpecFactory, SpecificationType


def test_creating_spec_from_dict():
    spec = SchemaSpecificationDTO.from_dict(
        {
            "location": {"path": "dummy://this"},
            "testobject": "doesnt matter",
            "spec_type": SpecificationType.SCHEMA,
            "columns": {"a": "b"},
            "blub": "a",  # this should not play a role when constructing a schema spec
        }
    )
    assert spec.spec_type == SpecificationType.SCHEMA
    assert isinstance(spec, SchemaSpecificationDTO)


class TestSpecFactory:
    def test_that_known_spec_type_is_created(self):
        # given a dict with a known spec type
        dict_ = {
            "location": {"path": "dummy://this"},
            "spec_type": "schema",
            "testobject": "doesnt matter",
            "columns": {"a": "b"},
        }

        # when creating a spec from the dict
        spec = SpecFactory().create_from_dict(dict_)

        # then the spec is created correctly
        assert isinstance(spec, SchemaSpecificationDTO)

        # and the spec type is correctly set
        assert spec.spec_type == SpecificationType.SCHEMA

        # when creating a spec from the dict with a known spec type in uppercase
        dict_["spec_type"] = "SCHEMA"
        spec = SpecFactory().create_from_dict(dict_)

        # then the spec is created correctly
        assert isinstance(spec, SchemaSpecificationDTO)
