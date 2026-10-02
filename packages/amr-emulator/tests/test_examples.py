"""Property test: synthesized examples always validate against their schema."""

from amr_emulator.examples import example_from_schema
from hypothesis import given
from hypothesis import strategies as st
from jsonschema import Draft4Validator

# A recursive strategy over the schema subset that appears in MiR specs.
_leaf = st.sampled_from(
    [
        {"type": "string"},
        {"type": "string", "format": "date-time"},
        {"type": "string", "minLength": 3},
        {"type": "integer"},
        {"type": "integer", "minimum": 5},
        {"type": "number"},
        {"type": "boolean"},
        {"enum": ["a", "b"]},
        {},
    ]
)


def _extend(children):
    names = st.sampled_from(["guid", "url", "name", "value", "state", "id"])
    return st.one_of(
        st.fixed_dictionaries({"type": st.just("array"), "items": children}),
        st.dictionaries(names, children, min_size=1, max_size=4).map(
            lambda props: {"type": "object", "properties": props}
        ),
        st.lists(children, min_size=1, max_size=3).map(lambda opts: {"anyOf": opts}),
    )


schemas = st.recursive(_leaf, _extend, max_leaves=12)


@given(schemas)
def test_example_validates_against_its_schema(schema):
    value = example_from_schema(schema)
    Draft4Validator(schema).validate(value)


def test_deep_recursion_is_bounded():
    schema: dict = {"type": "object", "properties": {}}
    node = schema
    for _ in range(200):
        child: dict = {"type": "object", "properties": {}}
        node["properties"]["child"] = child
        node = child
    value = example_from_schema(schema)
    assert isinstance(value, dict)  # terminated instead of recursing forever


def test_determinism():
    schema = {
        "type": "object",
        "properties": {"guid": {"type": "string"}, "value": {"type": "number"}},
    }
    assert example_from_schema(schema) == example_from_schema(schema)
