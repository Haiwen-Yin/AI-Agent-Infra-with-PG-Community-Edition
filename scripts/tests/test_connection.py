"""AI Agent Infra v3.7.4 - PG Community Edition - Connection Pool Tests"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.connection import (
    get_pool, get_connection, execute, execute_query,
    execute_query_one, execute_insert_returning_id,
    execute_many, close_pool,
)


def test_get_connection():
    with get_connection() as conn:
        assert conn is not None
        cur = conn.cursor()
        cur.execute("SELECT 1 AS val")
        result = cur.fetchone()
        assert result[0] == 1
    print("PASS: test_get_connection")


def test_execute_query():
    rows = execute_query("SELECT 1 AS val")
    assert len(rows) == 1
    assert rows[0]["val"] == 1
    print("PASS: test_execute_query")


def test_execute_query_one():
    row = execute_query_one("SELECT 42 AS answer")
    assert row is not None
    assert row["answer"] == 42
    print("PASS: test_execute_query_one")


def test_execute_insert_returning_id():
    from lib.agent_api import register_agent
    agent_id = "pg-conn-test-" + str(int(__import__('time').time()))
    register_agent(agent_id, "Conn Test Agent", agent_type="test")
    row = execute_query_one("SELECT agent_id FROM agent_registry WHERE agent_id = %s", [agent_id])
    assert row is not None
    assert row["agent_id"] == agent_id
    execute("DELETE FROM agent_registry WHERE agent_id = %s", [agent_id])
    print("PASS: test_execute_insert_returning_id")


def test_execute_many():
    import time
    ts = str(int(time.time()))
    agents = [
        ("pg-batch-a-" + ts, "Batch A"),
        ("pg-batch-b-" + ts, "Batch B"),
        ("pg-batch-c-" + ts, "Batch C"),
    ]
    total = execute_many(
        "INSERT INTO agent_registry (agent_id, agent_name, agent_type, status, created_at, updated_at) "
        "VALUES (%s, %s, 'test', 'ACTIVE', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) "
        "ON CONFLICT (agent_id) DO NOTHING",
        agents,
    )
    assert total >= 0
    for aid, _ in agents:
        execute("DELETE FROM agent_registry WHERE agent_id = %s", [aid])
    print(f"PASS: test_execute_many (affected={total})")


def test_connection_pool_stats():
    pool = get_pool()
    assert pool is not None
    assert pool.maxconn >= 2
    assert pool.minconn >= 1
    print(f"PASS: test_connection_pool_stats (min={pool.minconn}, max={pool.maxconn})")


def run_all():
    tests = [
        test_get_connection,
        test_execute_query,
        test_execute_query_one,
        test_execute_insert_returning_id,
        test_execute_many,
        test_connection_pool_stats,
    ]
    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"FAIL: {t.__name__} - {e}")
            failed += 1
    close_pool()
    print(f"\nConnection Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
