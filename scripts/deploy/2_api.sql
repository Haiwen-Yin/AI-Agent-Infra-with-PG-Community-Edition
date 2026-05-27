-- ============================================================================
-- PostgreSQL Memory System v2.3.1 - API Functions
-- ============================================================================

-- ============================================================================
-- Schema: memory_fusion
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS memory_fusion;

CREATE OR REPLACE FUNCTION memory_fusion.fuse_similar_memories(
    p_category     TEXT    DEFAULT NULL,
    p_min_similarity NUMERIC DEFAULT 0.85,
    p_dry_run      BOOLEAN DEFAULT TRUE
)
RETURNS TABLE(source_id BIGINT, target_id BIGINT, similarity NUMERIC, action TEXT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_pair RECORD;
    v_sim  NUMERIC;
BEGIN
    FOR v_pair IN
        SELECT e1.entity_id AS src, e2.entity_id AS tgt,
               similarity(e1.title, e2.title) AS sim
        FROM entities e1
        JOIN entities e2 ON e1.entity_id < e2.entity_id
                        AND e1.entity_type = 'MEMORY'
                        AND e2.entity_type = 'MEMORY'
                        AND e1.status = 'ACTIVE'
                        AND e2.status = 'ACTIVE'
        WHERE (p_category IS NULL OR (e1.category = p_category AND e2.category = p_category))
          AND similarity(e1.title, e2.title) >= p_min_similarity
    LOOP
        IF p_dry_run THEN
            action := 'WOULD_FUSE';
        ELSE
            INSERT INTO entity_edges (source_id, target_id, edge_type, strength, confidence)
            VALUES (v_pair.src, v_pair.tgt, 'SIMILAR_TO', v_pair.sim::NUMERIC, 0.9)
            ON CONFLICT DO NOTHING;

            UPDATE entities
            SET status = 'ARCHIVED', updated_at = now()
            WHERE entity_id = v_pair.tgt;

            action := 'FUSED';
        END IF;

        similarity := v_pair.sim;
        source_id  := v_pair.src;
        target_id  := v_pair.tgt;
        RETURN NEXT;
    END LOOP;

    RETURN;
END;
$$;

CREATE OR REPLACE FUNCTION memory_fusion.extract_knowledge_from_memories(
    p_category  TEXT DEFAULT NULL,
    p_min_count INT  DEFAULT 3
)
RETURNS TABLE(category TEXT, memory_count INT, knowledge_entity_id BIGINT)
LANGUAGE plpgsql
AS $$
DECLARE
    v_grp RECORD;
    v_new_id BIGINT;
BEGIN
    FOR v_grp IN
        SELECT e.category, COUNT(*) AS cnt,
               STRING_AGG(e.title, '; ') AS agg_names,
               STRING_AGG(COALESCE(e.description, ''), '; ') AS agg_desc
        FROM entities e
        WHERE e.entity_type = 'MEMORY'
          AND e.status = 'ACTIVE'
          AND (p_category IS NULL OR e.category = p_category)
        GROUP BY e.category
        HAVING COUNT(*) >= p_min_count
    LOOP
        INSERT INTO entities (entity_type, name, description, category, metadata, status)
        VALUES (
            'KNOWLEDGE',
            'Knowledge: ' || v_grp.category,
            v_grp.agg_desc,
            v_grp.category,
            jsonb_build_object('source_count', v_grp.cnt, 'source_names', v_grp.agg_names),
            'ACTIVE'
        )
        RETURNING entity_id INTO v_new_id;

        INSERT INTO knowledge_meta (entity_id, source_type, validation_status, confidence, version, is_current)
        VALUES (v_new_id, 'EXTRACTED', 'PENDING', 0.7, 1, TRUE);

        category := v_grp.category;
        memory_count := v_grp.cnt;
        knowledge_entity_id := v_new_id;
        RETURN NEXT;
    END LOOP;

    RETURN;
END;
$$;

CREATE OR REPLACE FUNCTION memory_fusion.decay_old_memories(
    p_days_threshold INT     DEFAULT 90,
    p_decay_factor   NUMERIC DEFAULT 0.5
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE entities
    SET priority = GREATEST(1, LEAST(5, ROUND(priority * p_decay_factor))),
        updated_at = now()
    WHERE entity_type = 'MEMORY'
      AND status = 'ACTIVE'
      AND created_at < now() - (p_days_threshold || ' days')::INTERVAL
      AND priority > 1;

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

CREATE OR REPLACE FUNCTION memory_fusion.get_fusion_stats()
RETURNS JSONB
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_memories      INT;
    v_knowledge     INT;
    v_edges         INT;
    v_similar_pairs INT;
    v_archived      INT;
BEGIN
    SELECT COUNT(*) INTO v_memories FROM entities WHERE entity_type = 'MEMORY' AND status = 'ACTIVE';
    SELECT COUNT(*) INTO v_knowledge FROM entities WHERE entity_type = 'KNOWLEDGE' AND status = 'ACTIVE';
    SELECT COUNT(*) INTO v_edges FROM entity_edges WHERE edge_type = 'SIMILAR_TO';
    SELECT COUNT(*) INTO v_similar_pairs FROM entity_edges WHERE edge_type = 'SIMILAR_TO';
    SELECT COUNT(*) INTO v_archived FROM entities WHERE entity_type = 'MEMORY' AND status = 'ARCHIVED';

    RETURN jsonb_build_object(
        'active_memories', v_memories,
        'active_knowledge', v_knowledge,
        'similar_edges', v_edges,
        'similar_pairs', v_similar_pairs,
        'archived_memories', v_archived
    );
END;
$$;

-- ============================================================================
-- Schema: knowledge_api
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS knowledge_api;

CREATE OR REPLACE FUNCTION knowledge_api.validate_concept(
    p_entity_id BIGINT,
    p_validator  TEXT DEFAULT 'SYSTEM'
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE knowledge_meta
    SET validation_status = 'VALIDATED',
        validated_at = now()
    WHERE entity_id = p_entity_id
      AND validation_status = 'PENDING';

    UPDATE entities
    SET updated_at = now()
    WHERE entity_id = p_entity_id;

    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION knowledge_api.deprecate_concept(
    p_entity_id BIGINT,
    p_reason     TEXT DEFAULT NULL
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE knowledge_meta
    SET is_current = FALSE,
        deprecated_at = now(),
        validation_status = 'DEPRECATED'
    WHERE entity_id = p_entity_id;

    UPDATE entities
    SET status = 'DEPRECATED',
        updated_at = now()
    WHERE entity_id = p_entity_id;

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION knowledge_api.create_concept_version(
    p_entity_id  BIGINT,
    p_new_content TEXT
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_old_meta  RECORD;
    v_new_id    BIGINT;
BEGIN
    SELECT * INTO v_old_meta FROM knowledge_meta WHERE entity_id = p_entity_id AND is_current = TRUE;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'No current knowledge_meta found for entity_id %', p_entity_id;
    END IF;

    UPDATE knowledge_meta
    SET is_current = FALSE
    WHERE entity_id = p_entity_id AND is_current = TRUE;

    INSERT INTO entities (entity_type, name, description, content, category, metadata, status, owned_by_agent, visibility, accessible_to)
    SELECT entity_type, name, description, p_new_content, category, metadata, 'ACTIVE', owned_by_agent, visibility, accessible_to
    FROM entities
    WHERE entity_id = p_entity_id
    RETURNING entity_id INTO v_new_id;

    INSERT INTO knowledge_meta (entity_id, source_type, source_entity_ids, validation_status, confidence, version, is_current)
    VALUES (
        v_new_id,
        v_old_meta.source_type,
        jsonb_build_array(p_entity_id),
        'PENDING',
        v_old_meta.confidence,
        v_old_meta.version + 1,
        TRUE
    );

    INSERT INTO entity_edges (source_id, target_id, edge_type, strength, confidence)
    VALUES (p_entity_id, v_new_id, 'EVOLVED_FROM', 1.0, 0.9);

    RETURN v_new_id;
END;
$$;

CREATE OR REPLACE FUNCTION knowledge_api.get_unvalidated()
RETURNS TABLE(entity_id BIGINT, name VARCHAR, category VARCHAR, validation_status VARCHAR, confidence NUMERIC, version INT)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT e.entity_id, e.title, e.category, km.validation_status, km.confidence, km.version
    FROM entities e
    JOIN knowledge_meta km ON e.entity_id = km.entity_id
    WHERE km.validation_status = 'PENDING'
      AND e.status = 'ACTIVE'
    ORDER BY km.confidence DESC;
END;
$$;

CREATE OR REPLACE FUNCTION knowledge_api.get_concept_lineage(p_entity_id BIGINT)
RETURNS JSONB
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_ancestors   JSONB;
    v_descendants JSONB;
BEGIN
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'entity_id', e.entity_id,
        'name', e.title,
        'edge_type', ee.edge_type
    )), '[]'::jsonb) INTO v_ancestors
    FROM entity_edges ee
    JOIN entities e ON ee.source_id = e.entity_id
    WHERE ee.target_id = p_entity_id
      AND ee.edge_type IN ('DERIVED_FROM', 'EVOLVED_FROM');

    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'entity_id', e.entity_id,
        'name', e.title,
        'edge_type', ee.edge_type
    )), '[]'::jsonb) INTO v_descendants
    FROM entity_edges ee
    JOIN entities e ON ee.target_id = e.entity_id
    WHERE ee.source_id = p_entity_id
      AND ee.edge_type IN ('DERIVED_FROM', 'EVOLVED_FROM');

    RETURN jsonb_build_object(
        'entity_id', p_entity_id,
        'ancestors', v_ancestors,
        'descendants', v_descendants
    );
