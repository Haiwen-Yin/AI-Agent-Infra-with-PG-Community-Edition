"""PostgreSQL Memory System v2.3.1 - Collaboration Group API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.collab_api import (
    create_collab_group, get_collab_group, update_collab_group,
    add_group_member, remove_group_member, list_group_members,
    get_agent_groups, share_memory_to_group, delete_collab_group,
)
from lib.agent_api import register_agent
from lib.memory_api import create_memory, delete_memory
from lib.connection import execute

_cleanup_groups = []
_cleanup_agents = []
_cleanup_memories = []
_cleanup_workspaces = []
_passed = 0
_failed = 0


def _cleanup():
    for group_id in _cleanup_groups:
        try:
            execute("DELETE FROM collab_group_members WHERE group_id = %s", (group_id,))
            execute("DELETE FROM collab_groups WHERE group_id = %s", (group_id,))
        except Exception:
            pass
    for agent_id in _cleanup_agents:
        try:
            execute("DELETE FROM agent_collaboration WHERE source_agent_id = %s OR target_agent_id = %s", (agent_id, agent_id))
            execute("DELETE FROM collab_group_members WHERE agent_id = %s", (agent_id,))
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
    _cleanup_groups.clear()
    _cleanup_agents.clear()
    _cleanup_memories.clear()
    _cleanup_workspaces.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def _make_agent(prefix="collab_agent"):
    agent_id = "test-agent-" + uuid.uuid4().hex[:8]
    register_agent(agent_id=agent_id, agent_name=prefix + " agent")
    _cleanup_agents.append(agent_id)
    return agent_id


def test_create_collab_group():
    try:
        group_id = create_collab_group(
            group_name="test group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
            description="test description",
        )
        ok = group_id is not None and isinstance(group_id, int)
        if ok:
            _cleanup_groups.append(group_id)
            fetched = get_collab_group(group_id)
            ok = fetched is not None and fetched.get("workspace_id") is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_collab_group: " + status)
    return ok


def test_get_collab_group():
    try:
        uid = uuid.uuid4().hex[:8]
        group_id = create_collab_group(
            group_name="get group " + uid,
            group_type="TEAM",
            description="get test description",
            sharing_policy="MODERATED",
        )
        _cleanup_groups.append(group_id)
        result = get_collab_group(group_id)
        ok = (
            result is not None
            and result.get("group_id") == group_id
            and result.get("group_name") == "get group " + uid
            and result.get("group_type") == "TEAM"
            and result.get("status") == "ACTIVE"
        )
        members = list_group_members(group_id)
        ok = ok and len(members) == 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_collab_group: " + status)
    return ok


def test_update_collab_group():
    try:
        group_id = create_collab_group(
            group_name="update group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        updated = update_collab_group(group_id, status="SUSPENDED")
        fetched = get_collab_group(group_id)
        ok = updated and fetched is not None and fetched.get("status") == "SUSPENDED"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update_collab_group: " + status)
    return ok


def test_add_group_member_lead():
    try:
        agent_id = _make_agent("collab_lead")
        group_id = create_collab_group(
            group_name="lead group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        member_id = add_group_member(group_id, agent_id, role="LEAD")
        ok = member_id is not None
        if ok:
            members = list_group_members(group_id)
            active = [m for m in members if m.get("status") == "ACTIVE"]
            ok = len(active) == 1 and active[0].get("personal_workspace_id") is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_add_group_member_lead: " + status)
    return ok


def test_add_group_member_observer():
    try:
        agent_id = _make_agent("collab_obs")
        group_id = create_collab_group(
            group_name="obs group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        member_id = add_group_member(group_id, agent_id, role="OBSERVER")
        ok = member_id is not None
        if ok:
            members = list_group_members(group_id)
            active = [m for m in members if m.get("status") == "ACTIVE"]
            ok = len(active) == 1 and active[0].get("personal_workspace_id") is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_add_group_member_observer: " + status)
    return ok


def test_remove_group_member():
    try:
        agent_id = _make_agent("collab_rem")
        group_id = create_collab_group(
            group_name="rem group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        add_group_member(group_id, agent_id, role="CONTRIBUTOR")
        removed = remove_group_member(group_id, agent_id)
        members = list_group_members(group_id)
        target = [m for m in members if m.get("agent_id") == agent_id]
        ok = removed and len(target) == 1 and target[0].get("status") == "REMOVED"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_remove_group_member: " + status)
    return ok


def test_list_group_members():
    try:
        a1 = _make_agent("collab_l1")
        a2 = _make_agent("collab_l2")
        a3 = _make_agent("collab_l3")
        group_id = create_collab_group(
            group_name="list group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        add_group_member(group_id, a1, role="LEAD")
        add_group_member(group_id, a2, role="CONTRIBUTOR")
        add_group_member(group_id, a3, role="OBSERVER")
        members = list_group_members(group_id)
        active = [m for m in members if m.get("status") == "ACTIVE"]
        ok = len(active) >= 3
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_list_group_members: " + status)
    return ok


def test_get_agent_groups():
    try:
        agent_id = _make_agent("collab_ag")
        group_id = create_collab_group(
            group_name="agent group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        add_group_member(group_id, agent_id, role="CONTRIBUTOR")
        groups = get_agent_groups(agent_id)
        ok = groups is not None and len(groups) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_agent_groups: " + status)
    return ok


def test_share_memory_to_group():
    try:
        agent_id = _make_agent("collab_share")
        mid = create_memory(title="shared memory", content="shared content")
        _cleanup_memories.append(mid)
        group_id = create_collab_group(
            group_name="share group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        collab_id = share_memory_to_group(group_id, mid, agent_id)
        ok = collab_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_share_memory_to_group: " + status)
    return ok


def test_delete_collab_group():
    try:
        group_id = create_collab_group(
            group_name="delete group " + uuid.uuid4().hex[:8],
            group_type="PROJECT",
        )
        _cleanup_groups.append(group_id)
        deleted = delete_collab_group(group_id)
        fetched = get_collab_group(group_id)
        ok = deleted and fetched is not None and fetched.get("status") == "ARCHIVED"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_delete_collab_group: " + status)
    return ok


def run_all():
    tests = [
        test_create_collab_group, test_get_collab_group,
        test_update_collab_group, test_add_group_member_lead,
        test_add_group_member_observer, test_remove_group_member,
        test_list_group_members, test_get_agent_groups,
        test_share_memory_to_group, test_delete_collab_group,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Collab: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()
