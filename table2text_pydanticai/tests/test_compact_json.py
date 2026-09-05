from __future__ import annotations

import json

from table2text.audit import compact_json


def test_compact_json_uses_minified_valid_json():
    value = {"items": [{"id": "e1", "value": 42}], "enabled": True}

    rendered = compact_json(value)

    assert rendered == '{"items":[{"id":"e1","value":42}],"enabled":true}'
    assert json.loads(rendered) == value


def test_compact_json_never_cuts_a_complete_record():
    value = {
        "items": [
            {"id": f"e{index}", "text": "evidence" * 100}
            for index in range(250)
        ]
    }

    rendered = compact_json(value)

    assert len(rendered) > 160_000
    assert json.loads(rendered) == value
    assert rendered.endswith("]}")