END;
$$;

-- ============================================================================
-- Schema: agent_perm
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS agent_perm;

CREATE OR REPLACE FUNCTION agent_perm.check_entity_access(
    p_agent_id    VARCHAR,
    p_entity_id   BIGINT,
    p_access_type VARCHAR
)
RETURNS TEXT
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_entity RECORD;
BEGIN
    SELECT entity_id, visibility, owned_by_agent, accessible_to
    INTO v_entity
    FROM entities
    WHERE entity_id = p_entity_id;

    IF NOT FOUND THEN
        RETURN 'DENIED:NO_ENTITY';
    END IF;

    IF v_entity.visibility = 'SHARED' THEN
        RETURN 'GRANTED';
    END IF;

    IF v_entity.visibility = 'PRIVATE' THEN
        IF v_entity.owned_by_agent = p_agent_id THEN
            RETURN 'GRANTED';
        END IF;
        RETURN 'DENIED:PRIVATE';
    END IF;

    IF v_entity.visibility = 'COLLABORATIVE' THEN
        IF v_entity.owned_by_agent = p_agent_id THEN
            RETURN 'GRANTED';
        END IF;
        IF v_entity.accessible_to @> jsonb_build_array(p_agent_id) THEN
            RETURN 'GRANTED';
        END IF;
        RETURN 'DENIED:NOT_IN_ACCESS_LIST';
    END IF;

    RETURN 'DENIED:UNKNOWN_VISIBILITY';
