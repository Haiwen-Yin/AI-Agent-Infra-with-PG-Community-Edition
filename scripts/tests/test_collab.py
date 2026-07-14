"""AI Agent Infra v3.10.1 - PG Community Edition - Collaboration Group API Tests"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.collab_api import (
    create_collab_group, get_collab_group, update_collab_group,
    add_collab_member, remove_collab_member, get_collab_members,
    archive_collab_group, list_collab_groups,
    share_entity_to_group, unshare_entity_from_group,
    get_agent_groups, cleanup_expired_groups,
)
from lib.agent_api import register_agent
from lib.memory_api import create_memory, delete_memory
from lib.connection import close_pool, execute

_group_id = None
_shared_entity_id = None
TS = str(int(time.time()))
AGENTS = [
    ("pg-collab-lead-" + TS, "Collab Lead"),
    ("pg-collab-member-" + TS, "Collab Member"),
    ("pg-collab-observer-" + TS, "Collab Observer"),
]


def _ensure_agents():
    for aid, name in AGENTS:
        try:
            register_agent(aid, name, agent_type="test")
        except Exception:
            pass


def test_create_collab_group():
    global _group_id
    _ensure_agents()
    _group_id = create_collab_group(
        name="PG Test Collab Group " + TS,
        group_type="PROJECT",
        description="A PG test collaboration group",
        coordinator_agent_id=AGENTS[0][0],
        sharing_policy="OPEN",
    )
    assert _group_id is not None
    print(f"PASS: test_create_collab_group (id={_group_id})")


def test_get_collab_group():
    group = get_collab_group(_group_id)
    assert group is not None
    assert group["group_name"] == "PG Test Collab Group " + TS
    assert group["workspace_id"] is not None
    print(f"PASS: test_get_collab_group (name={group['group_name']})")


def test_update_collab_group():
    ok = update_collab_group(_group_id, description="Updated PG collab description")
    assert ok
    group = get_collab_group(_group_id)
    assert group["description"] == "Updated PG collab description"
    print("PASS: test_update_collab_group")


def test_add_collab_member():
    mid = add_collab_member(_group_id, AGENTS[0][0], role="LEAD")
    assert mid is not None
    mid2 = add_collab_member(_group_id, AGENTS[1][0], role="CONTRIBUTOR")
    assert mid2 is not None
    mid3 = add_collab_member(_group_id, AGENTS[2][0], role="OBSERVER")
    assert mid3 is not None
    print(f"PASS: test_add_collab_member (lead_mid={mid})")


def test_remove_collab_member():
    ok = remove_collab_member(_group_id, AGENTS[2][0])
    assert ok
    members = get_collab_members(_group_id)
    active = [m for m in members if m.get("status") != "LEFT"]
    assert len(active) < 3
    print("PASS: test_remove_collab_member")


def test_get_collab_members():
    members = get_collab_members(_group_id)
    assert len(members) >= 3
    print(f"PASS: test_get_collab_members (count={len(members)})")


def test_archive_collab_group():
    ok = archive_collab_group(_group_id)
    assert ok
    group = get_collab_group(_group_id)
    assert group["status"] == "ARCHIVED"
    execute("UPDATE collab_groups SET status = 'ACTIVE' WHERE group_id = %s", [_group_id])
    print("PASS: test_archive_collab_group")


def test_list_collab_groups():
    results = list_collab_groups(status="ACTIVE")
    assert len(results) >= 1
    print(f"PASS: test_list_collab_groups (found={len(results)})")


def test_share_entity_to_group():
    global _shared_entity_id
    _shared_entity_id = create_memory("Shared Memory PG", "content for sharing", category="test-collab-pg")
    share_id = share_entity_to_group(
        group_id=_group_id,
        entity_id=_shared_entity_id,
        shared_by=AGENTS[0][0],
        share_type="READ",
    )
    assert share_id is True
    print(f"PASS: test_share_entity_to_group (share_id={share_id})")


def test_unshare_entity_from_group():
    ok = unshare_entity_from_group(_group_id, _shared_entity_id)
    assert ok
    print("PASS: test_unshare_entity_from_group")


def test_get_agent_groups():
    groups = get_agent_groups(AGENTS[0][0])
    assert len(groups) >= 1
    print(f"PASS: test_get_agent_groups (found={len(groups)})")


def test_cleanup_expired_groups():
    count = cleanup_expired_groups(max_age_hours=8760)
    assert isinstance(count, int)
    print(f"PASS: test_cleanup_expired_groups (archived={count})")


def _cleanup():
    if _shared_entity_id:
        try:
            delete_memory(_shared_entity_id)
        except Exception:
            pass
    if _group_id:
        try:
            execute("DELETE FROM collab_group_shares WHERE group_id = %s", [_group_id])
        except Exception:
            pass
        try:
            execute("DELETE FROM collab_group_members WHERE group_id = %s", [_group_id])
        except Exception:
            pass
        try:
            ws_row = execute("SELECT workspace_id FROM collab_groups WHERE group_id = %s", [_group_id])
        except Exception:
            pass
        try:
            execute("DELETE FROM collab_groups WHERE group_id = %s", [_group_id])
        except Exception:
            pass
    for aid, _ in AGENTS:
        try:
            execute("DELETE FROM agent_session WHERE agent_id = %s", [aid])
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
        test_create_collab_group,
        test_get_collab_group,
        test_update_collab_group,
        test_add_collab_member,
        test_remove_collab_member,
        test_get_collab_members,
        test_archive_collab_group,
        test_list_collab_groups,
        test_share_entity_to_group,
        test_unshare_entity_from_group,
        test_get_agent_groups,
        test_cleanup_expired_groups,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nCollab Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
