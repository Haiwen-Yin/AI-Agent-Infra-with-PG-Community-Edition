"""AI Agent Infra v3.6.2 - PG Community Edition - Spec API Tests"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.spec_api import (
    create_spec, get_spec, update_spec, list_specs,
    link_spec_to_plan, get_spec_plan_links,
    validate_spec, derive_spec, delete_spec,
)
from lib.agent_api import register_agent
from lib.task_plan_api import create_plan
from lib.connection import execute, close_pool

TS = str(int(time.time()))
TEST_AGENT = "pg-spec-agent-" + TS
AC = ["All items processed", "Error rate < 1%", "Throughput > 100/s"]
_entity_id = None
_plan_id = None
_derived_id = None


def test_create_spec():
    global _entity_id
    _entity_id = create_spec(
        title="PG Test Spec " + TS,
        summary="A PG test specification",
        content="Process all items with low error rate",
        category="test-spec",
        importance=8,
        owned_by_agent=TEST_AGENT,
        visibility="SHARED",
        spec_scope="processing",
        complexity="HIGH",
        acceptance_criteria=AC,
        constraints={"max_latency_ms": 500, "min_accuracy": 0.99},
    )
    assert isinstance(_entity_id, int)
    assert _entity_id > 0
    print(f"PASS: test_create_spec (id={_entity_id})")


def test_get_spec():
    spec = get_spec(_entity_id)
    assert spec is not None
    assert spec["title"] == "PG Test Spec " + TS
    assert spec["entity_type"] == "SPEC"
    assert spec["spec_status"] == "DRAFT"
    print(f"PASS: test_get_spec (title={spec['title']})")


def test_update_spec():
    ok = update_spec(_entity_id, title="Updated PG Spec " + TS, spec_status="APPROVED")
    assert ok
    spec = get_spec(_entity_id)
    assert spec["title"] == "Updated PG Spec " + TS
    assert spec["spec_status"] == "APPROVED"
    print("PASS: test_update_spec")


def test_list_specs():
    results = list_specs(spec_scope="processing")
    assert isinstance(results, list)
    assert len(results) >= 1
    print(f"PASS: test_list_specs (found={len(results)})")


def test_link_spec_to_plan():
    global _plan_id
    try:
        register_agent(TEST_AGENT, "PG Spec Test Agent", agent_type="test")
    except Exception:
        pass
    _plan_id = create_plan(
        agent_id=TEST_AGENT,
        goal="Execute spec " + TS,
        priority=5,
    )
    assert isinstance(_plan_id, int)
    assert _plan_id > 0
    link_id = link_spec_to_plan(_entity_id, _plan_id, "DRIVES", strength=1.0)
    assert link_id is not None
    print(f"PASS: test_link_spec_to_plan (plan_id={_plan_id}, link_id={link_id})")


def test_get_spec_plan_links():
    links = get_spec_plan_links(_entity_id)
    assert isinstance(links, list)
    assert len(links) >= 1
    assert links[0]["link_type"] == "DRIVES"
    print(f"PASS: test_get_spec_plan_links (found={len(links)})")


def test_validate_spec():
    report = validate_spec(_entity_id)
    assert isinstance(report, dict)
    assert "valid" in report
    assert "errors" in report
    assert isinstance(report["errors"], list)
    print(f"PASS: test_validate_spec (valid={report['valid']}, errors={len(report['errors'])})")


def test_derive_spec():
    global _derived_id
    _derived_id = derive_spec(_entity_id, "Derived PG Spec " + TS)
    assert isinstance(_derived_id, int)
    assert _derived_id > 0
    derived = get_spec(_derived_id)
    assert derived is not None
    assert derived["title"] == "Derived PG Spec " + TS
    print(f"PASS: test_derive_spec (id={_derived_id})")


def test_delete_spec():
    ok = delete_spec(_entity_id)
    assert ok
    spec = get_spec(_entity_id)
    assert spec is None
    print("PASS: test_delete_spec")


def _cleanup():
    for eid in [_derived_id, _entity_id]:
        if eid is not None:
            try:
                execute("DELETE FROM spec_plan_links WHERE spec_id = %s", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM entity_edges WHERE source_id = %s AND source_type = 'SPEC'", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM entity_edges WHERE target_id = %s AND target_type = 'SPEC'", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM spec_meta WHERE entity_id = %s AND entity_type = 'SPEC'", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'SPEC'", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM entity_embeddings WHERE entity_id = %s AND entity_type = 'SPEC'", [eid])
            except Exception:
                pass
            try:
                execute("DELETE FROM entities WHERE entity_id = %s AND entity_type = 'SPEC'", [eid])
            except Exception:
                pass
    if _plan_id is not None:
        try:
            execute("DELETE FROM plan_steps WHERE plan_id = %s", [_plan_id])
        except Exception:
            pass
        try:
            execute("DELETE FROM task_plans WHERE plan_id = %s", [_plan_id])
        except Exception:
            pass
    try:
        execute("DELETE FROM agent_session WHERE agent_id = %s", [TEST_AGENT])
    except Exception:
        pass
    try:
        execute("DELETE FROM agent_registry WHERE agent_id = %s", [TEST_AGENT])
    except Exception:
        pass


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_create_spec,
        test_get_spec,
        test_update_spec,
        test_list_specs,
        test_link_spec_to_plan,
        test_get_spec_plan_links,
        test_validate_spec,
        test_derive_spec,
        test_delete_spec,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nSpec Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