END;
$$;

CREATE OR REPLACE FUNCTION agent_perm.grant_access(
    p_agent_id   VARCHAR,
    p_entity_id  BIGINT,
    p_granted_by VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
DECLARE
    v_current_accessible JSONB;
BEGIN
    SELECT accessible_to INTO v_current_accessible
    FROM entities WHERE entity_id = p_entity_id;

    IF v_current_accessible @> jsonb_build_array(p_agent_id) THEN
        RETURN TRUE;
    END IF;

    UPDATE entities
    SET accessible_to = COALESCE(accessible_to, '[]'::jsonb) || jsonb_build_array(p_agent_id),
        visibility = 'COLLABORATIVE',
        updated_at = now()
    WHERE entity_id = p_entity_id;

    INSERT INTO entity_access_log (agent_id, entity_id, access_type)
    VALUES (p_agent_id, p_entity_id, 'SHARE');

    RETURN TRUE;
END;
$$;

CREATE OR REPLACE FUNCTION agent_perm.revoke_access(
    p_agent_id  VARCHAR,
    p_entity_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE entities
    SET accessible_to = (
            SELECT jsonb_agg(elem)
            FROM jsonb_array_elements(accessible_to) AS elem
            WHERE elem #>> '{}' <> p_agent_id
        ),
        updated_at = now()
    WHERE entity_id = p_entity_id
      AND accessible_to @> jsonb_build_array(p_agent_id);

    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION agent_perm.cleanup_expired_sessions()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE agent_session
    SET is_active = FALSE,
        end_time = now()
    WHERE is_active = TRUE
      AND last_activity < now() - INTERVAL '300 minutes';

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

CREATE OR REPLACE FUNCTION agent_perm.process_collaboration_requests()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE agent_collaboration
    SET status = 'EXPIRED'
    WHERE status = 'PENDING'
      AND created_at < now() - INTERVAL '7 days';

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

-- ============================================================================
-- Schema: session_cleanup
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS session_cleanup;

CREATE OR REPLACE FUNCTION session_cleanup.purge_access_logs(
    p_days_to_keep INT DEFAULT 90
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_access INT;
    v_perm   INT;
BEGIN
    DELETE FROM entity_access_log
    WHERE access_time < now() - (p_days_to_keep || ' days')::INTERVAL;
    GET DIAGNOSTICS v_access = ROW_COUNT;

    DELETE FROM agent_permission_log
    WHERE created_at < now() - (p_days_to_keep || ' days')::INTERVAL;
    GET DIAGNOSTICS v_perm = ROW_COUNT;

    RETURN v_access + v_perm;
END;
$$;

CREATE OR REPLACE FUNCTION session_cleanup.purge_inactive_sessions(
    p_days_to_keep INT DEFAULT 30
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    DELETE FROM agent_session
    WHERE is_active = FALSE
      AND end_time < now() - (p_days_to_keep || ' days')::INTERVAL;

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

CREATE OR REPLACE FUNCTION session_cleanup.archive_old_entities(
    p_days_threshold INT DEFAULT 180
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE entities
    SET status = 'ARCHIVED',
        updated_at = now()
    WHERE entity_type = 'MEMORY'
      AND status = 'ACTIVE'
      AND priority >= 3
      AND created_at < now() - (p_days_threshold || ' days')::INTERVAL;

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

CREATE OR REPLACE FUNCTION session_cleanup.update_tag_counts()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE tags t
    SET usage_count = (
        SELECT COUNT(*) FROM entity_tags et WHERE et.tag_id = t.tag_id
    );

    GET DIAGNOSTICS v_affected = ROW_COUNT;

    DELETE FROM tags WHERE usage_count = 0;

    RETURN v_affected;
END;
$$;


-- ============================================================================
-- knowledge_api additions (v2.2.0)
-- ============================================================================

CREATE OR REPLACE FUNCTION knowledge_api.record_review(
    p_entity_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE knowledge_meta
    SET review_count = review_count + 1,
        last_reviewed = now(),
        next_review = now() + LEAST(POWER(2, review_count + 1), 30) * INTERVAL '1 day'
    WHERE entity_id = p_entity_id;
    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION knowledge_api.get_due_reviews(
    p_limit INT DEFAULT 50
)
RETURNS TABLE(entity_id BIGINT, title VARCHAR, domain VARCHAR, next_review TIMESTAMPTZ)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT e.entity_id, e.title, km.domain, km.next_review
    FROM entities e
    JOIN knowledge_meta km ON e.entity_id = km.entity_id
    WHERE km.next_review <= now()
      AND e.status = 'ACTIVE'
      AND e.entity_type = 'KNOWLEDGE'
    ORDER BY km.next_review ASC
    LIMIT p_limit;
END;
$$;


-- ============================================================================
-- Schema: workspace_manager (v2.2.0)
-- ============================================================================

CREATE SCHEMA IF NOT EXISTS workspace_manager;

CREATE OR REPLACE FUNCTION workspace_manager.create_workspace(
    p_name          VARCHAR DEFAULT NULL,
    p_workspace_type VARCHAR DEFAULT 'CONVERSATION',
    p_isolation_mode VARCHAR DEFAULT 'SHARED',
    p_owner_user_id  VARCHAR DEFAULT NULL
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_workspace_id BIGINT;
BEGIN
    INSERT INTO workspaces (workspace_name, workspace_type, isolation_mode, owner_user_id)
    VALUES (p_name, p_workspace_type, p_isolation_mode, p_owner_user_id)
    RETURNING workspace_id INTO v_workspace_id;
    RETURN v_workspace_id;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.get_workspace(
    p_workspace_id BIGINT
)
RETURNS JSONB
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'workspace_id', workspace_id,
        'workspace_name', workspace_name,
        'workspace_type', workspace_type,
        'isolation_mode', isolation_mode,
        'owner_user_id', owner_user_id,
        'current_agent_id', current_agent_id,
        'current_session_id', current_session_id,
        'summary', summary,
        'metadata', metadata,
        'status', status,
        'created_at', created_at,
        'updated_at', updated_at
    ) INTO v_result
    FROM workspaces
    WHERE workspace_id = p_workspace_id;
    RETURN v_result;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.update_workspace_status(
    p_workspace_id BIGINT,
    p_new_status   VARCHAR
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE workspaces
    SET status = p_new_status, updated_at = now()
    WHERE workspace_id = p_workspace_id
      AND status IN ('ACTIVE', 'PAUSED');
    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.delete_workspace(
    p_workspace_id BIGINT
)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM workspaces WHERE workspace_id = p_workspace_id;
    RETURN FOUND;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.add_context_entry(
    p_workspace_id BIGINT,
    p_agent_id     VARCHAR,
    p_context_type VARCHAR,
    p_session_id   VARCHAR DEFAULT NULL,
    p_context_data JSONB DEFAULT '{}'
)
RETURNS BIGINT
LANGUAGE plpgsql
AS $$
DECLARE
    v_context_id BIGINT;
BEGIN
    INSERT INTO workspace_context (workspace_id, agent_id, session_id, context_type, context_data)
    VALUES (p_workspace_id, p_agent_id, p_session_id, p_context_type, p_context_data)
    RETURNING context_id INTO v_context_id;
    RETURN v_context_id;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.get_context_chain(
    p_workspace_id BIGINT,
    p_limit        INT DEFAULT 10
)
RETURNS TABLE(context_id BIGINT, context_type VARCHAR, context_data JSONB, created_at TIMESTAMPTZ)
LANGUAGE plpgsql STABLE
AS $$
BEGIN
    RETURN QUERY
    SELECT wc.context_id, wc.context_type, wc.context_data, wc.created_at
    FROM workspace_context wc
    WHERE wc.workspace_id = p_workspace_id
    ORDER BY wc.created_at DESC
    LIMIT p_limit;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.create_handoff(
    p_workspace_id    BIGINT,
    p_new_agent_id    VARCHAR,
    p_handoff_data    JSONB DEFAULT '{}'
)
RETURNS VARCHAR
LANGUAGE plpgsql
AS $$
DECLARE
    v_ws            RECORD;
    v_session_id    VARCHAR;
BEGIN
    SELECT * INTO v_ws FROM workspaces WHERE workspace_id = p_workspace_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Workspace not found: %', p_workspace_id;
    END IF;

    v_session_id := 'session-' || p_new_agent_id || '-' || extract(epoch from now())::TEXT;

    INSERT INTO agent_session (session_id, agent_id, owner_user_id, workspace_id,
                               predecessor_session_id, is_active, context)
    VALUES (v_session_id, p_new_agent_id, v_ws.owner_user_id, p_workspace_id,
            v_ws.current_session_id, TRUE, p_handoff_data);

    INSERT INTO workspace_context (workspace_id, agent_id, session_id, context_type, context_data)
    VALUES (p_workspace_id, p_new_agent_id, v_session_id, 'HANDOFF', p_handoff_data);

    UPDATE workspaces
    SET current_agent_id = p_new_agent_id,
        current_session_id = v_session_id,
        updated_at = now()
    WHERE workspace_id = p_workspace_id;

    RETURN v_session_id;
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.recover_to_checkpoint(
    p_workspace_id BIGINT
)
RETURNS JSONB
LANGUAGE plpgsql
AS $$
DECLARE
    v_ws         RECORD;
    v_checkpoint JSONB;
    v_tasks      JSONB;
    v_sessions   JSONB;
    v_entities   JSONB;
BEGIN
    SELECT * INTO v_ws FROM workspaces WHERE workspace_id = p_workspace_id;
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'context_id', context_id, 'context_type', context_type,
        'context_data', context_data, 'created_at', created_at
    )), '[]'::jsonb) INTO v_checkpoint
    FROM (
        SELECT context_id, context_type, context_data, created_at
        FROM workspace_context
        WHERE workspace_id = p_workspace_id
        ORDER BY created_at DESC LIMIT 5
    ) sub;

    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'plan_id', tp.plan_id, 'goal', tp.goal, 'status', tp.status
    )), '[]'::jsonb) INTO v_tasks
    FROM task_plans tp
    JOIN workspace_tasks wt ON tp.plan_id = wt.plan_id
    WHERE wt.workspace_id = p_workspace_id
      AND tp.status IN ('PENDING', 'RUNNING', 'BLOCKED');

    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'session_id', session_id, 'agent_id', agent_id, 'is_active', is_active
    )), '[]'::jsonb) INTO v_sessions
    FROM (
        SELECT session_id, agent_id, is_active
        FROM agent_session
        WHERE workspace_id = p_workspace_id
        ORDER BY start_time DESC LIMIT 5
    ) sub;

    IF v_ws.isolation_mode = 'ISOLATED' THEN
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'entity_id', entity_id, 'title', title, 'entity_type', entity_type
        )), '[]'::jsonb) INTO v_entities
        FROM (
            SELECT entity_id, title, entity_type
            FROM entities
            WHERE workspace_id = p_workspace_id
            ORDER BY updated_at DESC LIMIT 10
        ) sub;
    ELSE
        v_entities := '[]'::jsonb;
    END IF;

    RETURN jsonb_build_object(
        'workspace', row_to_json(v_ws),
        'context_chain', v_checkpoint,
        'active_tasks', v_tasks,
        'recent_sessions', v_sessions,
        'recent_entities', v_entities
    );
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.get_workspace_summary(
    p_workspace_id BIGINT
)
RETURNS JSONB
LANGUAGE plpgsql STABLE
AS $$
DECLARE
    v_ws         RECORD;
    v_ctx_count  INT;
    v_task_count INT;
