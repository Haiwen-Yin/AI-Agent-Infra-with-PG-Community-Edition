-- ============================================================================
-- PostgreSQL Memory System v2.0.0 - Scheduled Jobs (pg_cron)
-- ============================================================================

-- Install pg_cron extension
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- ============================================================================
-- Cron Jobs
-- ============================================================================

-- Memory fusion and decay: daily at 2:00 AM
SELECT cron.schedule(
    'memory_fusion_job',
    '0 2 * * *',
    $$SELECT memory_fusion.fuse_similar_memories(); SELECT memory_fusion.decay_old_memories();$$
);

-- Knowledge extraction: daily at 3:00 AM
SELECT cron.schedule(
    'knowledge_extraction_job',
    '0 3 * * *',
    $$SELECT memory_fusion.extract_knowledge_from_memories();$$
);

-- Session cleanup: every 30 minutes
SELECT cron.schedule(
    'session_cleanup_job',
    '*/30 * * * *',
    $$SELECT agent_perm.cleanup_expired_sessions(); SELECT session_cleanup.purge_inactive_sessions();$$
);

-- Access log purge: weekly on Sunday at 4:00 AM
SELECT cron.schedule(
    'access_log_purge_job',
    '0 4 * * 0',
    $$SELECT session_cleanup.purge_access_logs();$$
);

-- Tag count update: daily at 1:00 AM
SELECT cron.schedule(
    'tag_count_update_job',
    '0 1 * * *',
    $$SELECT session_cleanup.update_tag_counts();$$
);

-- Collaboration expiry: daily at 0:30 AM
SELECT cron.schedule(
    'collab_expiry_job',
    '30 0 * * *',
    $$SELECT agent_perm.process_collaboration_requests();$$
);

-- Entity archive: weekly on Sunday at 5:00 AM
SELECT cron.schedule(
    'entity_archive_job',
    '0 5 * * 0',
    $$SELECT session_cleanup.archive_old_entities();$$
);

-- ============================================================================
-- Verify: List all scheduled jobs
-- ============================================================================

SELECT jobid, schedule, command, nodename, nodeport, database, username, active
FROM cron.job
ORDER BY jobid;

-- ============================================================================
-- Alternative: If pg_cron is not available, use the following manual approach:
-- ============================================================================
--
-- Run these commands manually or via external scheduler (cron, systemd timer):
--
-- Memory fusion + decay (daily 2 AM):
--   psql -c "SELECT memory_fusion.fuse_similar_memories(); SELECT memory_fusion.decay_old_memories();"
--
-- Knowledge extraction (daily 3 AM):
--   psql -c "SELECT memory_fusion.extract_knowledge_from_memories();"
--
-- Session cleanup (every 30 min):
--   psql -c "SELECT agent_perm.cleanup_expired_sessions(); SELECT session_cleanup.purge_inactive_sessions();"
--
-- Access log purge (weekly Sunday 4 AM):
--   psql -c "SELECT session_cleanup.purge_access_logs();"
--
-- Tag count update (daily 1 AM):
--   psql -c "SELECT session_cleanup.update_tag_counts();"
--
-- Collaboration expiry (daily 0:30 AM):
--   psql -c "SELECT agent_perm.process_collaboration_requests();"
--
-- Entity archive (weekly Sunday 5 AM):
--   psql -c "SELECT session_cleanup.archive_old_entities();"
