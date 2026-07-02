"""AI Agent Infra v3.8.0 - PG Community Edition - Workspace API Tests"""

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from lib import workspace_api
from lib import agent_api
from lib import memory_api
from lib.connection import execute, close_pool

ws_id = None
ws2_id = None
ctx_id = None
TS = str(int(time.time()))
TEST_AGENT = "pg-ws-agent-" + TS
TEST_AGENT_2 = "pg-ws-agent2-" + TS


def test_create_workspace():
    global ws_id
    ws_id = workspace_api.create_workspace(
        owner_user_id='admin',
        name='PG User Workspace ' + TS,
        workspace_type='CONVERSATION',
    )
    assert isinstance(ws_id, int)
    assert ws_id > 0
    print(f"PASS: test_create_workspace (id={ws_id})")


def test_get_workspace():
    ws = workspace_api.get_workspace(ws_id)
    assert ws is not None
    assert 'PG User Workspace' in ws['workspace_name']
    assert ws['status'] == 'ACTIVE'
    assert ws['isolation_mode'] == 'SHARED'
    print(f"PASS: test_get_workspace (name={ws['workspace_name']}, status={ws['status']})")


def test_update_workspace():
    ok = workspace_api.update_workspace(ws_id, summary='PG test summary')
    assert ok
    ws = workspace_api.get_workspace(ws_id)
    assert ws['summary'] == 'PG test summary'
    print("PASS: test_update_workspace")


def test_pause_workspace():
    ok = workspace_api.pause_workspace(ws_id)
    assert ok
    ws = workspace_api.get_workspace(ws_id)
    assert ws['status'] == 'PAUSED'
    print("PASS: test_pause_workspace")


def test_complete_workspace():
    ok = workspace_api.complete_workspace(ws_id)
    assert ok
    ws = workspace_api.get_workspace(ws_id)
    assert ws['status'] == 'COMPLETED'
    execute("UPDATE workspaces SET status = 'ACTIVE' WHERE workspace_id = %s", [ws_id])
    print("PASS: test_complete_workspace")


def test_save_context():
    global ctx_id
    agent_api.register_agent(TEST_AGENT, 'PG WS Test Agent 1')
    ctx_id = workspace_api.save_context(
        workspace_id=ws_id,
        agent_id=TEST_AGENT,
        context_type='CHECKPOINT',
        context_data={
            "conversation": [{"role": "user", "content": "hello PG"}],
            "working_memory": {"findings": ["pg test"]},
        },
    )
    assert isinstance(ctx_id, int)
    assert ctx_id > 0
    print(f"PASS: test_save_context (id={ctx_id})")


def test_get_latest_context():
    latest = workspace_api.get_latest_context(ws_id)
    assert latest is not None
    assert latest['context_type'] in ('CHECKPOINT', 'HANDOFF', 'SUMMARY')
    print(f"PASS: test_get_latest_context (type={latest['context_type']})")


def test_get_context_chain():
    workspace_api.save_context(
        workspace_id=ws_id,
        agent_id=TEST_AGENT,
        context_type='HANDOFF',
        context_data={"info": "pg handoff data"},
    )
    chain = workspace_api.get_context_chain(ws_id)
    assert len(chain) >= 2
    types = {c['context_type'] for c in chain}
    assert 'CHECKPOINT' in types
    assert 'HANDOFF' in types
    print(f"PASS: test_get_context_chain (count={len(chain)})")


def test_create_handoff():
    global ws2_id
    ws2_id = workspace_api.create_workspace(
        owner_user_id='admin',
        name='PG Handoff Workspace ' + TS,
        workspace_type='CONVERSATION',
    )
    agent_api.register_agent(TEST_AGENT, 'PG WS Test Agent')
    agent_api.register_agent(TEST_AGENT_2, 'PG WS Test Agent 2')
    session_id = agent_api.create_session(
        agent_id=TEST_AGENT,
        workspace_id=ws2_id,
        owner_user_id='admin',
    )
    workspace_api.update_workspace(
        ws2_id,
        current_agent_id=TEST_AGENT,
        current_session_id=session_id,
    )
    handoff_session = workspace_api.create_handoff(
        workspace_id=ws2_id,
        new_agent_id=TEST_AGENT_2,
        handoff_data={'reason': 'pg test handoff'},
    )
    assert handoff_session is not None
    ws = workspace_api.get_workspace(ws2_id)
    assert ws['current_agent_id'] == TEST_AGENT_2
    print(f"PASS: test_create_handoff (session={handoff_session})")


def test_recover_to_checkpoint():
    ws = workspace_api.get_workspace(ws_id)
    assert ws is not None
    recovery = workspace_api.recover_to_checkpoint(ws_id)
    assert isinstance(recovery, dict)
    assert recovery.get('recovered') is True or 'context_data' in recovery
    print("PASS: test_recover_to_checkpoint")


def test_get_workspace_summary():
    summary = workspace_api.get_workspace_summary(ws_id)
    assert isinstance(summary, dict)
    assert 'workspace_id' in summary
    assert 'context_count' in summary
    assert 'session_count' in summary
    print(f"PASS: test_get_workspace_summary (contexts={summary['context_count']})")


def test_cleanup_abandoned():
    count = workspace_api.cleanup_abandoned(max_age_hours=8760)
    assert isinstance(count, int)
    print(f"PASS: test_cleanup_abandoned (affected={count})")


def _cleanup():
    for wid in [ws_id, ws2_id]:
        if wid:
            try:
                execute("DELETE FROM workspace_context WHERE workspace_id = %s", [wid])
            except Exception:
                pass
            try:
                execute("DELETE FROM workspace_tasks WHERE workspace_id = %s", [wid])
            except Exception:
                pass
            try:
                execute("DELETE FROM agent_session WHERE workspace_id = %s", [wid])
            except Exception:
                pass
            try:
                execute("DELETE FROM workspaces WHERE workspace_id = %s", [wid])
            except Exception:
                pass
    for aid in [TEST_AGENT, TEST_AGENT_2]:
        try:
            execute("DELETE FROM agent_session WHERE agent_id = %s", [aid])
        except Exception:
            pass
        try:
            execute("DELETE FROM agent_collaboration WHERE source_agent_id = %s OR target_agent_id = %s", [aid, aid])
        except Exception:
            pass
        try:
            execute("DELETE FROM agent_registry WHERE agent_id = %s", [aid])
        except Exception:
            pass


def run_all():
    passed = 0
    failed = 0
    for test_fn in [
        test_create_workspace,
        test_get_workspace,
        test_update_workspace,
        test_pause_workspace,
        test_complete_workspace,
        test_save_context,
        test_get_latest_context,
        test_get_context_chain,
        test_create_handoff,
        test_recover_to_checkpoint,
        test_get_workspace_summary,
        test_cleanup_abandoned,
    ]:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {test_fn.__name__} - {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    _cleanup()
    close_pool()
    print(f"\nWorkspace Tests: {passed} passed, {failed} failed")
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    sys.exit(0 if success else 1)