BEGIN
    SELECT * INTO v_ws FROM workspaces WHERE workspace_id = p_workspace_id;
    IF NOT FOUND THEN
        RETURN NULL;
    END IF;

    SELECT COUNT(*) INTO v_ctx_count
    FROM workspace_context WHERE workspace_id = p_workspace_id;

    SELECT COUNT(*) INTO v_task_count
    FROM workspace_tasks WHERE workspace_id = p_workspace_id;

    RETURN jsonb_build_object(
        'workspace_id', v_ws.workspace_id,
        'workspace_name', v_ws.workspace_name,
        'status', v_ws.status,
        'isolation_mode', v_ws.isolation_mode,
        'current_agent_id', v_ws.current_agent_id,
        'context_count', v_ctx_count,
        'task_count', v_task_count
    );
END;
$$;

CREATE OR REPLACE FUNCTION workspace_manager.cleanup_abandoned()
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE workspaces
    SET status = 'ARCHIVED', updated_at = now()
    WHERE status = 'ACTIVE'
      AND updated_at < now() - INTERVAL '30 days'
      AND workspace_id NOT IN (
          SELECT DISTINCT workspace_id FROM agent_session
          WHERE workspace_id IS NOT NULL AND is_active = TRUE
      );
    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$;

-- ============================================================================
-- Schema: spec_manager (v2.3.0)
-- ============================================================================

