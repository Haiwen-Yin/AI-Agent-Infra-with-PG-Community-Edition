"""PostgreSQL Memory System v2.3.1 - Memory API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.memory_api import (
    create_memory, get_memory, update_memory, delete_memory,
    search_memories, add_memory_tags, get_memory_tags,
    remove_memory_tag, count_memories, get_agent_memories,
)

_cleanup_ids = []
_passed = 0
_failed = 0


def _cleanup():
    for mid in _cleanup_ids:
        try:
            delete_memory(mid)
        except Exception:
            pass
    _cleanup_ids.clear()


def _record(ok):
    global _passed, _failed
    if ok:
        _passed += 1
    else:
        _failed += 1


def test_create():
    try:
        eid = create_memory(title="test title", content=f"test memory {uuid.uuid4()}")
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_create: {'PASS' if ok else 'FAIL'}")
    return ok


def test_create_with_options():
    try:
        eid = create_memory(
            title="optional fields",
            content="content with options",
            category="test",
            importance=8,
            summary="a summary",
            source_agent="tester",
            owned_by_agent="tester",
            visibility="SHARED",
        )
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
            fetched = get_memory(eid)
            ok = (fetched is not None
                  and fetched.get("category") == "test"
                  and fetched.get("importance") == 8
                  and fetched.get("visibility") == "SHARED")
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_create_with_options: {'PASS' if ok else 'FAIL'}")
    return ok


def test_get():
    try:
        eid = create_memory(title="test get", content="test get content")
        _cleanup_ids.append(eid)
        result = get_memory(eid)
        ok = result is not None and result.get("entity_id") == eid
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_get: {'PASS' if ok else 'FAIL'}")
    return ok


def test_get_nonexistent():
    try:
        result = get_memory(999999999999)
        ok = result is None
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_get_nonexistent: {'PASS' if ok else 'FAIL'}")
    return ok


def test_update():
    try:
        eid = create_memory(title="before update", content="test update before")
        _cleanup_ids.append(eid)
        updated = update_memory(eid, title="after update", importance=9)
        fetched = get_memory(eid)
        ok = updated and fetched is not None and fetched.get("title") == "after update" and fetched.get("importance") == 9
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_update: {'PASS' if ok else 'FAIL'}")
    return ok


def test_delete():
    try:
        eid = create_memory(title="test delete", content="test delete content")
        deleted = delete_memory(eid)
        result = get_memory(eid)
        ok = deleted and result is None
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_delete: {'PASS' if ok else 'FAIL'}")
    return ok


def test_search_by_keyword():
    try:
        unique = f"unique_search_{uuid.uuid4().hex[:8]}"
        eid = create_memory(title=unique, content="searchable content")
        _cleanup_ids.append(eid)
        results = search_memories(keyword=unique)
        ok = len(results) > 0
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_search_by_keyword: {'PASS' if ok else 'FAIL'}")
    return ok


def test_search_by_category():
    try:
        eid = create_memory(title="cat test", content="cat content", category="unittest")
        _cleanup_ids.append(eid)
        results = search_memories(category="unittest")
        ok = len(results) > 0
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_search_by_category: {'PASS' if ok else 'FAIL'}")
    return ok


def test_search_by_visibility():
    try:
        eid = create_memory(title="vis test", content="vis content", visibility="SHARED")
        _cleanup_ids.append(eid)
        results = search_memories(visibility="SHARED")
        ok = len(results) > 0
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_search_by_visibility: {'PASS' if ok else 'FAIL'}")
    return ok


def test_search_by_owned_by_agent():
    try:
        agent = f"test_agent_{uuid.uuid4().hex[:8]}"
        eid = create_memory(title="agent owned", content="agent content", owned_by_agent=agent)
        _cleanup_ids.append(eid)
        results = search_memories(owned_by_agent=agent)
        ok = len(results) > 0
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_search_by_owned_by_agent: {'PASS' if ok else 'FAIL'}")
    return ok


def test_search_with_limit_offset():
    try:
        for i in range(3):
            eid = create_memory(title=f"limit_test_{i}", content=f"limit content {i}")
            _cleanup_ids.append(eid)
        results = search_memories(keyword="limit_test", limit=2, offset=0)
        ok = len(results) <= 2
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_search_with_limit_offset: {'PASS' if ok else 'FAIL'}")
    return ok


def test_add_and_get_tags():
    try:
        eid = create_memory(title="tag test", content="tag content")
        _cleanup_ids.append(eid)
        added = add_memory_tags(eid, ["tag_alpha", "tag_beta"])
        tags = get_memory_tags(eid)
        ok = added >= 2 and len(tags) >= 2
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_add_and_get_tags: {'PASS' if ok else 'FAIL'}")
    return ok


def test_remove_tag():
    try:
        eid = create_memory(title="remove tag test", content="remove tag content")
        _cleanup_ids.append(eid)
        add_memory_tags(eid, ["tag_to_remove"])
        tags_before = get_memory_tags(eid)
        tag_id = tags_before[0]["tag_id"]
        removed = remove_memory_tag(eid, tag_id)
        tags_after = get_memory_tags(eid)
        ok = removed and len(tags_after) == len(tags_before) - 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_remove_tag: {'PASS' if ok else 'FAIL'}")
    return ok


def test_count_memories():
    try:
        before = count_memories()
        eid = create_memory(title="count test", content="count content")
        _cleanup_ids.append(eid)
        after = count_memories()
        ok = after >= before + 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_count_memories: {'PASS' if ok else 'FAIL'}")
    return ok


def test_count_memories_by_category():
    try:
        cat = f"catcount_{uuid.uuid4().hex[:8]}"
        eid = create_memory(title="catcount test", content="catcount content", category=cat)
        _cleanup_ids.append(eid)
        cnt = count_memories(category=cat)
        ok = cnt >= 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_count_memories_by_category: {'PASS' if ok else 'FAIL'}")
    return ok


def test_get_agent_memories():
    try:
        agent = f"mem_agent_{uuid.uuid4().hex[:8]}"
        eid = create_memory(title="agent mem", content="agent mem content", owned_by_agent=agent)
        _cleanup_ids.append(eid)
        results = get_agent_memories(agent, limit=10)
        ok = len(results) >= 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    _record(ok)
    print(f"  test_get_agent_memories: {'PASS' if ok else 'FAIL'}")
    return ok


def run_all():
    tests = [
        test_create, test_create_with_options, test_get, test_get_nonexistent,
        test_update, test_delete, test_search_by_keyword, test_search_by_category,
        test_search_by_visibility, test_search_by_owned_by_agent,
        test_search_with_limit_offset, test_add_and_get_tags, test_remove_tag,
        test_count_memories, test_count_memories_by_category, test_get_agent_memories,
    ]
    for t in tests:
        t()
    _cleanup()
    print(f"\n  Memory: {_passed} passed, {_failed} failed, {_passed + _failed} total")
    return _failed == 0


if __name__ == "__main__":
    run_all()
