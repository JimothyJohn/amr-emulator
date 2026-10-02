"""The conversion oracle: compare() must catch structural drift, ignore prose.

This module is what proves a PDF conversion equals the official 3.5.4
swagger.json, so a false "equivalent" here silently ships a wrong spec. Every
kind of structural difference must surface; every kind of prose-only
difference must not.
"""

import copy

from amr_spec_scraper.validate import compare, schema_signature
from hypothesis import example, given
from hypothesis import strategies as st


def _doc() -> dict:
    return {
        "swagger": "2.0",
        "paths": {
            "/robots": {
                "get": {
                    "description": "List robots",
                    "parameters": [
                        {"in": "query", "name": "limit", "type": "integer"},
                        {"in": "path", "name": "site_id", "type": "string"},
                    ],
                    "produces": ["application/json"],
                    "responses": {
                        "200": {"schema": {"$ref": "#/definitions/Robot"}},
                        "default": {"description": "error"},
                    },
                },
                "post": {
                    "parameters": [
                        {"in": "body", "name": "body", "schema": {"$ref": "#/definitions/Robot"}}
                    ],
                    "responses": {"201": {"schema": {"$ref": "#/definitions/Robot"}}},
                },
            }
        },
        "definitions": {
            "Robot": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "battery": {"type": "number", "format": "float"},
                    "modes": {"type": "array", "items": {"$ref": "#/definitions/Mode"}},
                },
            },
            "Mode": {"enum": ["moving", "charging"]},
        },
    }


def test_identical_documents_are_equivalent():
    assert compare(_doc(), _doc()) == []


def test_prose_only_differences_are_ignored():
    converted = _doc()
    converted["paths"]["/robots"]["get"]["description"] = "totally different prose"
    converted["paths"]["/robots"]["get"]["responses"]["200"]["description"] = "OK!"
    converted["definitions"]["Robot"]["properties"]["name"]["description"] = "robot name"
    assert compare(converted, _doc()) == []


def test_missing_operation_is_reported():
    converted = _doc()
    del converted["paths"]["/robots"]["post"]
    assert compare(converted, _doc()) == ["missing operation: POST /robots"]


def test_extra_operation_is_reported():
    converted = _doc()
    converted["paths"]["/robots"]["delete"] = {"responses": {"204": {"description": "gone"}}}
    assert compare(converted, _doc()) == ["extra operation: DELETE /robots"]


def test_changed_body_schema_is_reported():
    converted = _doc()
    converted["paths"]["/robots"]["post"]["parameters"][0]["schema"] = {"type": "string"}
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("POST /robots body:")


def test_changed_query_param_type_is_reported():
    converted = _doc()
    converted["paths"]["/robots"]["get"]["parameters"][0]["type"] = "string"
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("GET /robots params:")


def test_changed_response_schema_is_reported():
    converted = _doc()
    converted["paths"]["/robots"]["get"]["responses"]["200"]["schema"] = {"type": "string"}
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("GET /robots responses:")


def test_non_numeric_response_codes_are_ignored():
    converted = _doc()
    converted["paths"]["/robots"]["get"]["responses"]["default"] = {"schema": {"type": "string"}}
    assert compare(converted, _doc()) == []


def test_changed_produces_is_reported():
    converted = _doc()
    converted["paths"]["/robots"]["get"]["produces"] = ["text/html"]
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("GET /robots produces:")


def test_missing_and_extra_definitions_are_reported():
    converted = _doc()
    del converted["definitions"]["Mode"]
    converted["definitions"]["Invented"] = {"type": "object"}
    assert compare(converted, _doc()) == [
        "missing definition: Mode",
        "extra definition: Invented",
    ]


def test_changed_definition_property_is_reported():
    converted = _doc()
    converted["definitions"]["Robot"]["properties"]["battery"] = {"type": "string"}
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("definition Robot:")