CREATE OR REPLACE FUNCTION spec_manager.create_spec(
    p_title VARCHAR,
    p_content TEXT DEFAULT NULL,
    p_summary TEXT DEFAULT NULL,
    p_spec_scope VARCHAR DEFAULT NULL,
    p_complexity VARCHAR DEFAULT 'MEDIUM',
    p_acceptance_criteria JSONB DEFAULT NULL,
    p_spec_constraints JSONB DEFAULT NULL,
    p_importance INT DEFAULT 5,
    p_owned_by_agent VARCHAR DEFAULT NULL,
    p_visibility VARCHAR DEFAULT 'SHARED',
    p_workspace_id BIGINT DEFAULT NULL,
    p_parent_spec_id BIGINT DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_entity_id BIGINT;
BEGIN
    INSERT INTO entities (entity_type, title, content, summary, importance, owned_by_agent, visibility, workspace_id)
    VALUES ('SPEC', p_title, p_content, p_summary, p_importance, p_owned_by_agent, p_visibility, p_workspace_id)
    RETURNING entity_id INTO v_entity_id;

    INSERT INTO spec_meta (entity_id, spec_scope, complexity, acceptance_criteria, spec_constraints, parent_spec_id)
    VALUES (v_entity_id, p_spec_scope, p_complexity, p_acceptance_criteria, p_spec_constraints, p_parent_spec_id);

    RETURN v_entity_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION spec_manager.get_spec(p_entity_id BIGINT) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'entity_id', e.entity_id,
        'title', e.title,
        'content', e.content,
        'summary', e.summary,
        'importance', e.importance,
        'visibility', e.visibility,
        'owned_by_agent', e.owned_by_agent,
        'workspace_id', e.workspace_id,
        'spec_version', sm.spec_version,
        'spec_status', sm.spec_status,
        'spec_scope', sm.spec_scope,
        'complexity', sm.complexity,
        'acceptance_criteria', sm.acceptance_criteria,
        'spec_constraints', sm.spec_constraints,
        'parent_spec_id', sm.parent_spec_id
    ) INTO v_result
    FROM entities e
    JOIN spec_meta sm ON sm.entity_id = e.entity_id
    WHERE e.entity_id = p_entity_id AND e.entity_type = 'SPEC';

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION spec_manager.update_spec_status(p_entity_id BIGINT, p_new_status VARCHAR) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE spec_meta SET spec_status = p_new_status WHERE entity_id = p_entity_id;
    UPDATE entities SET updated_at = now() WHERE entity_id = p_entity_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION spec_manager.validate_spec(p_entity_id BIGINT) RETURNS JSONB AS $$
