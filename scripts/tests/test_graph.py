"""PostgreSQL Memory System v2.2.0 - Graph API Tests"""
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.graph_api import (
    get_neighbors, get_reachable, get_shortest_path,
    find_similar_entities, get_entity_context, get_graph_stats,
    get_subgraph, find_communities, graph_search,
)
from lib.knowledge_api import create_knowledge, add_edge, delete_knowledge

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


def _create_test_nodes(n=3):
    ids = []
    for i in range(n):
        eid = create_knowledge(
            title="graph node " + uuid.uuid4().hex[:8],
            content="content " + str(i),
            domain="graph_test",
        )
        ids.append(eid)
        _cleanup_ids.append(eid)
    if n >= 2:
        add_edge(ids[0], "KNOWLEDGE", ids[1], "RELATED_TO", strength=0.8)
    if n >= 3:
        add_edge(ids[1], "KNOWLEDGE", ids[2], "RELATED_TO", strength=0.6)
    return ids


def test_get_graph_stats():
    try:
        stats = get_graph_stats()
        ok = stats is not None and isinstance(stats, dict) and "vertex_count" in stats
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_graph_stats: " + status)
    return ok


def test_graph_search():
    try:
        _create_test_nodes(1)
        results = graph_search(keyword="graph node", entity_type="KNOWLEDGE", limit=10)
        ok = results is not None and isinstance(results, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_graph_search: " + status)
    return ok


def test_graph_search_by_category():
    try:
        eid = create_knowledge(
            title="cat search node " + uuid.uuid4().hex[:8],
            content="cat search content",
            domain="graph_test",
            category="graph_cat",
        )
        _cleanup_ids.append(eid)
        results = graph_search(category="graph_cat", min_importance=1, limit=10)
        ok = results is not None and isinstance(results, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_graph_search_by_category: " + status)
    return ok


def test_get_neighbors():
    try:
        ids = _create_test_nodes(2)
        neighbors = get_neighbors(ids[0], direction="both")
        ok = neighbors is not None and len(neighbors) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_neighbors: " + status)
    return ok


def test_get_neighbors_outgoing():
    try:
        ids = _create_test_nodes(2)
        neighbors = get_neighbors(ids[0], direction="outgoing")
        ok = neighbors is not None and len(neighbors) >= 1
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_neighbors_outgoing: " + status)
    return ok


def test_get_neighbors_with_filter():
    try:
        ids = _create_test_nodes(2)
        neighbors = get_neighbors(ids[0], direction="both", edge_type="RELATED_TO", min_strength=0.5)
        ok = neighbors is not None and isinstance(neighbors, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_neighbors_with_filter: " + status)
    return ok


def test_get_entity_context():
    try:
        ids = _create_test_nodes(2)
        context = get_entity_context(ids[0], depth=1)
        ok = context is not None and isinstance(context, dict)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_entity_context: " + status)
    return ok


def test_get_reachable():
    try:
        ids = _create_test_nodes(3)
        reachable = get_reachable(ids[0], max_hops=3)
        ok = reachable is not None and isinstance(reachable, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_reachable: " + status)
    return ok


def test_get_shortest_path():
    try:
        ids = _create_test_nodes(3)
        path = get_shortest_path(ids[0], ids[2], max_hops=5)
        ok = path is None or isinstance(path, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_shortest_path: " + status)
    return ok


def test_find_similar_entities():
    try:
        ids = _create_test_nodes(1)
        similar = find_similar_entities(ids[0], max_hops=2, limit=10)
        ok = similar is not None and isinstance(similar, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_find_similar_entities: " + status)
    return ok


def test_get_subgraph():
    try:
        ids = _create_test_nodes(3)
        sub = get_subgraph(ids, include_intermediate=True)
        ok = sub is not None and "vertices" in sub and "edges" in sub
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_get_subgraph: " + status)
    return ok


def test_find_communities():
    try:
        _create_test_nodes(3)
        communities = find_communities(entity_type="KNOWLEDGE", min_connections=1, limit=10)
        ok = communities is not None and isinstance(communities, list)
    except Exception as e:
        print("  Error: " + str(e))
        ok = False
    _record(ok)
    status = "PASS" if ok else "FAIL"
    print("  test_find_communities: " + status)
    return ok


def run_all():
    tests = [
        test_get_graph_stats, test_graph_search, test_graph_search_by_category,
        test_get_neighbors, test_get_neighbors_outgoing, test_get_neighbors_with_filter,
        test_get_entity_context, test_get_reachable, test_get_shortest_path,
        test_find_similar_entities, test_get_subgraph, test_find_communities,
    ]
    for t in tests:
        t()
    _cleanup()
    print("\n  Graph: {} passed, {} failed, {} total".format(_passed, _failed, _passed + _failed))
    return _failed == 0


if __name__ == "__main__":
    run_all()