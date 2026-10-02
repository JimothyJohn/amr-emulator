from amr_spec_scraper.diff import api_diff_markdown

OLD = {
    "paths": {
        "/status": {"get": {"responses": {"200": {"schema": {"$ref": "#/definitions/A"}}}}},
        "/legacy": {"get": {"responses": {"200": {}}}},
    },
    "definitions": {"A": {"type": "object", "properties": {"x": {"type": "string"}}}},
}
NEW = {
    "paths": {
        "/status": {
            "get": {"responses": {"200": {"schema": {"$ref": "#/definitions/A"}}}},
            "put": {"responses": {"200": {}}},
        },
    },
    "definitions": {
        "A": {"type": "object", "properties": {"x": {"type": "integer"}}},
        "B": {"type": "object"},
    },
}


def test_diff_reports_all_change_classes():
    md = api_diff_markdown(OLD, NEW, "1.0.0", "2.0.0")
    assert "API changes 1.0.0 → 2.0.0" in md
    assert "`PUT /status`" in md  # added op
    assert "`GET /legacy`" in md  # removed op
    assert "Added definitions" in md and "`B`" in md
    assert "Changed definitions" in md and "`A`" in md


def test_diff_identical_docs():
    md = api_diff_markdown(OLD, OLD, "1.0.0", "1.0.0")
    assert "_No structural changes._" in md
