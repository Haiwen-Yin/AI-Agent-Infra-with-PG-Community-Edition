"""PostgreSQL Memory System v2.3.1 - Agent API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.agent_api import (
    register_agent, get_agent, update_agent, decommission_agent,
    heartbeat, create_session, end_session, checkpoint_session,
    get_session_chain, get_active_sessions, log_access,
    get_access_log, create_collaboration, get_collaborations,
)
from lib.memory_api import create_memory, delete_memory
from lib.workspace_api import create_workspace

_cleanup_agents = []
_cleanup_sessions = []
_cleanup_memories = []
_cleanup_workspaces = []
_passed = 0
_failed = 0


def _cleanup():
    from lib.connection import execute
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
    for ws_id in _cleanup_workspaces:
        try:
            execute("DELETE FROM workspace_context WHERE workspace_id = %s", (ws_id,))
            execute("DELETE FROM agent_session WHERE workspace_id = %s", (ws_id,))
            execute("DELETE FROM workspaces WHERE workspace_id = %s", (ws_id,))
        except Exception:
            pass
    _cleanup_agents.clear()
    _cleanup_sessions.clear()
    _cleanup_memories.clear()
    _cleanup_workspaces.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def test_register_agent():
    try:
        agent_id = "test_agent_" + uuid.uuid4().hex[:8]
        result = register_agent(agent_id=agent_id, agent_name="Test Agent")
        ok = result == agent_id
        if ok:
            _cleanup_agents.append(agent_id)
            fetched = get_agent(agent_id)
            ok = fetched is not None and fetched.get("agent_id") == agent_id
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_register_agent: " + status)
    return ok


def test_register_agent_with_options():
    try:
        agent_id = "test_agent_opts_" + uuid.uuid4().hex[:8]
        result = register_agent(
            agent_id=agent_id,
            agent_name="Full Agent",
            agent_type="worker",
            description="A test worker agent",
            capabilities={"skill1": True, "skill2": True},
            config={"timeout": 30},
        )
        ok = result == agent_id
        if ok:
            _cleanup_agents.append(agent_id)
            fetched = get_agent(agent_id)
            ok = fetched is not None and fetched.get("agent_type") == "worker"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_register_agent_with_options: " + status)
    return ok


def test_get_agent():
    try:
        agent_id = "test_get_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Get Test Agent")
        _cleanup_agents.append(agent_id)
        result = get_agent(agent_id)
        ok = result is not None and result.get("agent_id") == agent_id and result.get("agent_name") == "Get Test Agent"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_agent: " + status)
    return ok


def test_get_agent_nonexistent():
    try:
        result = get_agent("nonexistent_agent_12345")
        ok = result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_agent_nonexistent: " + status)
    return ok


def test_update_agent():
    try:
        agent_id = "test_upd_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Before Update")
        _cleanup_agents.append(agent_id)
        updated = update_agent(agent_id, agent_name="After Update", description="updated desc")
        fetched = get_agent(agent_id)
        ok = updated and fetched is not None and fetched.get("agent_name") == "After Update"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update_agent: " + status)
    return ok


def test_decommission_agent():
    try:
        agent_id = "test_decom_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Decommission Agent")
        _cleanup_agents.append(agent_id)
        decommission_agent(agent_id)
        fetched = get_agent(agent_id)
        ok = fetched is not None and fetched.get("status") == "DECOMMISSIONED"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_decommission_agent: " + status)
    return ok


def test_heartbeat():
    try:
        agent_id = "test_hb_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Heartbeat Agent")
        _cleanup_agents.append(agent_id)
        result = heartbeat(agent_id)
        ok = result
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_heartbeat: " + status)
    return ok


def test_create_session():
    try:
        agent_id = "test_sess_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Session Agent")
        _cleanup_agents.append(agent_id)
        ws_id = create_workspace(name="session workspace")
        _cleanup_workspaces.append(ws_id)
        session_id = create_session(agent_id=agent_id, workspace_id=ws_id)
        ok = session_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_session: " + status)
    return ok


def test_end_session():
    try:
        agent_id = "test_end_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="End Session Agent")
        _cleanup_agents.append(agent_id)
        ws_id = create_workspace(name="end session workspace")
        _cleanup_workspaces.append(ws_id)
        session_id = create_session(agent_id=agent_id, workspace_id=ws_id)
        ended = end_session(session_id)
        ok = ended
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_end_session: " + status)
    return ok


def test_checkpoint_session():
    try:
        agent_id = "test_cp_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Checkpoint Agent")
        _cleanup_agents.append(agent_id)
        ws_id = create_workspace(name="checkpoint workspace")
        _cleanup_workspaces.append(ws_id)
        session_id = create_session(agent_id=agent_id, workspace_id=ws_id)
        result = checkpoint_session(session_id, {"step": 3, "progress": "halfway"})
        ok = result
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_checkpoint_session: " + status)
    return ok


def test_get_session_chain():
    try:
        agent_id = "test_chain_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Chain Agent")
        _cleanup_agents.append(agent_id)
        ws_id = create_workspace(name="chain workspace")
        _cleanup_workspaces.append(ws_id)
        s1 = create_session(agent_id=agent_id, workspace_id=ws_id)
        end_session(s1)
        s2 = create_session(agent_id=agent_id, workspace_id=ws_id, predecessor_session_id=s1)
        chain = get_session_chain(s2, limit=10)
        ok = chain is not None and len(chain) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_session_chain: " + status)
    return ok


def test_get_active_sessions():
    try:
        agent_id = "test_active_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Active Agent")
        _cleanup_agents.append(agent_id)
        ws_id = create_workspace(name="active workspace")
        _cleanup_workspaces.append(ws_id)
        create_session(agent_id=agent_id, workspace_id=ws_id)
        results = get_active_sessions(agent_id=agent_id)
        ok = len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_active_sessions: " + status)
    return ok


def test_log_access():
    try:
        agent_id = "test_log_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="Log Agent")
        _cleanup_agents.append(agent_id)
        eid = create_memory(title="access target", content="access content")
        _cleanup_memories.append(eid)
        ws_id = create_workspace(name="log workspace")
        _cleanup_workspaces.append(ws_id)
        session_id = create_session(agent_id=agent_id, workspace_id=ws_id)
        log_id = log_access(agent_id, eid, "READ", session_id=session_id)
        ok = log_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_log_access: " + status)
    return ok


def test_get_access_log():
    try:
        agent_id = "test_alog_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="ALog Agent")
        _cleanup_agents.append(agent_id)
        eid = create_memory(title="alog target", content="alog content")
        _cleanup_memories.append(eid)
        log_access(agent_id, eid, "WRITE")
        results = get_access_log(entity_id=eid)
        ok = len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_access_log: " + status)
    return ok


def test_get_access_log_by_agent():
    try:
        agent_id = "test_alog2_agent_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=agent_id, agent_name="ALog2 Agent")
        _cleanup_agents.append(agent_id)
        eid = create_memory(title="alog2 target", content="alog2 content")
        _cleanup_memories.append(eid)
        log_access(agent_id, eid, "READ")
        results = get_access_log(agent_id=agent_id, limit=10)
        ok = len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_access_log_by_agent: " + status)
    return ok


def test_create_collaboration():
    try:
        a1 = "test_coll1_" + uuid.uuid4().hex[:8]
        a2 = "test_coll2_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=a1, agent_name="Collab Agent 1")
        register_agent(agent_id=a2, agent_name="Collab Agent 2")
        _cleanup_agents.extend([a1, a2])
        eid = create_memory(title="coll target", content="coll content")
        _cleanup_memories.append(eid)
        coll_id = create_collaboration(a1, a2, "PEER_REVIEW", entity_id=eid, context={"review": True}, strength=0.8)
        ok = coll_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_collaboration: " + status)
    return ok


def test_get_collaborations():
    try:
        a1 = "test_gcoll1_" + uuid.uuid4().hex[:8]
        a2 = "test_gcoll2_" + uuid.uuid4().hex[:8]
        register_agent(agent_id=a1, agent_name="GCollab Agent 1")
        register_agent(agent_id=a2, agent_name="GCollab Agent 2")
        _cleanup_agents.extend([a1, a2])
        create_collaboration(a1, a2, "MENTORING")
        results = get_collaborations(agent_id=a1, limit=10)
        ok = len(results) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_collaborations: " + status)
    return ok


def run_all():
    tests = [
        test_register_agent, test_register_agent_with_options,
        test_get_agent, test_get_agent_nonexistent,
        test_update_agent, test_decommission_agent, test_heartbeat,
        test_create_session, test_end_session, test_checkpoint_session,
        test_get_session_chain, test_get_active_sessions,
        test_log_access, test_get_access_log, test_get_access_log_by_agent,
        test_create_collaboration, test_get_collaborations,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Agent: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()