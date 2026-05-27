"""PostgreSQL Memory System v2.3.1 - Credential & Pool Agent API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.agent_api import (
    register_agent, get_agent,
    issue_credential, verify_credential, get_credentials_for_user,
    revoke_credential, hibernate_agent, wake_agent,
    register_pool_agent, assign_pool_agent,
)
from lib.connection import execute

_cleanup_agents = []
_cleanup_credentials = []
_passed = 0
_failed = 0


def _cleanup():
    for agent_id in _cleanup_agents:
        try:
            execute("DELETE FROM agent_credentials WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_collaboration WHERE source_agent_id = %s OR target_agent_id = %s", (agent_id, agent_id))
            execute("DELETE FROM entity_access_log WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_session WHERE agent_id = %s", (agent_id,))
            execute("DELETE FROM agent_registry WHERE agent_id = %s", (agent_id,))
        except Exception:
            pass
    for cred_id in _cleanup_credentials:
        try:
            execute("DELETE FROM agent_credentials WHERE credential_id = %s", (cred_id,))
        except Exception:
            pass
    _cleanup_agents.clear()
    _cleanup_credentials.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def _make_agent(prefix="cred_agent"):
    agent_id = "test-agent-" + uuid.uuid4().hex[:8]
    register_agent(agent_id=agent_id, agent_name=prefix + " agent")
    _cleanup_agents.append(agent_id)
    return agent_id


def test_issue_credential():
    try:
        agent_id = _make_agent("cred_issue")
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        cred_id = issue_credential(
            agent_id=agent_id,
            user_id=user_id,
            cred_type="API_KEY",
            scope={"access_level": "READ"},
            expires_hours=24,
        )
        ok = cred_id is not None and isinstance(cred_id, int)
        if ok:
            _cleanup_credentials.append(cred_id)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_issue_credential: " + status)
    return ok


def test_verify_credential():
    try:
        agent_id = _make_agent("cred_verify")
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        cred_id = issue_credential(
            agent_id=agent_id,
            user_id=user_id,
            cred_type="SESSION",
            scope={"access_level": "FULL"},
            expires_hours=24,
        )
        _cleanup_credentials.append(cred_id)
        result = verify_credential(cred_id)
        ok = result is not None and result.get("credential_id") == cred_id and result.get("is_active") is True
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_verify_credential: " + status)
    return ok


def test_verify_expired_credential():
    try:
        agent_id = _make_agent("cred_exp")
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        cred_id = issue_credential(
            agent_id=agent_id,
            user_id=user_id,
            cred_type="TEMP",
            scope={"access_level": "LIMITED"},
            expires_hours=0,
        )
        _cleanup_credentials.append(cred_id)
        result = verify_credential(cred_id)
        ok = result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_verify_expired_credential: " + status)
    return ok


def test_get_credentials_for_user():
    try:
        agent_id = _make_agent("cred_user")
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        c1 = issue_credential(agent_id=agent_id, user_id=user_id, cred_type="API_KEY", scope={"r": True})
        c2 = issue_credential(agent_id=agent_id, user_id=user_id, cred_type="SESSION", scope={"w": True})
        _cleanup_credentials.extend([c1, c2])
        results = get_credentials_for_user(user_id)
        ok = results is not None and len(results) >= 2
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_credentials_for_user: " + status)
    return ok


def test_revoke_credential():
    try:
        agent_id = _make_agent("cred_revoke")
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        cred_id = issue_credential(
            agent_id=agent_id,
            user_id=user_id,
            cred_type="API_KEY",
            scope={"access_level": "FULL"},
            expires_hours=24,
        )
        _cleanup_credentials.append(cred_id)
        revoked = revoke_credential(cred_id)
        result = verify_credential(cred_id)
        ok = revoked and result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_revoke_credential: " + status)
    return ok


def test_hibernate_agent():
    try:
        agent_id = _make_agent("cred_hib")
        hibernated = hibernate_agent(agent_id)
        fetched = get_agent(agent_id)
        ok = hibernated and fetched is not None and fetched.get("status") == "DORMANT"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_hibernate_agent: " + status)
    return ok


def test_wake_agent():
    try:
        agent_id = _make_agent("cred_wake")
        hibernate_agent(agent_id)
        woken = wake_agent(agent_id)
        fetched = get_agent(agent_id)
        ok = woken and fetched is not None and fetched.get("status") == "ACTIVE"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_wake_agent: " + status)
    return ok


def test_register_pool_agent():
    try:
        agent_id = register_pool_agent(
            agent_name="test pool agent " + uuid.uuid4().hex[:8],
            capabilities={"task_type": "general"},
            skills_tags=["python", "testing"],
        )
        ok = agent_id is not None
        if ok:
            _cleanup_agents.append(agent_id)
            fetched = get_agent(agent_id)
            ok = fetched is not None and fetched.get("status") == "POOL"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_register_pool_agent: " + status)
    return ok


def test_assign_pool_agent():
    try:
        agent_id = register_pool_agent(
            agent_name="test assign pool " + uuid.uuid4().hex[:8],
            capabilities={"task_type": "coding"},
            skills_tags=["python", "coding"],
        )
        _cleanup_agents.append(agent_id)
        user_id = "test_user_" + uuid.uuid4().hex[:8]
        assigned_id = assign_pool_agent(user_id, required_skills=["python"])
        ok = assigned_id is not None
        if ok:
            fetched = get_agent(assigned_id)
            ok = fetched is not None and fetched.get("status") == "ACTIVE"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_assign_pool_agent: " + status)
    return ok


def run_all():
    tests = [
        test_issue_credential, test_verify_credential,
        test_verify_expired_credential, test_get_credentials_for_user,
        test_revoke_credential, test_hibernate_agent, test_wake_agent,
        test_register_pool_agent, test_assign_pool_agent,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Credential: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()
