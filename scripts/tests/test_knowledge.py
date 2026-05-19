import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.knowledge_api import (
    create_concept, get_concept, update_concept, delete_concept,
    create_relationship, search_concepts, get_statistics
)


class TestKnowledge(unittest.TestCase):

    def setUp(self):
        self._created_entity_ids = []
        self._created_edge_ids = []

    def tearDown(self):
        for eid in self._created_edge_ids:
            try:
                from lib.knowledge_api import delete_relationship
                delete_relationship(eid)
            except Exception:
                pass
        for eid in self._created_entity_ids:
            try:
                delete_concept(eid)
            except Exception:
                pass

    def _track_entity(self, entity_id):
        self._created_entity_ids.append(entity_id)
        return entity_id

    def _track_edge(self, edge_id):
        self._created_edge_ids.append(edge_id)
        return edge_id

    def test_create_concept(self):
        eid = create_concept('test_concept', 'FACT', description='a test concept')
        self._track_entity(eid)
        self.assertIsInstance(eid, int)
        self.assertGreater(eid, 0)

    def test_get_concept(self):
        eid = create_concept('get_concept', 'RULE', description='retrieve me')
        self._track_entity(eid)
        concept = get_concept(eid)
        self.assertIsNotNone(concept)
        self.assertEqual(concept['name'], 'get_concept')
        self.assertEqual(concept['validation_status'], 'PENDING')

    def test_update_concept(self):
        eid = create_concept('update_concept', 'FACT', description='old desc')
        self._track_entity(eid)
        update_concept(eid, description='new desc')
        concept = get_concept(eid)
        self.assertEqual(concept['description'], 'new desc')

    def test_create_relationship(self):
        eid1 = self._track_entity(create_concept('rel_src', 'FACT'))
        eid2 = self._track_entity(create_concept('rel_tgt', 'FACT'))
        edge_id = create_relationship(eid1, eid2, 'RELATED_TO')
        self._track_edge(edge_id)
        self.assertIsInstance(edge_id, int)
        self.assertGreater(edge_id, 0)

    def test_search_concepts(self):
        self._track_entity(create_concept('search_alpha', 'FACT', description='findable alpha'))
        self._track_entity(create_concept('search_beta', 'RULE', description='findable beta'))
        results = search_concepts(keyword='search')
        self.assertGreaterEqual(len(results), 2)

    def test_get_statistics(self):
        stats = get_statistics()
        self.assertIsInstance(stats, dict)
        self.assertIn('total_concepts', stats)

    def test_delete_concept(self):
        eid = create_concept('delete_me', 'FACT', description='gonna delete')
        result = delete_concept(eid)
        self.assertTrue(result)
        concept = get_concept(eid)
        self.assertIsNone(concept)


if __name__ == '__main__':
    unittest.main()
