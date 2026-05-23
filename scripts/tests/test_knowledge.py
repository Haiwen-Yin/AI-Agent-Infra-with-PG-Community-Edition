"""PostgreSQL Memory System v2.2.0 - Knowledge API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.knowledge_api import (
    create_knowledge, get_knowledge, update_knowledge, delete_knowledge,
    search_knowledge, add_edge, get_edges, add_knowledge_tags,
    get_knowledge_tags, remove_knowledge_tag, record_review,
    get_due_reviews, count_knowledge,
)

_cleanup_ids = []
_passed = 0
_failed = 0


def _cleanup():
    for kid in _cleanup_ids:
        try:
            delete_knowledge(kid)
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
        eid = create_knowledge(
            title="test knowledge " + str(uuid.uuid4()),
            content="test content",
        )
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create: " + status)
    return ok


def test_create_with_options():
    try:
        eid = create_knowledge(
            title="knowledge with options",
            content="content with domain/topic",
            domain="testing",
            topic="unit-tests",
            difficulty="BEGINNER",
            category="unittest",
            importance=7,
            summary="a summary",
            owned_by_agent="tester",
            visibility="SHARED",
        )
        ok = eid is not None
        if ok:
            _cleanup_ids.append(eid)
            fetched = get_knowledge(eid)
            ok = (
                fetched is not None
                and fetched.get("domain") == "testing"
                and fetched.get("topic") == "unit-tests"
                and fetched.get("difficulty") == "BEGINNER"
            )
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_create_with_options: " + status)
    return ok


def test_get():
    try:
        eid = create_knowledge(title="test get", content="get content")
        _cleanup_ids.append(eid)
        result = get_knowledge(eid)
        ok = result is not None and result.get("entity_id") == eid
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get: " + status)
    return ok


def test_get_nonexistent():
    try:
        result = get_knowledge(999999999999)
        ok = result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_nonexistent: " + status)
    return ok


def test_update():
    try:
        eid = create_knowledge(title="before update", content="update content")
        _cleanup_ids.append(eid)
        updated = update_knowledge(eid, title="after update", domain="new-domain")
        fetched = get_knowledge(eid)
        ok = updated and fetched is not None and fetched.get("title") == "after update" and fetched.get("domain") == "new-domain"
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_update: " + status)
    return ok


def test_delete():
    try:
        eid = create_knowledge(title="test delete", content="delete content")
        deleted = delete_knowledge(eid)
        result = get_knowledge(eid)
        ok = deleted and result is None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_delete: " + status)
    return ok


def test_search_by_domain():
    try:
        domain = "search_domain_" + uuid.uuid4().hex[:8]
        eid = create_knowledge(title="domain search", content="domain content", domain=domain)
        _cleanup_ids.append(eid)
        results = search_knowledge(domain=domain)
        ok = len(results) > 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_search_by_domain: " + status)
    return ok


def test_search_by_keyword():
    try:
        unique = "unique_kw_" + uuid.uuid4().hex[:8]
        eid = create_knowledge(title=unique, content="keyword content")
        _cleanup_ids.append(eid)
        results = search_knowledge(keyword=unique)
        ok = len(results) > 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_search_by_keyword: " + status)
    return ok


def test_search_by_topic():
    try:
        topic = "search_topic_" + uuid.uuid4().hex[:8]
        eid = create_knowledge(title="topic search", content="topic content", topic=topic)
        _cleanup_ids.append(eid)
        results = search_knowledge(topic=topic)
        ok = len(results) > 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_search_by_topic: " + status)
    return ok


def test_search_by_difficulty():
    try:
        eid = create_knowledge(title="difficulty search", content="difficulty content", difficulty="ADVANCED")
        _cleanup_ids.append(eid)
        results = search_knowledge(difficulty="ADVANCED")
        ok = len(results) > 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_search_by_difficulty: " + status)
    return ok


def test_add_edge():
    try:
        k1 = create_knowledge(title="edge source", content="c1")
        k2 = create_knowledge(title="edge target", content="c2")
        _cleanup_ids.extend([k1, k2])
        edge_id = add_edge(k1, "KNOWLEDGE", k2, "RELATED_TO", strength=0.9, confidence=0.85)
        ok = edge_id is not None
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_add_edge: " + status)
    return ok


def test_get_edges():
    try:
        k1 = create_knowledge(title="edge get src", content="c1")
        k2 = create_knowledge(title="edge get tgt", content="c2")
        _cleanup_ids.extend([k1, k2])
        add_edge(k1, "KNOWLEDGE", k2, "RELATED_TO")
        edges = get_edges(k1, direction="outgoing")
        ok = len(edges) > 0 and edges[0].get("target_id") == k2
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_edges: " + status)
    return ok


def test_get_edges_both():
    try:
        k1 = create_knowledge(title="edge both src", content="c1")
        k2 = create_knowledge(title="edge both tgt", content="c2")
        _cleanup_ids.extend([k1, k2])
        add_edge(k1, "KNOWLEDGE", k2, "RELATED_TO")
        edges = get_edges(k1, direction="both")
        ok = len(edges) > 0
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_edges_both: " + status)
    return ok


def test_add_and_get_tags():
    try:
        eid = create_knowledge(title="tag test", content="tag content")
        _cleanup_ids.append(eid)
        added = add_knowledge_tags(eid, ["ktag_alpha", "ktag_beta"])
        tags = get_knowledge_tags(eid)
        ok = added >= 2 and len(tags) >= 2
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_add_and_get_tags: " + status)
    return ok


def test_remove_knowledge_tag():
    try:
        eid = create_knowledge(title="remove ktag test", content="remove ktag content")
        _cleanup_ids.append(eid)
        add_knowledge_tags(eid, ["ktag_to_remove"])
        tags_before = get_knowledge_tags(eid)
        tag_id = tags_before[0]["tag_id"]
        removed = remove_knowledge_tag(eid, tag_id)
        tags_after = get_knowledge_tags(eid)
        ok = removed and len(tags_after) == len(tags_before) - 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_remove_knowledge_tag: " + status)
    return ok


def test_record_review():
    try:
        eid = create_knowledge(title="review test", content="review content")
        _cleanup_ids.append(eid)
        result = record_review(eid)
        fetched = get_knowledge(eid)
        ok = result and fetched is not None and fetched.get("review_count", 0) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_record_review: " + status)
    return ok


def test_get_due_reviews():
    try:
        result = get_due_reviews(limit=10)
        ok = result is not None and isinstance(result, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_due_reviews: " + status)
    return ok


def test_count_knowledge():
    try:
        before = count_knowledge()
        eid = create_knowledge(title="count test", content="count content")
        _cleanup_ids.append(eid)
        after = count_knowledge()
        ok = after >= before + 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_count_knowledge: " + status)
    return ok


def test_count_knowledge_by_domain():
    try:
        domain = "count_domain_" + uuid.uuid4().hex[:8]
        eid = create_knowledge(title="domain count", content="domain count content", domain=domain)
        _cleanup_ids.append(eid)
        cnt = count_knowledge(domain=domain)
        ok = cnt >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_count_knowledge_by_domain: " + status)
    return ok


def run_all():
    tests = [
        test_create, test_create_with_options, test_get, test_get_nonexistent,
        test_update, test_delete, test_search_by_domain, test_search_by_keyword,
        test_search_by_topic, test_search_by_difficulty,
        test_add_edge, test_get_edges, test_get_edges_both,
        test_add_and_get_tags, test_remove_knowledge_tag,
        test_record_review, test_get_due_reviews,
        test_count_knowledge, test_count_knowledge_by_domain,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Knowledge: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()
