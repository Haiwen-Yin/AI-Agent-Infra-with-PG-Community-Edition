"""AI Agent Infra v3.7.0 - PG Community Edition - Agent API Tests"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.agent_api import (
    register_agent, get_agent, update_agent, decommission_agent,
    heartbeat, register_pool_agent, assign_pool_agent,
)
from lib.connection import close_pool

TEST_AGENT = "pgtest-agent-1"
TEST_AGENT_2 = "pgtest-agent-2"
POOL_AGENT = "pgtest-pool-agent"
TS = str(int(time.time()))


def test_register_agent():
    agent_id = register_agent(
        agent_id=TEST_AGENT,
        agent_name="PG Test Agent " + TS,
        agent_type="test",
        description="Agent for PG testing",
    )
    assert isinstance(agent_id, str)
    assert agent_id == TEST_AGENT
    print(f"PASS: test_register_agent (id={agent_id})")


def test_get_agent():
    agent = get_agent(TEST_AGENT)
    assert agent is not None
    assert agent["agent_name"].startswith("PG Test Agent")
    assert agent["status"] == "ACTIVE"
    print(f"PASS: test_get_agent (name={agent['agent_name']})")


def test_update_agent():
    ok = update_agent(TEST_AGENT, description="Updated PG test agent")
    assert ok
    agent = get_agent(TEST_AGENT)
    assert agent["description"] == "Updated PG test agent"
    print("PASS: test_update_agent")


def test_decommission_agent():
    register_agent("decom-agent-" + TS, "Decom Agent", agent_type="test")
    ok = decommission_agent("decom-agent-" + TS)
    assert ok
    agent = get_agent("decom-agent-" + TS)
    assert agent["status"] == "DECOMMISSIONED"
    from lib.connection import execute
    execute("DELETE FROM agent_registry WHERE agent_id = %s", ["decom-agent-" + TS])
    print("PASS: test_decommission_agent")


def test_list_agents():
    from lib.connection import execute_query
    rows = execute_query("SELECT agent_id FROM agent_registry WHERE agent_id = %s", [TEST_AGENT])
    assert len(rows) >= 1
    print(f"PASS: test_list_agents (found={len(rows)})")


def test_pool_agent_register():
    register_agent(POOL_AGENT, "PG Pool Agent " + TS, agent_type="test")
    pool_config = {"max_idle_minutes": 60, "skills_tags": ["python", "sql", "postgresql"], "auto_wake": False}
    ok = register_pool_agent(POOL_AGENT, pool_config)
    assert ok
    agent = get_agent(POOL_AGENT)
    assert agent["status"] == "POOL"
    print("PASS: test_pool_agent_register")


def test_pool_agent_acquire():
    result = assign_pool_agent("pgtest-user-" + TS, required_skills=["python", "sql"])
    assert result is not None
    assert result["agent_id"] == POOL_AGENT
    assert result["status"] == "ACTIVE"
    print(f"PASS: test_pool_agent_acquire (assigned={result['agent_id']})")


def test_pool_agent_release():
    from lib.agent_api import hibernate_agent
    ok = hibernate_agent(POOL_AGENT)
    assert ok
    agent = get_agent(POOL_AGENT)
    assert agent["status"] == "POOL"
    print("PASS: test_pool_agent_release")


def _cleanup():
    from lib.connection import execute
    for aid in [TEST_AGENT, TEST_AGENT_2, POOL_AGENT]:
        try:
            execute("DELETE FROM agent_session WHERE agent_id = %s", [aid])
        except Exception:
            pass
        try:
            execute("DELETE FROM agent_collaboration WHERE source_agent_id = %s OR target_agent_id = %s", [aid, aid])
        except Exception:
            pass
        try:
            execute("DELETE FROM agent_credentials WHERE agent_id = %s", [aid])
        except Exception:
            pass
        try:
            execute("DELETE FROM agent_registry WHERE agent_id = %s", [aid])
        except Exception:
            pass


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_register_agent,
        test_get_agent,
        test_update_agent,
        test_decommission_agent,
        test_list_agents,
        test_pool_agent_register,
        test_pool_agent_acquire,
        test_pool_agent_release,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nAgent Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
