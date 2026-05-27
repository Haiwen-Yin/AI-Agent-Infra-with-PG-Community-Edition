"""PostgreSQL Memory System v2.3.1 - Harness API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.harness_api import (
    create_harness_template, get_harness_template, update_harness_template,
    delete_harness_template, list_harness_templates, get_template_with_variables,
    instantiate_harness_template, count_harness_templates,
)
from lib.agent_api import register_agent
from lib.connection import execute

_cleanup_ids = []
_cleanup_agents = []
_passed = 0
_failed = 0


def _cleanup():
    for eid in _cleanup_ids:
        try:
            delete_harness_template(eid)
        except Exception:
            pass
    for agent_id in _cleanup_agents:
        try:
            execute("DELETE FROM agent_session WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_registry WHERE agent_id = %s", (agent_id,))
        except Exception:
            pass
    _cleanup_ids.clear()
    _cleanup_agents.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "description": "User name", "default": "World"},
        "place": {"type": "string", "description": "Place name"},
    },
    "required": ["place"],
}

OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "greeting": {"type": "string"},
    },
}


def test_create():
    try:
        eid = create_harness_template(
            title="test_template_" + uuid.uuid4().hex[:8],
            summary="a test harness template",
            content="Hello {name}, welcome to {place}",
            category="unittest",
            importance=5,
            execution_mode="SEQUENTIAL",
        )
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create: " + status)
    return ok


def test_create_with_schemas():
    try:
        eid = create_harness_template(
            title="schema_template_" + uuid.uuid4().hex[:8],
            summary="template with schemas",
            content="Hello {name}, welcome to {place}",
            category="unittest",
            input_schema=INPUT_SCHEMA,
            output_schema=OUTPUT_SCHEMA,
            execution_mode="SEQUENTIAL",
        )
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
            fetched = get_harness_template(eid)
            ok = fetched is not None and fetched.get("input_schema") is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_with_schemas: " + status)
    return ok


def test_get():
    try:
        eid = create_harness_template(
            title="get_test_" + uuid.uuid4().hex[:8],
            summary="get test template",
            content="Test content",
        )
        _cleanup_ids.append(eid)
        result = get_harness_template(eid)
        ok = result is not None and result.get("entity_id") == eid
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get: " + status)
    return ok


def test_get_nonexistent():
    try:
        result = get_harness_template(999999999999)
        ok = result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_nonexistent: " + status)
    return ok


def test_update():
    try:
        eid = create_harness_template(
            title="update_test_" + uuid.uuid4().hex[:8],
            summary="before update",
            content="Before {x}",
        )
        _cleanup_ids.append(eid)
        updated = update_harness_template(eid, summary="after update", execution_mode="PARALLEL")
        fetched = get_harness_template(eid)
        ok = updated and fetched is not None and fetched.get("summary") == "after update"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update: " + status)
    return ok


def test_delete():
    try:
        eid = create_harness_template(
            title="delete_test_" + uuid.uuid4().hex[:8],
            summary="delete test",
            content="Delete me",
        )
        deleted = delete_harness_template(eid)
        result = get_harness_template(eid)
        ok = deleted and result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_delete: " + status)
    return ok


def test_list_harness_templates():
    try:
        eid = create_harness_template(
            title="list_test_" + uuid.uuid4().hex[:8],
            summary="list test",
            content="List me",
            category="list_test",
        )
        _cleanup_ids.append(eid)
        results = list_harness_templates(category="list_test", limit=10)
        ok = results is not None and len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_list_harness_templates: " + status)
    return ok


def test_list_by_execution_mode():
    try:
        eid = create_harness_template(
            title="mode_test_" + uuid.uuid4().hex[:8],
            summary="mode test",
            content="Mode content",
            execution_mode="PARALLEL",
        )
        _cleanup_ids.append(eid)
        results = list_harness_templates(execution_mode="PARALLEL", limit=10)
        ok = results is not None and isinstance(results, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_list_by_execution_mode: " + status)
    return ok


def test_get_template_with_variables():
    try:
        eid = create_harness_template(
            title="vars_test_" + uuid.uuid4().hex[:8],
            summary="variables test",
            content="Hello {name}",
            input_schema=INPUT_SCHEMA,
        )
        _cleanup_ids.append(eid)
        result = get_template_with_variables(eid)
        ok = result is not None and "variables" in result
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_template_with_variables: " + status)
    return ok


def test_instantiate_harness_template():
    try:
        agent_id = "harness_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Harness Agent")
        _cleanup_agents.append(agent_id)
        eid = create_harness_template(
            title="instantiate_test_" + uuid.uuid4().hex[:8],
            summary="instantiate test",
            content="Hello {name}, welcome to {place}",
            category="unittest",
        )
        _cleanup_ids.append(eid)
        instance_id = instantiate_harness_template(
            eid,
            variable_values={"name": "World", "place": "PostgreSQL"},
            agent_id=agent_id,
        )
        ok = instance_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_instantiate_harness_template: " + status)
    return ok


def test_count_harness_templates():
    try:
        before = count_harness_templates()
        eid = create_harness_template(
            title="count_test_" + uuid.uuid4().hex[:8],
            summary="count test",
            content="Count me",
        )
        _cleanup_ids.append(eid)
        after = count_harness_templates()
        ok = after >= before + 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_count_harness_templates: " + status)
    return ok


def test_count_harness_templates_by_category():
    try:
        cat = "count_cat_" + uuid.uuid4().hex[:8]
        eid = create_harness_template(
            title="countcat_test_" + uuid.uuid4().hex[:8],
            summary="count cat test",
            content="Count me by cat",
            category=cat,
        )
        _cleanup_ids.append(eid)
        cnt = count_harness_templates(category=cat)
        ok = cnt >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_count_harness_templates_by_category: " + status)
    return ok


def run_all():
    tests = [
        test_create, test_create_with_schemas, test_get, test_get_nonexistent,
        test_update, test_delete, test_list_harness_templates,
        test_list_by_execution_mode, test_get_template_with_variables,
        test_instantiate_harness_template, test_count_harness_templates,
        test_count_harness_templates_by_category,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Harness: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()