def test_changed_enum_values_are_reported():
    converted = _doc()
    converted["definitions"]["Mode"]["enum"] = ["moving", "idle"]
    problems = compare(converted, _doc())
    assert len(problems) == 1
    assert problems[0].startswith("definition Mode:")


def test_itemless_array_equals_object_item_array():
    # The PDF renders both as "< object > array"; they must compare equal.
    assert schema_signature({"type": "array"}) == schema_signature(
        {"type": "array", "items": {"type": "object"}}
    )


def test_converter_warnings_fail_validation():
    converted = _doc()
    converted["x-mir-converter-warnings"] = ["unrecognized schema notation on page 12"]
    assert compare(converted, _doc()) == ["unrecognized schema notation on page 12"]


# --- properties: signatures must be stable under prose and deep copies -------

_schemas = st.deferred(
    lambda: st.one_of(
        st.fixed_dictionaries({"type": st.sampled_from(["string", "boolean"])}),
        st.fixed_dictionaries(
            {"type": st.just("integer"), "format": st.sampled_from(["int32", "int64"])}
        ),
        st.fixed_dictionaries({"$ref": st.just("#/definitions/Robot")}),
        st.fixed_dictionaries({"enum": st.lists(st.text(max_size=5), max_size=3)}),
        st.fixed_dictionaries({"type": st.just("array"), "items": _schemas}),
        st.fixed_dictionaries(
            {
                "type": st.just("object"),
                "properties": st.dictionaries(
                    st.text(min_size=1, max_size=8), _schemas, max_size=3
                ),
            }
        ),
    )
)


@st.composite
def _docs(draw):
    paths = draw(
        st.dictionaries(
            st.text(min_size=1, max_size=10).map(lambda s: f"/{s}"),
            st.fixed_dictionaries(
                {
                    "get": st.fixed_dictionaries(
                        {
                            "responses": st.fixed_dictionaries(
                                {"200": st.fixed_dictionaries({"schema": _schemas})}
                            )
                        }
                    )
                }
            ),
            min_size=1,
            max_size=4,
        )
    )
    definitions = draw(st.dictionaries(st.text(min_size=1, max_size=8), _schemas, max_size=4))
    return {"swagger": "2.0", "paths": paths, "definitions": definitions}


def _sprinkle_prose(node, *, bare_map: bool = False) -> None:
    """Add description prose everywhere it is legal swagger — not inside bare
    maps (paths, properties, responses) where 'description' would be a name.
    Bare maps are tracked by position, not by key sniffing: a property named
    "type" must not make its properties map look like a schema."""
    if not isinstance(node, dict):
        return
    if not bare_map and any(k in node for k in ("type", "$ref", "enum", "schema", "responses")):
        node.setdefault("description", "prose the comparison must ignore")
    for key, value in node.items():
        _sprinkle_prose(
            value,
            bare_map=not bare_map and key in ("paths", "properties", "responses", "definitions"),
        )


@given(_docs())
def test_any_document_equals_itself(doc):
    assert compare(copy.deepcopy(doc), doc) == []


@given(_docs())
@example(
    # A property literally named "type" must not make its bare properties map
    # look like a schema and receive prose as a phantom property.
    {
        "swagger": "2.0",
        "paths": {"/0": {"get": {"responses": {"200": {"schema": {"type": "string"}}}}}},
        "definitions": {
            "0": {"type": "object", "properties": {"type": {"$ref": "#/definitions/Robot"}}}
        },
    }
)
def test_prose_never_affects_equivalence(doc):
    prosed = copy.deepcopy(doc)
    _sprinkle_prose(prosed["paths"])
    for schema in prosed["definitions"].values():
        _sprinkle_prose(schema)
    assert compare(prosed, doc) == []


@given(_docs())
def test_missing_and_extra_are_mirror_images(doc):
    truncated = copy.deepcopy(doc)
    path = next(iter(truncated["paths"]))
    del truncated["paths"][path]
    assert compare(truncated, doc) == [f"missing operation: GET {path}"]
    assert compare(doc, truncated) == [f"extra operation: GET {path}"]