DECLARE
    v_spec JSONB;
    v_errors TEXT[] := '{}';
    v_warnings TEXT[] := '{}';
BEGIN
    SELECT jsonb_build_object('title', e.title, 'acceptance_criteria', sm.acceptance_criteria, 'spec_constraints', sm.spec_constraints)
    INTO v_spec
    FROM entities e JOIN spec_meta sm ON sm.entity_id = e.entity_id
    WHERE e.entity_id = p_entity_id AND e.entity_type = 'SPEC';

    IF v_spec IS NULL THEN RETURN jsonb_build_object('valid', false, 'errors', ARRAY['Spec not found']); END IF;
    IF v_spec->>'acceptance_criteria' IS NULL OR v_spec->>'acceptance_criteria' = 'null' THEN
        v_errors := array_append(v_errors, 'No acceptance criteria defined');
    END IF;

    RETURN jsonb_build_object('valid', array_length(v_errors, 1) IS NULL, 'errors', v_errors, 'warnings', v_warnings);
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION spec_manager.link_spec_to_plan(
    p_spec_id BIGINT, p_plan_id BIGINT, p_link_type VARCHAR DEFAULT 'DRIVES', p_link_strength NUMERIC DEFAULT 1.0
) RETURNS BIGINT AS $$
DECLARE
    v_link_id BIGINT;
