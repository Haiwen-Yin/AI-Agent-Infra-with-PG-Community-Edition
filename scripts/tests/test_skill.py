"""AI Agent Infra v3.10.0 - PG Community Edition - Skill API Tests"""

import sys
import os
import json
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.skill_api import (
    register_skill, get_skill, update_skill, delete_skill,
    list_skills, search_skills, validate_skill,
    deprecate_skill, register_skill_via_admin,
    upload_skill_resource, discover_skills, get_skill_dependencies,
)
from lib.connection import close_pool

TS = str(int(time.time()))
_skill_ids = []


def test_register_skill():
    sid = register_skill("PG Skill Test " + TS, skill_type="CUSTOM", category="test-pg")
    assert isinstance(sid, int)
    assert sid > 0
    _skill_ids.append(sid)
    print(f"PASS: test_register_skill (id={sid})")


def test_get_skill():
    sid = register_skill("PG Get Skill Test " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    skill = get_skill(sid)
    assert skill is not None
    assert "PG Get Skill Test" in skill.get("skill_name", "")
    assert "skill_type" in skill
    assert "status" in skill
    print(f"PASS: test_get_skill (id={sid})")


def test_update_skill():
    sid = register_skill("PG Update Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    ok = update_skill(sid, skill_name="pg_updated_skill_" + TS)
    assert ok
    skill = get_skill(sid)
    assert skill["skill_name"] == "pg_updated_skill_" + TS
    print(f"PASS: test_update_skill (id={sid})")


def test_delete_skill():
    sid = register_skill("PG Delete Skill " + TS, skill_type="CUSTOM", category="test-pg")
    ok = delete_skill(sid)
    assert ok
    skill = get_skill(sid)
    assert skill is not None and skill.get("status") == "DEPRECATED"
    print("PASS: test_delete_skill")


def test_list_skills():
    sid1 = register_skill("PG List Skill 1 " + TS, skill_type="CUSTOM", category="test-pg")
    sid2 = register_skill("PG List Skill 2 " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.extend([sid1, sid2])
    skills = list_skills(skill_status="ACTIVE")
    assert len(skills) >= 2
    print(f"PASS: test_list_skills (count={len(skills)})")


def test_search_skills():
    sid = register_skill("PG Searchable Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    results = search_skills("PG Searchable")
    assert isinstance(results, list)
    print(f"PASS: test_search_skills (found={len(results)})")


def test_validate_skill():
    sid = register_skill("PG Valid Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    result = validate_skill(sid)
    assert result["valid"] is True
    assert len(result["errors"]) == 0

    result_bad = validate_skill(99999999)
    assert result_bad["valid"] is False
    print("PASS: test_validate_skill")


def test_deprecate_skill():
    sid = register_skill("PG Deprecate Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    ok = deprecate_skill(sid)
    assert ok
    skill = get_skill(sid)
    assert skill["status"] == "DEPRECATED"
    print(f"PASS: test_deprecate_skill (status={skill['status']})")


def test_register_skill_via_admin():
    result = register_skill_via_admin(
        admin_url="http://localhost:9999",
        admin_token="AT_invalid_token",
        title="PG Admin Skill " + TS,
        skill_name="pg_admin_skill_" + TS,
    )
    assert result is None
    print("PASS: test_register_skill_via_admin")


def test_upload_skill_resource():
    sid = register_skill("PG Resource Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    result = upload_skill_resource(sid, "test.py", b"print('hello from PG skill')")
    assert result is not None
    assert "filename" in result
    assert result["filename"] == "test.py"
    print(f"PASS: test_upload_skill_resource (skill_id={sid})")


def test_discover_skills():
    sid = register_skill("PG Discover Skill " + TS, skill_type="CUSTOM", category="test-pg")
    _skill_ids.append(sid)
    results = discover_skills(skill_type="CUSTOM")
    assert isinstance(results, list)
    print(f"PASS: test_discover_skills (found={len(results)})")


def test_get_skill_dependencies():
    sid = register_skill("PG Dep Skill " + TS, skill_type="CUSTOM", category="test-pg",
                         dependencies=[99999990, 99999991])
    _skill_ids.append(sid)
    deps = get_skill_dependencies(sid)
    assert isinstance(deps, list)
    assert len(deps) == 0
    print("PASS: test_get_skill_dependencies")


def _cleanup():
    for sid in _skill_ids:
        try:
            delete_skill(sid)
        except Exception:
            pass
    _skill_ids.clear()


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_register_skill,
        test_get_skill,
        test_update_skill,
        test_delete_skill,
        test_list_skills,
        test_search_skills,
        test_validate_skill,
        test_deprecate_skill,
        test_register_skill_via_admin,
        test_upload_skill_resource,
        test_discover_skills,
        test_get_skill_dependencies,
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
    print(f"\nSkill Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
