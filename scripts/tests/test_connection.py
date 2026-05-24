"""PostgreSQL Memory System v2.2.1 - Connection Pool Tests"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.connection import get_pool, get_connection, close_pool, execute, execute_query, execute_query_one

_passed = 0
_failed = 0


def test_pool_creation():
    global _passed, _failed
    try:
        pool = get_pool()
        ok = pool is not None
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_pool_creation: {'PASS' if ok else 'FAIL'}")
    return ok


def test_get_connection():
    global _passed, _failed
    try:
        with get_connection() as conn:
            ok = conn is not None
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_get_connection: {'PASS' if ok else 'FAIL'}")
    return ok


def test_execute():
    global _passed, _failed
    try:
        rowcount = execute("SELECT 1")
        ok = rowcount is not None
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_execute: {'PASS' if ok else 'FAIL'}")
    return ok


def test_execute_query():
    global _passed, _failed
    try:
        rows = execute_query("SELECT 1 AS val")
        ok = len(rows) > 0 and rows[0]['val'] == 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_execute_query: {'PASS' if ok else 'FAIL'}")
    return ok


def test_execute_query_one():
    global _passed, _failed
    try:
        row = execute_query_one("SELECT 1 AS val")
        ok = row is not None and row['val'] == 1
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_execute_query_one: {'PASS' if ok else 'FAIL'}")
    return ok


def test_close_pool():
    global _passed, _failed
    try:
        close_pool()
        ok = True
    except Exception as e:
        print(f"  Error: {e}")
        ok = False
    if ok:
        _passed += 1
    else:
        _failed += 1
    print(f"  test_close_pool: {'PASS' if ok else 'FAIL'}")
    return ok


def run_all():
    tests = [
        test_pool_creation,
        test_get_connection,
        test_execute,
        test_execute_query,
        test_execute_query_one,
        test_close_pool,
    ]
    for t in tests:
        t()
    print(f"\n  Connection: {_passed} passed, {_failed} failed, {_passed + _failed} total")
    return _failed == 0


if __name__ == "__main__":
    run_all()