BEGIN
    INSERT INTO spec_plan_links (spec_id, plan_id, link_type, link_strength)
    VALUES (p_spec_id, p_plan_id, p_link_type, p_link_strength)
    ON CONFLICT (spec_id, plan_id, link_type) DO NOTHING
    RETURNING link_id INTO v_link_id;
    RETURN v_link_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION spec_manager.get_spec_plan_links(p_spec_id BIGINT) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'link_id', spl.link_id,
        'plan_id', spl.plan_id,
        'link_type', spl.link_type,
        'link_strength', spl.link_strength,
        'goal', tp.goal,
        'status', tp.status
    )), '[]'::jsonb) INTO v_result
    FROM spec_plan_links spl
    LEFT JOIN task_plans tp ON tp.plan_id = spl.plan_id
    WHERE spl.spec_id = p_spec_id;
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Schema: collab_group_manager (v2.3.0)
-- ============================================================================

CREATE OR REPLACE FUNCTION collab_group_manager.create_group(
    p_group_name VARCHAR,
    p_group_type VARCHAR DEFAULT 'TEAM',
    p_description TEXT DEFAULT NULL,
    p_sharing_policy VARCHAR DEFAULT 'OPEN',
    p_coordinator_agent_id VARCHAR DEFAULT NULL
) RETURNS BIGINT AS $$
DECLARE
    v_group_id BIGINT;
    v_workspace_id BIGINT;
