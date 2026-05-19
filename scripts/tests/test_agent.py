import sys
import os
import unittest
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib.agent_api import (
    register_agent, get_agent, list_agents, disable_agent, enable_agent,
    create_session, close_session, get_active_sessions,
    log_access, get_access_history,
    request_collaboration, approve_collaboration, reject_collaboration
)
from lib.memory_api import create_memory
from lib.connection import execute


class TestAgent(unittest.TestCase):

    def setUp(self):
        self._agent_ids = []
        self._session_ids = []
        self._entity_ids = []
        self._collab_ids = []

    def tearDown(self):
        for cid in self._collab_ids:
            try:
                execute("DELETE FROM agent_collaboration WHERE collab_id = %s", (cid,))
            except Exception:
                pass
        for sid in self._session_ids:
            try:
                close_session(sid)
            except Exception:
                pass
        for eid in self._entity_ids:
            try:
                execute("DELETE FROM entity_access_log WHERE entity_id = %s", (eid,))
            except Exception:
                pass
            try:
                from lib.memory_api import delete_memory
                delete_memory(eid)
            except Exception:
                pass
        for aid in self._agent_ids:
            try:
                execute("DELETE FROM agent_permission_log WHERE agent_id = %s", (aid,))
            except Exception:
                pass
            try:
                execute("DELETE FROM agent_session WHERE agent_id = %s", (aid,))
            except Exception:
                pass
            try:
                execute("DELETE FROM agent_registry WHERE agent_id = %s", (aid,))
            except Exception:
                pass

    def _new_agent_id(self):
        aid = f"test_agent_{uuid.uuid4().hex[:8]}"
        self._agent_ids.append(aid)
        return aid

    def test_register_agent(self):
        aid = self._new_agent_id()
        result = register_agent(aid, 'TestAgent', agent_type='test')
        self.assertTrue(result)

    def test_get_agent(self):
        aid = self._new_agent_id()
        register_agent(aid, 'TestAgentGet', agent_type='test')
        agent = get_agent(aid)
        self.assertIsNotNone(agent)
        self.assertEqual(agent['agent_name'], 'TestAgentGet')

    def test_list_agents(self):
        aid = self._new_agent_id()
        register_agent(aid, 'TestAgentList', agent_type='test')
        agents = list_agents(status='ACTIVE')
        self.assertIsInstance(agents, list)
        self.assertGreaterEqual(len(agents), 1)

    def test_session_lifecycle(self):
        aid = self._new_agent_id()
        register_agent(aid, 'SessionAgent', agent_type='test')
        sid = create_session(aid)
        self._session_ids.append(sid)
        self.assertIsInstance(sid, str)
        sessions = get_active_sessions(agent_id=aid)
        active = [s for s in sessions if s['session_id'] == sid]
        self.assertGreaterEqual(len(active), 1)
        close_session(sid)
        sessions_after = get_active_sessions(agent_id=aid)
        active_after = [s for s in sessions_after if s['session_id'] == sid]
        self.assertEqual(len(active_after), 0)

    def test_access_logging(self):
        aid = self._new_agent_id()
        register_agent(aid, 'AccessAgent', agent_type='test')
        eid = create_memory('access_test', 'content', category='test')
        self._entity_ids.append(eid)
        log_access(aid, eid, access_type='READ')
        history = get_access_history(aid)
        self.assertGreaterEqual(len(history), 1)

    def test_agent_lifecycle(self):
        aid = self._new_agent_id()
        register_agent(aid, 'LifecycleAgent', agent_type='test')
        disable_agent(aid)
        agent = get_agent(aid)
        self.assertEqual(agent['status'], 'DISABLED')
        enable_agent(aid)
        agent = get_agent(aid)
        self.assertEqual(agent['status'], 'ACTIVE')

    def test_collaboration(self):
        aid1 = self._new_agent_id()
        aid2 = self._new_agent_id()
        register_agent(aid1, 'CollabAgent1', agent_type='test')
        register_agent(aid2, 'CollabAgent2', agent_type='test')
        eid = create_memory('collab_test', 'shared content', category='test')
        self._entity_ids.append(eid)
        collab_id = request_collaboration(aid1, aid2, eid, reason='test collab')
        self._collab_ids.append(collab_id)
        self.assertIsInstance(collab_id, int)
        result = approve_collaboration(collab_id)
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
