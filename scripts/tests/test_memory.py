import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.memory_api import (
    create_memory, get_memory, update_memory, delete_memory,
    search_memories, get_agent_memories, count_memories
)


class TestMemory(unittest.TestCase):

    def setUp(self):
        self._created_ids = []

    def tearDown(self):
        for eid in self._created_ids:
            try:
                delete_memory(eid)
            except Exception:
                pass

    def _track(self, entity_id):
        self._created_ids.append(entity_id)
        return entity_id

    def test_create_memory(self):
        eid = create_memory('test_create', 'content', category='test')
        self._track(eid)
        self.assertIsInstance(eid, int)
        self.assertGreater(eid, 0)

    def test_get_memory(self):
        eid = create_memory('test_get', 'some content', category='general')
        self._track(eid)
        mem = get_memory(eid)
        self.assertIsNotNone(mem)
        self.assertEqual(mem['name'], 'test_get')
        self.assertEqual(mem['content'], 'some content')
        self.assertEqual(mem['category'], 'general')

    def test_update_memory(self):
        eid = create_memory('test_update', 'original', category='test')
        self._track(eid)
        result = update_memory(eid, name='updated_name')
        self.assertTrue(result)
        mem = get_memory(eid)
        self.assertEqual(mem['name'], 'updated_name')

    def test_delete_memory(self):
        eid = create_memory('test_delete', 'bye', category='test')
        result = delete_memory(eid)
        self.assertTrue(result)
        mem = get_memory(eid)
        self.assertIsNone(mem)

    def test_search_memories(self):
        eid1 = self._track(create_memory('alpha_search_test', 'content alpha', category='search'))
        eid2 = self._track(create_memory('beta_search_test', 'content beta', category='search'))
        results = search_memories(keyword='search_test')
        self.assertGreaterEqual(len(results), 2)

    def test_get_agent_memories(self):
        eid = create_memory('agent_mem', 'agent content', category='test', owned_by_agent='test_agent_001')
        self._track(eid)
        results = get_agent_memories('test_agent_001')
        self.assertGreaterEqual(len(results), 1)

    def test_count_memories(self):
        before = count_memories()
        eid = self._track(create_memory('count_test', 'counting', category='test'))
        after = count_memories()
        self.assertGreater(after, before)


if __name__ == '__main__':
    unittest.main()