BEGIN
    INSERT INTO workspaces (workspace_name, workspace_type, isolation_mode)
    VALUES (p_group_name || ' (Shared)', 'COLLAB_GROUP', 'SHARED')
    RETURNING workspace_id INTO v_workspace_id;

    INSERT INTO collab_groups (group_name, group_type, description, workspace_id, coordinator_agent_id, sharing_policy)
    VALUES (p_group_name, p_group_type, p_description, v_workspace_id, p_coordinator_agent_id, p_sharing_policy)
    RETURNING group_id INTO v_group_id;

    RETURN v_group_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.get_group(p_group_id BIGINT) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'group_id', cg.group_id,
        'group_name', cg.group_name,
        'group_type', cg.group_type,
        'description', cg.description,
        'workspace_id', cg.workspace_id,
        'coordinator_agent_id', cg.coordinator_agent_id,
        'sharing_policy', cg.sharing_policy,
        'status', cg.status,
        'member_count', (SELECT COUNT(*) FROM collab_group_members WHERE group_id = p_group_id AND status = 'ACTIVE')
    ) INTO v_result
    FROM collab_groups cg
    WHERE cg.group_id = p_group_id;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.update_group(p_group_id BIGINT, p_status VARCHAR DEFAULT NULL, p_sharing_policy VARCHAR DEFAULT NULL) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE collab_groups SET
        status = COALESCE(p_status, status),
        sharing_policy = COALESCE(p_sharing_policy, sharing_policy),
        updated_at = now()
    WHERE group_id = p_group_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.add_member(
    p_group_id BIGINT, p_agent_id VARCHAR, p_role VARCHAR DEFAULT 'CONTRIBUTOR'
) RETURNS BIGINT AS $$
DECLARE
    v_member_id BIGINT;
    v_ws_id BIGINT;
BEGIN
    IF p_role IN ('LEAD', 'CONTRIBUTOR') THEN
        INSERT INTO workspaces (workspace_name, workspace_type, isolation_mode)
        VALUES ((SELECT group_name FROM collab_groups WHERE group_id = p_group_id) || ' - ' || p_agent_id, 'PERSONAL_IN_GROUP', 'ISOLATED')
        RETURNING workspace_id INTO v_ws_id;
    END IF;

    INSERT INTO collab_group_members (group_id, agent_id, role, personal_workspace_id)
    VALUES (p_group_id, p_agent_id, p_role, v_ws_id)
    ON CONFLICT (group_id, agent_id) DO UPDATE SET status = 'ACTIVE', role = EXCLUDED.role, personal_workspace_id = COALESCE(collab_group_members.personal_workspace_id, EXCLUDED.personal_workspace_id)
    RETURNING member_id INTO v_member_id;

    RETURN v_member_id;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.remove_member(p_group_id BIGINT, p_agent_id VARCHAR) RETURNS BOOLEAN AS $$
BEGIN
    UPDATE collab_group_members SET status = 'REMOVED' WHERE group_id = p_group_id AND agent_id = p_agent_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.get_group_members(p_group_id BIGINT) RETURNS JSONB AS $$
DECLARE
    v_result JSONB;
BEGIN
    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'member_id', cgm.member_id,
        'agent_id', cgm.agent_id,
        'role', cgm.role,
        'personal_workspace_id', cgm.personal_workspace_id,
        'joined_at', cgm.joined_at,
        'status', cgm.status
    )), '[]'::jsonb) INTO v_result
    FROM collab_group_members cgm
    WHERE cgm.group_id = p_group_id AND cgm.status = 'ACTIVE';
    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION collab_group_manager.cleanup_groups() RETURNS INT AS $$
DECLARE
    v_affected INT;
BEGIN
    UPDATE collab_groups SET status = 'ARCHIVED', updated_at = now()
    WHERE status = 'ACTIVE'
      AND group_id NOT IN (SELECT DISTINCT group_id FROM collab_group_members WHERE status = 'ACTIVE');
    GET DIAGNOSTICS v_affected = ROW_COUNT;
    RETURN v_affected;
END;
$$ LANGUAGE plpgsql;
