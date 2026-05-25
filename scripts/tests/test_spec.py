"""PostgreSQL Memory System v2.3.0 - Spec API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.spec_api import (
    create_spec, get_spec, update_spec, list_specs, delete_spec,
    link_spec_to_plan, get_spec_plan_links, derive_spec,
    validate_plan_against_spec,
)
from lib.task_plan_api import create_plan, delete_plan
from lib.agent_api import register_agent
from lib.connection import execute

_cleanup_specs = []
_cleanup_plans = []
_cleanup_agents = []
_passed = 0
_failed = 0


def _cleanup():
    for spec_id in _cleanup_specs:
        try:
            execute("DELETE FROM spec_plan_links WHERE spec_id = %s", (spec_id,))
            execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s", (spec_id, spec_id))
            execute("DELETE FROM entity_tags WHERE entity_id = %s AND entity_type = 'SPEC'", (spec_id,))
            execute("DELETE FROM spec_meta WHERE entity_id = %s", (spec_id,))
            execute("DELETE FROM entities WHERE entity_id = %s AND entity_type = 'SPEC'", (spec_id,))
        except Exception:
            pass
    for plan_id in _cleanup_plans:
        try:
            delete_plan(plan_id)
        except Exception:
            pass
    for agent_id in _cleanup_agents:
        try:
            execute("DELETE FROM agent_session WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_registry WHERE agent_id = %s", (agent_id,))
        except Exception:
            pass
    _cleanup_specs.clear()
    _cleanup_plans.clear()
    _cleanup_agents.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def _make_agent(prefix="spec_agent"):
    agent_id = prefix + "_" + uuid.uuid4().hex[:8]
    register_agent(agent_id=agent_id, agent_name=prefix + " agent")
    _cleanup_agents.append(agent_id)
    return agent_id


def test_create_spec():
    try:
        entity_data = {
            "title": "test spec " + uuid.uuid4().hex[:8],
            "content": "spec content",
            "category": "requirement",
            "importance": 7,
        }
        spec_meta = {
            "spec_version": 1,
            "spec_status": "DRAFT",
            "complexity": "MEDIUM",
        }
        spec_id = create_spec(entity_data, spec_meta)
        ok = spec_id is not None and isinstance(spec_id, int)
        if ok:
            _cleanup_specs.append(spec_id)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_spec: " + status)
    return ok


def test_get_spec():
    try:
        uid = uuid.uuid4().hex[:8]
        entity_data = {
            "title": "get spec " + uid,
            "content": "get spec content",
            "summary": "get spec summary",
            "category": "feature",
            "importance": 8,
        }
        spec_meta = {
            "spec_version": 2,
            "spec_status": "APPROVED",
            "acceptance_criteria": ["ac1", "ac2"],
            "spec_constraints": {"max_latency": 100},
            "spec_scope": "module",
            "complexity": "HIGH",
        }
        spec_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(spec_id)
        result = get_spec(spec_id)
        ok = (
            result is not None
            and result.get("entity_id") == spec_id
            and result.get("title") == "get spec " + uid
            and result.get("spec_status") == "APPROVED"
            and result.get("spec_version") == 2
            and result.get("complexity") == "HIGH"
        )
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_spec: " + status)
    return ok


def test_update_spec():
    try:
        entity_data = {
            "title": "update spec before " + uuid.uuid4().hex[:8],
            "content": "before content",
        }
        spec_meta = {"spec_status": "DRAFT", "complexity": "LOW"}
        spec_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(spec_id)
        updated = update_spec(
            spec_id,
            entity_data={"title": "update spec after", "status": "ACTIVE"},
            spec_meta={"spec_status": "APPROVED"},
        )
        fetched = get_spec(spec_id)
        ok = (
            updated
            and fetched is not None
            and fetched.get("title") == "update spec after"
            and fetched.get("spec_status") == "APPROVED"
        )
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update_spec: " + status)
    return ok


def test_list_specs():
    try:
        for i in range(3):
            entity_data = {
                "title": "list spec " + uuid.uuid4().hex[:8],
                "content": "list content " + str(i),
            }
            spec_meta = {"spec_status": "DRAFT"}
            sid = create_spec(entity_data, spec_meta)
            _cleanup_specs.append(sid)
        results = list_specs()
        ok = results is not None and len(results) >= 3
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_list_specs: " + status)
    return ok


def test_delete_spec():
    try:
        entity_data = {
            "title": "delete spec " + uuid.uuid4().hex[:8],
            "content": "delete content",
        }
        spec_meta = {"spec_status": "DRAFT"}
        spec_id = create_spec(entity_data, spec_meta)
        deleted = delete_spec(spec_id)
        fetched = get_spec(spec_id)
        ok = deleted and fetched is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_delete_spec: " + status)
    return ok


def test_link_spec_to_plan():
    try:
        agent_id = _make_agent("spec_link")
        entity_data = {
            "title": "link spec " + uuid.uuid4().hex[:8],
            "content": "link content",
            "owned_by_agent": agent_id,
        }
        spec_meta = {"spec_status": "APPROVED"}
        spec_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(spec_id)
        plan_id = create_plan(agent_id=agent_id, goal="link plan goal")
        _cleanup_plans.append(plan_id)
        link_id = link_spec_to_plan(spec_id, plan_id)
        ok = link_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_link_spec_to_plan: " + status)
    return ok


def test_get_spec_plan_links():
    try:
        agent_id = _make_agent("spec_plink")
        entity_data = {
            "title": "plink spec " + uuid.uuid4().hex[:8],
            "content": "plink content",
            "owned_by_agent": agent_id,
        }
        spec_meta = {"spec_status": "APPROVED"}
        spec_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(spec_id)
        plan_id = create_plan(agent_id=agent_id, goal="plink plan goal")
        _cleanup_plans.append(plan_id)
        link_spec_to_plan(spec_id, plan_id)
        links = get_spec_plan_links(spec_id)
        ok = links is not None and len(links) >= 1 and links[0].get("plan_id") == plan_id
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_spec_plan_links: " + status)
    return ok


def test_derive_spec():
    try:
        entity_data = {
            "title": "parent spec " + uuid.uuid4().hex[:8],
            "content": "parent content",
        }
        spec_meta = {"spec_status": "APPROVED", "complexity": "HIGH"}
        parent_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(parent_id)
        child_entity = {
            "title": "child spec " + uuid.uuid4().hex[:8],
            "content": "child content",
        }
        child_meta = {"spec_status": "DRAFT"}
        child_id = derive_spec(parent_id, child_entity, child_meta)
        ok = child_id is not None
        if ok:
            _cleanup_specs.append(child_id)
            fetched = get_spec(child_id)
            ok = (
                fetched is not None
                and fetched.get("parent_spec_id") == parent_id
                and fetched.get("complexity") == "HIGH"
            )
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_derive_spec: " + status)
    return ok


def test_validate_plan_against_spec():
    try:
        agent_id = _make_agent("spec_validate")
        entity_data = {
            "title": "validate spec " + uuid.uuid4().hex[:8],
            "content": "validate content",
            "owned_by_agent": agent_id,
        }
        spec_meta = {
            "spec_status": "APPROVED",
            "acceptance_criteria": ["must pass all tests", "must handle errors"],
            "spec_constraints": {"blocked": False},
            "complexity": "MEDIUM",
        }
        spec_id = create_spec(entity_data, spec_meta)
        _cleanup_specs.append(spec_id)
        plan_id = create_plan(agent_id=agent_id, goal="validate plan goal", priority=8)
        _cleanup_plans.append(plan_id)
        link_spec_to_plan(spec_id, plan_id)
        result = validate_plan_against_spec(spec_id, plan_id)
        ok = result is not None and result.get("valid") is True and len(result.get("errors", [])) == 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_validate_plan_against_spec: " + status)
    return ok


def run_all():
    tests = [
        test_create_spec, test_get_spec, test_update_spec,
        test_list_specs, test_delete_spec, test_link_spec_to_plan,
        test_get_spec_plan_links, test_derive_spec,
        test_validate_plan_against_spec,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Spec: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()
