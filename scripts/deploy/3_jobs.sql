-- ============================================================================
-- PostgreSQL Memory System v2.2.1 - Scheduled Jobs
-- ============================================================================
-- NOTE: pg_cron must be installed and configured before running this script.
-- See deployment.md for pg_cron setup instructions.
-- If pg_cron is not available, skip this file and schedule jobs manually.

DO $$ BEGIN
    CREATE EXTENSION IF NOT EXISTS pg_cron;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'pg_cron not available. Job scheduling skipped. Install pg_cron first.';
    RETURN;
END $$;

-- Memory fusion: merge similar memories + decay priorities
SELECT cron.schedule(
    'memory_fusion_job',
    '0 2 * * *',
    $$SELECT memory_fusion.fuse_similar_memories(p_dry_run := false)$$
);

-- Knowledge extraction from memory patterns
SELECT cron.schedule(
    'knowledge_extraction_job',
    '0 3 * * *',
    $$SELECT memory_fusion.extract_knowledge_from_memories()$$
);

-- Knowledge review scheduling
SELECT cron.schedule(
    'knowledge_review_job',
    '0 6 * * *',
    $$SELECT knowledge_api.record_review(e.entity_id) FROM knowledge_api.get_due_reviews() AS e$$
);

-- Session cleanup every 30 minutes
SELECT cron.schedule(
    'session_cleanup_job',
    '*/30 * * * *',
    $$SELECT agent_perm.cleanup_expired_sessions()$$
);

-- Access log purge (weekly Sunday 04:00)
SELECT cron.schedule(
    'access_log_purge_job',
    '0 4 * * 0',
    $$SELECT session_cleanup.purge_access_logs(90)$$
);

-- Entity archive (weekly Sunday 05:00)
SELECT cron.schedule(
    'entity_archive_job',
    '0 5 * * 0',
    $$SELECT session_cleanup.archive_old_entities(180)$$
);

-- Collaboration expiry
SELECT cron.schedule(
    'collab_expiry_job',
    '30 0 * * *',
    $$SELECT agent_perm.process_collaboration_requests()$$
);

-- Workspace cleanup (daily 01:00)
SELECT cron.schedule(
    'workspace_cleanup_job',
    '0 1 * * *',
    $$SELECT workspace_manager.cleanup_abandoned()$$
);

-- Stale workspace detection (hourly)
SELECT cron.schedule(
    'stale_workspace_detect_job',
    '0 * * * *',
    $$UPDATE workspaces SET status = 'PAUSED', updated_at = now() WHERE status = 'ACTIVE' AND updated_at < now() - INTERVAL '7 days' AND workspace_id NOT IN (SELECT DISTINCT workspace_id FROM agent_session WHERE workspace_id IS NOT NULL AND is_active = TRUE)$$
);
