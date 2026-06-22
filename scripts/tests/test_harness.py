"""AI Agent Infra v3.7.3 - PG Community Edition - Harness Template API Tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.harness_api import (
    create_harness_template, get_harness_template,
    update_harness_template, list_harness_templates,
    instantiate_harness, validate_harness_input,
    delete_harness_template,
)
from lib.connection import close_pool

INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "role": {"type": "string", "default": "Analyst"},
        "domain": {"type": "string", "default": "general"},
        "input": {"type": "string", "default": ""},
    },
    "required": ["role", "domain"],
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "result": {"type": "string"},
        "confidence": {"type": "number"},
    },
}

_entity_id = None


def test_create_harness_template():
    global _entity_id
    _entity_id = create_harness_template(
        title="PG Test Harness " + str(int(__import__('time').time())),
        summary="A PG test harness template",
        content="You are a {role} specializing in {domain}. Analyze: {input}",
        category="test-harness-pg",
        input_schema=INPUT_SCHEMA,
        output_schema=OUTPUT_SCHEMA,
        execution_mode="SEQUENTIAL",
        importance=7,
        owned_by_agent="test-agent-pg",
        visibility="SHARED",
    )
    assert isinstance(_entity_id, int)
    assert _entity_id > 0
    print(f"PASS: test_create_harness_template (id={_entity_id})")


def test_get_harness_template():
    tpl = get_harness_template(_entity_id)
    assert tpl is not None
    assert "PG Test Harness" in tpl["title"]
    assert tpl["category"] == "test-harness-pg"
    assert tpl["execution_mode"] == "SEQUENTIAL"
    print(f"PASS: test_get_harness_template (title={tpl['title']})")


def test_update_harness_template():
    ok = update_harness_template(_entity_id, title="Updated PG Harness")
    assert ok
    tpl = get_harness_template(_entity_id)
    assert tpl["title"] == "Updated PG Harness"
    print("PASS: test_update_harness_template")


def test_list_harness_templates():
    results = list_harness_templates(category="test-harness-pg")
    assert len(results) >= 1
    print(f"PASS: test_list_harness_templates (found={len(results)})")


def test_instantiate_harness():
    instance_id = instantiate_harness(
        _entity_id,
        variable_values={"role": "Engineer", "domain": "testing", "input": "sample PG data"},
        agent_id="test-agent-pg",
    )
    assert isinstance(instance_id, int)
    assert instance_id > 0
    print(f"PASS: test_instantiate_harness (instance_id={instance_id})")


def test_validate_harness_input():
    result = validate_harness_input(
        _entity_id,
        input_values={"role": "Engineer", "domain": "testing"},
    )
    assert result["valid"] is True
    assert len(result["errors"]) == 0

    result_bad = validate_harness_input(
        _entity_id,
        input_values={"role": "Engineer"},
    )
    assert result_bad["valid"] is False
    assert len(result_bad["errors"]) >= 1
    print("PASS: test_validate_harness_input")


def _cleanup():
    global _entity_id
    if _entity_id:
        try:
            delete_harness_template(_entity_id)
        except Exception:
            pass
        _entity_id = None


def run_all():
    global _entity_id
    passed = 0
    failed = 0

    tests = [
        test_create_harness_template,
        test_get_harness_template,
        test_update_harness_template,
        test_list_harness_templates,
        test_instantiate_harness,
        test_validate_harness_input,
    ]

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nHarness Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
