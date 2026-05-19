-- ============================================================================
-- PostgreSQL Memory System v2.0.0 - API Functions
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
               similarity(e1.name, e2.name) AS sim
        FROM entities e1
        JOIN entities e2 ON e1.entity_id < e2.entity_id
                        AND e1.entity_type = 'MEMORY'
                        AND e2.entity_type = 'MEMORY'
                        AND e1.status = 'ACTIVE'
                        AND e2.status = 'ACTIVE'
        WHERE (p_category IS NULL OR (e1.category = p_category AND e2.category = p_category))
          AND similarity(e1.name, e2.name) >= p_min_similarity
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
               STRING_AGG(e.name, '; ') AS agg_names,
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
    SELECT e.entity_id, e.name, e.category, km.validation_status, km.confidence, km.version
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
        'name', e.name,
        'edge_type', ee.edge_type
    )), '[]'::jsonb) INTO v_ancestors
    FROM entity_edges ee
    JOIN entities e ON ee.source_id = e.entity_id
    WHERE ee.target_id = p_entity_id
      AND ee.edge_type IN ('DERIVED_FROM', 'EVOLVED_FROM');

    SELECT COALESCE(jsonb_agg(jsonb_build_object(
        'entity_id', e.entity_id,
        'name', e.name,
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
