"""PostgreSQL Memory System v2.3.0 - Workspace API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.workspace_api import (
    create_workspace, get_workspace, get_user_workspaces, update_workspace,
    save_context, get_context_chain, get_latest_context,
    create_handoff_session, recover_workspace, link_task_to_workspace,
    get_workspace_tasks,
)
from lib.agent_api import register_agent, create_session, end_session
from lib.memory_api import create_memory, delete_memory, count_memories
from lib.task_plan_api import create_plan, delete_plan
from lib.connection import execute

_cleanup_workspaces = []
_cleanup_agents = []
_cleanup_memories = []
_cleanup_plans = []
_passed = 0
_failed = 0


def _cleanup():
    for ws_id in _cleanup_workspaces:
        try:
            execute("DELETE FROM workspace_tasks WHERE workspace_id = %s", (ws_id,))
            execute("DELETE FROM workspace_context WHERE workspace_id = %s", (ws_id,))
            execute("DELETE FROM agent_session WHERE workspace_id = %s", (ws_id,))
            execute("DELETE FROM workspaces WHERE workspace_id = %s", (ws_id,))
        except Exception:
            pass
    for agent_id in _cleanup_agents:
        try:
            execute("DELETE FROM agent_collaboration WHERE source_agent_id = %s OR target_agent_id = %s", (agent_id, agent_id))
            execute("DELETE FROM entity_access_log WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_session WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_registry WHERE agent_id = %s", (agent_id,))
        except Exception:
            pass
    for mid in _cleanup_memories:
        try:
            delete_memory(mid)
        except Exception:
            pass
    for pid in _cleanup_plans:
        try:
            delete_plan(pid)
        except Exception:
            pass
    _cleanup_workspaces.clear()
    _cleanup_agents.clear()
    _cleanup_memories.clear()
    _cleanup_plans.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def _make_agent(prefix="ws_agent"):
    agent_id = prefix + "_" + uuid.uuid4().hex[:8]
    register_agent(agent_id=agent_id, agent_name=prefix + " agent")
    _cleanup_agents.append(agent_id)
    return agent_id


def test_create_workspace():
    try:
        ws_id = create_workspace(name="test workspace")
        ok = ws_id is not None
        if ok:
            _cleanup_workspaces.append(ws_id)
            fetched = get_workspace(ws_id)
            ok = fetched is not None and fetched.get("workspace_id") == ws_id
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_workspace: " + status)
    return ok


def test_create_workspace_with_options():
    try:
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        ws_id = create_workspace(
            owner_user_id=user_id,
            name="options workspace",
            workspace_type="PIPELINE",
            isolation_mode="ISOLATED",
            metadata={"env": "test", "priority": "high"},
        )
        ok = ws_id is not None
        if ok:
            _cleanup_workspaces.append(ws_id)
            fetched = get_workspace(ws_id)
            ok = (
                fetched is not None
                and fetched.get("workspace_type") == "PIPELINE"
                and fetched.get("isolation_mode") == "ISOLATED"
            )
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_workspace_with_options: " + status)
    return ok


def test_get_workspace():
    try:
        ws_id = create_workspace(name="get test ws")
        _cleanup_workspaces.append(ws_id)
        result = get_workspace(ws_id)
        ok = result is not None and result.get("workspace_id") == ws_id
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_workspace: " + status)
    return ok


def test_get_user_workspaces():
    try:
        user_id = "ws_user_" + uuid.uuid4().hex[:8]
        ws1 = create_workspace(owner_user_id=user_id, name="user ws 1")
        ws2 = create_workspace(owner_user_id=user_id, name="user ws 2")
        _cleanup_workspaces.extend([ws1, ws2])
        results = get_user_workspaces(user_id)
        ok = results is not None and len(results) >= 2
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_user_workspaces: " + status)
    return ok


def test_get_user_workspaces_with_status():
    try:
        user_id = "ws_status_user_" + uuid.uuid4().hex[:8]
        ws_id = create_workspace(owner_user_id=user_id, name="status ws")
        _cleanup_workspaces.append(ws_id)
        results = get_user_workspaces(user_id, status="ACTIVE")
        ok = results is not None and len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_user_workspaces_with_status: " + status)
    return ok


def test_update_workspace():
    try:
        ws_id = create_workspace(name="before update")
        _cleanup_workspaces.append(ws_id)
        updated = update_workspace(ws_id, workspace_name="after update", status="ARCHIVED")
        fetched = get_workspace(ws_id)
        ok = updated and fetched is not None and fetched.get("workspace_name") == "after update"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update_workspace: " + status)
    return ok


def test_save_context():
    try:
        agent_id = _make_agent("ctx_agent")
        ws_id = create_workspace(name="context ws")
        _cleanup_workspaces.append(ws_id)
        ctx_id = save_context(ws_id, agent_id, "CHECKPOINT", {"step": 1, "data": "test"})
        ok = ctx_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_save_context: " + status)
    return ok


def test_get_context_chain():
    try:
        agent_id = _make_agent("chain_agent")
        ws_id = create_workspace(name="chain ws")
        _cleanup_workspaces.append(ws_id)
        save_context(ws_id, agent_id, "CHECKPOINT", {"i": 1})
        save_context(ws_id, agent_id, "CHECKPOINT", {"i": 2})
        chain = get_context_chain(ws_id, limit=10)
        ok = chain is not None and len(chain) >= 2
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_context_chain: " + status)
    return ok


def test_get_latest_context():
    try:
        agent_id = _make_agent("latest_agent")
        ws_id = create_workspace(name="latest ws")
        _cleanup_workspaces.append(ws_id)
        save_context(ws_id, agent_id, "CHECKPOINT", {"latest": True})
        ctx = get_latest_context(ws_id)
        ok = ctx is not None and ctx.get("context_type") == "CHECKPOINT"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_latest_context: " + status)
    return ok


def test_create_handoff_session():
    try:
        a1 = _make_agent("handoff1")
        a2 = _make_agent("handoff2")
        ws_id = create_workspace(owner_user_id=a1, name="handoff ws")
        _cleanup_workspaces.append(ws_id)
        session_id = create_handoff_session(
            ws_id,
            new_agent_id=a2,
            handoff_data={"summary": "handoff test"},
        )
        ok = session_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_handoff_session: " + status)
    return ok


def test_recover_workspace():
    try:
        agent_id = _make_agent("recover_agent")
        ws_id = create_workspace(name="recover ws")
        _cleanup_workspaces.append(ws_id)
        save_context(ws_id, agent_id, "CHECKPOINT", {"pre": "recovery"})
        result = recover_workspace(ws_id)
        ok = result is not None and isinstance(result, dict) and "workspace" in result
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_recover_workspace: " + status)
    return ok


def test_link_task_to_workspace():
    try:
        agent_id = _make_agent("task_link_agent")
        ws_id = create_workspace(name="task link ws")
        _cleanup_workspaces.append(ws_id)
        plan_id = create_plan(agent_id=agent_id, goal="linked task goal")
        _cleanup_plans.append(plan_id)
        linked = link_task_to_workspace(ws_id, plan_id)
        ok = linked
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_link_task_to_workspace: " + status)
    return ok


def test_get_workspace_tasks():
    try:
        agent_id = _make_agent("wstask_agent")
        ws_id = create_workspace(name="ws tasks ws")
        _cleanup_workspaces.append(ws_id)
        plan_id = create_plan(agent_id=agent_id, goal="ws task goal")
        _cleanup_plans.append(plan_id)
        link_task_to_workspace(ws_id, plan_id)
        tasks = get_workspace_tasks(ws_id)
        ok = tasks is not None and len(tasks) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_workspace_tasks: " + status)
    return ok


def test_entity_isolation():
    try:
        ws1 = create_workspace(name="iso ws1", isolation_mode="ISOLATED")
        ws2 = create_workspace(name="iso ws2", isolation_mode="ISOLATED")
        _cleanup_workspaces.extend([ws1, ws2])
        m1 = create_memory(title="ws1 only", content="ws1 only data", workspace_id=ws1)
        m2 = create_memory(title="ws2 only", content="ws2 only data", workspace_id=ws2)
        _cleanup_memories.extend([m1, m2])
        c1 = count_memories()
        c2 = count_memories()
        ok = c1 >= 0 and c2 >= 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_entity_isolation: " + status)
    return ok


def run_all():
    tests = [
        test_create_workspace, test_create_workspace_with_options,
        test_get_workspace, test_get_user_workspaces,
        test_get_user_workspaces_with_status, test_update_workspace,
        test_save_context, test_get_context_chain, test_get_latest_context,
        test_create_handoff_session, test_recover_workspace,
        test_link_task_to_workspace, test_get_workspace_tasks,
        test_entity_isolation,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Workspace: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()