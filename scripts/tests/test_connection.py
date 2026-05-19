import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.connection import get_pool, get_connection, execute_query, execute_query_one, execute, close_pool


class TestConnection(unittest.TestCase):

    def test_pool_init(self):
        pool = get_pool()
        self.assertIsNotNone(pool)

    def test_get_connection(self):
        with get_connection() as conn:
            self.assertIsNotNone(conn)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                self.assertIsNotNone(cur.fetchone())

    def test_execute_query(self):
        rows = execute_query("SELECT 1 AS val")
        self.assertIsInstance(rows, list)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0], {'val': 1})

    def test_execute_query_one(self):
        row = execute_query_one("SELECT 1 AS val")
        self.assertIsInstance(row, dict)
        self.assertEqual(row, {'val': 1})

    def test_execute_dml(self):
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("CREATE TEMP TABLE _test_conn (id INT, name TEXT)")
                conn.commit()
        rowcount = execute("INSERT INTO _test_conn (id, name) VALUES (%s, %s)", (1, 'hello'))
        self.assertGreater(rowcount, 0)
        rows = execute_query("SELECT * FROM _test_conn")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['name'], 'hello')
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS _test_conn")
                conn.commit()

    def test_close_pool(self):
        close_pool()
        pool = get_pool()
        self.assertIsNotNone(pool)


if __name__ == '__main__':
    unittest.main()
