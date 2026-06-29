"""AI Agent Infra v3.7.5 - PG Community Edition - Property Graph API Tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.graph_api import (
    add_edge, get_neighbors, get_reachable, remove_edge,
    find_similar_entities, get_entity_context, graph_search,
    get_subgraph,
)
from lib.memory_api import create_memory, delete_memory
from lib.knowledge_api import create_knowledge, delete_knowledge
from lib.connection import close_pool, execute

_test_ids = []


def test_add_edge():
    m1 = create_memory("Graph Edge Test A", "content a", category="graph-test-pg", importance=8, owned_by_agent="graph-tester-pg")
    m2 = create_memory("Graph Edge Test B", "content b", category="graph-test-pg", importance=6, owned_by_agent="graph-tester-pg")
    _test_ids.extend([m1, m2])

    result = add_edge(m1, "MEMORY", m2, "SIMILAR_TO", 0.85, 0.9)
    assert result is not None
    print(f"PASS: test_add_edge (result={result})")


def test_get_neighbors():
    if not _test_ids:
        print("SKIP: test_get_neighbors (no test entities)")
        return
    m1 = _test_ids[0]
    neighbors = get_neighbors(m1, direction="outgoing")
    assert len(neighbors) >= 1
    out_types = {n["edge_type"] for n in neighbors}
    assert "SIMILAR_TO" in out_types
    print(f"PASS: test_get_neighbors (count={len(neighbors)})")


def test_get_reachable():
    if not _test_ids:
        print("SKIP: test_get_reachable (no test entities)")
        return
    reachable = get_reachable(_test_ids[0], max_hops=2, limit=10)
    assert isinstance(reachable, list)
    print(f"PASS: test_get_reachable (found={len(reachable)})")


def test_remove_edge():
    if len(_test_ids) < 2:
        print("SKIP: test_remove_edge (need 2 test entities)")
        return
    m1, m2 = _test_ids[0], _test_ids[1]
    edge_rows = execute(
        "SELECT edge_id FROM entity_edges WHERE source_id = %s AND target_id = %s AND edge_type = 'SIMILAR_TO' LIMIT 1",
        [m1, m2],
    )
    edge_query = execute(
        "SELECT edge_id FROM entity_edges WHERE source_id = %s AND target_id = %s AND edge_type = 'SIMILAR_TO' LIMIT 1",
        [m1, m2],
    )
    from lib.connection import execute_query
    rows = execute_query(
        "SELECT edge_id FROM entity_edges WHERE source_id = %s AND target_id = %s AND edge_type = 'SIMILAR_TO' LIMIT 1",
        [m1, m2],
    )
    if rows:
        edge_id = rows[0]["edge_id"]
        ok = remove_edge(edge_id)
        assert ok
        print(f"PASS: test_remove_edge (edge_id={edge_id})")
    else:
        print("SKIP: test_remove_edge (no edge found)")

    add_edge(m1, "MEMORY", m2, "RELATED_TO", 0.7, 0.8)


def test_find_similar_entities():
    if not _test_ids:
        print("SKIP: test_find_similar_entities (no test entity)")
        return
    similar = find_similar_entities(_test_ids[0], max_hops=2, limit=10)
    assert isinstance(similar, list)
    print(f"PASS: test_find_similar_entities (found={len(similar)})")


def test_get_entity_context():
    if not _test_ids:
        print("SKIP: test_get_entity_context (no test entity)")
        return
    ctx = get_entity_context(_test_ids[0])
    assert ctx is not None
    assert "entity_id" in ctx
    assert "neighbors" in ctx
    assert "neighbor_count" in ctx
    assert "neighbors_by_type" in ctx
    assert "neighbors_by_edge" in ctx
    print(f"PASS: test_get_entity_context (neighbors={ctx['neighbor_count']})")


def test_graph_search():
    results = graph_search(entity_type="MEMORY", limit=5)
    assert isinstance(results, list)
    print(f"PASS: test_graph_search (found={len(results)})")


def test_get_subgraph():
    if not _test_ids:
        print("SKIP: test_get_subgraph (no test entities)")
        return
    sub = get_subgraph(_test_ids[:3])
    assert "vertices" in sub
    assert "edges" in sub
    assert len(sub["vertices"]) >= 1
    print(f"PASS: test_get_subgraph (vertices={len(sub['vertices'])}, edges={len(sub['edges'])})")


def _cleanup():
    for eid in _test_ids:
        try:
            execute("DELETE FROM entity_tags WHERE entity_id = %s", [eid])
        except Exception:
            pass
    for eid in _test_ids:
        try:
            execute("DELETE FROM entity_edges WHERE source_id = %s OR target_id = %s", [eid, eid])
        except Exception:
            pass
    for eid in list(reversed(_test_ids)):
        try:
            delete_knowledge(eid)
        except Exception:
            pass
    for eid in list(reversed(_test_ids)):
        try:
            delete_memory(eid)
        except Exception:
            pass
    _test_ids.clear()


def run_all():
    passed = 0
    failed = 0
    tests = [
        test_add_edge,
        test_get_neighbors,
        test_get_reachable,
        test_remove_edge,
        test_find_similar_entities,
        test_get_entity_context,
        test_graph_search,
        test_get_subgraph,
    ]
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} - {e}")
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nGraph Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
