--
-- PostgreSQL database dump
--

-- ============================================================
-- Schema owner configuration (adjust if not using default pgsql)
-- ============================================================
\set schema_owner 'pgsql'

\restrict VcAj5J5oNBrPslUHp6nHjRhkrqhnWbVSvhjvs2bkENgycNjLKIqFnra5ZxcIB9j

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

DROP POLICY IF EXISTS wt_agent_isolation ON public.workspace_tasks;
DROP POLICY IF EXISTS ws_agent_isolation ON public.workspaces;
DROP POLICY IF EXISTS wc_agent_isolation ON public.workspace_context;
DROP POLICY IF EXISTS spl_agent_isolation ON public.spec_plan_links;
DROP POLICY IF EXISTS spec_meta_end_user ON public.spec_meta;
DROP POLICY IF EXISTS spec_meta_aiadmin ON public.spec_meta;
DROP POLICY IF EXISTS skm_agent_isolation ON public.skill_meta;
DROP POLICY IF EXISTS knowledge_meta_end_user ON public.knowledge_meta;
DROP POLICY IF EXISTS knowledge_meta_aiadmin ON public.knowledge_meta;
DROP POLICY IF EXISTS harness_meta_end_user ON public.harness_meta;
DROP POLICY IF EXISTS harness_meta_aiadmin ON public.harness_meta;
DROP POLICY IF EXISTS et_agent_isolation ON public.entity_tags;
DROP POLICY IF EXISTS entities_agent_isolation ON public.entities;
DROP POLICY IF EXISTS ee_agent_isolation ON public.entity_embeddings;
DROP POLICY IF EXISTS edges_agent_isolation ON public.entity_edges;
DROP POLICY IF EXISTS eal_agent_isolation ON public.entity_access_log;
DROP POLICY IF EXISTS col_agent_isolation ON public.agent_collaboration;
DROP POLICY IF EXISTS cb_agent_isolation ON public.context_branches;
DROP POLICY IF EXISTS bml_agent_isolation ON public.branch_merge_log;
DROP POLICY IF EXISTS as_agent_isolation ON public.agent_session;
DROP POLICY IF EXISTS apl_agent_isolation ON public.agent_permission_log;
DROP POLICY IF EXISTS ac_agent_isolation ON public.agent_credentials;
ALTER TABLE IF EXISTS ONLY public.workspace_tasks DROP CONSTRAINT IF EXISTS fk_wt_workspace;
ALTER TABLE IF EXISTS ONLY public.workspace_context DROP CONSTRAINT IF EXISTS fk_wc_workspace;
ALTER TABLE IF EXISTS ONLY public.workspace_context DROP CONSTRAINT IF EXISTS fk_wc_parent;
ALTER TABLE IF EXISTS ONLY public.workspace_context DROP CONSTRAINT IF EXISTS fk_wc_branch;
ALTER TABLE IF EXISTS ONLY public.workspace_context DROP CONSTRAINT IF EXISTS fk_wc_agent;
ALTER TABLE IF EXISTS public.task_plans DROP CONSTRAINT IF EXISTS fk_tp_branch;
ALTER TABLE IF EXISTS public.task_plans DROP CONSTRAINT IF EXISTS fk_tp_agent;
ALTER TABLE IF EXISTS ONLY public.task_steps DROP CONSTRAINT IF EXISTS fk_step_plan;
ALTER TABLE IF EXISTS public.agent_session DROP CONSTRAINT IF EXISTS fk_session_workspace;
ALTER TABLE IF EXISTS public.agent_session DROP CONSTRAINT IF EXISTS fk_session_branch;
ALTER TABLE IF EXISTS public.agent_session DROP CONSTRAINT IF EXISTS fk_session_agent;
ALTER TABLE IF EXISTS ONLY public.knowledge_meta DROP CONSTRAINT IF EXISTS fk_km_entity;
ALTER TABLE IF EXISTS ONLY public.entity_tags DROP CONSTRAINT IF EXISTS fk_et_tag;
ALTER TABLE IF EXISTS ONLY public.entity_tags DROP CONSTRAINT IF EXISTS fk_et_entity;
ALTER TABLE IF EXISTS public.entities DROP CONSTRAINT IF EXISTS fk_entities_workspace;
ALTER TABLE IF EXISTS ONLY public.entity_embeddings DROP CONSTRAINT IF EXISTS fk_ee_entity;
ALTER TABLE IF EXISTS ONLY public.entity_edges DROP CONSTRAINT IF EXISTS fk_edge_source;
ALTER TABLE IF EXISTS public.entity_access_log DROP CONSTRAINT IF EXISTS fk_eal_agent;
ALTER TABLE IF EXISTS ONLY public.agent_collaboration DROP CONSTRAINT IF EXISTS fk_col_target;
ALTER TABLE IF EXISTS ONLY public.agent_collaboration DROP CONSTRAINT IF EXISTS fk_col_source;
ALTER TABLE IF EXISTS ONLY public.collab_group_members DROP CONSTRAINT IF EXISTS fk_cgm_workspace;
ALTER TABLE IF EXISTS ONLY public.collab_group_members DROP CONSTRAINT IF EXISTS fk_cgm_group;
ALTER TABLE IF EXISTS ONLY public.collab_group_members DROP CONSTRAINT IF EXISTS fk_cgm_agent;
ALTER TABLE IF EXISTS ONLY public.collab_groups DROP CONSTRAINT IF EXISTS fk_cg_workspace;
ALTER TABLE IF EXISTS ONLY public.collab_groups DROP CONSTRAINT IF EXISTS fk_cg_coordinator;
ALTER TABLE IF EXISTS ONLY public.collab_groups DROP CONSTRAINT IF EXISTS fk_cg_branch;
ALTER TABLE IF EXISTS ONLY public.context_branches DROP CONSTRAINT IF EXISTS fk_cb_workspace;
ALTER TABLE IF EXISTS ONLY public.context_branches DROP CONSTRAINT IF EXISTS fk_cb_parent;
ALTER TABLE IF EXISTS ONLY public.context_branches DROP CONSTRAINT IF EXISTS fk_cb_agent;
ALTER TABLE IF EXISTS ONLY public.branch_merge_log DROP CONSTRAINT IF EXISTS fk_bml_tgt;
ALTER TABLE IF EXISTS ONLY public.branch_merge_log DROP CONSTRAINT IF EXISTS fk_bml_src;
ALTER TABLE IF EXISTS ONLY public.agent_registry DROP CONSTRAINT IF EXISTS fk_ar_created_by;
ALTER TABLE IF EXISTS ONLY public.agent_credentials DROP CONSTRAINT IF EXISTS fk_ac_agent;
DROP TRIGGER IF EXISTS trg_workspaces_updated_at ON public.workspaces;
DROP TRIGGER IF EXISTS trg_task_plans_updated_at ON public.task_plans;
DROP TRIGGER IF EXISTS trg_system_users_updated_at ON public.system_users;
DROP TRIGGER IF EXISTS trg_system_config_updated_at ON public.system_config;
DROP TRIGGER IF EXISTS trg_skill_meta_updated_at ON public.skill_meta;
DROP TRIGGER IF EXISTS trg_entities_search_vector ON public.entities;
DROP TRIGGER IF EXISTS trg_collab_groups_updated_at ON public.collab_groups;
DROP TRIGGER IF EXISTS trg_agent_registry_updated_at ON public.agent_registry;
DROP INDEX IF EXISTS public.idx_ws_status;
DROP INDEX IF EXISTS public.idx_ws_owner;
DROP INDEX IF EXISTS public.idx_ws_alias;
DROP INDEX IF EXISTS public.idx_wc_workspace;
DROP INDEX IF EXISTS public.idx_wc_visibility;
DROP INDEX IF EXISTS public.idx_wc_type;
DROP INDEX IF EXISTS public.idx_wc_branch;
DROP INDEX IF EXISTS public.idx_wc_agent;
DROP INDEX IF EXISTS public.idx_ttc_step;
DROP INDEX IF EXISTS public.idx_ttc_plan;
DROP INDEX IF EXISTS public.idx_ts_plan;
DROP INDEX IF EXISTS public.idx_tp_branch;
DROP INDEX IF EXISTS public.idx_tp_agent;
DROP INDEX IF EXISTS public.idx_td_target;
DROP INDEX IF EXISTS public.idx_td_source;
DROP INDEX IF EXISTS public.idx_tcs_plan;
DROP INDEX IF EXISTS public.idx_spl_spec;
DROP INDEX IF EXISTS public.idx_spl_plan;
DROP INDEX IF EXISTS public.idx_sm_spec_status;
DROP INDEX IF EXISTS public.idx_sm_scope;
DROP INDEX IF EXISTS public.idx_sm_complexity;
DROP INDEX IF EXISTS public.idx_sm_branch;
DROP INDEX IF EXISTS public.idx_skm_type;
DROP INDEX IF EXISTS public.idx_skm_status;
DROP INDEX IF EXISTS public.idx_skm_name;
DROP INDEX IF EXISTS public.idx_km_topic;
DROP INDEX IF EXISTS public.idx_km_next_review;
DROP INDEX IF EXISTS public.idx_km_domain;
DROP INDEX IF EXISTS public.idx_km_difficulty;
DROP INDEX IF EXISTS public.idx_hm_exec_mode;
DROP INDEX IF EXISTS public.idx_et_tag;
DROP INDEX IF EXISTS public.idx_ee_model;
DROP INDEX IF EXISTS public.idx_ee_embedding;
DROP INDEX IF EXISTS public.idx_edges_type;
DROP INDEX IF EXISTS public.idx_edges_target_type;
DROP INDEX IF EXISTS public.idx_edges_target;
DROP INDEX IF EXISTS public.idx_col_target;
DROP INDEX IF EXISTS public.idx_col_source;
DROP INDEX IF EXISTS public.idx_cgm_group;
DROP INDEX IF EXISTS public.idx_cgm_agent;
DROP INDEX IF EXISTS public.idx_cg_workspace;
DROP INDEX IF EXISTS public.idx_cg_type;
DROP INDEX IF EXISTS public.idx_cg_status;
DROP INDEX IF EXISTS public.idx_cb_workspace;
DROP INDEX IF EXISTS public.idx_cb_type;
DROP INDEX IF EXISTS public.idx_cb_status;
DROP INDEX IF EXISTS public.idx_cb_parent;
DROP INDEX IF EXISTS public.idx_cb_agent;
DROP INDEX IF EXISTS public.idx_bml_tgt;
DROP INDEX IF EXISTS public.idx_bml_src;
DROP INDEX IF EXISTS public.idx_ar_user;
DROP INDEX IF EXISTS public.idx_ar_type;
DROP INDEX IF EXISTS public.idx_ar_status;
DROP INDEX IF EXISTS public.idx_ar_role;
DROP INDEX IF EXISTS public.idx_ar_created_by;
DROP INDEX IF EXISTS public.idx_apl_agent;
DROP INDEX IF EXISTS public.idx_ac_user;
DROP INDEX IF EXISTS public.idx_ac_agent;
DROP INDEX IF EXISTS public.idx_ac_active;
DROP INDEX IF EXISTS public.idx_eal_entity;
DROP INDEX IF EXISTS public.idx_eal_time;
DROP INDEX IF EXISTS public.idx_entities_workspace;
DROP INDEX IF EXISTS public.idx_entities_visibility;
DROP INDEX IF EXISTS public.idx_entities_status;
DROP INDEX IF EXISTS public.idx_entities_search;
DROP INDEX IF EXISTS public.idx_entities_owned_by;
DROP INDEX IF EXISTS public.idx_entities_category;
DROP INDEX IF EXISTS public.idx_as_workspace;
DROP INDEX IF EXISTS public.idx_as_predecessor;
DROP INDEX IF EXISTS public.idx_as_owner;
DROP INDEX IF EXISTS public.idx_as_agent;
ALTER TABLE IF EXISTS ONLY public.workspaces DROP CONSTRAINT IF EXISTS workspaces_pkey;
ALTER TABLE IF EXISTS ONLY public.workspace_context DROP CONSTRAINT IF EXISTS workspace_context_pkey;
ALTER TABLE IF EXISTS ONLY public.tags DROP CONSTRAINT IF EXISTS uk_tags_name;
ALTER TABLE IF EXISTS ONLY public.system_users DROP CONSTRAINT IF EXISTS uk_su_username;
ALTER TABLE IF EXISTS ONLY public.spec_plan_links DROP CONSTRAINT IF EXISTS uk_spl_link;
ALTER TABLE IF EXISTS ONLY public.collab_group_members DROP CONSTRAINT IF EXISTS uk_cgm_membership;
ALTER TABLE IF EXISTS ONLY public.task_tool_calls DROP CONSTRAINT IF EXISTS task_tool_calls_pkey;
ALTER TABLE IF EXISTS ONLY public.task_steps DROP CONSTRAINT IF EXISTS task_steps_pkey;
ALTER TABLE IF EXISTS ONLY public.task_plans_paused DROP CONSTRAINT IF EXISTS task_plans_paused_pkey;
ALTER TABLE IF EXISTS ONLY public.task_plans_default DROP CONSTRAINT IF EXISTS task_plans_default_pkey;
ALTER TABLE IF EXISTS ONLY public.task_plans_completed DROP CONSTRAINT IF EXISTS task_plans_completed_pkey;
ALTER TABLE IF EXISTS ONLY public.task_plans_cancelled DROP CONSTRAINT IF EXISTS task_plans_cancelled_pkey;
ALTER TABLE IF EXISTS ONLY public.task_plans_active DROP CONSTRAINT IF EXISTS task_plans_active_pkey;
ALTER TABLE IF EXISTS ONLY public.task_dependencies DROP CONSTRAINT IF EXISTS task_dependencies_pkey;
ALTER TABLE IF EXISTS ONLY public.task_context_snapshots DROP CONSTRAINT IF EXISTS task_context_snapshots_pkey;
ALTER TABLE IF EXISTS ONLY public.tags DROP CONSTRAINT IF EXISTS tags_pkey;
ALTER TABLE IF EXISTS ONLY public.system_users DROP CONSTRAINT IF EXISTS system_users_pkey;
ALTER TABLE IF EXISTS ONLY public.system_config DROP CONSTRAINT IF EXISTS system_config_pkey;
ALTER TABLE IF EXISTS ONLY public.spec_plan_links DROP CONSTRAINT IF EXISTS spec_plan_links_pkey;
ALTER TABLE IF EXISTS ONLY public.skill_meta DROP CONSTRAINT IF EXISTS skill_meta_pkey;
ALTER TABLE IF EXISTS ONLY public.workspace_tasks DROP CONSTRAINT IF EXISTS pk_workspace_tasks;
ALTER TABLE IF EXISTS ONLY public.task_plans DROP CONSTRAINT IF EXISTS pk_task_plans;
ALTER TABLE IF EXISTS ONLY public.spec_meta DROP CONSTRAINT IF EXISTS pk_spec_meta;
ALTER TABLE IF EXISTS ONLY public.knowledge_meta DROP CONSTRAINT IF EXISTS pk_knowledge_meta;
ALTER TABLE IF EXISTS ONLY public.harness_meta DROP CONSTRAINT IF EXISTS pk_harness_meta;
ALTER TABLE IF EXISTS ONLY public.entity_tags DROP CONSTRAINT IF EXISTS pk_entity_tags;
ALTER TABLE IF EXISTS ONLY public.entity_embeddings DROP CONSTRAINT IF EXISTS pk_entity_embeddings;
ALTER TABLE IF EXISTS ONLY public.entity_edges DROP CONSTRAINT IF EXISTS entity_edges_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_task_output DROP CONSTRAINT IF EXISTS entities_task_output_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_spec DROP CONSTRAINT IF EXISTS entities_spec_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_skill DROP CONSTRAINT IF EXISTS entities_skill_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_other DROP CONSTRAINT IF EXISTS entities_other_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_memory DROP CONSTRAINT IF EXISTS entities_memory_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_knowledge DROP CONSTRAINT IF EXISTS entities_knowledge_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_harness_template DROP CONSTRAINT IF EXISTS entities_harness_template_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_experience DROP CONSTRAINT IF EXISTS entities_experience_pkey;
ALTER TABLE IF EXISTS ONLY public.entities_default DROP CONSTRAINT IF EXISTS entities_default_pkey;
ALTER TABLE IF EXISTS ONLY public.entities DROP CONSTRAINT IF EXISTS pk_entities;
ALTER TABLE IF EXISTS ONLY public.context_branches DROP CONSTRAINT IF EXISTS context_branches_pkey;
ALTER TABLE IF EXISTS ONLY public.collab_groups DROP CONSTRAINT IF EXISTS collab_groups_pkey;
ALTER TABLE IF EXISTS ONLY public.collab_group_members DROP CONSTRAINT IF EXISTS collab_group_members_pkey;
ALTER TABLE IF EXISTS ONLY public.branch_merge_log DROP CONSTRAINT IF EXISTS branch_merge_log_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_session_inactive DROP CONSTRAINT IF EXISTS agent_session_inactive_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_session_active DROP CONSTRAINT IF EXISTS agent_session_active_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_session DROP CONSTRAINT IF EXISTS pk_agent_session;
ALTER TABLE IF EXISTS ONLY public.agent_registry DROP CONSTRAINT IF EXISTS agent_registry_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_permission_log DROP CONSTRAINT IF EXISTS agent_permission_log_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_credentials DROP CONSTRAINT IF EXISTS agent_credentials_pkey;
ALTER TABLE IF EXISTS ONLY public.agent_collaboration DROP CONSTRAINT IF EXISTS agent_collaboration_pkey;
DROP TABLE IF EXISTS public.workspace_tasks;
DROP VIEW IF EXISTS public.v_memory_entities;
DROP VIEW IF EXISTS public.v_entity_graph;
DROP VIEW IF EXISTS public.v_branch_comparison;
DROP TABLE IF EXISTS public.workspace_context;
DROP VIEW IF EXISTS public.v_active_sessions;
DROP TABLE IF EXISTS public.workspaces;
DROP TABLE IF EXISTS public.task_tool_calls;
DROP TABLE IF EXISTS public.task_steps;
DROP TABLE IF EXISTS public.task_plans_paused;
DROP TABLE IF EXISTS public.task_plans_default;
DROP TABLE IF EXISTS public.task_plans_completed;
DROP TABLE IF EXISTS public.task_plans_cancelled;
DROP TABLE IF EXISTS public.task_plans_active;
DROP TABLE IF EXISTS public.task_plans;
DROP TABLE IF EXISTS public.task_dependencies;
DROP TABLE IF EXISTS public.task_context_snapshots;
DROP TABLE IF EXISTS public.tags;
DROP TABLE IF EXISTS public.system_users;
DROP TABLE IF EXISTS public.system_config;
DROP TABLE IF EXISTS public.spec_plan_links;
DROP TABLE IF EXISTS public.spec_meta;
DROP TABLE IF EXISTS public.skill_meta;
DROP TABLE IF EXISTS public.knowledge_meta;
DROP TABLE IF EXISTS public.harness_meta;
DROP TABLE IF EXISTS public.entity_tags;
DROP TABLE IF EXISTS public.entity_embeddings;
DROP TABLE IF EXISTS public.entity_edges;
DROP TABLE IF EXISTS public.entity_access_log_max;
DROP TABLE IF EXISTS public.entity_access_log_202606;
DROP TABLE IF EXISTS public.entity_access_log_202605;
DROP TABLE IF EXISTS public.entity_access_log;
DROP TABLE IF EXISTS public.entities_task_output;
DROP TABLE IF EXISTS public.entities_spec;
DROP TABLE IF EXISTS public.entities_skill;
DROP TABLE IF EXISTS public.entities_other;
DROP TABLE IF EXISTS public.entities_memory;
DROP TABLE IF EXISTS public.entities_knowledge;
DROP TABLE IF EXISTS public.entities_harness_template;
DROP TABLE IF EXISTS public.entities_experience;
DROP TABLE IF EXISTS public.entities_default;
DROP TABLE IF EXISTS public.entities;
DROP TABLE IF EXISTS public.context_branches;
DROP TABLE IF EXISTS public.collab_groups;
DROP TABLE IF EXISTS public.collab_group_members;
DROP TABLE IF EXISTS public.branch_merge_log;
DROP TABLE IF EXISTS public.agent_session_inactive;
DROP TABLE IF EXISTS public.agent_session_active;
DROP TABLE IF EXISTS public.agent_session;
DROP TABLE IF EXISTS public.agent_registry;
DROP TABLE IF EXISTS public.agent_permission_log;
DROP TABLE IF EXISTS public.agent_credentials;
DROP TABLE IF EXISTS public.agent_collaboration;
DROP FUNCTION IF EXISTS public.workspace_manager_create(p_workspace_name character varying, p_workspace_type character varying, p_isolation_mode character varying, p_owner_user_id character varying, p_current_agent_id character varying, p_metadata jsonb);
DROP FUNCTION IF EXISTS public.workspace_manager_add_context(p_workspace_id bigint, p_agent_id character varying, p_context_type character varying, p_context_data jsonb, p_session_id bigint, p_parent_context_id bigint, p_branch_id bigint, p_visibility character varying);
DROP FUNCTION IF EXISTS public.update_updated_at_column();
DROP FUNCTION IF EXISTS public.spec_manager_link_plan(p_spec_id bigint, p_plan_id bigint, p_link_type character varying, p_link_strength numeric);
DROP FUNCTION IF EXISTS public.spec_manager_create(p_title character varying, p_content text, p_acceptance_criteria jsonb, p_spec_constraints jsonb, p_spec_scope character varying, p_complexity character varying, p_owned_by_agent character varying, p_workspace_id bigint, p_branch_id bigint);
DROP FUNCTION IF EXISTS public.session_cleanup_expired();
DROP FUNCTION IF EXISTS public.session_cleanup_dormant_agents();
DROP FUNCTION IF EXISTS public.memory_fusion_vector_search(p_query_vector public.vector, p_entity_type character varying, p_limit integer, p_threshold double precision);
DROP FUNCTION IF EXISTS public.memory_fusion_search(p_query text, p_entity_type character varying, p_limit integer);
DROP FUNCTION IF EXISTS public.memory_fusion_retrieve(p_entity_id bigint);
DROP FUNCTION IF EXISTS public.memory_fusion_create(p_entity_type character varying, p_title character varying, p_content text, p_summary character varying, p_category character varying, p_visibility character varying, p_importance numeric, p_owned_by_agent character varying, p_source_agent character varying, p_workspace_id bigint, p_branch_id bigint);
DROP FUNCTION IF EXISTS public.knowledge_api_validate(p_entity_id bigint, p_status character varying);
DROP FUNCTION IF EXISTS public.knowledge_api_schedule_review(p_entity_id bigint, p_interval_days integer);
DROP FUNCTION IF EXISTS public.knowledge_api_create(p_title character varying, p_content text, p_domain character varying, p_topic character varying, p_difficulty character varying, p_source_type character varying, p_confidence numeric, p_owned_by_agent character varying, p_workspace_id bigint);
DROP FUNCTION IF EXISTS public.entities_search_vector_update();
DROP FUNCTION IF EXISTS public.embedding_generate_batch(p_texts text[], p_api_url text, p_model text);
DROP FUNCTION IF EXISTS public.embedding_generate_batch(p_texts text[]);
DROP FUNCTION IF EXISTS public.embedding_generate_and_store(p_entity_id bigint, p_entity_type character varying, p_text text);
DROP FUNCTION IF EXISTS public.embedding_generate(p_text text, p_api_url text, p_model text);
DROP FUNCTION IF EXISTS public.embedding_generate(p_text text);
DROP FUNCTION IF EXISTS public.db_crypto_rotate_key(p_old_key text, p_new_key text);
DROP FUNCTION IF EXISTS public.db_crypto_encrypt(p_plaintext text, p_key text);
DROP FUNCTION IF EXISTS public.db_crypto_decrypt(p_ciphertext text, p_key text);
DROP FUNCTION IF EXISTS public.collab_group_manager_create(p_group_name character varying, p_group_type character varying, p_description text, p_workspace_id bigint, p_coordinator_agent_id character varying, p_sharing_policy character varying);
DROP FUNCTION IF EXISTS public.collab_group_manager_add_member(p_group_id bigint, p_agent_id character varying, p_role character varying);
DROP FUNCTION IF EXISTS public.agent_perm_grant(p_agent_id character varying, p_action character varying, p_target_type character varying, p_target_id character varying, p_details jsonb);
DROP FUNCTION IF EXISTS public.agent_perm_check(p_agent_id character varying, p_action character varying, p_target_type character varying, p_target_id character varying);
DROP SCHEMA IF EXISTS public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA public;


--
-- Name: agent_perm_check(character varying, character varying, character varying, character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.agent_perm_check(p_agent_id character varying, p_action character varying, p_target_type character varying, p_target_id character varying) RETURNS boolean
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_count INT;
BEGIN
    SELECT COUNT(*) INTO v_count FROM AGENT_PERMISSION_LOG
    WHERE agent_id = p_agent_id AND action = 'GRANT'
      AND target_type = p_target_type AND target_id = p_target_id;
    RETURN v_count > 0;
END;
$$;


--
-- Name: agent_perm_grant(character varying, character varying, character varying, character varying, jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.agent_perm_grant(p_agent_id character varying, p_action character varying, p_target_type character varying, p_target_id character varying, p_details jsonb DEFAULT NULL::jsonb) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_log_id BIGINT;
BEGIN
    INSERT INTO AGENT_PERMISSION_LOG (agent_id, action, target_type, target_id, details)
    VALUES (p_agent_id, p_action, p_target_type, p_target_id, p_details)
    RETURNING log_id INTO v_log_id;
    RETURN v_log_id;
END;
$$;


--
-- Name: collab_group_manager_add_member(bigint, character varying, character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.collab_group_manager_add_member(p_group_id bigint, p_agent_id character varying, p_role character varying DEFAULT 'MEMBER'::character varying) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_member_id BIGINT;
BEGIN
    INSERT INTO COLLAB_GROUP_MEMBERS (group_id, agent_id, role)
    VALUES (p_group_id, p_agent_id, p_role)
    RETURNING member_id INTO v_member_id;
    RETURN v_member_id;
END;
$$;


--
-- Name: collab_group_manager_create(character varying, character varying, text, bigint, character varying, character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.collab_group_manager_create(p_group_name character varying, p_group_type character varying DEFAULT 'PROJECT'::character varying, p_description text DEFAULT NULL::text, p_workspace_id bigint DEFAULT NULL::bigint, p_coordinator_agent_id character varying DEFAULT NULL::character varying, p_sharing_policy character varying DEFAULT 'OPEN'::character varying) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_group_id BIGINT;
BEGIN
    INSERT INTO COLLAB_GROUPS (group_name, group_type, description, workspace_id,
        coordinator_agent_id, sharing_policy)
    VALUES (p_group_name, p_group_type, p_description, p_workspace_id,
        p_coordinator_agent_id, p_sharing_policy)
    RETURNING group_id INTO v_group_id;
    RETURN v_group_id;
END;
$$;


--
-- Name: db_crypto_decrypt(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.db_crypto_decrypt(p_ciphertext text, p_key text DEFAULT NULL::text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_key TEXT;
    v_iv BYTEA;
    v_encrypted BYTEA;
BEGIN
    IF p_key IS NULL THEN
        SELECT config_value INTO v_key FROM system_config WHERE config_key = 'credential_encryption_key';
    ELSE
        v_key := p_key;
    END IF;
    v_iv := decode(substring(p_ciphertext, 1, 32), 'hex');
    v_encrypted := decode(substring(p_ciphertext, 33), 'hex');
    RETURN convert_from(decrypt_iv(v_encrypted, v_key::bytea, v_iv, 'aes'), 'UTF8');
END;
$$;


--
-- Name: db_crypto_encrypt(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.db_crypto_encrypt(p_plaintext text, p_key text DEFAULT NULL::text) RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_key TEXT;
    v_iv BYTEA;
BEGIN
    IF p_key IS NULL THEN
        SELECT config_value INTO v_key FROM system_config WHERE config_key = 'credential_encryption_key';
    ELSE
        v_key := p_key;
    END IF;
    v_iv := gen_random_bytes(16);
    RETURN encode(v_iv || encrypt_iv(p_plaintext::bytea, v_key::bytea, v_iv, 'aes'), 'hex');
END;
$$;


--
-- Name: db_crypto_rotate_key(text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.db_crypto_rotate_key(p_old_key text, p_new_key text) RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_count INT := 0;
    v_rec RECORD;
    v_decrypted TEXT;
BEGIN
    FOR v_rec IN SELECT credential_id, credential_value FROM agent_credentials WHERE is_active = TRUE LOOP
        v_decrypted := db_crypto_decrypt(v_rec.credential_value, p_old_key);
        UPDATE agent_credentials SET credential_value = db_crypto_encrypt(v_decrypted, p_new_key)
        WHERE credential_id = v_rec.credential_id;
        v_count := v_count + 1;
    END LOOP;
    UPDATE system_config SET config_value = p_new_key WHERE config_key = 'credential_encryption_key';
    RETURN v_count;
END;
$$;


--
-- Name: embedding_generate(text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.embedding_generate(p_text text) RETURNS public.vector
    LANGUAGE plpython3u
    AS $$
import json
import urllib.request
try:
    embedding_url = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_url'")[0]['config_value']
    embedding_model = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_model'")[0]['config_value']
    data = json.dumps({'input': p_text, 'model': embedding_model}).encode('utf-8')
    req = urllib.request.Request(embedding_url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    embedding = result['data'][0]['embedding']
    return '[' + ','.join(str(x) for x in embedding) + ']'
except Exception as e:
    plpy.warning('embedding_generate failed: ' + str(e))
    return None
$$;


--
-- Name: embedding_generate(text, text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.embedding_generate(p_text text, p_api_url text DEFAULT 'http://10.10.10.1:12345/v1/embeddings'::text, p_model text DEFAULT 'text-embedding-bge-m3'::text) RETURNS public.vector
    LANGUAGE plpython3u
    AS $$
import requests
import json

if not p_text or not p_text.strip():
    return None

payload = {"model": p_model, "input": p_text, "encoding_format": "float"}
try:
    resp = requests.post(p_api_url, json=payload, timeout=30)
    resp.raise_for_status()
    result = resp.json()
    if "data" in result and len(result["data"]) > 0:
        embedding = result["data"][0]["embedding"]
        return embedding
    return None
except Exception as e:
    plpy.warning(f"Embedding generation failed: {e}")
    return None
$$;


--
-- Name: embedding_generate_and_store(bigint, character varying, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.embedding_generate_and_store(p_entity_id bigint, p_entity_type character varying, p_text text) RETURNS void
    LANGUAGE plpython3u
    AS $_$
import json
import urllib.request
try:
    embedding_url = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_url'")[0]['config_value']
    embedding_model = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_model'")[0]['config_value']
    data = json.dumps({'input': p_text, 'model': embedding_model}).encode('utf-8')
    req = urllib.request.Request(embedding_url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    embedding = result['data'][0]['embedding']
    dim = len(embedding)
    vec_str = '[' + ','.join(str(x) for x in embedding) + ']'
    plpy.execute(plpy.prepare(
        "INSERT INTO entity_embeddings (entity_id, entity_type, embedding, embedding_model, embedding_dim) "
        "VALUES ($1, $2, $3::vector, $4, $5) "
        "ON CONFLICT (entity_id, entity_type) DO UPDATE SET embedding = EXCLUDED.embedding, "
        "embedding_model = EXCLUDED.embedding_model, embedded_at = CURRENT_TIMESTAMP",
        ['bigint', 'varchar', 'text', 'varchar', 'int']),
        [p_entity_id, p_entity_type, vec_str, embedding_model, dim])
except Exception as e:
    plpy.warning('embedding_generate_and_store failed: ' + str(e))
$_$;


--
-- Name: embedding_generate_batch(text[]); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.embedding_generate_batch(p_texts text[]) RETURNS text[]
    LANGUAGE plpython3u
    AS $$
import json
import urllib.request
try:
    embedding_url = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_url'")[0]['config_value']
    embedding_model = plpy.execute("SELECT config_value FROM system_config WHERE config_key = 'embedding_model'")[0]['config_value']
    data = json.dumps({'input': list(p_texts), 'model': embedding_model}).encode('utf-8')
    req = urllib.request.Request(embedding_url, data=data, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    results = []
    for item in result['data']:
        embedding = item['embedding']
        results.append('[' + ','.join(str(x) for x in embedding) + ']')
    return results
except Exception as e:
    plpy.warning('embedding_generate_batch failed: ' + str(e))
    return [None] * len(p_texts)
$$;


--
-- Name: embedding_generate_batch(text[], text, text); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.embedding_generate_batch(p_texts text[], p_api_url text DEFAULT 'http://10.10.10.1:12345/v1/embeddings'::text, p_model text DEFAULT 'text-embedding-bge-m3'::text) RETURNS SETOF public.vector
    LANGUAGE plpython3u
    AS $$
import requests
import json

if not p_texts:
    return

payload = {"model": p_model, "input": list(p_texts), "encoding_format": "float"}
try:
    resp = requests.post(p_api_url, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()
    if "data" in result:
        sorted_data = sorted(result["data"], key=lambda x: x["index"])
        for item in sorted_data:
            yield item["embedding"]
except Exception as e:
    plpy.warning(f"Batch embedding generation failed: {e}")
$$;


--
-- Name: entities_search_vector_update(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.entities_search_vector_update() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.search_vector := 
        setweight(to_tsvector('english', COALESCE(NEW.title, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.summary, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.content, '')), 'C');
    RETURN NEW;
END;
$$;


--
-- Name: knowledge_api_create(character varying, text, character varying, character varying, character varying, character varying, numeric, character varying, bigint); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.knowledge_api_create(p_title character varying, p_content text, p_domain character varying DEFAULT NULL::character varying, p_topic character varying DEFAULT NULL::character varying, p_difficulty character varying DEFAULT 'INTERMEDIATE'::character varying, p_source_type character varying DEFAULT NULL::character varying, p_confidence numeric DEFAULT NULL::numeric, p_owned_by_agent character varying DEFAULT NULL::character varying, p_workspace_id bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_entity_id BIGINT;
BEGIN
    INSERT INTO ENTITIES (entity_type, title, content, visibility, importance, owned_by_agent, workspace_id)
    VALUES ('KNOWLEDGE', p_title, p_content, 'SHARED', 7, p_owned_by_agent, p_workspace_id)
    RETURNING entity_id INTO v_entity_id;
    INSERT INTO KNOWLEDGE_META (entity_id, domain, topic, difficulty, source_type, confidence)
    VALUES (v_entity_id, p_domain, p_topic, p_difficulty, p_source_type, p_confidence);
    RETURN v_entity_id;
END;
$$;


--
-- Name: knowledge_api_schedule_review(bigint, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.knowledge_api_schedule_review(p_entity_id bigint, p_interval_days integer DEFAULT 30) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE KNOWLEDGE_META SET next_review = CURRENT_TIMESTAMP + (p_interval_days || ' days')::INTERVAL
    WHERE entity_id = p_entity_id;
END;
$$;


--
-- Name: knowledge_api_validate(bigint, character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.knowledge_api_validate(p_entity_id bigint, p_status character varying DEFAULT 'VALIDATED'::character varying) RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE KNOWLEDGE_META SET validation_status = p_status,
        review_count = review_count + 1,
        last_reviewed = CURRENT_TIMESTAMP
    WHERE entity_id = p_entity_id;
END;
$$;


--
-- Name: memory_fusion_create(character varying, character varying, text, character varying, character varying, character varying, numeric, character varying, character varying, bigint, bigint); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.memory_fusion_create(p_entity_type character varying, p_title character varying, p_content text, p_summary character varying DEFAULT NULL::character varying, p_category character varying DEFAULT NULL::character varying, p_visibility character varying DEFAULT 'SHARED'::character varying, p_importance numeric DEFAULT 5, p_owned_by_agent character varying DEFAULT NULL::character varying, p_source_agent character varying DEFAULT NULL::character varying, p_workspace_id bigint DEFAULT NULL::bigint, p_branch_id bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_entity_id BIGINT;
BEGIN
    INSERT INTO ENTITIES (entity_type, title, content, summary, category, visibility, importance,
        owned_by_agent, source_agent, workspace_id, branch_id)
    VALUES (p_entity_type, p_title, p_content, p_summary, p_category, p_visibility, p_importance,
        p_owned_by_agent, p_source_agent, p_workspace_id, p_branch_id)
    RETURNING entity_id INTO v_entity_id;
    RETURN v_entity_id;
END;
$$;


--
-- Name: memory_fusion_retrieve(bigint); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.memory_fusion_retrieve(p_entity_id bigint) RETURNS TABLE(entity_id bigint, entity_type character varying, title character varying, content text, summary character varying, category character varying, status character varying, importance numeric, owned_by_agent character varying, visibility character varying, workspace_id bigint, retrieval_count integer, created_at timestamp without time zone, updated_at timestamp without time zone)
    LANGUAGE plpgsql
    AS $$
BEGIN
    UPDATE ENTITIES SET retrieval_count = retrieval_count + 1 WHERE entity_id = p_entity_id;
    RETURN QUERY SELECT e.entity_id, e.entity_type, e.title, e.content, e.summary, e.category,
        e.status, e.importance, e.owned_by_agent, e.visibility, e.workspace_id,
        e.retrieval_count, e.created_at, e.updated_at
    FROM ENTITIES e WHERE e.entity_id = p_entity_id;
    RETURN;
END;
$$;


--
-- Name: memory_fusion_search(text, character varying, integer); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.memory_fusion_search(p_query text, p_entity_type character varying DEFAULT NULL::character varying, p_limit integer DEFAULT 20) RETURNS TABLE(entity_id bigint, entity_type character varying, title character varying, summary character varying, rank real)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT e.entity_id, e.entity_type, e.title, e.summary,
        ts_rank(e.search_vector, plainto_tsquery('english', p_query)) AS rank
    FROM ENTITIES e
    WHERE e.search_vector @@ plainto_tsquery('english', p_query)
      AND (p_entity_type IS NULL OR e.entity_type = p_entity_type)
      AND e.status = 'ACTIVE'
    ORDER BY rank DESC
    LIMIT p_limit;
END;
$$;


--
-- Name: memory_fusion_vector_search(public.vector, character varying, integer, double precision); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.memory_fusion_vector_search(p_query_vector public.vector, p_entity_type character varying DEFAULT NULL::character varying, p_limit integer DEFAULT 20, p_threshold double precision DEFAULT 0.7) RETURNS TABLE(entity_id bigint, entity_type character varying, title character varying, similarity double precision)
    LANGUAGE plpgsql
    AS $$
BEGIN
    RETURN QUERY
    SELECT ee.entity_id, ee.entity_type, e.title,
        1 - (ee.embedding <=> p_query_vector) AS similarity
    FROM ENTITY_EMBEDDINGS ee
    JOIN ENTITIES e ON e.entity_id = ee.entity_id AND e.entity_type = ee.entity_type
    WHERE (p_entity_type IS NULL OR ee.entity_type = p_entity_type)
      AND e.status = 'ACTIVE'
      AND 1 - (ee.embedding <=> p_query_vector) >= p_threshold
    ORDER BY ee.embedding <=> p_query_vector
    LIMIT p_limit;
END;
$$;


--
-- Name: session_cleanup_dormant_agents(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.session_cleanup_dormant_agents() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_timeout_min INT;
    v_count INT;
BEGIN
    SELECT config_value::INT INTO v_timeout_min FROM SYSTEM_CONFIG WHERE config_key = 'dormant_timeout_min';
    UPDATE AGENT_REGISTRY SET status = 'DORMANT'
    WHERE status = 'ACTIVE'
      AND last_active_at < CURRENT_TIMESTAMP - (v_timeout_min || ' minutes')::INTERVAL;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$;


--
-- Name: session_cleanup_expired(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.session_cleanup_expired() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_timeout_min INT;
    v_count INT;
BEGIN
    SELECT config_value::INT INTO v_timeout_min FROM SYSTEM_CONFIG WHERE config_key = 'session_timeout_min';
    UPDATE AGENT_SESSION SET is_active = FALSE
    WHERE is_active = TRUE
      AND last_active_at < CURRENT_TIMESTAMP - (v_timeout_min || ' minutes')::INTERVAL;
    GET DIAGNOSTICS v_count = ROW_COUNT;
    RETURN v_count;
END;
$$;


--
-- Name: spec_manager_create(character varying, text, jsonb, jsonb, character varying, character varying, character varying, bigint, bigint); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.spec_manager_create(p_title character varying, p_content text, p_acceptance_criteria jsonb DEFAULT NULL::jsonb, p_spec_constraints jsonb DEFAULT NULL::jsonb, p_spec_scope character varying DEFAULT NULL::character varying, p_complexity character varying DEFAULT 'MEDIUM'::character varying, p_owned_by_agent character varying DEFAULT NULL::character varying, p_workspace_id bigint DEFAULT NULL::bigint, p_branch_id bigint DEFAULT NULL::bigint) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_entity_id BIGINT;
BEGIN
    INSERT INTO ENTITIES (entity_type, title, content, visibility, importance, owned_by_agent, workspace_id)
    VALUES ('SPEC', p_title, p_content, 'SHARED', 8, p_owned_by_agent, p_workspace_id)
    RETURNING entity_id INTO v_entity_id;
    INSERT INTO SPEC_META (entity_id, acceptance_criteria, spec_constraints, spec_scope, complexity, branch_id)
    VALUES (v_entity_id, p_acceptance_criteria, p_spec_constraints, p_spec_scope, p_complexity, p_branch_id);
    RETURN v_entity_id;
END;
$$;


--
-- Name: spec_manager_link_plan(bigint, bigint, character varying, numeric); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.spec_manager_link_plan(p_spec_id bigint, p_plan_id bigint, p_link_type character varying DEFAULT 'DRIVES'::character varying, p_link_strength numeric DEFAULT 1.0) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_link_id BIGINT;
BEGIN
    INSERT INTO SPEC_PLAN_LINKS (spec_id, plan_id, link_type, link_strength)
    VALUES (p_spec_id, p_plan_id, p_link_type, p_link_strength)
    RETURNING link_id INTO v_link_id;
    RETURN v_link_id;
END;
$$;


--
-- Name: update_updated_at_column(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_updated_at_column() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$;


--
-- Name: workspace_manager_add_context(bigint, character varying, character varying, jsonb, bigint, bigint, bigint, character varying); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.workspace_manager_add_context(p_workspace_id bigint, p_agent_id character varying, p_context_type character varying, p_context_data jsonb, p_session_id bigint DEFAULT NULL::bigint, p_parent_context_id bigint DEFAULT NULL::bigint, p_branch_id bigint DEFAULT NULL::bigint, p_visibility character varying DEFAULT 'SHARED'::character varying) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_context_id BIGINT;
BEGIN
    INSERT INTO WORKSPACE_CONTEXT (workspace_id, agent_id, context_type, context_data,
        session_id, parent_context_id, branch_id, visibility)
    VALUES (p_workspace_id, p_agent_id, p_context_type, p_context_data,
        p_session_id, p_parent_context_id, p_branch_id, p_visibility)
    RETURNING context_id INTO v_context_id;
    RETURN v_context_id;
END;
$$;


--
-- Name: workspace_manager_create(character varying, character varying, character varying, character varying, character varying, jsonb); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.workspace_manager_create(p_workspace_name character varying, p_workspace_type character varying DEFAULT 'CONVERSATION'::character varying, p_isolation_mode character varying DEFAULT 'SHARED'::character varying, p_owner_user_id character varying DEFAULT NULL::character varying, p_current_agent_id character varying DEFAULT NULL::character varying, p_metadata jsonb DEFAULT NULL::jsonb) RETURNS bigint
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_workspace_id BIGINT;
BEGIN
    INSERT INTO WORKSPACES (workspace_name, workspace_type, isolation_mode, owner_user_id,
        current_agent_id, metadata)
    VALUES (p_workspace_name, p_workspace_type, p_isolation_mode, p_owner_user_id,
        p_current_agent_id, p_metadata)
    RETURNING workspace_id INTO v_workspace_id;
    RETURN v_workspace_id;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agent_collaboration; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_collaboration (
    collab_id bigint NOT NULL,
    source_agent_id character varying(64) NOT NULL,
    target_agent_id character varying(64) NOT NULL,
    col_type character varying(64) NOT NULL,
    entity_id bigint,
    context jsonb,
    strength numeric(5,4) DEFAULT 1.0000 NOT NULL,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_col_strength CHECK (((strength >= (0)::numeric) AND (strength <= (1)::numeric)))
);


--
-- Name: agent_collaboration_collab_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agent_collaboration ALTER COLUMN collab_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agent_collaboration_collab_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agent_credentials; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_credentials (
    credential_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    user_id character varying(64) NOT NULL,
    credential_type character varying(32) NOT NULL,
    credential_value text NOT NULL,
    scope jsonb NOT NULL,
    expires_at timestamp without time zone,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ac_active CHECK ((is_active = ANY (ARRAY[true, false]))),
    CONSTRAINT ck_ac_type CHECK (((credential_type)::text = ANY ((ARRAY['ACCESS_TOKEN'::character varying, 'SESSION_KEY'::character varying, 'PASSWORD_HASH'::character varying])::text[])))
);


--
-- Name: agent_credentials_credential_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agent_credentials ALTER COLUMN credential_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agent_credentials_credential_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agent_permission_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_permission_log (
    log_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    action character varying(32) NOT NULL,
    target_type character varying(64) NOT NULL,
    target_id character varying(64) NOT NULL,
    details jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_apl_action CHECK (((action)::text = ANY ((ARRAY['GRANT'::character varying, 'REVOKE'::character varying, 'DENY'::character varying])::text[])))
);


--
-- Name: agent_permission_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agent_permission_log ALTER COLUMN log_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agent_permission_log_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agent_registry; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_registry (
    agent_id character varying(64) NOT NULL,
    agent_name character varying(256) NOT NULL,
    agent_type character varying(64),
    capabilities jsonb,
    config jsonb,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_by_agent_id character varying(64),
    agent_role character varying(32) DEFAULT 'WORKER'::character varying NOT NULL,
    current_user_id character varying(64),
    pool_config jsonb,
    last_active_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    description text,
    wm_entity_id bigint,
    last_seen_at timestamp without time zone,
    CONSTRAINT ck_ar_role CHECK (((agent_role)::text = ANY ((ARRAY['WORKER'::character varying, 'COORDINATOR'::character varying, 'SYSTEM'::character varying])::text[]))),
    CONSTRAINT ck_ar_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying, 'SUSPENDED'::character varying, 'DECOMMISSIONED'::character varying, 'DORMANT'::character varying, 'POOL'::character varying])::text[])))
);


--
-- Name: agent_session; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_session (
    session_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    owner_user_id character varying(64),
    workspace_id bigint,
    predecessor_session_id bigint,
    branch_id bigint,
    is_active boolean DEFAULT true NOT NULL,
    context jsonb,
    last_active_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_as_is_active CHECK ((is_active = ANY (ARRAY[true, false])))
)
PARTITION BY LIST (is_active);


--
-- Name: agent_session_active; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_session_active (
    session_id bigint CONSTRAINT agent_session_session_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT agent_session_agent_id_not_null NOT NULL,
    owner_user_id character varying(64),
    workspace_id bigint,
    predecessor_session_id bigint,
    branch_id bigint,
    is_active boolean DEFAULT true CONSTRAINT agent_session_is_active_not_null NOT NULL,
    context jsonb,
    last_active_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT agent_session_created_at_not_null NOT NULL,
    CONSTRAINT ck_as_is_active CHECK ((is_active = ANY (ARRAY[true, false])))
);


--
-- Name: agent_session_inactive; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agent_session_inactive (
    session_id bigint CONSTRAINT agent_session_session_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT agent_session_agent_id_not_null NOT NULL,
    owner_user_id character varying(64),
    workspace_id bigint,
    predecessor_session_id bigint,
    branch_id bigint,
    is_active boolean DEFAULT true CONSTRAINT agent_session_is_active_not_null NOT NULL,
    context jsonb,
    last_active_at timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT agent_session_created_at_not_null NOT NULL,
    CONSTRAINT ck_as_is_active CHECK ((is_active = ANY (ARRAY[true, false])))
);


--
-- Name: agent_session_session_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.agent_session ALTER COLUMN session_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.agent_session_session_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: branch_merge_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.branch_merge_log (
    log_id bigint NOT NULL,
    source_branch_id bigint NOT NULL,
    target_branch_id bigint NOT NULL,
    merge_status character varying(32) DEFAULT 'PENDING'::character varying NOT NULL,
    conflicts_json jsonb,
    merged_at timestamp without time zone,
    merged_by_agent character varying(64),
    CONSTRAINT ck_bml_status CHECK (((merge_status)::text = ANY ((ARRAY['PENDING'::character varying, 'SUCCESS'::character varying, 'PARTIAL'::character varying, 'CONFLICT'::character varying, 'ABORTED'::character varying])::text[])))
);


--
-- Name: branch_merge_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.branch_merge_log ALTER COLUMN log_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.branch_merge_log_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: collab_group_members; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collab_group_members (
    member_id bigint NOT NULL,
    group_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    role character varying(32) DEFAULT 'MEMBER'::character varying NOT NULL,
    personal_workspace_id bigint,
    branch_id bigint,
    joined_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status character varying(16) DEFAULT 'ACTIVE'::character varying NOT NULL,
    CONSTRAINT ck_cgm_role CHECK (((role)::text = ANY ((ARRAY['LEAD'::character varying, 'MEMBER'::character varying, 'OBSERVER'::character varying, 'CONTRIBUTOR'::character varying])::text[]))),
    CONSTRAINT ck_cgm_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'LEFT'::character varying, 'REMOVED'::character varying])::text[])))
);


--
-- Name: collab_group_members_member_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.collab_group_members ALTER COLUMN member_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.collab_group_members_member_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: collab_groups; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.collab_groups (
    group_id bigint NOT NULL,
    group_name character varying(256) NOT NULL,
    group_type character varying(32) DEFAULT 'PROJECT'::character varying NOT NULL,
    description text,
    workspace_id bigint,
    coordinator_agent_id character varying(64),
    sharing_policy character varying(32) DEFAULT 'OPEN'::character varying NOT NULL,
    branch_id bigint,
    spec_id bigint,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_cg_policy CHECK (((sharing_policy)::text = ANY ((ARRAY['OPEN'::character varying, 'MODERATED'::character varying, 'RESTRICTED'::character varying])::text[]))),
    CONSTRAINT ck_cg_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'PAUSED'::character varying, 'ARCHIVED'::character varying])::text[]))),
    CONSTRAINT ck_cg_type CHECK (((group_type)::text = ANY ((ARRAY['PROJECT'::character varying, 'TEAM'::character varying, 'AD_HOC'::character varying, 'PIPELINE'::character varying])::text[])))
);


--
-- Name: collab_groups_group_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.collab_groups ALTER COLUMN group_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.collab_groups_group_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: context_branches; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.context_branches (
    branch_id bigint NOT NULL,
    workspace_id bigint NOT NULL,
    parent_branch_id bigint,
    branch_name character varying(256) NOT NULL,
    branch_type character varying(32) DEFAULT 'FORK'::character varying NOT NULL,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    source_context_id bigint,
    agent_id character varying(64),
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    merged_at timestamp without time zone,
    abandoned_at timestamp without time zone,
    description text,
    is_lesson boolean DEFAULT false NOT NULL,
    lesson_tags jsonb,
    CONSTRAINT ck_cb_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'MERGED'::character varying, 'ABANDONED'::character varying, 'PAUSED'::character varying])::text[]))),
    CONSTRAINT ck_cb_type CHECK (((branch_type)::text = ANY ((ARRAY['EXPLORATION'::character varying, 'ROLLBACK'::character varying, 'HANDOFF'::character varying, 'PARALLEL'::character varying, 'FORK'::character varying])::text[])))
);


--
-- Name: context_branches_branch_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.context_branches ALTER COLUMN branch_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.context_branches_branch_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entities; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities (
    entity_id bigint NOT NULL,
    entity_type character varying(32) NOT NULL,
    title character varying(512) NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    importance numeric(3,1) DEFAULT 5 NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
)
PARTITION BY LIST (entity_type);


--
-- Name: entities_default; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_default (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_entity_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.entities ALTER COLUMN entity_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entities_entity_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entities_experience; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_experience (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_harness_template; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_harness_template (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_knowledge; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_knowledge (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_memory; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_memory (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_other; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_other (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_skill; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_skill (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_spec; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_spec (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entities_task_output; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entities_task_output (
    entity_id bigint CONSTRAINT entities_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entities_entity_type_not_null NOT NULL,
    title character varying(512) CONSTRAINT entities_title_not_null NOT NULL,
    content text,
    summary character varying(2000),
    category character varying(64),
    status character varying(32) DEFAULT 'ACTIVE'::character varying CONSTRAINT entities_status_not_null NOT NULL,
    importance numeric(3,1) DEFAULT 5 CONSTRAINT entities_importance_not_null NOT NULL,
    owned_by_agent character varying(64),
    source_agent character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying CONSTRAINT entities_visibility_not_null NOT NULL,
    workspace_id bigint,
    branch_id bigint,
    retrieval_count integer DEFAULT 0 CONSTRAINT entities_retrieval_count_not_null NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entities_updated_at_not_null NOT NULL,
    expires_at timestamp without time zone,
    search_vector tsvector,
    CONSTRAINT ck_entities_importance CHECK (((importance >= (1)::numeric) AND (importance <= (10)::numeric))),
    CONSTRAINT ck_entities_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'ARCHIVED'::character varying, 'DELETED'::character varying, 'DRAFT'::character varying])::text[]))),
    CONSTRAINT ck_entities_type CHECK (((entity_type)::text = ANY ((ARRAY['MEMORY'::character varying, 'KNOWLEDGE'::character varying, 'TASK_OUTPUT'::character varying, 'EXPERIENCE'::character varying, 'HARNESS_TEMPLATE'::character varying, 'SPEC'::character varying, 'SKILL'::character varying, 'OTHER'::character varying])::text[]))),
    CONSTRAINT ck_entities_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: entity_access_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_access_log (
    log_id bigint NOT NULL,
    entity_id bigint NOT NULL,
    entity_type character varying(32) NOT NULL,
    agent_id character varying(64) NOT NULL,
    access_type character varying(32) NOT NULL,
    session_id bigint,
    context jsonb,
    access_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_eal_access_type CHECK (((access_type)::text = ANY ((ARRAY['READ'::character varying, 'WRITE'::character varying, 'DELETE'::character varying, 'SEARCH'::character varying, 'EMBED'::character varying])::text[])))
)
PARTITION BY RANGE (access_time);


--
-- Name: entity_access_log_202605; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_access_log_202605 (
    log_id bigint CONSTRAINT entity_access_log_log_id_not_null NOT NULL,
    entity_id bigint CONSTRAINT entity_access_log_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entity_access_log_entity_type_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT entity_access_log_agent_id_not_null NOT NULL,
    access_type character varying(32) CONSTRAINT entity_access_log_access_type_not_null NOT NULL,
    session_id bigint,
    context jsonb,
    access_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entity_access_log_access_time_not_null NOT NULL,
    CONSTRAINT ck_eal_access_type CHECK (((access_type)::text = ANY ((ARRAY['READ'::character varying, 'WRITE'::character varying, 'DELETE'::character varying, 'SEARCH'::character varying, 'EMBED'::character varying])::text[])))
);


--
-- Name: entity_access_log_202606; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_access_log_202606 (
    log_id bigint CONSTRAINT entity_access_log_log_id_not_null NOT NULL,
    entity_id bigint CONSTRAINT entity_access_log_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entity_access_log_entity_type_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT entity_access_log_agent_id_not_null NOT NULL,
    access_type character varying(32) CONSTRAINT entity_access_log_access_type_not_null NOT NULL,
    session_id bigint,
    context jsonb,
    access_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entity_access_log_access_time_not_null NOT NULL,
    CONSTRAINT ck_eal_access_type CHECK (((access_type)::text = ANY ((ARRAY['READ'::character varying, 'WRITE'::character varying, 'DELETE'::character varying, 'SEARCH'::character varying, 'EMBED'::character varying])::text[])))
);


--
-- Name: entity_access_log_log_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.entity_access_log ALTER COLUMN log_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entity_access_log_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entity_access_log_max; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_access_log_max (
    log_id bigint CONSTRAINT entity_access_log_log_id_not_null NOT NULL,
    entity_id bigint CONSTRAINT entity_access_log_entity_id_not_null NOT NULL,
    entity_type character varying(32) CONSTRAINT entity_access_log_entity_type_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT entity_access_log_agent_id_not_null NOT NULL,
    access_type character varying(32) CONSTRAINT entity_access_log_access_type_not_null NOT NULL,
    session_id bigint,
    context jsonb,
    access_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT entity_access_log_access_time_not_null NOT NULL,
    CONSTRAINT ck_eal_access_type CHECK (((access_type)::text = ANY ((ARRAY['READ'::character varying, 'WRITE'::character varying, 'DELETE'::character varying, 'SEARCH'::character varying, 'EMBED'::character varying])::text[])))
);


--
-- Name: entity_edges; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_edges (
    edge_id bigint NOT NULL,
    source_id bigint NOT NULL,
    source_type character varying(32) NOT NULL,
    target_id bigint NOT NULL,
    target_type character varying(32),
    edge_type character varying(64) NOT NULL,
    strength numeric(5,4) DEFAULT 1.0000 NOT NULL,
    confidence numeric(5,4) DEFAULT 1.0000 NOT NULL,
    metadata jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_edge_confidence CHECK (((confidence >= (0)::numeric) AND (confidence <= (1)::numeric))),
    CONSTRAINT ck_edge_strength CHECK (((strength >= (0)::numeric) AND (strength <= (1)::numeric)))
);


--
-- Name: entity_edges_edge_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.entity_edges ALTER COLUMN edge_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.entity_edges_edge_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: entity_embeddings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_embeddings (
    entity_id bigint NOT NULL,
    entity_type character varying(32) NOT NULL,
    embedding public.vector(1024) NOT NULL,
    embedding_model character varying(128),
    embedding_dim integer DEFAULT 1024 NOT NULL,
    embedded_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: entity_tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.entity_tags (
    entity_id bigint NOT NULL,
    entity_type character varying(32) NOT NULL,
    tag_id bigint NOT NULL
);


--
-- Name: harness_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.harness_meta (
    entity_id bigint NOT NULL,
    entity_type character varying(32) DEFAULT 'HARNESS_TEMPLATE'::character varying NOT NULL,
    template_version character varying(32) NOT NULL,
    input_schema jsonb,
    output_schema jsonb,
    execution_mode character varying(32) DEFAULT 'SEQUENTIAL'::character varying NOT NULL,
    CONSTRAINT ck_hm_entity_type CHECK (((entity_type)::text = 'HARNESS_TEMPLATE'::text)),
    CONSTRAINT ck_hm_exec_mode CHECK (((execution_mode)::text = ANY ((ARRAY['SEQUENTIAL'::character varying, 'PARALLEL'::character varying, 'CONDITIONAL'::character varying])::text[])))
);


--
-- Name: knowledge_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.knowledge_meta (
    entity_id bigint NOT NULL,
    entity_type character varying(32) DEFAULT 'KNOWLEDGE'::character varying NOT NULL,
    domain character varying(128),
    topic character varying(256),
    difficulty character varying(16) DEFAULT 'INTERMEDIATE'::character varying NOT NULL,
    review_count integer DEFAULT 0 NOT NULL,
    last_reviewed timestamp without time zone,
    next_review timestamp without time zone,
    CONSTRAINT ck_km_difficulty CHECK (((difficulty)::text = ANY ((ARRAY['BEGINNER'::character varying, 'INTERMEDIATE'::character varying, 'ADVANCED'::character varying, 'EXPERT'::character varying])::text[]))),
    CONSTRAINT ck_km_entity_type CHECK (((entity_type)::text = 'KNOWLEDGE'::text))
);


--
-- Name: skill_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.skill_meta (
    skill_id bigint NOT NULL,
    skill_name character varying(256) NOT NULL,
    skill_version character varying(32),
    description text,
    skill_type character varying(32) DEFAULT 'TOOL'::character varying NOT NULL,
    category character varying(64),
    visibility character varying(16) DEFAULT 'SHARED'::character varying NOT NULL,
    owned_by_agent character varying(64),
    input_schema jsonb,
    output_schema jsonb,
    dependencies jsonb,
    resource_path character varying(2048),
    download_count integer DEFAULT 0 NOT NULL,
    rating numeric(3,2),
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone,
    CONSTRAINT ck_skm_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'DEPRECATED'::character varying, 'DISABLED'::character varying])::text[]))),
    CONSTRAINT ck_skm_type CHECK (((skill_type)::text = ANY ((ARRAY['TOOL'::character varying, 'TEMPLATE'::character varying, 'WORKFLOW'::character varying, 'CUSTOM'::character varying])::text[]))),
    CONSTRAINT ck_skm_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: skill_meta_skill_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.skill_meta ALTER COLUMN skill_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.skill_meta_skill_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: spec_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spec_meta (
    entity_id bigint NOT NULL,
    entity_type character varying(32) DEFAULT 'SPEC'::character varying NOT NULL,
    spec_version integer DEFAULT 1 NOT NULL,
    spec_status character varying(32) DEFAULT 'DRAFT'::character varying NOT NULL,
    acceptance_criteria jsonb,
    spec_constraints jsonb,
    spec_scope character varying(64),
    complexity character varying(16) DEFAULT 'MEDIUM'::character varying NOT NULL,
    branch_id bigint,
    parent_spec_id bigint,
    CONSTRAINT ck_sm_complexity CHECK (((complexity)::text = ANY ((ARRAY['LOW'::character varying, 'MEDIUM'::character varying, 'HIGH'::character varying, 'CRITICAL'::character varying])::text[]))),
    CONSTRAINT ck_sm_entity_type CHECK (((entity_type)::text = 'SPEC'::text)),
    CONSTRAINT ck_sm_spec_status CHECK (((spec_status)::text = ANY ((ARRAY['DRAFT'::character varying, 'REVIEWED'::character varying, 'APPROVED'::character varying, 'IMPLEMENTED'::character varying, 'DEPRECATED'::character varying])::text[])))
);


--
-- Name: spec_plan_links; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.spec_plan_links (
    link_id bigint NOT NULL,
    spec_id bigint NOT NULL,
    plan_id bigint NOT NULL,
    link_type character varying(32) NOT NULL,
    link_strength numeric(5,4) DEFAULT 1.0000 NOT NULL,
    CONSTRAINT ck_spl_strength CHECK (((link_strength >= (0)::numeric) AND (link_strength <= (1)::numeric))),
    CONSTRAINT ck_spl_type CHECK (((link_type)::text = ANY ((ARRAY['DRIVES'::character varying, 'VALIDATES'::character varying, 'CONSTRAINS'::character varying, 'EXTENDS'::character varying])::text[])))
);


--
-- Name: spec_plan_links_link_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.spec_plan_links ALTER COLUMN link_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.spec_plan_links_link_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: system_config; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_config (
    config_key character varying(128) NOT NULL,
    config_value text NOT NULL,
    description text,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: system_users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.system_users (
    user_id bigint NOT NULL,
    username character varying(128) NOT NULL,
    password_hash text,
    salt character varying(128),
    role character varying(64) DEFAULT 'USER'::character varying NOT NULL,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    auth_source character varying(16) DEFAULT 'LOCAL'::character varying NOT NULL,
    ldap_dn character varying(512),
    last_ldap_sync timestamp without time zone,
    last_login timestamp without time zone,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_su_auth_source CHECK (((auth_source)::text = ANY ((ARRAY['LOCAL'::character varying, 'LDAP'::character varying])::text[]))),
    CONSTRAINT ck_su_role CHECK (((role)::text = ANY ((ARRAY['ADMIN'::character varying, 'USER'::character varying, 'SERVICE'::character varying])::text[]))),
    CONSTRAINT ck_su_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'INACTIVE'::character varying, 'LOCKED'::character varying])::text[])))
);


--
-- Name: system_users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.system_users ALTER COLUMN user_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.system_users_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: tags; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tags (
    tag_id bigint NOT NULL,
    tag_name character varying(128) NOT NULL,
    tag_group character varying(64),
    usage_count integer DEFAULT 0 NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: tags_tag_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.tags ALTER COLUMN tag_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.tags_tag_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: task_context_snapshots; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_context_snapshots (
    snapshot_id bigint NOT NULL,
    plan_id bigint NOT NULL,
    snapshot_type character varying(64) DEFAULT 'AUTO'::character varying NOT NULL,
    context_data jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: task_context_snapshots_snapshot_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.task_context_snapshots ALTER COLUMN snapshot_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_context_snapshots_snapshot_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: task_dependencies; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_dependencies (
    dep_id bigint NOT NULL,
    source_plan_id bigint NOT NULL,
    target_plan_id bigint NOT NULL,
    dep_type character varying(64) DEFAULT 'HARD'::character varying NOT NULL,
    CONSTRAINT ck_dep_type CHECK (((dep_type)::text = ANY ((ARRAY['HARD'::character varying, 'SOFT'::character varying, 'TRIGGERS'::character varying, 'RELATES_TO'::character varying])::text[])))
);


--
-- Name: task_dependencies_dep_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.task_dependencies ALTER COLUMN dep_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_dependencies_dep_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: task_plans; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans (
    plan_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    goal text NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying NOT NULL,
    priority integer DEFAULT 5 NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
)
PARTITION BY LIST (status);


--
-- Name: task_plans_active; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans_active (
    plan_id bigint CONSTRAINT task_plans_plan_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT task_plans_agent_id_not_null NOT NULL,
    goal text CONSTRAINT task_plans_goal_not_null NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying CONSTRAINT task_plans_status_not_null NOT NULL,
    priority integer DEFAULT 5 CONSTRAINT task_plans_priority_not_null NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_updated_at_not_null NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: task_plans_cancelled; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans_cancelled (
    plan_id bigint CONSTRAINT task_plans_plan_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT task_plans_agent_id_not_null NOT NULL,
    goal text CONSTRAINT task_plans_goal_not_null NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying CONSTRAINT task_plans_status_not_null NOT NULL,
    priority integer DEFAULT 5 CONSTRAINT task_plans_priority_not_null NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_updated_at_not_null NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: task_plans_completed; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans_completed (
    plan_id bigint CONSTRAINT task_plans_plan_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT task_plans_agent_id_not_null NOT NULL,
    goal text CONSTRAINT task_plans_goal_not_null NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying CONSTRAINT task_plans_status_not_null NOT NULL,
    priority integer DEFAULT 5 CONSTRAINT task_plans_priority_not_null NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_updated_at_not_null NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: task_plans_default; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans_default (
    plan_id bigint CONSTRAINT task_plans_plan_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT task_plans_agent_id_not_null NOT NULL,
    goal text CONSTRAINT task_plans_goal_not_null NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying CONSTRAINT task_plans_status_not_null NOT NULL,
    priority integer DEFAULT 5 CONSTRAINT task_plans_priority_not_null NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_updated_at_not_null NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: task_plans_paused; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_plans_paused (
    plan_id bigint CONSTRAINT task_plans_plan_id_not_null NOT NULL,
    agent_id character varying(64) CONSTRAINT task_plans_agent_id_not_null NOT NULL,
    goal text CONSTRAINT task_plans_goal_not_null NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying CONSTRAINT task_plans_status_not_null NOT NULL,
    priority integer DEFAULT 5 CONSTRAINT task_plans_priority_not_null NOT NULL,
    strategy character varying(64),
    result_summary text,
    branch_id bigint,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_created_at_not_null NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP CONSTRAINT task_plans_updated_at_not_null NOT NULL,
    CONSTRAINT ck_tp_priority CHECK (((priority >= 1) AND (priority <= 10))),
    CONSTRAINT ck_tp_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'CANCELLED'::character varying])::text[])))
);


--
-- Name: task_plans_plan_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.task_plans ALTER COLUMN plan_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_plans_plan_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: task_steps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_steps (
    step_id bigint NOT NULL,
    plan_id bigint NOT NULL,
    plan_status character varying(30) NOT NULL,
    step_order integer NOT NULL,
    description text NOT NULL,
    tool_name character varying(128),
    tool_input jsonb,
    tool_output jsonb,
    loop_id bigint,
    step_completion_type character varying(20) DEFAULT 'MANUAL' NOT NULL,
    status character varying(30) DEFAULT 'PENDING'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ts_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'BLOCKED'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'SKIPPED'::character varying, 'WAITING_LOOP'::character varying])::text[]))),
    CONSTRAINT ck_ts_completion CHECK (((step_completion_type)::text = ANY ((ARRAY['MANUAL'::character varying, 'LOOP'::character varying, 'SPEC'::character varying])::text[])))
);


--
-- Name: task_steps_step_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.task_steps ALTER COLUMN step_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_steps_step_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: task_tool_calls; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.task_tool_calls (
    call_id bigint NOT NULL,
    plan_id bigint NOT NULL,
    step_id bigint,
    tool_name character varying(128) NOT NULL,
    tool_input jsonb,
    tool_output jsonb,
    status character varying(30),
    duration_ms integer,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ttc_status CHECK (((status)::text = ANY ((ARRAY['PENDING'::character varying, 'RUNNING'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'TIMEOUT'::character varying])::text[])))
);


--
-- Name: task_tool_calls_call_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.task_tool_calls ALTER COLUMN call_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.task_tool_calls_call_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: workspaces; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspaces (
    workspace_id bigint NOT NULL,
    workspace_name character varying(256) NOT NULL,
    workspace_type character varying(32) DEFAULT 'CONVERSATION'::character varying NOT NULL,
    workspace_alias character varying(256),
    isolation_mode character varying(16) DEFAULT 'SHARED'::character varying NOT NULL,
    owner_user_id character varying(64),
    current_agent_id character varying(64),
    current_session_id bigint,
    branch_id bigint,
    summary text,
    metadata jsonb,
    status character varying(32) DEFAULT 'ACTIVE'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_ws_isolation CHECK (((isolation_mode)::text = ANY ((ARRAY['SHARED'::character varying, 'ISOLATED'::character varying])::text[]))),
    CONSTRAINT ck_ws_status CHECK (((status)::text = ANY ((ARRAY['ACTIVE'::character varying, 'PAUSED'::character varying, 'COMPLETED'::character varying, 'ABANDONED'::character varying])::text[]))),
    CONSTRAINT ck_ws_type CHECK (((workspace_type)::text = ANY ((ARRAY['CONVERSATION'::character varying, 'PROJECT'::character varying, 'TASK_CHAIN'::character varying, 'AUTONOMOUS'::character varying, 'COLLAB_GROUP'::character varying, 'PERSONAL_IN_GROUP'::character varying])::text[])))
);


--
-- Name: v_active_sessions; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_active_sessions AS
 SELECT s.session_id,
    s.agent_id,
    s.owner_user_id,
    s.workspace_id,
    s.predecessor_session_id,
    s.branch_id,
    s.context,
    s.last_active_at,
    s.created_at,
    ar.agent_name,
    ar.agent_type,
    ar.agent_role,
    w.workspace_name,
    w.workspace_type
   FROM ((public.agent_session s
     JOIN public.agent_registry ar ON (((ar.agent_id)::text = (s.agent_id)::text)))
     LEFT JOIN public.workspaces w ON ((w.workspace_id = s.workspace_id)))
  WHERE (s.is_active = true);


--
-- Name: workspace_context; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspace_context (
    context_id bigint NOT NULL,
    workspace_id bigint NOT NULL,
    agent_id character varying(64) NOT NULL,
    session_id bigint,
    context_type character varying(32) NOT NULL,
    context_data jsonb NOT NULL,
    parent_context_id bigint,
    branch_id bigint,
    visibility character varying(20) DEFAULT 'SHARED'::character varying NOT NULL,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_wc_type CHECK (((context_type)::text = ANY ((ARRAY['CHECKPOINT'::character varying, 'HANDOFF'::character varying, 'SUMMARY'::character varying, 'ERROR_STATE'::character varying, 'AUTO_SAVE'::character varying, 'CHAT_MESSAGE'::character varying, 'BRANCH_POINT'::character varying])::text[]))),
    CONSTRAINT ck_ws_ctx_visibility CHECK (((visibility)::text = ANY ((ARRAY['PRIVATE'::character varying, 'SHARED'::character varying, 'PUBLIC'::character varying])::text[])))
);


--
-- Name: v_branch_comparison; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_branch_comparison AS
 SELECT b1.branch_id AS branch_a,
    b2.branch_id AS branch_b,
    b1.source_context_id AS common_ancestor,
    b1.workspace_id,
    ( SELECT count(*) AS count
           FROM public.workspace_context wc
          WHERE (wc.branch_id = b1.branch_id)) AS ctx_count_a,
    ( SELECT count(*) AS count
           FROM public.workspace_context wc
          WHERE (wc.branch_id = b2.branch_id)) AS ctx_count_b,
    b1.agent_id AS agent_a,
    b2.agent_id AS agent_b,
    b1.branch_type AS type_a,
    b2.branch_type AS type_b,
    b1.status AS status_a,
    b2.status AS status_b
   FROM (public.context_branches b1
     JOIN public.context_branches b2 ON (((b1.workspace_id = b2.workspace_id) AND (b1.source_context_id = b2.source_context_id) AND (b1.branch_id < b2.branch_id))));


--
-- Name: v_entity_graph; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_entity_graph AS
 SELECT eg.edge_id,
    eg.source_id,
    eg.source_type,
    eg.target_id,
    eg.target_type,
    eg.edge_type,
    eg.strength,
    eg.confidence,
    eg.metadata,
    eg.created_at,
    se.title AS source_title,
    se.category AS source_category,
    te.title AS target_title,
    te.category AS target_category
   FROM ((public.entity_edges eg
     JOIN public.entities se ON (((se.entity_id = eg.source_id) AND ((se.entity_type)::text = (eg.source_type)::text))))
     JOIN public.entities te ON ((te.entity_id = eg.target_id)));


--
-- Name: v_memory_entities; Type: VIEW; Schema: public; Owner: -
--

CREATE VIEW public.v_memory_entities AS
 SELECT entity_id,
    entity_type,
    title,
    content,
    summary,
    category,
    status,
    importance,
    owned_by_agent,
    source_agent,
    visibility,
    workspace_id,
    branch_id,
    retrieval_count,
    created_at,
    updated_at,
    expires_at
   FROM public.entities e
  WHERE ((entity_type)::text = 'MEMORY'::text);


--
-- Name: workspace_context_context_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.workspace_context ALTER COLUMN context_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.workspace_context_context_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: workspace_tasks; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.workspace_tasks (
    workspace_id bigint NOT NULL,
    plan_id bigint NOT NULL
);


--
-- Name: workspaces_workspace_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.workspaces ALTER COLUMN workspace_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.workspaces_workspace_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: agent_session_active; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_session ATTACH PARTITION public.agent_session_active FOR VALUES IN (true);


--
-- Name: agent_session_inactive; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_session ATTACH PARTITION public.agent_session_inactive FOR VALUES IN (false);


--
-- Name: entities_default; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_default DEFAULT;


--
-- Name: entities_experience; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_experience FOR VALUES IN ('EXPERIENCE');


--
-- Name: entities_harness_template; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_harness_template FOR VALUES IN ('HARNESS_TEMPLATE');


--
-- Name: entities_knowledge; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_knowledge FOR VALUES IN ('KNOWLEDGE');


--
-- Name: entities_memory; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_memory FOR VALUES IN ('MEMORY');


--
-- Name: entities_other; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_other FOR VALUES IN ('OTHER');


--
-- Name: entities_skill; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_skill FOR VALUES IN ('SKILL');


--
-- Name: entities_spec; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_spec FOR VALUES IN ('SPEC');


--
-- Name: entities_task_output; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities ATTACH PARTITION public.entities_task_output FOR VALUES IN ('TASK_OUTPUT');


--
-- Name: entity_access_log_202605; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_access_log ATTACH PARTITION public.entity_access_log_202605 FOR VALUES FROM (MINVALUE) TO ('2026-06-01 00:00:00');


--
-- Name: entity_access_log_202606; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_access_log ATTACH PARTITION public.entity_access_log_202606 FOR VALUES FROM ('2026-06-01 00:00:00') TO ('2026-07-01 00:00:00');


--
-- Name: entity_access_log_max; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_access_log ATTACH PARTITION public.entity_access_log_max FOR VALUES FROM ('2026-07-01 00:00:00') TO (MAXVALUE);


--
-- Name: task_plans_active; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans ATTACH PARTITION public.task_plans_active FOR VALUES IN ('ACTIVE');


--
-- Name: task_plans_cancelled; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans ATTACH PARTITION public.task_plans_cancelled FOR VALUES IN ('CANCELLED');


--
-- Name: task_plans_completed; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans ATTACH PARTITION public.task_plans_completed FOR VALUES IN ('COMPLETED');


--
-- Name: task_plans_default; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans ATTACH PARTITION public.task_plans_default DEFAULT;


--
-- Name: task_plans_paused; Type: TABLE ATTACH; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans ATTACH PARTITION public.task_plans_paused FOR VALUES IN ('PAUSED');


--
-- Data for Name: agent_collaboration; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_collaboration (collab_id, source_agent_id, target_agent_id, col_type, entity_id, context, strength, status, created_at) FROM stdin;
\.


--
-- Data for Name: agent_credentials; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_credentials (credential_id, agent_id, user_id, credential_type, credential_value, scope, expires_at, is_active, created_at) FROM stdin;
\.


--
-- Data for Name: agent_permission_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_permission_log (log_id, agent_id, action, target_type, target_id, details, created_at) FROM stdin;
\.


--
-- Data for Name: agent_registry; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_registry (agent_id, agent_name, agent_type, capabilities, config, status, created_by_agent_id, agent_role, current_user_id, pool_config, last_active_at, created_at, updated_at, description, wm_entity_id, last_seen_at) FROM stdin;
pg-collab-lead-1781622078	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:20.142276	2026-06-16 11:01:20.142276	\N	\N	\N
pg-collab-member-1781622078	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:20.145579	2026-06-16 11:01:20.145579	\N	\N	\N
pg-collab-observer-1781622078	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:20.148858	2026-06-16 11:01:20.148858	\N	\N	\N
pg-collab-lead-1781624408	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:40:09.942451	2026-06-16 11:40:09.942451	\N	\N	\N
pg-collab-member-1781624408	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:40:09.945604	2026-06-16 11:40:09.945604	\N	\N	\N
pg-ws-agent-1781622078	PG WS Test Agent 1	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:21.346244	2026-06-16 11:01:21.346244	\N	\N	\N
pg-collab-observer-1781624408	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:40:09.949864	2026-06-16 11:40:09.949864	\N	\N	\N
pg-collab-lead-1781623468	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:24:29.944813	2026-06-16 11:24:29.944813	\N	\N	\N
pg-collab-member-1781623468	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:24:29.947737	2026-06-16 11:24:29.947737	\N	\N	\N
pg-collab-observer-1781623468	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:24:29.950789	2026-06-16 11:24:29.950789	\N	\N	\N
pg-ws-agent-1781624408	PG WS Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:40:11.232689	2026-06-16 11:40:11.255528	\N	\N	2026-06-16 11:40:11.255528
pg-ws-agent2-1781624408	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:40:11.258333	2026-06-16 11:40:11.258333	\N	\N	\N
recovery-test-agent	Recovery Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 09:58:30.070461	2026-06-16 11:46:42.771254	\N	\N	2026-06-16 10:46:42.748835
rc-return-test-agent	RC Return Test	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 09:58:57.202669	2026-06-16 11:46:42.802318	\N	\N	2026-06-16 11:46:42.802318
pg-collab-lead-1781624636	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:57.91324	2026-06-16 11:43:57.91324	\N	\N	\N
pg-collab-member-1781624636	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:57.916429	2026-06-16 11:43:57.916429	\N	\N	\N
pg-collab-lead-1781622060	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:01.80325	2026-06-16 11:01:01.80325	\N	\N	\N
pg-collab-member-1781622060	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:01.806741	2026-06-16 11:01:01.806741	\N	\N	\N
pg-collab-observer-1781622060	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:01.809813	2026-06-16 11:01:01.809813	\N	\N	\N
pg-collab-observer-1781624636	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:57.919077	2026-06-16 11:43:57.919077	\N	\N	\N
pgtest-pool-agent	PG Pool Agent 1781624801	test	\N	{"pool_config": {"auto_wake": false, "skills_tags": ["python", "sql", "postgresql"], "max_idle_minutes": 60}}	POOL	\N	WORKER	\N	\N	2026-06-16 11:46:42.861253	2026-06-16 11:01:01.770662	2026-06-16 11:46:42.871985	\N	\N	2026-06-16 11:46:42.847093
pg-ws-agent-1781622060	PG WS Test Agent 1	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:03.278106	2026-06-16 11:01:03.278106	\N	\N	\N
pg-collab-lead-1781623308	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:21:50.041111	2026-06-16 11:21:50.041111	\N	\N	\N
pg-collab-member-1781623308	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:21:50.043828	2026-06-16 11:21:50.043828	\N	\N	\N
pg-ws-agent-1781623468	PG WS Test Agent 1	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:24:31.177152	2026-06-16 11:24:31.177152	\N	\N	\N
pg-ws-agent2-1781623468	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:24:31.19855	2026-06-16 11:24:31.19855	\N	\N	\N
pg-collab-observer-1781623308	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:21:50.046188	2026-06-16 11:21:50.046188	\N	\N	\N
pg-spec-agent-1781624636	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:59.229089	2026-06-16 11:43:59.229089	\N	\N	\N
pg-ws-agent-1781624171	PG WS Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:36:14.293933	2026-06-16 11:36:14.317265	\N	\N	2026-06-16 11:36:14.317265
pg-ws-agent-1781624636	PG WS Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:59.341243	2026-06-16 11:43:59.364696	\N	\N	2026-06-16 11:43:59.364696
pg-ws-agent2-1781624636	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:43:59.367345	2026-06-16 11:43:59.367345	\N	\N	\N
pg-spec-agent-1781624646	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:44:06.654491	2026-06-16 11:44:06.654491	\N	\N	\N
pg-ws-agent-1781623308	PG WS Test Agent 1	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:21:51.155283	2026-06-16 11:21:51.155283	\N	\N	\N
pg-ws-agent2-1781623308	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:21:51.177497	2026-06-16 11:21:51.177497	\N	\N	\N
pg-spec-agent-1781624736	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:45:36.657458	2026-06-16 11:45:36.657458	\N	\N	\N
pg-spec-agent-1781624754	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:45:54.662563	2026-06-16 11:45:54.662563	\N	\N	\N
pg-ws-agent-1781623917	PG WS Test Agent 1	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:32:00.224376	2026-06-16 11:32:00.224376	\N	\N	\N
pg-ws-agent2-1781623917	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:32:00.245892	2026-06-16 11:32:00.245892	\N	\N	\N
pg-ws-agent2-1781624117	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:35:17.65655	2026-06-16 11:35:17.65655	\N	\N	\N
pg-spec-agent-1781624762	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:02.619111	2026-06-16 11:46:02.619111	\N	\N	\N
pg-ws-agent2-1781624171	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:36:14.320179	2026-06-16 11:36:14.320179	\N	\N	\N
pg-spec-agent-1781624795	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:35.664817	2026-06-16 11:46:35.664817	\N	\N	\N
admin-test-agent	Admin Test Agent	BUSINESS	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 09:58:29.642031	2026-06-16 11:46:42.288928	Test agent for admin registration	\N	2026-06-16 11:46:42.288928
full-flow-agent	Full Flow Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 09:58:29.659382	2026-06-16 11:46:42.3116	\N	\N	2026-06-16 11:46:42.3116
pgtest-agent-1	PG Test Agent 1781624801	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:01:01.723913	2026-06-16 11:46:42.819927	Updated PG test agent	\N	2026-06-16 11:46:42.811685
pg-collab-lead-1781624801	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:42.87801	2026-06-16 11:46:42.87801	\N	\N	\N
pg-collab-member-1781624801	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:42.882013	2026-06-16 11:46:42.882013	\N	\N	\N
pg-collab-observer-1781624801	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:42.884878	2026-06-16 11:46:42.884878	\N	\N	\N
pg-collab-lead-1781623917	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:31:58.932875	2026-06-16 11:31:58.932875	\N	\N	\N
pg-collab-member-1781623917	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:31:58.935931	2026-06-16 11:31:58.935931	\N	\N	\N
pg-collab-observer-1781623917	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:31:58.938748	2026-06-16 11:31:58.938748	\N	\N	\N
pg-ws-agent-1781624271	PG WS Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:37:54.31636	2026-06-16 11:37:54.338826	\N	\N	2026-06-16 11:37:54.338826
pg-ws-agent2-1781624271	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:37:54.341662	2026-06-16 11:37:54.341662	\N	\N	\N
pg-spec-agent-1781624801	PG Spec Test Agent	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:44.191801	2026-06-16 11:46:44.191801	\N	\N	\N
pg-ws-agent-1781624801	PG WS Test Agent	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:44.295088	2026-06-16 11:46:44.316494	\N	\N	2026-06-16 11:46:44.316494
pg-ws-agent2-1781624801	PG WS Test Agent 2	\N	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:46:44.319336	2026-06-16 11:46:44.319336	\N	\N	\N
pg-collab-lead-1781624171	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:36:12.95522	2026-06-16 11:36:12.95522	\N	\N	\N
pg-collab-member-1781624171	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:36:12.958342	2026-06-16 11:36:12.958342	\N	\N	\N
pg-collab-observer-1781624171	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:36:12.962629	2026-06-16 11:36:12.962629	\N	\N	\N
pg-collab-lead-1781624271	Collab Lead	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:37:52.952309	2026-06-16 11:37:52.952309	\N	\N	\N
pg-collab-member-1781624271	Collab Member	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:37:52.955701	2026-06-16 11:37:52.955701	\N	\N	\N
pg-collab-observer-1781624271	Collab Observer	test	\N	\N	ACTIVE	\N	WORKER	\N	\N	\N	2026-06-16 11:37:52.959024	2026-06-16 11:37:52.959024	\N	\N	\N
\.


--
-- Data for Name: agent_session_active; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_session_active (session_id, agent_id, owner_user_id, workspace_id, predecessor_session_id, branch_id, is_active, context, last_active_at, created_at) FROM stdin;
2	pg-ws-agent-1781623468	admin	10	\N	\N	t	\N	\N	2026-06-16 11:24:31.201544
3	pg-ws-agent2-1781623468	admin	10	2	1	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:24:31.222242
4	pg-ws-agent-1781623917	admin	15	\N	\N	t	\N	\N	2026-06-16 11:32:00.248277
5	pg-ws-agent2-1781623917	admin	15	4	2	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:32:00.264721
7	pg-ws-agent-1781624171	admin	21	\N	\N	t	\N	\N	2026-06-16 11:36:14.324547
8	pg-ws-agent2-1781624171	admin	21	7	3	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:36:14.34368
9	pg-ws-agent-1781624271	admin	26	\N	\N	t	\N	\N	2026-06-16 11:37:54.345329
10	pg-ws-agent2-1781624271	admin	26	9	4	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:37:54.363203
11	pg-ws-agent-1781624408	admin	31	\N	\N	t	\N	\N	2026-06-16 11:40:11.261753
12	pg-ws-agent2-1781624408	admin	31	11	5	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:40:11.278684
13	pg-ws-agent-1781624636	admin	36	\N	\N	t	\N	\N	2026-06-16 11:43:59.370986
14	pg-ws-agent2-1781624636	admin	36	13	6	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:43:59.388255
15	pg-ws-agent-1781624801	admin	41	\N	\N	t	\N	\N	2026-06-16 11:46:44.323309
16	pg-ws-agent2-1781624801	admin	41	15	7	t	{"reason": "pg test handoff"}	\N	2026-06-16 11:46:44.341784
\.


--
-- Data for Name: agent_session_inactive; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agent_session_inactive (session_id, agent_id, owner_user_id, workspace_id, predecessor_session_id, branch_id, is_active, context, last_active_at, created_at) FROM stdin;
\.


--
-- Data for Name: branch_merge_log; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.branch_merge_log (log_id, source_branch_id, target_branch_id, merge_status, conflicts_json, merged_at, merged_by_agent) FROM stdin;
\.


--
-- Data for Name: collab_group_members; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.collab_group_members (member_id, group_id, agent_id, role, personal_workspace_id, branch_id, joined_at, status) FROM stdin;
1	1	pg-collab-lead-1781623308	LEAD	2	\N	2026-06-16 11:21:50.073149	ACTIVE
2	1	pg-collab-member-1781623308	CONTRIBUTOR	3	\N	2026-06-16 11:21:50.078851	ACTIVE
3	1	pg-collab-observer-1781623308	OBSERVER	\N	\N	2026-06-16 11:21:50.081264	LEFT
4	2	pg-collab-lead-1781623468	LEAD	7	\N	2026-06-16 11:24:29.979019	ACTIVE
5	2	pg-collab-member-1781623468	CONTRIBUTOR	8	\N	2026-06-16 11:24:29.986274	ACTIVE
6	2	pg-collab-observer-1781623468	OBSERVER	\N	\N	2026-06-16 11:24:29.990731	LEFT
7	3	pg-collab-lead-1781623917	LEAD	12	\N	2026-06-16 11:31:58.969234	ACTIVE
8	3	pg-collab-member-1781623917	CONTRIBUTOR	13	\N	2026-06-16 11:31:58.976582	ACTIVE
9	3	pg-collab-observer-1781623917	OBSERVER	\N	\N	2026-06-16 11:31:58.980394	LEFT
10	4	pg-collab-lead-1781624171	LEAD	18	\N	2026-06-16 11:36:12.994533	ACTIVE
11	4	pg-collab-member-1781624171	CONTRIBUTOR	19	\N	2026-06-16 11:36:13.000596	ACTIVE
12	4	pg-collab-observer-1781624171	OBSERVER	\N	\N	2026-06-16 11:36:13.003597	LEFT
13	5	pg-collab-lead-1781624271	LEAD	23	\N	2026-06-16 11:37:52.99558	ACTIVE
14	5	pg-collab-member-1781624271	CONTRIBUTOR	24	\N	2026-06-16 11:37:53.002873	ACTIVE
15	5	pg-collab-observer-1781624271	OBSERVER	\N	\N	2026-06-16 11:37:53.025899	LEFT
16	6	pg-collab-lead-1781624408	LEAD	28	\N	2026-06-16 11:40:09.988275	ACTIVE
17	6	pg-collab-member-1781624408	CONTRIBUTOR	29	\N	2026-06-16 11:40:09.994482	ACTIVE
18	6	pg-collab-observer-1781624408	OBSERVER	\N	\N	2026-06-16 11:40:09.998775	LEFT
19	7	pg-collab-lead-1781624636	LEAD	33	\N	2026-06-16 11:43:57.950131	ACTIVE
20	7	pg-collab-member-1781624636	CONTRIBUTOR	34	\N	2026-06-16 11:43:57.957387	ACTIVE
21	7	pg-collab-observer-1781624636	OBSERVER	\N	\N	2026-06-16 11:43:57.960072	LEFT
22	8	pg-collab-lead-1781624801	LEAD	38	\N	2026-06-16 11:46:42.91565	ACTIVE
23	8	pg-collab-member-1781624801	CONTRIBUTOR	39	\N	2026-06-16 11:46:42.921622	ACTIVE
24	8	pg-collab-observer-1781624801	OBSERVER	\N	\N	2026-06-16 11:46:42.924905	LEFT
\.


--
-- Data for Name: collab_groups; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.collab_groups (group_id, group_name, group_type, description, workspace_id, coordinator_agent_id, sharing_policy, branch_id, spec_id, status, metadata, created_at, updated_at) FROM stdin;
1	PG Test Collab Group 1781623308	PROJECT	Updated PG collab description	1	pg-collab-lead-1781623308	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:21:50.052387	2026-06-16 11:21:50.099454
2	PG Test Collab Group 1781623468	PROJECT	Updated PG collab description	6	pg-collab-lead-1781623468	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:24:29.957821	2026-06-16 11:24:30.010026
3	PG Test Collab Group 1781623917	PROJECT	Updated PG collab description	11	pg-collab-lead-1781623917	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:31:58.94602	2026-06-16 11:31:59.005406
4	PG Test Collab Group 1781624171	PROJECT	Updated PG collab description	17	pg-collab-lead-1781624171	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:36:12.969356	2026-06-16 11:36:13.028372
5	PG Test Collab Group 1781624271	PROJECT	Updated PG collab description	22	pg-collab-lead-1781624271	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:37:52.966225	2026-06-16 11:37:53.078242
6	PG Test Collab Group 1781624408	PROJECT	Updated PG collab description	27	pg-collab-lead-1781624408	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:40:09.957583	2026-06-16 11:40:10.023867
7	PG Test Collab Group 1781624636	PROJECT	Updated PG collab description	32	pg-collab-lead-1781624636	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:43:57.926052	2026-06-16 11:43:57.983686
8	PG Test Collab Group 1781624801	PROJECT	Updated PG collab description	37	pg-collab-lead-1781624801	OPEN	\N	\N	ACTIVE	\N	2026-06-16 11:46:42.891334	2026-06-16 11:46:42.950959
\.


--
-- Data for Name: context_branches; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.context_branches (branch_id, workspace_id, parent_branch_id, branch_name, branch_type, status, source_context_id, agent_id, created_at, merged_at, abandoned_at, description, is_lesson, lesson_tags) FROM stdin;
1	10	\N	handoff-to-pg-ws-agent2-1781623468	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781623468	2026-06-16 11:24:31.216361	\N	\N	Handoff from pg-ws-agent-1781623468 to pg-ws-agent2-1781623468	f	\N
2	15	\N	handoff-to-pg-ws-agent2-1781623917	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781623917	2026-06-16 11:32:00.260606	\N	\N	Handoff from pg-ws-agent-1781623917 to pg-ws-agent2-1781623917	f	\N
3	21	\N	handoff-to-pg-ws-agent2-1781624171	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781624171	2026-06-16 11:36:14.338087	\N	\N	Handoff from pg-ws-agent-1781624171 to pg-ws-agent2-1781624171	f	\N
4	26	\N	handoff-to-pg-ws-agent2-1781624271	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781624271	2026-06-16 11:37:54.358698	\N	\N	Handoff from pg-ws-agent-1781624271 to pg-ws-agent2-1781624271	f	\N
5	31	\N	handoff-to-pg-ws-agent2-1781624408	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781624408	2026-06-16 11:40:11.273901	\N	\N	Handoff from pg-ws-agent-1781624408 to pg-ws-agent2-1781624408	f	\N
6	36	\N	handoff-to-pg-ws-agent2-1781624636	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781624636	2026-06-16 11:43:59.383712	\N	\N	Handoff from pg-ws-agent-1781624636 to pg-ws-agent2-1781624636	f	\N
7	41	\N	handoff-to-pg-ws-agent2-1781624801	HANDOFF	ACTIVE	\N	pg-ws-agent2-1781624801	2026-06-16 11:46:44.337666	\N	\N	Handoff from pg-ws-agent-1781624801 to pg-ws-agent2-1781624801	f	\N
\.


--
-- Data for Name: entities_default; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_default (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
\.


--
-- Data for Name: entities_experience; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_experience (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
\.


--
-- Data for Name: entities_harness_template; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_harness_template (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
9	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:24:30.960977	2026-06-16 11:24:30.972126	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
14	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:31:59.955285	2026-06-16 11:31:59.967556	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
17	HARNESS_TEMPLATE	PG Test Harness 1781624100	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:35:00.651687	2026-06-16 11:35:00.651687	\N	'1781624100':4A 'analyz':17C 'domain':16C 'har':3A,8B 'input':18C 'pg':1A,6B 'role':13C 'special':14C 'templat':9B 'test':2A,7B
21	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:36:14.026957	2026-06-16 11:36:14.038659	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
23	HARNESS_TEMPLATE	PG Test Harness 1781624181	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:36:21.62818	2026-06-16 11:36:21.62818	\N	'1781624181':4A 'analyz':17C 'domain':16C 'har':3A,8B 'input':18C 'pg':1A,6B 'role':13C 'special':14C 'templat':9B 'test':2A,7B
28	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:37:54.053696	2026-06-16 11:37:54.065065	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
30	HARNESS_TEMPLATE	test harness	\N	test	test	ACTIVE	5.0	\N	\N	SHARED	\N	\N	0	2026-06-16 11:38:37.542701	2026-06-16 11:38:37.542701	\N	'har':2A 'test':1A,3B
36	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:40:10.976981	2026-06-16 11:40:10.988713	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
41	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:43:58.927127	2026-06-16 11:43:58.93794	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
56	HARNESS_TEMPLATE	Updated PG Harness	You are a {role} specializing in {domain}. Analyze: {input}	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:46:43.923334	2026-06-16 11:46:43.935503	\N	'analyz':16C 'domain':15C 'har':3A,7B 'input':17C 'pg':2A,5B 'role':12C 'special':13C 'templat':8B 'test':6B 'updat':1A
\.


--
-- Data for Name: entities_knowledge; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_knowledge (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
\.


--
-- Data for Name: entities_memory; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_memory (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
6	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:24:30.016679	2026-06-16 11:24:30.016679	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
7	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:24:30.889216	2026-06-16 11:24:30.889216	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
8	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:24:30.892839	2026-06-16 11:24:30.892839	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
11	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:31:59.014942	2026-06-16 11:31:59.014942	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
12	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:31:59.877635	2026-06-16 11:31:59.877635	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
13	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:31:59.88094	2026-06-16 11:31:59.88094	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
16	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:34:03.652174	2026-06-16 11:34:03.652174	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
18	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:36:13.035604	2026-06-16 11:36:13.035604	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
19	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:36:13.951626	2026-06-16 11:36:13.951626	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
20	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:36:13.9555	2026-06-16 11:36:13.9555	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
24	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	SHARED	\N	\N	0	2026-06-16 11:37:10.644219	2026-06-16 11:37:10.644219	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
25	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:37:53.087122	2026-06-16 11:37:53.087122	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
26	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:37:53.982896	2026-06-16 11:37:53.982896	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
27	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:37:53.987192	2026-06-16 11:37:53.987192	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
31	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:39:50.62022	2026-06-16 11:39:50.62022	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
32	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:39:50.627469	2026-06-16 11:39:50.627469	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
33	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:40:10.033099	2026-06-16 11:40:10.033099	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
34	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:40:10.9099	2026-06-16 11:40:10.9099	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
35	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:40:10.913149	2026-06-16 11:40:10.913149	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
38	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:43:57.992829	2026-06-16 11:43:57.992829	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
39	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:43:58.859477	2026-06-16 11:43:58.859477	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
40	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:43:58.863089	2026-06-16 11:43:58.863089	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
53	MEMORY	Shared Memory PG	content for sharing	\N	test-collab-pg	ACTIVE	5.0	\N	\N	PRIVATE	\N	\N	0	2026-06-16 11:46:42.958241	2026-06-16 11:46:42.958241	\N	'content':4C 'memori':2A 'pg':3A 'share':1A,6C
54	MEMORY	Graph Edge Test A	content a	\N	graph-test-pg	ACTIVE	8.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:46:43.846308	2026-06-16 11:46:43.846308	\N	'content':4C 'edg':2A 'graph':1A 'test':3A
55	MEMORY	Graph Edge Test B	content b	\N	graph-test-pg	ACTIVE	6.0	graph-tester-pg	\N	PRIVATE	\N	\N	0	2026-06-16 11:46:43.850005	2026-06-16 11:46:43.850005	\N	'b':4A,6C 'content':5C 'edg':2A 'graph':1A 'test':3A
\.


--
-- Data for Name: entities_other; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_other (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
\.


--
-- Data for Name: entities_skill; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_skill (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
\.


--
-- Data for Name: entities_spec; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_spec (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
45	SPEC	test spec	test content	\N	test	ACTIVE	5.0	\N	\N	SHARED	\N	\N	0	2026-06-16 11:44:57.527618	2026-06-16 11:44:57.527618	\N	'content':4C 'spec':2A 'test':1A,3C
46	SPEC	updated spec	test	\N	test	ACTIVE	5.0	\N	\N	SHARED	\N	\N	0	2026-06-16 11:45:26.516789	2026-06-16 11:45:26.535615	\N	'spec':2A 'test':3C 'updat':1A
48	SPEC	Derived PG Spec 1781624736	Process all items with low error rate	A PG test specification	test-spec	ACTIVE	8.0	pg-spec-agent-1781624736	\N	SHARED	\N	\N	0	2026-06-16 11:45:36.683578	2026-06-16 11:45:36.683578	\N	'1781624736':4A 'deriv':1A 'error':14C 'item':11C 'low':13C 'pg':2A,6B 'process':9C 'rate':15C 'spec':3A 'specif':8B 'test':7B
50	SPEC	Derived PG Spec 1781624754	Process all items with low error rate	A PG test specification	test-spec	ACTIVE	8.0	pg-spec-agent-1781624754	\N	SHARED	\N	\N	0	2026-06-16 11:45:54.709913	2026-06-16 11:45:54.709913	\N	'1781624754':4A 'deriv':1A 'error':14C 'item':11C 'low':13C 'pg':2A,6B 'process':9C 'rate':15C 'spec':3A 'specif':8B 'test':7B
52	SPEC	Derived PG Spec 1781624795	Process all items with low error rate	A PG test specification	test-spec	ACTIVE	8.0	pg-spec-agent-1781624795	\N	SHARED	\N	\N	0	2026-06-16 11:46:35.699257	2026-06-16 11:46:35.699257	\N	'1781624795':4A 'deriv':1A 'error':14C 'item':11C 'low':13C 'pg':2A,6B 'process':9C 'rate':15C 'spec':3A 'specif':8B 'test':7B
59	SPEC	Derived PG Spec 1781624801	Process all items with low error rate	A PG test specification	test-spec	ACTIVE	8.0	pg-spec-agent-1781624801	\N	SHARED	\N	\N	0	2026-06-16 11:46:44.220793	2026-06-16 11:46:44.220793	\N	'1781624801':4A 'deriv':1A 'error':14C 'item':11C 'low':13C 'pg':2A,6B 'process':9C 'rate':15C 'spec':3A 'specif':8B 'test':7B
\.


--
-- Data for Name: entities_task_output; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entities_task_output (entity_id, entity_type, title, content, summary, category, status, importance, owned_by_agent, source_agent, visibility, workspace_id, branch_id, retrieval_count, created_at, updated_at, expires_at, search_vector) FROM stdin;
10	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:24:30.98268	2026-06-16 11:24:30.98268	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
15	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:31:59.981543	2026-06-16 11:31:59.981543	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
22	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:36:14.055794	2026-06-16 11:36:14.055794	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
29	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:37:54.078193	2026-06-16 11:37:54.078193	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
37	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:40:11.001587	2026-06-16 11:40:11.001587	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
42	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:43:58.953036	2026-06-16 11:43:58.953036	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
57	TASK_OUTPUT	Instance of Updated PG Harness	You are a Engineer specializing in testing. Analyze: sample PG data	A PG test harness template	test-harness-pg	ACTIVE	7.0	test-agent-pg	test-agent-pg	SHARED	\N	\N	0	2026-06-16 11:46:43.949639	2026-06-16 11:46:43.949639	\N	'analyz':18C 'data':21C 'engin':14C 'har':5A,9B 'instanc':1A 'pg':4A,7B,20C 'sampl':19C 'special':15C 'templat':10B 'test':8B,17C 'updat':3A
\.


--
-- Data for Name: entity_access_log_202605; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_access_log_202605 (log_id, entity_id, entity_type, agent_id, access_type, session_id, context, access_time) FROM stdin;
\.


--
-- Data for Name: entity_access_log_202606; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_access_log_202606 (log_id, entity_id, entity_type, agent_id, access_type, session_id, context, access_time) FROM stdin;
\.


--
-- Data for Name: entity_access_log_max; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_access_log_max (log_id, entity_id, entity_type, agent_id, access_type, session_id, context, access_time) FROM stdin;
\.


--
-- Data for Name: entity_edges; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_edges (edge_id, source_id, source_type, target_id, target_type, edge_type, strength, confidence, metadata, created_at) FROM stdin;
2	7	MEMORY	8	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:24:30.933601
3	10	TASK_OUTPUT	9	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:24:30.988084
5	12	MEMORY	13	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:31:59.921577
6	15	TASK_OUTPUT	14	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:31:59.985085
8	19	MEMORY	20	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:36:13.994611
9	22	TASK_OUTPUT	21	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:36:14.059607
11	26	MEMORY	27	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:37:54.022531
12	29	TASK_OUTPUT	28	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:37:54.082451
14	31	MEMORY	32	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:39:50.666913
16	34	MEMORY	35	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:40:10.946413
17	37	TASK_OUTPUT	36	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:40:11.004659
19	39	MEMORY	40	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:43:58.895123
20	42	TASK_OUTPUT	41	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:43:58.957474
21	48	SPEC	47	\N	DERIVES_FROM	1.0000	1.0000	\N	2026-06-16 11:45:36.690658
22	50	SPEC	49	\N	DERIVES_FROM	1.0000	1.0000	\N	2026-06-16 11:45:54.717455
23	52	SPEC	51	\N	DERIVES_FROM	1.0000	1.0000	\N	2026-06-16 11:46:35.705959
25	54	MEMORY	55	\N	RELATED_TO	0.7000	0.8000	\N	2026-06-16 11:46:43.887181
26	57	TASK_OUTPUT	56	\N	USES_HARNESS	1.0000	1.0000	\N	2026-06-16 11:46:43.953461
27	59	SPEC	58	\N	DERIVES_FROM	1.0000	1.0000	\N	2026-06-16 11:46:44.227375
\.


--
-- Data for Name: entity_embeddings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_embeddings (entity_id, entity_type, embedding, embedding_model, embedding_dim, embedded_at) FROM stdin;
\.


--
-- Data for Name: entity_tags; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.entity_tags (entity_id, entity_type, tag_id) FROM stdin;
\.


--
-- Data for Name: harness_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.harness_meta (entity_id, entity_type, template_version, input_schema, output_schema, execution_mode) FROM stdin;
9	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
14	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
17	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
21	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
23	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
28	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
30	HARNESS_TEMPLATE	1	\N	\N	SEQUENTIAL
36	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
41	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
56	HARNESS_TEMPLATE	1	{"type": "object", "required": ["role", "domain"], "properties": {"role": {"type": "string", "default": "Analyst"}, "input": {"type": "string", "default": ""}, "domain": {"type": "string", "default": "general"}}}	{"type": "object", "properties": {"result": {"type": "string"}, "confidence": {"type": "number"}}}	SEQUENTIAL
\.


--
-- Data for Name: knowledge_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.knowledge_meta (entity_id, entity_type, domain, topic, difficulty, review_count, last_reviewed, next_review) FROM stdin;
\.


--
-- Data for Name: skill_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.skill_meta (skill_id, skill_name, skill_version, description, skill_type, category, visibility, owned_by_agent, input_schema, output_schema, dependencies, resource_path, download_count, rating, status, created_at, updated_at) FROM stdin;
52	test_skill	1.0	test desc	TOOL	test	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:27:33.308564	\N
55	autocommit_test	1.0.0	\N	CUSTOM	test	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:31:21.56726	\N
56	PG Skill Test 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.06519	\N
57	PG Get Skill Test 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.070673	\N
58	PG Update Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.078052	\N
59	PG Delete Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:32:00.084362	2026-06-16 11:32:00.0909
60	PG List Skill 1 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.097629	\N
61	PG List Skill 2 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.100703	\N
62	PG Searchable Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.108469	\N
63	PG Valid Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.11555	\N
64	PG Deprecate Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.1257	\N
65	PG Resource Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/65/test.py	0	\N	ACTIVE	2026-06-16 11:32:00.149853	2026-06-16 11:32:00.163667
66	PG Discover Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:00.169119	\N
67	PG Dep Skill 1781623917	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:32:00.176332	\N
68	PG Skill Test 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.642748	\N
69	PG Get Skill Test 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.650389	\N
70	PG Update Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.666963	\N
107	PG Skill Test 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.081699	\N
71	PG Delete Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:32:07.681409	2026-06-16 11:32:07.687437
72	PG List Skill 1 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.696563	\N
73	PG List Skill 2 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.699748	\N
74	PG Searchable Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.707077	\N
75	PG Valid Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.716184	\N
76	PG Deprecate Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.724961	\N
77	PG Resource Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/77/test.py	0	\N	ACTIVE	2026-06-16 11:32:07.759992	2026-06-16 11:32:07.768299
78	PG Discover Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:32:07.772333	\N
79	PG Dep Skill 1781623927	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:32:07.780103	\N
80	key_test	1.0.0	\N	CUSTOM	\N	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:33:43.552833	\N
81	PG Skill Test 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.138919	\N
82	PG Get Skill Test 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.143011	\N
83	pg_updated_skill_1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.150261	2026-06-16 11:36:14.154491
98	PG Delete Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:37:54.183148	2026-06-16 11:37:54.190366
84	PG Delete Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:36:14.162424	2026-06-16 11:36:14.169235
85	PG List Skill 1 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.17601	\N
86	PG List Skill 2 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.178984	\N
87	PG Searchable Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.184959	\N
88	PG Valid Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.191775	\N
89	PG Deprecate Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:36:14.201483	2026-06-16 11:36:14.204698
90	PG Resource Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/90/test.py	0	\N	ACTIVE	2026-06-16 11:36:14.229858	2026-06-16 11:36:14.237479
91	PG Discover Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:14.241131	\N
92	PG Dep Skill 1781624171	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:36:14.248574	\N
93	PG List Skill 1 1781624201	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:41.645654	\N
94	PG List Skill 2 1781624201	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:36:41.652108	\N
95	PG Skill Test 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.162236	\N
96	PG Get Skill Test 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.166503	\N
97	pg_updated_skill_1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.172985	2026-06-16 11:37:54.176897
99	PG List Skill 1 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.197354	\N
100	PG List Skill 2 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.200395	\N
101	PG Searchable Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.20836	\N
102	PG Valid Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.215505	\N
103	PG Deprecate Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:37:54.225643	2026-06-16 11:37:54.228629
104	PG Resource Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/104/test.py	0	\N	ACTIVE	2026-06-16 11:37:54.255287	2026-06-16 11:37:54.263005
105	PG Discover Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:37:54.266724	\N
106	PG Dep Skill 1781624271	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:37:54.273858	\N
108	PG Get Skill Test 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.08626	\N
109	pg_updated_skill_1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.093748	2026-06-16 11:40:11.096231
111	PG List Skill 1 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.115483	\N
110	PG Delete Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:40:11.101982	2026-06-16 11:40:11.10947
112	PG List Skill 2 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.118026	\N
113	PG Searchable Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.125643	\N
114	PG Valid Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.132391	\N
115	PG Deprecate Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:40:11.142784	2026-06-16 11:40:11.146114
116	PG Resource Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/116/test.py	0	\N	ACTIVE	2026-06-16 11:40:11.170205	2026-06-16 11:40:11.177449
117	PG Discover Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:40:11.181082	\N
118	PG Dep Skill 1781624408	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:40:11.188114	\N
119	PG Skill Test 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.034954	\N
120	PG Get Skill Test 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.0396	\N
121	pg_updated_skill_1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.046353	2026-06-16 11:43:59.049293
122	PG Delete Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:43:59.057409	2026-06-16 11:43:59.063186
123	PG List Skill 1 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.071448	\N
124	PG List Skill 2 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.074256	\N
125	PG Searchable Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.081833	\N
126	PG Valid Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.089562	\N
127	PG Deprecate Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:43:59.100851	2026-06-16 11:43:59.104005
128	PG Resource Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/128/test.py	0	\N	ACTIVE	2026-06-16 11:43:59.131389	2026-06-16 11:43:59.14394
129	PG Discover Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:43:59.148502	\N
130	PG Dep Skill 1781624636	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:43:59.157491	\N
131	PG Skill Test 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.03332	\N
132	PG Get Skill Test 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.038377	\N
133	pg_updated_skill_1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.044757	2026-06-16 11:46:44.047251
134	PG Delete Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:46:44.053232	2026-06-16 11:46:44.060073
135	PG List Skill 1 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.066349	\N
136	PG List Skill 2 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.06983	\N
137	PG Searchable Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.077972	\N
138	PG Valid Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.084982	\N
139	PG Deprecate Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	DEPRECATED	2026-06-16 11:46:44.096984	2026-06-16 11:46:44.100365
140	PG Resource Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	skill_resources/140/test.py	0	\N	ACTIVE	2026-06-16 11:46:44.125905	2026-06-16 11:46:44.13443
141	PG Discover Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	\N	\N	0	\N	ACTIVE	2026-06-16 11:46:44.138617	\N
142	PG Dep Skill 1781624801	1.0.0	\N	CUSTOM	test-pg	SHARED	\N	\N	\N	[99999990, 99999991]	\N	0	\N	ACTIVE	2026-06-16 11:46:44.145465	\N
\.


--
-- Data for Name: spec_meta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spec_meta (entity_id, entity_type, spec_version, spec_status, acceptance_criteria, spec_constraints, spec_scope, complexity, branch_id, parent_spec_id) FROM stdin;
45	SPEC	1	DRAFT	\N	\N	\N	MEDIUM	\N	\N
46	SPEC	1	DRAFT	\N	\N	\N	MEDIUM	\N	\N
48	SPEC	1	DRAFT	["All items processed", "Error rate < 1%", "Throughput > 100/s"]	{"min_accuracy": 0.99, "max_latency_ms": 500}	processing	HIGH	\N	47
50	SPEC	1	DRAFT	["All items processed", "Error rate < 1%", "Throughput > 100/s"]	{"min_accuracy": 0.99, "max_latency_ms": 500}	processing	HIGH	\N	49
52	SPEC	1	DRAFT	["All items processed", "Error rate < 1%", "Throughput > 100/s"]	{"min_accuracy": 0.99, "max_latency_ms": 500}	processing	HIGH	\N	51
59	SPEC	1	DRAFT	["All items processed", "Error rate < 1%", "Throughput > 100/s"]	{"min_accuracy": 0.99, "max_latency_ms": 500}	processing	HIGH	\N	58
\.


--
-- Data for Name: spec_plan_links; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.spec_plan_links (link_id, spec_id, plan_id, link_type, link_strength) FROM stdin;
\.


--
-- Data for Name: system_config; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.system_config (config_key, config_value, description, updated_at) FROM stdin;
recovery_codes.rc-return-test-agent	[{"hash": "6bba93fceb6c95271845b87182283a1894e37bf175c5bb001114d6ce9c857498", "used": false}, {"hash": "2ccac0c697c104e2f2c354740d7745fd3eb2a5fa94ef7032357a839bb9fe132e", "used": false}, {"hash": "a84425088df7ddb56e798ac02136b8608c4d0e0da356325a8e02a91e46beb702", "used": false}, {"hash": "c887c460307eb4ade21aa955ea7687a4f8fb98989e9cb6784d749cd6d4f36c96", "used": false}, {"hash": "dd0f1e0dba662da035e3d6dbc7b6bca24642cc8d3ed4498426f19b95ae45d7b3", "used": false}, {"hash": "a9bba064c595210c1c3063826f974e8df208da6579d866d3ff02c3ff9cafeb40", "used": false}, {"hash": "29c2bfc11fdd5255286c3595271f1b19e2efdd3c07124fc5f6151f731c669ad1", "used": false}, {"hash": "f56d436b804500ccdd76508083856c3f3deb7fcbc3b9ac2b31f5274d19675037", "used": false}]	Recovery codes for agent rc-return-test-agent	2026-06-16 11:46:42.807818
recovery_codes.recovery-test-agent	[{"hash": "8c294b2ad9ae6154180b487999e9daae2ff2cc0316503d22a761bf23e5e1377a", "used": true}, {"hash": "afbae7e7d23ab8df6e70d397ff48138f1a0d7eca45b6f0c45c7818f0c4c3d3ef", "used": true}, {"hash": "b46eb2c8e552ea65a2d2a322c7f9075d0c899462a9c823e18bd00f1b7b8771f4", "used": true}, {"hash": "999cf100834cb96eb601db61f66e6cdfb25b4bd836f935a9f83111692dfaca42", "used": false}, {"hash": "0fb35beb2f85843a4316b363ba174ea3d2d836c16e273afffb7a7e48d720f597", "used": false}, {"hash": "b7d8c38d6281bd0ba57ac271eeabf3e8d4faf00788dc71f2ecf46119a17fa95c", "used": false}, {"hash": "c6bd377fccb103c941f1413e1ec8fcdba5ae6a44c3aa4b6e15cf7f7172cd5026", "used": false}, {"hash": "17619052df3608057d06afc1beca3a715409f26077fa9dead97063f3999c6bb9", "used": false}]	Recovery codes for agent recovery-test-agent	2026-06-16 11:46:42.762263
admin.registration_token	AT_68c74621ab206420b18df1897acd6188e651937c4c959ffaa030ccb4b5f14fe8	Admin token for Agent registration (encrypted)	2026-06-16 11:46:43.833367
recovery_codes.admin-test-agent	[{"hash": "fd5fa4548750163032c71d973d0b0d6923564bcaab4a5c2f0b7ac4a72978129d", "used": false}, {"hash": "e89e71d0949c5d5075d1fe2fe0b88f533658b227045bdd2ba1c3a771d55e999d", "used": false}, {"hash": "34d0e47650789a838d8b1ad77630b81853caa8d94a5dc7fdb80c3a0a56043b94", "used": false}, {"hash": "ead839cba92b78a3168eb688b663876f952995ca684f492b66369dc4618c24e5", "used": false}, {"hash": "de4ac3c5b4bb1e8603f265b4d301408b77e5e654a7a8a6984dd9df6a7eccc1af", "used": false}, {"hash": "7c46f0ce307ba0b761276786c70a3c8393733c4037358c9a4170a9db24b147a5", "used": false}, {"hash": "30e349b0d9553b6d6fec0627c004fd40d61c3370774ac624e2d74f8820d25bc9", "used": false}, {"hash": "d5be105a1c58e39330c95a7fa74bebef17faf9a7628b39b6c778a0d132e6e6dd", "used": false}]	Recovery codes for agent admin-test-agent	2026-06-16 11:46:42.29575
recovery_codes.full-flow-agent	[{"hash": "54d79c473ffd7c579964fe8c97d6253ecb86de5015c7aa7dab39283f57186e46", "used": false}, {"hash": "7f0422dc205c5aecceeb4be0b778b4c28149f6c0b83587fa3c591c95f6eac7b5", "used": false}, {"hash": "074cf277efc62dce098017349cacf2be199111857e18515ac932689da82d7346", "used": false}, {"hash": "ced9ece93e61e9261a392725f97e62a180a429c1614cece012f581daf08c8b27", "used": false}, {"hash": "cdc7196ade2f9a67ece94d7ab3895a20d1926eda592fb86b15d64b5410663351", "used": false}, {"hash": "dc4ae141519081288c13fe51bf3675a5043f59decdcb68fd4c84df4bf2af46d4", "used": false}, {"hash": "a60ba0309dc37ba18eafb9c996472703f615298ce66c07e00b07aadbbeef1ff1", "used": false}, {"hash": "736ccbdc444ccfc0e9ef1d6eba9cd8cd68aed14260506dda3eb2f60cc5344717", "used": false}]	Recovery codes for agent full-flow-agent	2026-06-16 11:46:42.316415
\.


--
-- Data for Name: system_users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.system_users (user_id, username, password_hash, salt, role, status, auth_source, ldap_dn, last_ldap_sync, last_login, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: tags; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tags (tag_id, tag_name, tag_group, usage_count, created_at) FROM stdin;
\.


--
-- Data for Name: task_context_snapshots; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_context_snapshots (snapshot_id, plan_id, snapshot_type, context_data, created_at) FROM stdin;
\.


--
-- Data for Name: task_dependencies; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_dependencies (dep_id, source_plan_id, target_plan_id, dep_type) FROM stdin;
\.


--
-- Data for Name: task_plans_active; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_plans_active (plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_plans_cancelled; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_plans_cancelled (plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_plans_completed; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_plans_completed (plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_plans_default; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_plans_default (plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id, created_at, updated_at) FROM stdin;
1	pg-spec-agent-1781624636	Execute spec 1781624636	PENDING	5	\N	\N	\N	2026-06-16 11:43:59.232201	2026-06-16 11:43:59.232201
2	pg-spec-agent-1781624646	Execute spec 1781624646	PENDING	5	\N	\N	\N	2026-06-16 11:44:06.65858	2026-06-16 11:44:06.65858
3	pg-spec-agent-1781624736	Execute spec 1781624736	PENDING	5	\N	\N	\N	2026-06-16 11:45:36.660784	2026-06-16 11:45:36.660784
4	pg-spec-agent-1781624754	Execute spec 1781624754	PENDING	5	\N	\N	\N	2026-06-16 11:45:54.666769	2026-06-16 11:45:54.666769
5	pg-spec-agent-1781624762	Execute spec 1781624762	PENDING	5	\N	\N	\N	2026-06-16 11:46:02.623598	2026-06-16 11:46:02.623598
6	pg-spec-agent-1781624795	Execute spec 1781624795	PENDING	5	\N	\N	\N	2026-06-16 11:46:35.668	2026-06-16 11:46:35.668
7	pg-spec-agent-1781624801	Execute spec 1781624801	PENDING	5	\N	\N	\N	2026-06-16 11:46:44.194958	2026-06-16 11:46:44.194958
\.


--
-- Data for Name: task_plans_paused; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_plans_paused (plan_id, agent_id, goal, status, priority, strategy, result_summary, branch_id, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: task_steps; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_steps (step_id, plan_id, plan_status, step_order, description, tool_name, tool_input, tool_output, status, created_at) FROM stdin;
\.


--
-- Data for Name: task_tool_calls; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.task_tool_calls (call_id, plan_id, step_id, tool_name, tool_input, tool_output, status, duration_ms, created_at) FROM stdin;
\.


--
-- Data for Name: workspace_context; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.workspace_context (context_id, workspace_id, agent_id, session_id, context_type, context_data, parent_context_id, branch_id, visibility, created_at) FROM stdin;
1	4	pg-ws-agent-1781623308	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:21:51.158628
2	4	pg-ws-agent-1781623308	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:21:51.166705
3	9	pg-ws-agent-1781623468	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:24:31.180735
4	9	pg-ws-agent-1781623468	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:24:31.189299
5	10	pg-ws-agent2-1781623468	2	BRANCH_POINT	{"branch_id": 1, "branch_name": "handoff-to-pg-ws-agent2-1781623468", "branch_type": "HANDOFF", "fork_context_id": null}	\N	1	SHARED	2026-06-16 11:24:31.216361
6	10	pg-ws-agent2-1781623468	3	HANDOFF	{"reason": "pg test handoff"}	\N	1	SHARED	2026-06-16 11:24:31.225776
7	14	pg-ws-agent-1781623917	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:32:00.227462
8	14	pg-ws-agent-1781623917	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:32:00.235673
9	15	pg-ws-agent2-1781623917	4	BRANCH_POINT	{"branch_id": 2, "branch_name": "handoff-to-pg-ws-agent2-1781623917", "branch_type": "HANDOFF", "fork_context_id": null}	\N	2	SHARED	2026-06-16 11:32:00.260606
10	15	pg-ws-agent2-1781623917	5	HANDOFF	{"reason": "pg test handoff"}	\N	2	SHARED	2026-06-16 11:32:00.267432
11	20	pg-ws-agent-1781624171	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:36:14.297409
12	20	pg-ws-agent-1781624171	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:36:14.306243
13	21	pg-ws-agent2-1781624171	7	BRANCH_POINT	{"branch_id": 3, "branch_name": "handoff-to-pg-ws-agent2-1781624171", "branch_type": "HANDOFF", "fork_context_id": null}	\N	3	SHARED	2026-06-16 11:36:14.338087
14	21	pg-ws-agent2-1781624171	8	HANDOFF	{"reason": "pg test handoff"}	\N	3	SHARED	2026-06-16 11:36:14.34664
15	25	pg-ws-agent-1781624271	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:37:54.32002
16	25	pg-ws-agent-1781624271	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:37:54.328343
17	26	pg-ws-agent2-1781624271	9	BRANCH_POINT	{"branch_id": 4, "branch_name": "handoff-to-pg-ws-agent2-1781624271", "branch_type": "HANDOFF", "fork_context_id": null}	\N	4	SHARED	2026-06-16 11:37:54.358698
18	26	pg-ws-agent2-1781624271	10	HANDOFF	{"reason": "pg test handoff"}	\N	4	SHARED	2026-06-16 11:37:54.368296
19	30	pg-ws-agent-1781624408	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:40:11.236278
20	30	pg-ws-agent-1781624408	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:40:11.244171
21	31	pg-ws-agent2-1781624408	11	BRANCH_POINT	{"branch_id": 5, "branch_name": "handoff-to-pg-ws-agent2-1781624408", "branch_type": "HANDOFF", "fork_context_id": null}	\N	5	SHARED	2026-06-16 11:40:11.273901
22	31	pg-ws-agent2-1781624408	12	HANDOFF	{"reason": "pg test handoff"}	\N	5	SHARED	2026-06-16 11:40:11.281628
23	35	pg-ws-agent-1781624636	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:43:59.345406
24	35	pg-ws-agent-1781624636	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:43:59.353888
25	36	pg-ws-agent2-1781624636	13	BRANCH_POINT	{"branch_id": 6, "branch_name": "handoff-to-pg-ws-agent2-1781624636", "branch_type": "HANDOFF", "fork_context_id": null}	\N	6	SHARED	2026-06-16 11:43:59.383712
26	36	pg-ws-agent2-1781624636	14	HANDOFF	{"reason": "pg test handoff"}	\N	6	SHARED	2026-06-16 11:43:59.392248
27	40	pg-ws-agent-1781624801	\N	CHECKPOINT	{"conversation": [{"role": "user", "content": "hello PG"}], "working_memory": {"findings": ["pg test"]}}	\N	\N	SHARED	2026-06-16 11:46:44.298135
28	40	pg-ws-agent-1781624801	\N	HANDOFF	{"info": "pg handoff data"}	\N	\N	SHARED	2026-06-16 11:46:44.307186
29	41	pg-ws-agent2-1781624801	15	BRANCH_POINT	{"branch_id": 7, "branch_name": "handoff-to-pg-ws-agent2-1781624801", "branch_type": "HANDOFF", "fork_context_id": null}	\N	7	SHARED	2026-06-16 11:46:44.337666
30	41	pg-ws-agent2-1781624801	16	HANDOFF	{"reason": "pg test handoff"}	\N	7	SHARED	2026-06-16 11:46:44.345003
\.


--
-- Data for Name: workspace_tasks; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.workspace_tasks (workspace_id, plan_id) FROM stdin;
\.


--
-- Data for Name: workspaces; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.workspaces (workspace_id, workspace_name, workspace_type, workspace_alias, isolation_mode, owner_user_id, current_agent_id, current_session_id, branch_id, summary, metadata, status, created_at, updated_at) FROM stdin;
1	CollabGroup: PG Test Collab Group 1781623308	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781623308"}	ACTIVE	2026-06-16 11:21:50.048998	2026-06-16 11:21:50.048998
2	Personal: pg-collab-lead-1781623308 in 1	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781623308", "group_id": 1}	ACTIVE	2026-06-16 11:21:50.069927	2026-06-16 11:21:50.069927
3	Personal: pg-collab-member-1781623308 in 1	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781623308", "group_id": 1}	ACTIVE	2026-06-16 11:21:50.076333	2026-06-16 11:21:50.076333
21	PG Handoff Workspace 1781624171	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781624171	8	\N	\N	\N	ACTIVE	2026-06-16 11:36:14.314196	2026-06-16 11:36:14.349329
5	PG Handoff Workspace 1781623308	CONVERSATION	\N	SHARED	admin	\N	\N	\N	\N	\N	ACTIVE	2026-06-16 11:21:51.173948	2026-06-16 11:21:51.173948
4	PG User Workspace 1781623308	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781623308	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:21:51.127215	2026-06-16 11:21:51.190365
6	CollabGroup: PG Test Collab Group 1781623468	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781623468"}	ACTIVE	2026-06-16 11:24:29.954334	2026-06-16 11:24:29.954334
7	Personal: pg-collab-lead-1781623468 in 2	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781623468", "group_id": 2}	ACTIVE	2026-06-16 11:24:29.975839	2026-06-16 11:24:29.975839
8	Personal: pg-collab-member-1781623468 in 2	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781623468", "group_id": 2}	ACTIVE	2026-06-16 11:24:29.983034	2026-06-16 11:24:29.983034
20	PG User Workspace 1781624171	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781624171	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:36:14.260507	2026-06-16 11:36:14.364309
22	CollabGroup: PG Test Collab Group 1781624271	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781624271"}	ACTIVE	2026-06-16 11:37:52.96253	2026-06-16 11:37:52.96253
10	PG Handoff Workspace 1781623468	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781623468	3	\N	\N	\N	ACTIVE	2026-06-16 11:24:31.195201	2026-06-16 11:24:31.228875
9	PG User Workspace 1781623468	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781623468	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:24:31.144673	2026-06-16 11:24:31.238155
11	CollabGroup: PG Test Collab Group 1781623917	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781623917"}	ACTIVE	2026-06-16 11:31:58.942079	2026-06-16 11:31:58.942079
12	Personal: pg-collab-lead-1781623917 in 3	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781623917", "group_id": 3}	ACTIVE	2026-06-16 11:31:58.966144	2026-06-16 11:31:58.966144
13	Personal: pg-collab-member-1781623917 in 3	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781623917", "group_id": 3}	ACTIVE	2026-06-16 11:31:58.97331	2026-06-16 11:31:58.97331
23	Personal: pg-collab-lead-1781624271 in 5	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781624271", "group_id": 5}	ACTIVE	2026-06-16 11:37:52.992179	2026-06-16 11:37:52.992179
24	Personal: pg-collab-member-1781624271 in 5	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781624271", "group_id": 5}	ACTIVE	2026-06-16 11:37:52.999566	2026-06-16 11:37:52.999566
15	PG Handoff Workspace 1781623917	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781623917	5	\N	\N	\N	ACTIVE	2026-06-16 11:32:00.242111	2026-06-16 11:32:00.270009
14	PG User Workspace 1781623917	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781623917	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:32:00.190879	2026-06-16 11:32:00.283293
16	PG Handoff Workspace 1781624117	CONVERSATION	\N	SHARED	admin	\N	\N	\N	\N	\N	ACTIVE	2026-06-16 11:35:17.651475	2026-06-16 11:35:17.651475
17	CollabGroup: PG Test Collab Group 1781624171	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781624171"}	ACTIVE	2026-06-16 11:36:12.96579	2026-06-16 11:36:12.96579
18	Personal: pg-collab-lead-1781624171 in 4	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781624171", "group_id": 4}	ACTIVE	2026-06-16 11:36:12.990522	2026-06-16 11:36:12.990522
19	Personal: pg-collab-member-1781624171 in 4	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781624171", "group_id": 4}	ACTIVE	2026-06-16 11:36:12.997692	2026-06-16 11:36:12.997692
26	PG Handoff Workspace 1781624271	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781624271	10	\N	\N	\N	ACTIVE	2026-06-16 11:37:54.335941	2026-06-16 11:37:54.371369
25	PG User Workspace 1781624271	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781624271	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:37:54.284239	2026-06-16 11:37:54.388377
27	CollabGroup: PG Test Collab Group 1781624408	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781624408"}	ACTIVE	2026-06-16 11:40:09.953865	2026-06-16 11:40:09.953865
28	Personal: pg-collab-lead-1781624408 in 6	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781624408", "group_id": 6}	ACTIVE	2026-06-16 11:40:09.984974	2026-06-16 11:40:09.984974
29	Personal: pg-collab-member-1781624408 in 6	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781624408", "group_id": 6}	ACTIVE	2026-06-16 11:40:09.991326	2026-06-16 11:40:09.991326
33	Personal: pg-collab-lead-1781624636 in 7	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781624636", "group_id": 7}	ACTIVE	2026-06-16 11:43:57.947309	2026-06-16 11:43:57.947309
34	Personal: pg-collab-member-1781624636 in 7	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781624636", "group_id": 7}	ACTIVE	2026-06-16 11:43:57.953893	2026-06-16 11:43:57.953893
31	PG Handoff Workspace 1781624408	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781624408	12	\N	\N	\N	ACTIVE	2026-06-16 11:40:11.251346	2026-06-16 11:40:11.284289
30	PG User Workspace 1781624408	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781624408	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:40:11.200036	2026-06-16 11:40:11.300715
32	CollabGroup: PG Test Collab Group 1781624636	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781624636"}	ACTIVE	2026-06-16 11:43:57.922575	2026-06-16 11:43:57.922575
35	PG User Workspace 1781624636	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781624636	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:43:59.31009	2026-06-16 11:43:59.410477
36	PG Handoff Workspace 1781624636	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781624636	14	\N	\N	\N	ACTIVE	2026-06-16 11:43:59.36177	2026-06-16 11:43:59.395174
37	CollabGroup: PG Test Collab Group 1781624801	COLLAB_GROUP	\N	SHARED	\N	\N	\N	\N	\N	{"group_type": "PROJECT", "collab_group_name": "PG Test Collab Group 1781624801"}	ACTIVE	2026-06-16 11:46:42.888139	2026-06-16 11:46:42.888139
38	Personal: pg-collab-lead-1781624801 in 8	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "LEAD", "agent_id": "pg-collab-lead-1781624801", "group_id": 8}	ACTIVE	2026-06-16 11:46:42.912579	2026-06-16 11:46:42.912579
39	Personal: pg-collab-member-1781624801 in 8	PERSONAL_IN_GROUP	\N	ISOLATED	\N	\N	\N	\N	\N	{"role": "CONTRIBUTOR", "agent_id": "pg-collab-member-1781624801", "group_id": 8}	ACTIVE	2026-06-16 11:46:42.918717	2026-06-16 11:46:42.918717
41	PG Handoff Workspace 1781624801	CONVERSATION	\N	SHARED	admin	pg-ws-agent2-1781624801	16	\N	\N	\N	ACTIVE	2026-06-16 11:46:44.313625	2026-06-16 11:46:44.348306
40	PG User Workspace 1781624801	CONVERSATION	\N	SHARED	admin	pg-ws-agent-1781624801	\N	\N	PG test summary	\N	ACTIVE	2026-06-16 11:46:44.262408	2026-06-16 11:46:44.364425
\.


--
-- Name: agent_collaboration_collab_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agent_collaboration_collab_id_seq', 1, false);


--
-- Name: agent_credentials_credential_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agent_credentials_credential_id_seq', 1, false);


--
-- Name: agent_permission_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agent_permission_log_log_id_seq', 1, false);


--
-- Name: agent_session_session_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agent_session_session_id_seq', 16, true);


--
-- Name: branch_merge_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.branch_merge_log_log_id_seq', 1, false);


--
-- Name: collab_group_members_member_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.collab_group_members_member_id_seq', 24, true);


--
-- Name: collab_groups_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.collab_groups_group_id_seq', 8, true);


--
-- Name: context_branches_branch_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.context_branches_branch_id_seq', 7, true);


--
-- Name: entities_entity_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.entities_entity_id_seq', 59, true);


--
-- Name: entity_access_log_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.entity_access_log_log_id_seq', 1, false);


--
-- Name: entity_edges_edge_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.entity_edges_edge_id_seq', 27, true);


--
-- Name: skill_meta_skill_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.skill_meta_skill_id_seq', 142, true);


--
-- Name: spec_plan_links_link_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.spec_plan_links_link_id_seq', 2, true);


--
-- Name: system_users_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.system_users_user_id_seq', 1, false);


--
-- Name: tags_tag_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tags_tag_id_seq', 1, false);


--
-- Name: task_context_snapshots_snapshot_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_context_snapshots_snapshot_id_seq', 1, false);


--
-- Name: task_dependencies_dep_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_dependencies_dep_id_seq', 1, false);


--
-- Name: task_plans_plan_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_plans_plan_id_seq', 7, true);


--
-- Name: task_steps_step_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_steps_step_id_seq', 1, false);


--
-- Name: task_tool_calls_call_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.task_tool_calls_call_id_seq', 1, false);


--
-- Name: workspace_context_context_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.workspace_context_context_id_seq', 30, true);


--
-- Name: workspaces_workspace_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.workspaces_workspace_id_seq', 41, true);


--
-- Name: agent_collaboration agent_collaboration_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_collaboration
    ADD CONSTRAINT agent_collaboration_pkey PRIMARY KEY (collab_id);


--
-- Name: agent_credentials agent_credentials_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_credentials
    ADD CONSTRAINT agent_credentials_pkey PRIMARY KEY (credential_id);


--
-- Name: agent_permission_log agent_permission_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_permission_log
    ADD CONSTRAINT agent_permission_log_pkey PRIMARY KEY (log_id);


--
-- Name: agent_registry agent_registry_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_registry
    ADD CONSTRAINT agent_registry_pkey PRIMARY KEY (agent_id);


--
-- Name: agent_session pk_agent_session; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_session
    ADD CONSTRAINT pk_agent_session PRIMARY KEY (session_id, is_active);


--
-- Name: agent_session_active agent_session_active_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_session_active
    ADD CONSTRAINT agent_session_active_pkey PRIMARY KEY (session_id, is_active);


--
-- Name: agent_session_inactive agent_session_inactive_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_session_inactive
    ADD CONSTRAINT agent_session_inactive_pkey PRIMARY KEY (session_id, is_active);


--
-- Name: branch_merge_log branch_merge_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branch_merge_log
    ADD CONSTRAINT branch_merge_log_pkey PRIMARY KEY (log_id);


--
-- Name: collab_group_members collab_group_members_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_group_members
    ADD CONSTRAINT collab_group_members_pkey PRIMARY KEY (member_id);


--
-- Name: collab_groups collab_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_groups
    ADD CONSTRAINT collab_groups_pkey PRIMARY KEY (group_id);


--
-- Name: context_branches context_branches_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.context_branches
    ADD CONSTRAINT context_branches_pkey PRIMARY KEY (branch_id);


--
-- Name: entities pk_entities; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities
    ADD CONSTRAINT pk_entities PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_default entities_default_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_default
    ADD CONSTRAINT entities_default_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_experience entities_experience_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_experience
    ADD CONSTRAINT entities_experience_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_harness_template entities_harness_template_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_harness_template
    ADD CONSTRAINT entities_harness_template_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_knowledge entities_knowledge_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_knowledge
    ADD CONSTRAINT entities_knowledge_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_memory entities_memory_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_memory
    ADD CONSTRAINT entities_memory_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_other entities_other_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_other
    ADD CONSTRAINT entities_other_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_skill entities_skill_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_skill
    ADD CONSTRAINT entities_skill_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_spec entities_spec_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_spec
    ADD CONSTRAINT entities_spec_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entities_task_output entities_task_output_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entities_task_output
    ADD CONSTRAINT entities_task_output_pkey PRIMARY KEY (entity_id, entity_type);


--
-- Name: entity_edges entity_edges_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_edges
    ADD CONSTRAINT entity_edges_pkey PRIMARY KEY (edge_id);


--
-- Name: entity_embeddings pk_entity_embeddings; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_embeddings
    ADD CONSTRAINT pk_entity_embeddings PRIMARY KEY (entity_id, entity_type);


--
-- Name: entity_tags pk_entity_tags; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_tags
    ADD CONSTRAINT pk_entity_tags PRIMARY KEY (entity_id, entity_type, tag_id);


--
-- Name: harness_meta pk_harness_meta; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.harness_meta
    ADD CONSTRAINT pk_harness_meta PRIMARY KEY (entity_id, entity_type);


--
-- Name: knowledge_meta pk_knowledge_meta; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.knowledge_meta
    ADD CONSTRAINT pk_knowledge_meta PRIMARY KEY (entity_id, entity_type);


--
-- Name: spec_meta pk_spec_meta; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spec_meta
    ADD CONSTRAINT pk_spec_meta PRIMARY KEY (entity_id, entity_type);


--
-- Name: task_plans pk_task_plans; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans
    ADD CONSTRAINT pk_task_plans PRIMARY KEY (plan_id, status);


--
-- Name: workspace_tasks pk_workspace_tasks; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_tasks
    ADD CONSTRAINT pk_workspace_tasks PRIMARY KEY (workspace_id, plan_id);


--
-- Name: skill_meta skill_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.skill_meta
    ADD CONSTRAINT skill_meta_pkey PRIMARY KEY (skill_id);


--
-- Name: spec_plan_links spec_plan_links_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spec_plan_links
    ADD CONSTRAINT spec_plan_links_pkey PRIMARY KEY (link_id);


--
-- Name: system_config system_config_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_config
    ADD CONSTRAINT system_config_pkey PRIMARY KEY (config_key);


--
-- Name: system_users system_users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_users
    ADD CONSTRAINT system_users_pkey PRIMARY KEY (user_id);


--
-- Name: tags tags_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT tags_pkey PRIMARY KEY (tag_id);


--
-- Name: task_context_snapshots task_context_snapshots_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_context_snapshots
    ADD CONSTRAINT task_context_snapshots_pkey PRIMARY KEY (snapshot_id);


--
-- Name: task_dependencies task_dependencies_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_dependencies
    ADD CONSTRAINT task_dependencies_pkey PRIMARY KEY (dep_id);


--
-- Name: task_plans_active task_plans_active_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans_active
    ADD CONSTRAINT task_plans_active_pkey PRIMARY KEY (plan_id, status);


--
-- Name: task_plans_cancelled task_plans_cancelled_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans_cancelled
    ADD CONSTRAINT task_plans_cancelled_pkey PRIMARY KEY (plan_id, status);


--
-- Name: task_plans_completed task_plans_completed_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans_completed
    ADD CONSTRAINT task_plans_completed_pkey PRIMARY KEY (plan_id, status);


--
-- Name: task_plans_default task_plans_default_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans_default
    ADD CONSTRAINT task_plans_default_pkey PRIMARY KEY (plan_id, status);


--
-- Name: task_plans_paused task_plans_paused_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_plans_paused
    ADD CONSTRAINT task_plans_paused_pkey PRIMARY KEY (plan_id, status);


--
-- Name: task_steps task_steps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_steps
    ADD CONSTRAINT task_steps_pkey PRIMARY KEY (step_id);


--
-- Name: task_tool_calls task_tool_calls_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_tool_calls
    ADD CONSTRAINT task_tool_calls_pkey PRIMARY KEY (call_id);


--
-- Name: collab_group_members uk_cgm_membership; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_group_members
    ADD CONSTRAINT uk_cgm_membership UNIQUE (group_id, agent_id);


--
-- Name: spec_plan_links uk_spl_link; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.spec_plan_links
    ADD CONSTRAINT uk_spl_link UNIQUE (spec_id, plan_id, link_type);


--
-- Name: system_users uk_su_username; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.system_users
    ADD CONSTRAINT uk_su_username UNIQUE (username);


--
-- Name: tags uk_tags_name; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tags
    ADD CONSTRAINT uk_tags_name UNIQUE (tag_name);


--
-- Name: workspace_context workspace_context_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_context
    ADD CONSTRAINT workspace_context_pkey PRIMARY KEY (context_id);


--
-- Name: workspaces workspaces_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspaces
    ADD CONSTRAINT workspaces_pkey PRIMARY KEY (workspace_id);


--
-- Name: idx_as_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_as_agent ON ONLY public.agent_session USING btree (agent_id);


--
-- Name: agent_session_active_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_active_agent_id_idx ON public.agent_session_active USING btree (agent_id);


--
-- Name: idx_as_owner; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_as_owner ON ONLY public.agent_session USING btree (owner_user_id);


--
-- Name: agent_session_active_owner_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_active_owner_user_id_idx ON public.agent_session_active USING btree (owner_user_id);


--
-- Name: idx_as_predecessor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_as_predecessor ON ONLY public.agent_session USING btree (predecessor_session_id);


--
-- Name: agent_session_active_predecessor_session_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_active_predecessor_session_id_idx ON public.agent_session_active USING btree (predecessor_session_id);


--
-- Name: idx_as_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_as_workspace ON ONLY public.agent_session USING btree (workspace_id);


--
-- Name: agent_session_active_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_active_workspace_id_idx ON public.agent_session_active USING btree (workspace_id);


--
-- Name: agent_session_inactive_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_inactive_agent_id_idx ON public.agent_session_inactive USING btree (agent_id);


--
-- Name: agent_session_inactive_owner_user_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_inactive_owner_user_id_idx ON public.agent_session_inactive USING btree (owner_user_id);


--
-- Name: agent_session_inactive_predecessor_session_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_inactive_predecessor_session_id_idx ON public.agent_session_inactive USING btree (predecessor_session_id);


--
-- Name: agent_session_inactive_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX agent_session_inactive_workspace_id_idx ON public.agent_session_inactive USING btree (workspace_id);


--
-- Name: idx_entities_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_category ON ONLY public.entities USING btree (category);


--
-- Name: entities_default_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_category_idx ON public.entities_default USING btree (category);


--
-- Name: idx_entities_owned_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_owned_by ON ONLY public.entities USING btree (owned_by_agent);


--
-- Name: entities_default_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_owned_by_agent_idx ON public.entities_default USING btree (owned_by_agent);


--
-- Name: idx_entities_search; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_search ON ONLY public.entities USING gin (search_vector);


--
-- Name: entities_default_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_search_vector_idx ON public.entities_default USING gin (search_vector);


--
-- Name: idx_entities_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_status ON ONLY public.entities USING btree (status);


--
-- Name: entities_default_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_status_idx ON public.entities_default USING btree (status);


--
-- Name: idx_entities_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_visibility ON ONLY public.entities USING btree (visibility);


--
-- Name: entities_default_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_visibility_idx ON public.entities_default USING btree (visibility);


--
-- Name: idx_entities_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_entities_workspace ON ONLY public.entities USING btree (workspace_id);


--
-- Name: entities_default_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_default_workspace_id_idx ON public.entities_default USING btree (workspace_id);


--
-- Name: entities_experience_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_category_idx ON public.entities_experience USING btree (category);


--
-- Name: entities_experience_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_owned_by_agent_idx ON public.entities_experience USING btree (owned_by_agent);


--
-- Name: entities_experience_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_search_vector_idx ON public.entities_experience USING gin (search_vector);


--
-- Name: entities_experience_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_status_idx ON public.entities_experience USING btree (status);


--
-- Name: entities_experience_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_visibility_idx ON public.entities_experience USING btree (visibility);


--
-- Name: entities_experience_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_experience_workspace_id_idx ON public.entities_experience USING btree (workspace_id);


--
-- Name: entities_harness_template_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_category_idx ON public.entities_harness_template USING btree (category);


--
-- Name: entities_harness_template_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_owned_by_agent_idx ON public.entities_harness_template USING btree (owned_by_agent);


--
-- Name: entities_harness_template_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_search_vector_idx ON public.entities_harness_template USING gin (search_vector);


--
-- Name: entities_harness_template_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_status_idx ON public.entities_harness_template USING btree (status);


--
-- Name: entities_harness_template_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_visibility_idx ON public.entities_harness_template USING btree (visibility);


--
-- Name: entities_harness_template_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_harness_template_workspace_id_idx ON public.entities_harness_template USING btree (workspace_id);


--
-- Name: entities_knowledge_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_category_idx ON public.entities_knowledge USING btree (category);


--
-- Name: entities_knowledge_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_owned_by_agent_idx ON public.entities_knowledge USING btree (owned_by_agent);


--
-- Name: entities_knowledge_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_search_vector_idx ON public.entities_knowledge USING gin (search_vector);


--
-- Name: entities_knowledge_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_status_idx ON public.entities_knowledge USING btree (status);


--
-- Name: entities_knowledge_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_visibility_idx ON public.entities_knowledge USING btree (visibility);


--
-- Name: entities_knowledge_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_knowledge_workspace_id_idx ON public.entities_knowledge USING btree (workspace_id);


--
-- Name: entities_memory_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_category_idx ON public.entities_memory USING btree (category);


--
-- Name: entities_memory_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_owned_by_agent_idx ON public.entities_memory USING btree (owned_by_agent);


--
-- Name: entities_memory_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_search_vector_idx ON public.entities_memory USING gin (search_vector);


--
-- Name: entities_memory_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_status_idx ON public.entities_memory USING btree (status);


--
-- Name: entities_memory_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_visibility_idx ON public.entities_memory USING btree (visibility);


--
-- Name: entities_memory_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_memory_workspace_id_idx ON public.entities_memory USING btree (workspace_id);


--
-- Name: entities_other_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_category_idx ON public.entities_other USING btree (category);


--
-- Name: entities_other_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_owned_by_agent_idx ON public.entities_other USING btree (owned_by_agent);


--
-- Name: entities_other_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_search_vector_idx ON public.entities_other USING gin (search_vector);


--
-- Name: entities_other_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_status_idx ON public.entities_other USING btree (status);


--
-- Name: entities_other_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_visibility_idx ON public.entities_other USING btree (visibility);


--
-- Name: entities_other_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_other_workspace_id_idx ON public.entities_other USING btree (workspace_id);


--
-- Name: entities_skill_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_category_idx ON public.entities_skill USING btree (category);


--
-- Name: entities_skill_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_owned_by_agent_idx ON public.entities_skill USING btree (owned_by_agent);


--
-- Name: entities_skill_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_search_vector_idx ON public.entities_skill USING gin (search_vector);


--
-- Name: entities_skill_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_status_idx ON public.entities_skill USING btree (status);


--
-- Name: entities_skill_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_visibility_idx ON public.entities_skill USING btree (visibility);


--
-- Name: entities_skill_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_skill_workspace_id_idx ON public.entities_skill USING btree (workspace_id);


--
-- Name: entities_spec_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_category_idx ON public.entities_spec USING btree (category);


--
-- Name: entities_spec_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_owned_by_agent_idx ON public.entities_spec USING btree (owned_by_agent);


--
-- Name: entities_spec_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_search_vector_idx ON public.entities_spec USING gin (search_vector);


--
-- Name: entities_spec_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_status_idx ON public.entities_spec USING btree (status);


--
-- Name: entities_spec_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_visibility_idx ON public.entities_spec USING btree (visibility);


--
-- Name: entities_spec_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_spec_workspace_id_idx ON public.entities_spec USING btree (workspace_id);


--
-- Name: entities_task_output_category_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_category_idx ON public.entities_task_output USING btree (category);


--
-- Name: entities_task_output_owned_by_agent_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_owned_by_agent_idx ON public.entities_task_output USING btree (owned_by_agent);


--
-- Name: entities_task_output_search_vector_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_search_vector_idx ON public.entities_task_output USING gin (search_vector);


--
-- Name: entities_task_output_status_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_status_idx ON public.entities_task_output USING btree (status);


--
-- Name: entities_task_output_visibility_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_visibility_idx ON public.entities_task_output USING btree (visibility);


--
-- Name: entities_task_output_workspace_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entities_task_output_workspace_id_idx ON public.entities_task_output USING btree (workspace_id);


--
-- Name: idx_eal_time; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eal_time ON ONLY public.entity_access_log USING btree (access_time);


--
-- Name: entity_access_log_202605_access_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_202605_access_time_idx ON public.entity_access_log_202605 USING btree (access_time);


--
-- Name: idx_eal_entity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_eal_entity ON ONLY public.entity_access_log USING btree (entity_id);


--
-- Name: entity_access_log_202605_entity_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_202605_entity_id_idx ON public.entity_access_log_202605 USING btree (entity_id);


--
-- Name: entity_access_log_202606_access_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_202606_access_time_idx ON public.entity_access_log_202606 USING btree (access_time);


--
-- Name: entity_access_log_202606_entity_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_202606_entity_id_idx ON public.entity_access_log_202606 USING btree (entity_id);


--
-- Name: entity_access_log_max_access_time_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_max_access_time_idx ON public.entity_access_log_max USING btree (access_time);


--
-- Name: entity_access_log_max_entity_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX entity_access_log_max_entity_id_idx ON public.entity_access_log_max USING btree (entity_id);


--
-- Name: idx_ac_active; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ac_active ON public.agent_credentials USING btree (is_active);


--
-- Name: idx_ac_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ac_agent ON public.agent_credentials USING btree (agent_id);


--
-- Name: idx_ac_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ac_user ON public.agent_credentials USING btree (user_id);


--
-- Name: idx_apl_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_apl_agent ON public.agent_permission_log USING btree (agent_id);


--
-- Name: idx_ar_created_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ar_created_by ON public.agent_registry USING btree (created_by_agent_id);


--
-- Name: idx_ar_role; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ar_role ON public.agent_registry USING btree (agent_role);


--
-- Name: idx_ar_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ar_status ON public.agent_registry USING btree (status);


--
-- Name: idx_ar_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ar_type ON public.agent_registry USING btree (agent_type);


--
-- Name: idx_ar_user; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ar_user ON public.agent_registry USING btree (current_user_id);


--
-- Name: idx_bml_src; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bml_src ON public.branch_merge_log USING btree (source_branch_id);


--
-- Name: idx_bml_tgt; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_bml_tgt ON public.branch_merge_log USING btree (target_branch_id);


--
-- Name: idx_cb_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cb_agent ON public.context_branches USING btree (agent_id);


--
-- Name: idx_cb_parent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cb_parent ON public.context_branches USING btree (parent_branch_id);


--
-- Name: idx_cb_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cb_status ON public.context_branches USING btree (status);


--
-- Name: idx_cb_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cb_type ON public.context_branches USING btree (branch_type);


--
-- Name: idx_cb_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cb_workspace ON public.context_branches USING btree (workspace_id);


--
-- Name: idx_cg_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cg_status ON public.collab_groups USING btree (status);


--
-- Name: idx_cg_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cg_type ON public.collab_groups USING btree (group_type);


--
-- Name: idx_cg_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cg_workspace ON public.collab_groups USING btree (workspace_id);


--
-- Name: idx_cgm_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cgm_agent ON public.collab_group_members USING btree (agent_id);


--
-- Name: idx_cgm_group; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_cgm_group ON public.collab_group_members USING btree (group_id);


--
-- Name: idx_col_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_col_source ON public.agent_collaboration USING btree (source_agent_id);


--
-- Name: idx_col_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_col_target ON public.agent_collaboration USING btree (target_agent_id);


--
-- Name: idx_edges_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_edges_target ON public.entity_edges USING btree (target_id);


--
-- Name: idx_edges_target_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_edges_target_type ON public.entity_edges USING btree (target_id, edge_type);


--
-- Name: idx_edges_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_edges_type ON public.entity_edges USING btree (edge_type);


--
-- Name: idx_ee_embedding; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ee_embedding ON public.entity_embeddings USING hnsw (embedding public.vector_cosine_ops);


--
-- Name: idx_ee_model; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ee_model ON public.entity_embeddings USING btree (embedding_model);


--
-- Name: idx_et_tag; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_et_tag ON public.entity_tags USING btree (tag_id);


--
-- Name: idx_hm_exec_mode; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_hm_exec_mode ON public.harness_meta USING btree (execution_mode);


--
-- Name: idx_km_difficulty; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_km_difficulty ON public.knowledge_meta USING btree (difficulty);


--
-- Name: idx_km_domain; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_km_domain ON public.knowledge_meta USING btree (domain);


--
-- Name: idx_km_next_review; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_km_next_review ON public.knowledge_meta USING btree (next_review) WHERE (next_review IS NOT NULL);


--
-- Name: idx_km_topic; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_km_topic ON public.knowledge_meta USING btree (topic);


--
-- Name: idx_skm_name; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_skm_name ON public.skill_meta USING btree (skill_name);


--
-- Name: idx_skm_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_skm_status ON public.skill_meta USING btree (status);


--
-- Name: idx_skm_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_skm_type ON public.skill_meta USING btree (skill_type);


--
-- Name: idx_sm_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sm_branch ON public.spec_meta USING btree (branch_id) WHERE (branch_id IS NOT NULL);


--
-- Name: idx_sm_complexity; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sm_complexity ON public.spec_meta USING btree (complexity);


--
-- Name: idx_sm_scope; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sm_scope ON public.spec_meta USING btree (spec_scope) WHERE (spec_scope IS NOT NULL);


--
-- Name: idx_sm_spec_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_sm_spec_status ON public.spec_meta USING btree (spec_status);


--
-- Name: idx_spl_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_spl_plan ON public.spec_plan_links USING btree (plan_id);


--
-- Name: idx_spl_spec; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_spl_spec ON public.spec_plan_links USING btree (spec_id);


--
-- Name: idx_tcs_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tcs_plan ON public.task_context_snapshots USING btree (plan_id);


--
-- Name: idx_td_source; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_td_source ON public.task_dependencies USING btree (source_plan_id);


--
-- Name: idx_td_target; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_td_target ON public.task_dependencies USING btree (target_plan_id);


--
-- Name: idx_tp_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tp_agent ON ONLY public.task_plans USING btree (agent_id);


--
-- Name: idx_tp_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_tp_branch ON ONLY public.task_plans USING btree (branch_id);


--
-- Name: idx_ts_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ts_plan ON public.task_steps USING btree (plan_id);


--
-- Name: idx_ttc_plan; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ttc_plan ON public.task_tool_calls USING btree (plan_id);


--
-- Name: idx_ttc_step; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ttc_step ON public.task_tool_calls USING btree (step_id);


--
-- Name: idx_wc_agent; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wc_agent ON public.workspace_context USING btree (agent_id);


--
-- Name: idx_wc_branch; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wc_branch ON public.workspace_context USING btree (branch_id);


--
-- Name: idx_wc_type; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wc_type ON public.workspace_context USING btree (context_type);


--
-- Name: idx_wc_visibility; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wc_visibility ON public.workspace_context USING btree (visibility);


--
-- Name: idx_wc_workspace; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_wc_workspace ON public.workspace_context USING btree (workspace_id);


--
-- Name: idx_ws_alias; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ws_alias ON public.workspaces USING btree (workspace_alias);


--
-- Name: idx_ws_owner; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ws_owner ON public.workspaces USING btree (owner_user_id);


--
-- Name: idx_ws_status; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_ws_status ON public.workspaces USING btree (status);


--
-- Name: task_plans_active_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_active_agent_id_idx ON public.task_plans_active USING btree (agent_id);


--
-- Name: task_plans_active_branch_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_active_branch_id_idx ON public.task_plans_active USING btree (branch_id);


--
-- Name: task_plans_cancelled_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_cancelled_agent_id_idx ON public.task_plans_cancelled USING btree (agent_id);


--
-- Name: task_plans_cancelled_branch_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_cancelled_branch_id_idx ON public.task_plans_cancelled USING btree (branch_id);


--
-- Name: task_plans_completed_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_completed_agent_id_idx ON public.task_plans_completed USING btree (agent_id);


--
-- Name: task_plans_completed_branch_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_completed_branch_id_idx ON public.task_plans_completed USING btree (branch_id);


--
-- Name: task_plans_default_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_default_agent_id_idx ON public.task_plans_default USING btree (agent_id);


--
-- Name: task_plans_default_branch_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_default_branch_id_idx ON public.task_plans_default USING btree (branch_id);


--
-- Name: task_plans_paused_agent_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_paused_agent_id_idx ON public.task_plans_paused USING btree (agent_id);


--
-- Name: task_plans_paused_branch_id_idx; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX task_plans_paused_branch_id_idx ON public.task_plans_paused USING btree (branch_id);


--
-- Name: agent_session_active_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_agent ATTACH PARTITION public.agent_session_active_agent_id_idx;


--
-- Name: agent_session_active_owner_user_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_owner ATTACH PARTITION public.agent_session_active_owner_user_id_idx;


--
-- Name: agent_session_active_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_agent_session ATTACH PARTITION public.agent_session_active_pkey;


--
-- Name: agent_session_active_predecessor_session_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_predecessor ATTACH PARTITION public.agent_session_active_predecessor_session_id_idx;


--
-- Name: agent_session_active_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_workspace ATTACH PARTITION public.agent_session_active_workspace_id_idx;


--
-- Name: agent_session_inactive_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_agent ATTACH PARTITION public.agent_session_inactive_agent_id_idx;


--
-- Name: agent_session_inactive_owner_user_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_owner ATTACH PARTITION public.agent_session_inactive_owner_user_id_idx;


--
-- Name: agent_session_inactive_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_agent_session ATTACH PARTITION public.agent_session_inactive_pkey;


--
-- Name: agent_session_inactive_predecessor_session_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_predecessor ATTACH PARTITION public.agent_session_inactive_predecessor_session_id_idx;


--
-- Name: agent_session_inactive_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_as_workspace ATTACH PARTITION public.agent_session_inactive_workspace_id_idx;


--
-- Name: entities_default_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_default_category_idx;


--
-- Name: entities_default_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_default_owned_by_agent_idx;


--
-- Name: entities_default_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_default_pkey;


--
-- Name: entities_default_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_default_search_vector_idx;


--
-- Name: entities_default_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_default_status_idx;


--
-- Name: entities_default_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_default_visibility_idx;


--
-- Name: entities_default_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_default_workspace_id_idx;


--
-- Name: entities_experience_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_experience_category_idx;


--
-- Name: entities_experience_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_experience_owned_by_agent_idx;


--
-- Name: entities_experience_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_experience_pkey;


--
-- Name: entities_experience_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_experience_search_vector_idx;


--
-- Name: entities_experience_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_experience_status_idx;


--
-- Name: entities_experience_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_experience_visibility_idx;


--
-- Name: entities_experience_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_experience_workspace_id_idx;


--
-- Name: entities_harness_template_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_harness_template_category_idx;


--
-- Name: entities_harness_template_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_harness_template_owned_by_agent_idx;


--
-- Name: entities_harness_template_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_harness_template_pkey;


--
-- Name: entities_harness_template_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_harness_template_search_vector_idx;


--
-- Name: entities_harness_template_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_harness_template_status_idx;


--
-- Name: entities_harness_template_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_harness_template_visibility_idx;


--
-- Name: entities_harness_template_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_harness_template_workspace_id_idx;


--
-- Name: entities_knowledge_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_knowledge_category_idx;


--
-- Name: entities_knowledge_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_knowledge_owned_by_agent_idx;


--
-- Name: entities_knowledge_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_knowledge_pkey;


--
-- Name: entities_knowledge_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_knowledge_search_vector_idx;


--
-- Name: entities_knowledge_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_knowledge_status_idx;


--
-- Name: entities_knowledge_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_knowledge_visibility_idx;


--
-- Name: entities_knowledge_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_knowledge_workspace_id_idx;


--
-- Name: entities_memory_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_memory_category_idx;


--
-- Name: entities_memory_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_memory_owned_by_agent_idx;


--
-- Name: entities_memory_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_memory_pkey;


--
-- Name: entities_memory_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_memory_search_vector_idx;


--
-- Name: entities_memory_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_memory_status_idx;


--
-- Name: entities_memory_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_memory_visibility_idx;


--
-- Name: entities_memory_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_memory_workspace_id_idx;


--
-- Name: entities_other_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_other_category_idx;


--
-- Name: entities_other_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_other_owned_by_agent_idx;


--
-- Name: entities_other_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_other_pkey;


--
-- Name: entities_other_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_other_search_vector_idx;


--
-- Name: entities_other_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_other_status_idx;


--
-- Name: entities_other_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_other_visibility_idx;


--
-- Name: entities_other_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_other_workspace_id_idx;


--
-- Name: entities_skill_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_skill_category_idx;


--
-- Name: entities_skill_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_skill_owned_by_agent_idx;


--
-- Name: entities_skill_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_skill_pkey;


--
-- Name: entities_skill_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_skill_search_vector_idx;


--
-- Name: entities_skill_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_skill_status_idx;


--
-- Name: entities_skill_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_skill_visibility_idx;


--
-- Name: entities_skill_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_skill_workspace_id_idx;


--
-- Name: entities_spec_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_spec_category_idx;


--
-- Name: entities_spec_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_spec_owned_by_agent_idx;


--
-- Name: entities_spec_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_spec_pkey;


--
-- Name: entities_spec_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_spec_search_vector_idx;


--
-- Name: entities_spec_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_spec_status_idx;


--
-- Name: entities_spec_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_spec_visibility_idx;


--
-- Name: entities_spec_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_spec_workspace_id_idx;


--
-- Name: entities_task_output_category_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_category ATTACH PARTITION public.entities_task_output_category_idx;


--
-- Name: entities_task_output_owned_by_agent_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_owned_by ATTACH PARTITION public.entities_task_output_owned_by_agent_idx;


--
-- Name: entities_task_output_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_entities ATTACH PARTITION public.entities_task_output_pkey;


--
-- Name: entities_task_output_search_vector_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_search ATTACH PARTITION public.entities_task_output_search_vector_idx;


--
-- Name: entities_task_output_status_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_status ATTACH PARTITION public.entities_task_output_status_idx;


--
-- Name: entities_task_output_visibility_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_visibility ATTACH PARTITION public.entities_task_output_visibility_idx;


--
-- Name: entities_task_output_workspace_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_entities_workspace ATTACH PARTITION public.entities_task_output_workspace_id_idx;


--
-- Name: entity_access_log_202605_access_time_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_time ATTACH PARTITION public.entity_access_log_202605_access_time_idx;


--
-- Name: entity_access_log_202605_entity_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_entity ATTACH PARTITION public.entity_access_log_202605_entity_id_idx;


--
-- Name: entity_access_log_202606_access_time_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_time ATTACH PARTITION public.entity_access_log_202606_access_time_idx;


--
-- Name: entity_access_log_202606_entity_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_entity ATTACH PARTITION public.entity_access_log_202606_entity_id_idx;


--
-- Name: entity_access_log_max_access_time_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_time ATTACH PARTITION public.entity_access_log_max_access_time_idx;


--
-- Name: entity_access_log_max_entity_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_eal_entity ATTACH PARTITION public.entity_access_log_max_entity_id_idx;


--
-- Name: task_plans_active_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_agent ATTACH PARTITION public.task_plans_active_agent_id_idx;


--
-- Name: task_plans_active_branch_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_branch ATTACH PARTITION public.task_plans_active_branch_id_idx;


--
-- Name: task_plans_active_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_task_plans ATTACH PARTITION public.task_plans_active_pkey;


--
-- Name: task_plans_cancelled_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_agent ATTACH PARTITION public.task_plans_cancelled_agent_id_idx;


--
-- Name: task_plans_cancelled_branch_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_branch ATTACH PARTITION public.task_plans_cancelled_branch_id_idx;


--
-- Name: task_plans_cancelled_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_task_plans ATTACH PARTITION public.task_plans_cancelled_pkey;


--
-- Name: task_plans_completed_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_agent ATTACH PARTITION public.task_plans_completed_agent_id_idx;


--
-- Name: task_plans_completed_branch_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_branch ATTACH PARTITION public.task_plans_completed_branch_id_idx;


--
-- Name: task_plans_completed_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_task_plans ATTACH PARTITION public.task_plans_completed_pkey;


--
-- Name: task_plans_default_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_agent ATTACH PARTITION public.task_plans_default_agent_id_idx;


--
-- Name: task_plans_default_branch_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_branch ATTACH PARTITION public.task_plans_default_branch_id_idx;


--
-- Name: task_plans_default_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_task_plans ATTACH PARTITION public.task_plans_default_pkey;


--
-- Name: task_plans_paused_agent_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_agent ATTACH PARTITION public.task_plans_paused_agent_id_idx;


--
-- Name: task_plans_paused_branch_id_idx; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.idx_tp_branch ATTACH PARTITION public.task_plans_paused_branch_id_idx;


--
-- Name: task_plans_paused_pkey; Type: INDEX ATTACH; Schema: public; Owner: -
--

ALTER INDEX public.pk_task_plans ATTACH PARTITION public.task_plans_paused_pkey;


--
-- Name: agent_registry trg_agent_registry_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_agent_registry_updated_at BEFORE UPDATE ON public.agent_registry FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: collab_groups trg_collab_groups_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_collab_groups_updated_at BEFORE UPDATE ON public.collab_groups FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: entities trg_entities_search_vector; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_entities_search_vector BEFORE INSERT OR UPDATE OF title, summary, content ON public.entities FOR EACH ROW EXECUTE FUNCTION public.entities_search_vector_update();


--
-- Name: skill_meta trg_skill_meta_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_skill_meta_updated_at BEFORE UPDATE ON public.skill_meta FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: system_config trg_system_config_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_system_config_updated_at BEFORE UPDATE ON public.system_config FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: system_users trg_system_users_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_system_users_updated_at BEFORE UPDATE ON public.system_users FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: task_plans trg_task_plans_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_task_plans_updated_at BEFORE UPDATE ON public.task_plans FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: workspaces trg_workspaces_updated_at; Type: TRIGGER; Schema: public; Owner: -
--

CREATE TRIGGER trg_workspaces_updated_at BEFORE UPDATE ON public.workspaces FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();


--
-- Name: agent_credentials fk_ac_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_credentials
    ADD CONSTRAINT fk_ac_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: agent_registry fk_ar_created_by; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_registry
    ADD CONSTRAINT fk_ar_created_by FOREIGN KEY (created_by_agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: branch_merge_log fk_bml_src; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branch_merge_log
    ADD CONSTRAINT fk_bml_src FOREIGN KEY (source_branch_id) REFERENCES public.context_branches(branch_id);


--
-- Name: branch_merge_log fk_bml_tgt; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.branch_merge_log
    ADD CONSTRAINT fk_bml_tgt FOREIGN KEY (target_branch_id) REFERENCES public.context_branches(branch_id);


--
-- Name: context_branches fk_cb_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.context_branches
    ADD CONSTRAINT fk_cb_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: context_branches fk_cb_parent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.context_branches
    ADD CONSTRAINT fk_cb_parent FOREIGN KEY (parent_branch_id) REFERENCES public.context_branches(branch_id) ON DELETE SET NULL;


--
-- Name: context_branches fk_cb_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.context_branches
    ADD CONSTRAINT fk_cb_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;


--
-- Name: collab_groups fk_cg_branch; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_groups
    ADD CONSTRAINT fk_cg_branch FOREIGN KEY (branch_id) REFERENCES public.context_branches(branch_id) ON DELETE SET NULL;


--
-- Name: collab_groups fk_cg_coordinator; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_groups
    ADD CONSTRAINT fk_cg_coordinator FOREIGN KEY (coordinator_agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: collab_groups fk_cg_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_groups
    ADD CONSTRAINT fk_cg_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id);


--
-- Name: collab_group_members fk_cgm_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_group_members
    ADD CONSTRAINT fk_cgm_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: collab_group_members fk_cgm_group; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_group_members
    ADD CONSTRAINT fk_cgm_group FOREIGN KEY (group_id) REFERENCES public.collab_groups(group_id) ON DELETE CASCADE;


--
-- Name: collab_group_members fk_cgm_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.collab_group_members
    ADD CONSTRAINT fk_cgm_workspace FOREIGN KEY (personal_workspace_id) REFERENCES public.workspaces(workspace_id);


--
-- Name: agent_collaboration fk_col_source; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_collaboration
    ADD CONSTRAINT fk_col_source FOREIGN KEY (source_agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: agent_collaboration fk_col_target; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agent_collaboration
    ADD CONSTRAINT fk_col_target FOREIGN KEY (target_agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: entity_access_log fk_eal_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.entity_access_log
    ADD CONSTRAINT fk_eal_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: entity_edges fk_edge_source; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_edges
    ADD CONSTRAINT fk_edge_source FOREIGN KEY (source_id, source_type) REFERENCES public.entities(entity_id, entity_type) ON DELETE CASCADE;


--
-- Name: entity_embeddings fk_ee_entity; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_embeddings
    ADD CONSTRAINT fk_ee_entity FOREIGN KEY (entity_id, entity_type) REFERENCES public.entities(entity_id, entity_type) ON DELETE CASCADE;


--
-- Name: entities fk_entities_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.entities
    ADD CONSTRAINT fk_entities_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id);


--
-- Name: entity_tags fk_et_entity; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_tags
    ADD CONSTRAINT fk_et_entity FOREIGN KEY (entity_id, entity_type) REFERENCES public.entities(entity_id, entity_type) ON DELETE CASCADE;


--
-- Name: entity_tags fk_et_tag; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.entity_tags
    ADD CONSTRAINT fk_et_tag FOREIGN KEY (tag_id) REFERENCES public.tags(tag_id);


--
-- Name: knowledge_meta fk_km_entity; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.knowledge_meta
    ADD CONSTRAINT fk_km_entity FOREIGN KEY (entity_id, entity_type) REFERENCES public.entities(entity_id, entity_type) ON DELETE CASCADE;


--
-- Name: agent_session fk_session_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.agent_session
    ADD CONSTRAINT fk_session_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: agent_session fk_session_branch; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.agent_session
    ADD CONSTRAINT fk_session_branch FOREIGN KEY (branch_id) REFERENCES public.context_branches(branch_id) ON DELETE SET NULL;


--
-- Name: agent_session fk_session_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.agent_session
    ADD CONSTRAINT fk_session_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id);


--
-- Name: task_steps fk_step_plan; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.task_steps
    ADD CONSTRAINT fk_step_plan FOREIGN KEY (plan_id, plan_status) REFERENCES public.task_plans(plan_id, status);


--
-- Name: task_plans fk_tp_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.task_plans
    ADD CONSTRAINT fk_tp_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: task_plans fk_tp_branch; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE public.task_plans
    ADD CONSTRAINT fk_tp_branch FOREIGN KEY (branch_id) REFERENCES public.context_branches(branch_id) ON DELETE SET NULL;


--
-- Name: workspace_context fk_wc_agent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_context
    ADD CONSTRAINT fk_wc_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id);


--
-- Name: workspace_context fk_wc_branch; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_context
    ADD CONSTRAINT fk_wc_branch FOREIGN KEY (branch_id) REFERENCES public.context_branches(branch_id) ON DELETE SET NULL;


--
-- Name: workspace_context fk_wc_parent; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_context
    ADD CONSTRAINT fk_wc_parent FOREIGN KEY (parent_context_id) REFERENCES public.workspace_context(context_id) ON DELETE SET NULL;


--
-- Name: workspace_context fk_wc_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_context
    ADD CONSTRAINT fk_wc_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;


--
-- Name: workspace_tasks fk_wt_workspace; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.workspace_tasks
    ADD CONSTRAINT fk_wt_workspace FOREIGN KEY (workspace_id) REFERENCES public.workspaces(workspace_id) ON DELETE CASCADE;


--
-- Name: agent_credentials ac_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY ac_agent_isolation ON public.agent_credentials USING (((agent_id)::text = current_setting('app.current_agent_id'::text, true)));


--
-- Name: agent_collaboration; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_collaboration ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_credentials; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_credentials ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_permission_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_permission_log ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_session; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.agent_session ENABLE ROW LEVEL SECURITY;

--
-- Name: agent_permission_log apl_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY apl_agent_isolation ON public.agent_permission_log USING ((((agent_id)::text = current_setting('app.current_agent_id'::text, true)) OR (EXISTS ( SELECT 1
   FROM public.agent_registry ar
  WHERE (((ar.agent_id)::text = current_setting('app.current_agent_id'::text, true)) AND ((ar.agent_role)::text = 'COORDINATOR'::text))))));


--
-- Name: agent_session as_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY as_agent_isolation ON public.agent_session USING ((((agent_id)::text = current_setting('app.current_agent_id'::text, true)) OR (EXISTS ( SELECT 1
   FROM public.agent_registry ar
  WHERE (((ar.agent_id)::text = current_setting('app.current_agent_id'::text, true)) AND ((ar.agent_role)::text = 'COORDINATOR'::text))))));


--
-- Name: branch_merge_log bml_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY bml_agent_isolation ON public.branch_merge_log USING ((EXISTS ( SELECT 1
   FROM public.context_branches b
  WHERE ((b.branch_id = ANY (ARRAY[branch_merge_log.source_branch_id, branch_merge_log.target_branch_id])) AND (EXISTS ( SELECT 1
           FROM public.workspaces w
          WHERE ((w.workspace_id = b.workspace_id) AND (((w.isolation_mode)::text = 'SHARED'::text) OR ((w.current_agent_id)::text = current_setting('app.current_agent_id'::text, true))))))))));


--
-- Name: branch_merge_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.branch_merge_log ENABLE ROW LEVEL SECURITY;

--
-- Name: context_branches cb_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY cb_agent_isolation ON public.context_branches USING ((EXISTS ( SELECT 1
   FROM public.workspaces w
  WHERE ((w.workspace_id = context_branches.workspace_id) AND (((w.isolation_mode)::text = 'SHARED'::text) OR ((w.current_agent_id)::text = current_setting('app.current_agent_id'::text, true)))))));


--
-- Name: agent_collaboration col_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY col_agent_isolation ON public.agent_collaboration USING ((((source_agent_id)::text = current_setting('app.current_agent_id'::text, true)) OR ((target_agent_id)::text = current_setting('app.current_agent_id'::text, true))));


--
-- Name: collab_group_members; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collab_group_members ENABLE ROW LEVEL SECURITY;

--
-- Name: collab_groups; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.collab_groups ENABLE ROW LEVEL SECURITY;

--
-- Name: context_branches; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.context_branches ENABLE ROW LEVEL SECURITY;

--
-- Name: entity_access_log eal_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY eal_agent_isolation ON public.entity_access_log USING ((((agent_id)::text = current_setting('app.current_agent_id'::text, true)) OR (EXISTS ( SELECT 1
   FROM public.agent_registry ar
  WHERE (((ar.agent_id)::text = current_setting('app.current_agent_id'::text, true)) AND ((ar.agent_role)::text = 'COORDINATOR'::text))))));


--
-- Name: entity_edges edges_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY edges_agent_isolation ON public.entity_edges USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = entity_edges.source_id) AND ((e.entity_type)::text = (entity_edges.source_type)::text) AND (((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((e.visibility)::text = 'PRIVATE'::text) AND ((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true))))))));


--
-- Name: entity_embeddings ee_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY ee_agent_isolation ON public.entity_embeddings USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = entity_embeddings.entity_id) AND ((e.entity_type)::text = (entity_embeddings.entity_type)::text) AND (((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((e.visibility)::text = 'PRIVATE'::text) AND ((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true))))))));


--
-- Name: entities; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.entities ENABLE ROW LEVEL SECURITY;

--
-- Name: entities entities_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY entities_agent_isolation ON public.entities USING ((((visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((visibility)::text = 'PRIVATE'::text) AND ((owned_by_agent)::text = current_setting('app.current_agent_id'::text, true)))));


--
-- Name: entity_access_log; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.entity_access_log ENABLE ROW LEVEL SECURITY;

--
-- Name: entity_edges; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.entity_edges ENABLE ROW LEVEL SECURITY;

--
-- Name: entity_embeddings; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.entity_embeddings ENABLE ROW LEVEL SECURITY;

--
-- Name: entity_tags; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.entity_tags ENABLE ROW LEVEL SECURITY;

--
-- Name: entity_tags et_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY et_agent_isolation ON public.entity_tags USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = entity_tags.entity_id) AND ((e.entity_type)::text = (entity_tags.entity_type)::text) AND (((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((e.visibility)::text = 'PRIVATE'::text) AND ((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true))))))));


--
-- Name: harness_meta; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.harness_meta ENABLE ROW LEVEL SECURITY;

--
-- Name: harness_meta harness_meta_aiadmin; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY harness_meta_aiadmin ON public.harness_meta TO pgsql USING (true) WITH CHECK (true);


--
-- Name: harness_meta harness_meta_end_user; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY harness_meta_end_user ON public.harness_meta USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = harness_meta.entity_id) AND ((e.entity_type)::text = (harness_meta.entity_type)::text) AND (((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true)) OR ((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])))))));


--
-- Name: knowledge_meta; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.knowledge_meta ENABLE ROW LEVEL SECURITY;

--
-- Name: knowledge_meta knowledge_meta_aiadmin; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY knowledge_meta_aiadmin ON public.knowledge_meta TO pgsql USING (true) WITH CHECK (true);


--
-- Name: knowledge_meta knowledge_meta_end_user; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY knowledge_meta_end_user ON public.knowledge_meta USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = knowledge_meta.entity_id) AND ((e.entity_type)::text = (knowledge_meta.entity_type)::text) AND (((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true)) OR ((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])))))));


--
-- Name: skill_meta; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.skill_meta ENABLE ROW LEVEL SECURITY;

--
-- Name: skill_meta skm_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY skm_agent_isolation ON public.skill_meta USING ((((visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((visibility)::text = 'PRIVATE'::text) AND ((owned_by_agent)::text = current_setting('app.current_agent_id'::text, true)))));


--
-- Name: spec_meta; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.spec_meta ENABLE ROW LEVEL SECURITY;

--
-- Name: spec_meta spec_meta_aiadmin; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY spec_meta_aiadmin ON public.spec_meta TO pgsql USING (true) WITH CHECK (true);


--
-- Name: spec_meta spec_meta_end_user; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY spec_meta_end_user ON public.spec_meta USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = spec_meta.entity_id) AND ((e.entity_type)::text = (spec_meta.entity_type)::text) AND (((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true)) OR ((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])))))));


--
-- Name: spec_plan_links; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.spec_plan_links ENABLE ROW LEVEL SECURITY;

--
-- Name: spec_plan_links spl_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY spl_agent_isolation ON public.spec_plan_links USING ((EXISTS ( SELECT 1
   FROM public.entities e
  WHERE ((e.entity_id = spec_plan_links.spec_id) AND (((e.visibility)::text = ANY ((ARRAY['SHARED'::character varying, 'PUBLIC'::character varying])::text[])) OR (((e.visibility)::text = 'PRIVATE'::text) AND ((e.owned_by_agent)::text = current_setting('app.current_agent_id'::text, true))))))));


--
-- Name: task_plans; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.task_plans ENABLE ROW LEVEL SECURITY;

--
-- Name: task_steps; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.task_steps ENABLE ROW LEVEL SECURITY;

--
-- Name: workspace_context wc_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY wc_agent_isolation ON public.workspace_context USING ((EXISTS ( SELECT 1
   FROM public.workspaces w
  WHERE ((w.workspace_id = workspace_context.workspace_id) AND (((w.isolation_mode)::text = 'SHARED'::text) OR ((w.current_agent_id)::text = current_setting('app.current_agent_id'::text, true)))))));


--
-- Name: workspace_context; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.workspace_context ENABLE ROW LEVEL SECURITY;

--
-- Name: workspace_tasks; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.workspace_tasks ENABLE ROW LEVEL SECURITY;

--
-- Name: workspaces; Type: ROW SECURITY; Schema: public; Owner: -
--

ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;

--
-- Name: workspaces ws_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY ws_agent_isolation ON public.workspaces USING ((((isolation_mode)::text = 'SHARED'::text) OR ((owner_user_id)::text = current_setting('app.current_agent_id'::text, true)) OR ((current_agent_id)::text = current_setting('app.current_agent_id'::text, true))));


--
-- Name: workspace_tasks wt_agent_isolation; Type: POLICY; Schema: public; Owner: -
--

CREATE POLICY wt_agent_isolation ON public.workspace_tasks USING ((EXISTS ( SELECT 1
   FROM public.workspaces w
  WHERE ((w.workspace_id = workspace_tasks.workspace_id) AND (((w.isolation_mode)::text = 'SHARED'::text) OR ((w.current_agent_id)::text = current_setting('app.current_agent_id'::text, true)))))));


--


-- ============================================================================
-- Loop Engineering Tables [NEW v3.7.5]
-- ============================================================================

-- Add LOOP_DEFINITION to entities type constraint
ALTER TABLE public.entities DROP CONSTRAINT IF EXISTS ck_entities_type;
ALTER TABLE public.entities ADD CONSTRAINT ck_entities_type
    CHECK (entity_type IN ('MEMORY','KNOWLEDGE','TASK_OUTPUT','EXPERIENCE','HARNESS_TEMPLATE','SPEC','SKILL','LOOP_DEFINITION','OTHER'));

-- 24. loop_meta (sidecar to entities, like harness_meta)
CREATE TABLE IF NOT EXISTS public.loop_meta (
    entity_id           BIGINT       NOT NULL,
    entity_type         VARCHAR(32)  DEFAULT 'LOOP_DEFINITION' NOT NULL,
    loop_version        VARCHAR(32)  DEFAULT '1.0' NOT NULL,
    goal_definition     JSONB        NOT NULL,
    stop_conditions     JSONB        NOT NULL,
    evaluation_config   JSONB        NOT NULL,
    trigger_config      JSONB,
    harness_template_id BIGINT,
    workspace_id        BIGINT,
    branch_id           BIGINT,
    spec_id             BIGINT,
    parent_loop_id      BIGINT,
    collab_group_id     BIGINT,
    CONSTRAINT pk_loop_meta PRIMARY KEY (entity_id, entity_type),
    CONSTRAINT fk_lm_entity FOREIGN KEY (entity_id, entity_type) REFERENCES public.entities(entity_id, entity_type) ON DELETE CASCADE,
    CONSTRAINT fk_lm_collab FOREIGN KEY (collab_group_id) REFERENCES public.collab_groups(group_id),
    CONSTRAINT ck_lm_entity_type CHECK (entity_type = 'LOOP_DEFINITION')
);

-- 25. loop_runs (partitioned by LIST(status) like task_plans)
CREATE TABLE IF NOT EXISTS public.loop_runs (
    run_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    loop_id          BIGINT       NOT NULL,
    agent_id         VARCHAR(64)  NOT NULL,
    trigger_type     VARCHAR(32)  DEFAULT 'MANUAL' NOT NULL,
    trigger_source   VARCHAR(256),
    status           VARCHAR(30)  DEFAULT 'PENDING' NOT NULL,
    iteration_count  INTEGER      DEFAULT 0 NOT NULL,
    total_tokens     BIGINT       DEFAULT 0 NOT NULL,
    final_result     VARCHAR(4000),
    error_message    VARCHAR(2000),
    parent_run_id    BIGINT,
    started_at       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at     TIMESTAMP,
    CONSTRAINT fk_lr_agent FOREIGN KEY (agent_id) REFERENCES public.agent_registry(agent_id),
    CONSTRAINT fk_lr_parent_run FOREIGN KEY (parent_run_id) REFERENCES public.loop_runs(run_id),
    CONSTRAINT ck_lr_status CHECK (status IN ('PENDING','RUNNING','PAUSED','COMPLETED','STOPPED','FAILED','TIMEOUT')),
    CONSTRAINT ck_lr_trigger CHECK (trigger_type IN ('MANUAL','SCHEDULE','EVENT','HOOK'))
);

CREATE INDEX IF NOT EXISTS idx_lr_loop ON public.loop_runs(loop_id);
CREATE INDEX IF NOT EXISTS idx_lr_agent ON public.loop_runs(agent_id);
CREATE INDEX IF NOT EXISTS idx_lr_status ON public.loop_runs(status);
CREATE INDEX IF NOT EXISTS idx_lr_parent_run ON public.loop_runs(parent_run_id);

-- 26. loop_iterations (FK to loop_runs, like task_steps to task_plans)
CREATE TABLE IF NOT EXISTS public.loop_iterations (
    iteration_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    run_id             BIGINT       NOT NULL,
    iteration_order    INTEGER      NOT NULL,
    plan_data          JSONB,
    actions            JSONB,
    observations       JSONB,
    evaluation_result  JSONB,
    evaluation_passed  VARCHAR(1)   DEFAULT 'N' NOT NULL,
    adjustment         JSONB,
    token_usage        BIGINT       DEFAULT 0 NOT NULL,
    started_at         TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    completed_at       TIMESTAMP,
    CONSTRAINT fk_li_run FOREIGN KEY (run_id) REFERENCES public.loop_runs(run_id) ON DELETE CASCADE,
    CONSTRAINT ck_li_passed CHECK (evaluation_passed IN ('Y','N'))
);

CREATE INDEX IF NOT EXISTS idx_li_run ON public.loop_iterations(run_id);
CREATE INDEX IF NOT EXISTS idx_li_order ON public.loop_iterations(iteration_order);

-- 27. loop_hooks (non-partitioned, like context_branches)
CREATE TABLE IF NOT EXISTS public.loop_hooks (
    hook_id     BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    loop_id     BIGINT       NOT NULL,
    hook_event  VARCHAR(32)  NOT NULL,
    hook_type   VARCHAR(32)  NOT NULL,
    hook_config JSONB,
    priority    INTEGER      DEFAULT 5 NOT NULL,
    enabled     VARCHAR(1)   DEFAULT 'Y' NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT ck_lh_event CHECK (hook_event IN ('PRE_RUN','POST_ITERATION','ON_STOP','ON_FAIL','ON_TIMEOUT','ON_START')),
    CONSTRAINT ck_lh_type CHECK (hook_type IN ('WEBHOOK','SCRIPT','NOTIFICATION','LOG','MCP_CALL')),
    CONSTRAINT ck_lh_enabled CHECK (enabled IN ('Y','N')),
    CONSTRAINT ck_lh_priority CHECK (priority BETWEEN 1 AND 10)
);

CREATE INDEX IF NOT EXISTS idx_lh_loop ON public.loop_hooks(loop_id);

-- 27b. task_loop_binding
CREATE TABLE IF NOT EXISTS public.task_loop_binding (
    binding_id BIGSERIAL PRIMARY KEY,
    step_id BIGINT NOT NULL REFERENCES public.task_steps(step_id),
    loop_id BIGINT NOT NULL,
    binding_type VARCHAR(20) DEFAULT 'COMPLETION',
    auto_start VARCHAR(1) DEFAULT 'N',
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT ck_tlb_type CHECK (binding_type IN ('COMPLETION','VALIDATION')),
    CONSTRAINT ck_tlb_auto CHECK (auto_start IN ('Y','N'))
);

CREATE INDEX IF NOT EXISTS idx_tlb_step ON public.task_loop_binding(step_id);
CREATE INDEX IF NOT EXISTS idx_tlb_loop ON public.task_loop_binding(loop_id);

-- RLS Policies for Loop tables
ALTER TABLE public.loop_meta ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.loop_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.loop_iterations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.loop_hooks ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS lm_agent_isolation ON public.loop_meta;
CREATE POLICY lm_agent_isolation ON public.loop_meta
    USING (EXISTS (
        SELECT 1 FROM public.entities e
        WHERE e.entity_id = loop_meta.entity_id
        AND (e.owned_by_agent = current_setting('app.current_agent_id', TRUE)
             OR e.visibility IN ('SHARED','PUBLIC'))
    ));

DROP POLICY IF EXISTS lr_agent_isolation ON public.loop_runs;
CREATE POLICY lr_agent_isolation ON public.loop_runs
    USING (agent_id = current_setting('app.current_agent_id', TRUE)
           OR EXISTS (
               SELECT 1 FROM public.entities e
               JOIN public.loop_meta m ON e.entity_id = m.entity_id
               WHERE e.entity_id = loop_runs.loop_id
               AND e.visibility IN ('SHARED','PUBLIC')
           ));

DROP POLICY IF EXISTS li_agent_isolation ON public.loop_iterations;
CREATE POLICY li_agent_isolation ON public.loop_iterations
    USING (EXISTS (
        SELECT 1 FROM public.loop_runs r
        WHERE r.run_id = loop_iterations.run_id
        AND (r.agent_id = current_setting('app.current_agent_id', TRUE)
             OR EXISTS (
                 SELECT 1 FROM public.entities e
                 JOIN public.loop_meta m ON e.entity_id = m.entity_id
                 WHERE e.entity_id = r.loop_id AND e.visibility IN ('SHARED','PUBLIC')
             ))
    ));

DROP POLICY IF EXISTS lh_agent_isolation ON public.loop_hooks;
CREATE POLICY lh_agent_isolation ON public.loop_hooks
    USING (EXISTS (
        SELECT 1 FROM public.entities e
        WHERE e.entity_id = loop_hooks.loop_id
        AND (e.owned_by_agent = current_setting('app.current_agent_id', TRUE)
             OR e.visibility IN ('SHARED','PUBLIC'))
    ));

-- Allow aiadmin full access
DROP POLICY IF EXISTS lm_owner_all ON public.loop_meta;
CREATE POLICY lm_owner_all ON public.loop_meta FOR ALL USING (current_user = :'schema_owner');
DROP POLICY IF EXISTS lr_owner_all ON public.loop_runs;
CREATE POLICY lr_owner_all ON public.loop_runs FOR ALL USING (current_user = :'schema_owner');
DROP POLICY IF EXISTS li_owner_all ON public.loop_iterations;
CREATE POLICY li_owner_all ON public.loop_iterations FOR ALL USING (current_user = :'schema_owner');
DROP POLICY IF EXISTS lh_owner_all ON public.loop_hooks;
CREATE POLICY lh_owner_all ON public.loop_hooks FOR ALL USING (current_user = :'schema_owner');

CREATE INDEX IF NOT EXISTS idx_lm_spec ON public.loop_meta(spec_id);
CREATE INDEX IF NOT EXISTS idx_lm_parent_loop ON public.loop_meta(parent_loop_id);
CREATE INDEX IF NOT EXISTS idx_lm_collab ON public.loop_meta(collab_group_id);
CREATE INDEX IF NOT EXISTS idx_ts_loop ON public.task_steps(loop_id);
CREATE INDEX IF NOT EXISTS idx_ts_completion ON public.task_steps(step_completion_type);


-- PostgreSQL database dump complete
--

\unrestrict VcAj5J5oNBrPslUHp6nHjRhkrqhnWbVSvhjvs2bkENgycNjLKIqFnra5ZxcIB9j


-- v3.7.5 Extensions
-- v3.7.5 Extensions: Agent Communication, Orchestration, Events, Observability, Tools
-- ============================================================

-- D5: Add TRACE_ID columns for distributed tracing
-- ALTER TABLE AGENT_SESSION ADD (TRACE_ID VARCHAR(64));


-- ALTER TABLE TASK_PLANS ADD (TRACE_ID VARCHAR(64));


-- ALTER TABLE LOOP_RUNS ADD (TRACE_ID VARCHAR(64));


-- ALTER TABLE TASK_TOOL_CALLS ADD (TRACE_ID VARCHAR(64));
-- ALTER TABLE TASK_TOOL_CALLS ADD (PARENT_TOOL_CALL_ID VARCHAR(64) REFERENCES TASK_TOOL_CALLS(CALL_ID));
CREATE INDEX IDX_TTC_TRACE ON TASK_TOOL_CALLS(TRACE_ID);
CREATE INDEX IDX_TTC_PARENT ON TASK_TOOL_CALLS(PARENT_TOOL_CALL_ID);

-- ALTER TABLE ENTITY_ACCESS_LOG ADD (TRACE_ID VARCHAR(64));
-- ALTER TABLE ENTITY_ACCESS_LOG ADD (DURATION_MS BIGINT);


-- ALTER TABLE WORKSPACE_CONTEXT ADD (TRACE_ID VARCHAR(64));

-- D6: Extend HARNESS_META with tool registry columns
-- ALTER TABLE HARNESS_META ADD (TOOL_SOURCE VARCHAR(32));
-- ALTER TABLE HARNESS_META ADD (TOOL_NAMESPACE VARCHAR(64));
-- ALTER TABLE HARNESS_META ADD (TOOL_VERSION VARCHAR(32));
-- ALTER TABLE HARNESS_META ADD (INPUT_SCHEMA JSONB);
-- ALTER TABLE HARNESS_META ADD (OUTPUT_SCHEMA JSONB);
-- ALTER TABLE HARNESS_META ADD (TOOL_ENABLED VARCHAR(1) DEFAULT 'Y');
CREATE INDEX IDX_HM_NS ON HARNESS_META(TOOL_NAMESPACE);
CREATE INDEX IDX_HM_SOURCE ON HARNESS_META(TOOL_SOURCE);

-- ============================================================
-- 35. COLLAB_MESSAGES (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE COLLAB_MESSAGES (
    MESSAGE_ID           VARCHAR(64)   PRIMARY KEY,
    GROUP_ID             VARCHAR(64)   NOT NULL,
    SENDER_AGENT_ID      VARCHAR(64)   NOT NULL,
    RECEIVER_AGENT_ID    VARCHAR(64),
    PARENT_MESSAGE_ID    VARCHAR(64),
    THREAD_ID            VARCHAR(64),
    SUBJECT              VARCHAR(500),
    BODY                 TEXT           NOT NULL,
    MESSAGE_TYPE         VARCHAR(32)   DEFAULT 'TEXT' NOT NULL,
    PRIORITY             VARCHAR(16)   DEFAULT 'NORMAL' NOT NULL,
    STATUS               VARCHAR(16)   DEFAULT 'SENT' NOT NULL,
    ATTACHMENT_ENTITY_ID VARCHAR(64),
    READ_AT              TIMESTAMP,
    CREATED_AT           TIMESTAMP      DEFAULT NOW() NOT NULL,
    CONSTRAINT FK_CM_GROUP FOREIGN KEY (GROUP_ID) REFERENCES COLLAB_GROUPS(GROUP_ID) ON DELETE CASCADE,
    CONSTRAINT FK_CM_SENDER FOREIGN KEY (SENDER_AGENT_ID) REFERENCES AGENT_REGISTRY(AGENT_ID),
    CONSTRAINT FK_CM_RECEIVER FOREIGN KEY (RECEIVER_AGENT_ID) REFERENCES AGENT_REGISTRY(AGENT_ID),
    CONSTRAINT FK_CM_PARENT FOREIGN KEY (PARENT_MESSAGE_ID) REFERENCES COLLAB_MESSAGES(MESSAGE_ID) ON DELETE SET NULL,
    CONSTRAINT FK_CM_THREAD FOREIGN KEY (THREAD_ID) REFERENCES COLLAB_MESSAGES(MESSAGE_ID) ON DELETE SET NULL,
    CONSTRAINT FK_CM_ATTACHMENT FOREIGN KEY (ATTACHMENT_ENTITY_ID) REFERENCES ENTITIES(ENTITY_ID),
    CONSTRAINT CK_CM_TYPE CHECK (MESSAGE_TYPE IN ('TEXT','QUERY','RESPONSE','ALERT','NOTIFICATION','COMMAND','REPORT')),
    CONSTRAINT CK_CM_PRIORITY CHECK (PRIORITY IN ('LOW','NORMAL','HIGH','URGENT')),
    CONSTRAINT CK_CM_STATUS CHECK (STATUS IN ('SENT','DELIVERED','READ','DELETED'))
);
CREATE INDEX IDX_CM_GROUP ON COLLAB_MESSAGES(GROUP_ID, CREATED_AT DESC);
CREATE INDEX IDX_CM_RECEIVER ON COLLAB_MESSAGES(RECEIVER_AGENT_ID, STATUS, CREATED_AT DESC);
CREATE INDEX IDX_CM_SENDER ON COLLAB_MESSAGES(SENDER_AGENT_ID, CREATED_AT DESC);
CREATE INDEX IDX_CM_THREAD ON COLLAB_MESSAGES(THREAD_ID, CREATED_AT);

-- ============================================================
-- 36. STEP_RETRY_POLICY (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE STEP_RETRY_POLICY (
    POLICY_ID          VARCHAR(64)  PRIMARY KEY,
    STEP_ID           VARCHAR(64)  NOT NULL,
    MAX_RETRIES        INTEGER   DEFAULT 3,
    BACKOFF_SECONDS    INTEGER   DEFAULT 5,
    BACKOFF_MULTIPLIER NUMERIC(3,1)   DEFAULT 2.0,
    TIMEOUT_SECONDS    BIGINT,
    FALLBACK_ACTION    VARCHAR(32)  DEFAULT 'FAIL',
    RETRY_COUNT        INTEGER   DEFAULT 0,
    LAST_RETRY_AT      TIMESTAMP,
    CREATED_AT         TIMESTAMP     DEFAULT NOW() NOT NULL,
    CONSTRAINT FK_SRP_STEP FOREIGN KEY (STEP_ID) REFERENCES TASK_STEPS(STEP_ID) ON DELETE CASCADE,
    CONSTRAINT CK_SRP_FALLBACK CHECK (FALLBACK_ACTION IN ('FAIL','SKIP','USE_CACHED','NOTIFY_COORDINATOR'))
);
CREATE INDEX IDX_SRP_STEP ON STEP_RETRY_POLICY(STEP_ID);

-- ============================================================
-- 37. STEP_EXECUTION_PLAN (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE STEP_EXECUTION_PLAN (
    PLAN_ID            VARCHAR(64)  PRIMARY KEY,
    ROOT_PLAN_ID       VARCHAR(64)  NOT NULL,
    STEP_GROUP_ID      INTEGER,
    STEP_ORDER         INTEGER   NOT NULL,
    STEP_ID            VARCHAR(64)  NOT NULL,
    PARENT_STEP_ID     VARCHAR(64),
    PARALLEL_GROUP     INTEGER,
    STATUS             VARCHAR(16)  DEFAULT 'PENDING',
    ASSIGNED_AGENT_ID  VARCHAR(64),
    STARTED_AT         TIMESTAMP,
    COMPLETED_AT       TIMESTAMP,
    CONSTRAINT FK_SEP_PLAN FOREIGN KEY (ROOT_PLAN_ID) REFERENCES TASK_PLANS(PLAN_ID),
    CONSTRAINT FK_SEP_STEP FOREIGN KEY (STEP_ID) REFERENCES TASK_STEPS(STEP_ID),
    CONSTRAINT FK_SEP_AGENT FOREIGN KEY (ASSIGNED_AGENT_ID) REFERENCES AGENT_REGISTRY(AGENT_ID),
    CONSTRAINT CK_SEP_STATUS CHECK (STATUS IN ('PENDING','RUNNING','COMPLETED','FAILED','SKIPPED','BLOCKED'))
);
CREATE INDEX IDX_SEP_PLAN ON STEP_EXECUTION_PLAN(ROOT_PLAN_ID, STEP_ORDER);
CREATE INDEX IDX_SEP_STATUS ON STEP_EXECUTION_PLAN(STATUS);

-- ============================================================
-- 38. EVENT_LOG (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE EVENT_LOG (
    EVENT_ID     VARCHAR(64)  PRIMARY KEY,
    EVENT_TYPE   VARCHAR(64)  NOT NULL,
    SOURCE_ID    VARCHAR(64),
    SOURCE_TYPE  VARCHAR(32),
    PAYLOAD      JSONB,
    CREATED_AT   TIMESTAMP     DEFAULT NOW() NOT NULL
);
CREATE INDEX IDX_EL_TYPE ON EVENT_LOG(EVENT_TYPE, CREATED_AT DESC);
CREATE INDEX IDX_EL_SOURCE ON EVENT_LOG(SOURCE_ID, EVENT_TYPE);

-- ============================================================
-- 39. EVENT_SUBSCRIPTIONS (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE EVENT_SUBSCRIPTIONS (
    SUB_ID         VARCHAR(64)  PRIMARY KEY,
    AGENT_ID       VARCHAR(64)  NOT NULL,
    EVENT_TYPE     VARCHAR(64)  NOT NULL,
    FILTER_PATTERN VARCHAR(500),
    ENABLED        VARCHAR(1)   DEFAULT 'Y' NOT NULL,
    CREATED_AT     TIMESTAMP     DEFAULT NOW() NOT NULL,
    CONSTRAINT FK_ES_AGENT FOREIGN KEY (AGENT_ID) REFERENCES AGENT_REGISTRY(AGENT_ID),
    CONSTRAINT CK_ES_ENABLED CHECK (ENABLED IN ('Y','N')),
    CONSTRAINT UK_ES_AGENT_EVENT UNIQUE (AGENT_ID, EVENT_TYPE)
);
CREATE INDEX IDX_ES_EVENT ON EVENT_SUBSCRIPTIONS(EVENT_TYPE, ENABLED);

-- ============================================================
-- 40. AGENT_CAPABILITY_INDEX (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE AGENT_CAPABILITY_INDEX (
    CAP_ID        VARCHAR(64)  PRIMARY KEY,
    AGENT_ID      VARCHAR(64)  NOT NULL,
    CAPABILITY    VARCHAR(256) NOT NULL,
    CONFIDENCE    NUMERIC(5,4)   DEFAULT 1.0000,
    LAST_VERIFIED_AT TIMESTAMP,
    CREATED_AT    TIMESTAMP     DEFAULT NOW() NOT NULL,
    CONSTRAINT FK_ACI_AGENT FOREIGN KEY (AGENT_ID) REFERENCES AGENT_REGISTRY(AGENT_ID)
);
CREATE INDEX IDX_ACI_CAP ON AGENT_CAPABILITY_INDEX(CAPABILITY);
CREATE INDEX IDX_ACI_AGENT ON AGENT_CAPABILITY_INDEX(AGENT_ID);

-- ============================================================
-- 41. TOOL_REGISTRY (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE TOOL_REGISTRY (
    TOOL_ID          VARCHAR(64)  PRIMARY KEY,
    TOOL_NAME        VARCHAR(256) NOT NULL,
    TOOL_NAMESPACE   VARCHAR(64)  NOT NULL,
    TOOL_VERSION     VARCHAR(32),
    DESCRIPTION      VARCHAR(2000),
    INPUT_SCHEMA     JSONB,
    OUTPUT_SCHEMA    JSONB,
    RUNTIME_REQS     JSONB,
    TOOL_TYPE        VARCHAR(32)  DEFAULT 'API',
    STATUS           VARCHAR(16)  DEFAULT 'ACTIVE',
    CALL_COUNT       BIGINT  DEFAULT 0,
    LAST_CALLED_AT   TIMESTAMP,
    CREATED_AT       TIMESTAMP     DEFAULT NOW() NOT NULL,
    UPDATED_AT       TIMESTAMP     DEFAULT NOW() NOT NULL,
    CONSTRAINT UK_TR_NAME UNIQUE (TOOL_NAME, TOOL_VERSION),
    CONSTRAINT CK_TR_TYPE CHECK (TOOL_TYPE IN ('API','FUNCTION','SQL','SCRIPT','WEBHOOK')),
    CONSTRAINT CK_TR_STATUS CHECK (STATUS IN ('ACTIVE','DEPRECATED','RETIRED'))
);
CREATE INDEX IDX_TR_NS ON TOOL_REGISTRY(TOOL_NAMESPACE);
CREATE INDEX IDX_TR_TYPE ON TOOL_REGISTRY(TOOL_TYPE);
CREATE INDEX IDX_TR_STATUS ON TOOL_REGISTRY(STATUS);

-- ============================================================
-- 42. TOOL_CHAINS (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE TOOL_CHAINS (
    CHAIN_ID         VARCHAR(64)  PRIMARY KEY,
    CHAIN_NAME       VARCHAR(256) NOT NULL,
    DESCRIPTION      VARCHAR(2000),
    CREATED_BY       VARCHAR(64),
    CREATED_AT       TIMESTAMP     DEFAULT NOW() NOT NULL,
    UPDATED_AT       TIMESTAMP     DEFAULT NOW() NOT NULL
);

-- ============================================================
-- 43. TOOL_CHAIN_STEPS (Non-Partitioned) [NEW v3.7.5]
-- ============================================================

CREATE TABLE TOOL_CHAIN_STEPS (
    CHAIN_STEP_ID    VARCHAR(64)  PRIMARY KEY,
    CHAIN_ID         VARCHAR(64)  NOT NULL,
    STEP_ORDER       INTEGER   NOT NULL,
    TOOL_ID          VARCHAR(64)  NOT NULL,
    INPUT_MAPPING    JSONB,
    OUTPUT_MAPPING   JSONB,
    PARALLEL_GROUP   INTEGER,
    TIMEOUT_SECONDS  BIGINT,
    CONSTRAINT FK_TCS_CHAIN FOREIGN KEY (CHAIN_ID) REFERENCES TOOL_CHAINS(CHAIN_ID) ON DELETE CASCADE,
    CONSTRAINT FK_TCS_TOOL FOREIGN KEY (TOOL_ID) REFERENCES TOOL_REGISTRY(TOOL_ID)
);
CREATE INDEX IDX_TCS_CHAIN ON TOOL_CHAIN_STEPS(CHAIN_ID, STEP_ORDER);

-- ============================================================



-- ============================================================
-- v3.9.0 Extensions: MCP, Human-in-the-Loop Approval, Model Routing
-- ============================================================

-- Add approval columns to STEP_EXECUTION_PLAN
ALTER TABLE STEP_EXECUTION_PLAN ADD COLUMN IF NOT EXISTS REQUIRES_APPROVAL CHAR(1) DEFAULT 'N';
ALTER TABLE STEP_EXECUTION_PLAN ADD COLUMN IF NOT EXISTS APPROVED_BY VARCHAR(64);
ALTER TABLE STEP_EXECUTION_PLAN ADD COLUMN IF NOT EXISTS APPROVED_AT TIMESTAMP;

-- Add approval column to LOOP_META
ALTER TABLE LOOP_META ADD COLUMN IF NOT EXISTS REQUIRE_APPROVAL CHAR(1) DEFAULT 'N';

-- Add approval column to TOOL_REGISTRY
ALTER TABLE TOOL_REGISTRY ADD COLUMN IF NOT EXISTS REQUIRES_APPROVAL CHAR(1) DEFAULT 'N';

-- 44. APPROVAL_REQUESTS [NEW v3.9.0]
CREATE TABLE IF NOT EXISTS APPROVAL_REQUESTS (
    APPROVAL_ID      VARCHAR(64)   PRIMARY KEY,
    ENTITY_TYPE      VARCHAR(32)   NOT NULL,
    ENTITY_ID        VARCHAR(64)   NOT NULL,
    REQUESTED_BY     VARCHAR(64)   NOT NULL,
    APPROVAL_STATUS  VARCHAR(16)   DEFAULT 'PENDING' NOT NULL,
    APPROVED_BY      VARCHAR(64),
    APPROVED_AT      TIMESTAMP,
    REJECT_REASON    VARCHAR(500),
    CREATED_AT       TIMESTAMP     DEFAULT NOW() NOT NULL,
    CONSTRAINT CK_AR_STATUS CHECK (APPROVAL_STATUS IN ('PENDING','APPROVED','REJECTED')),
    CONSTRAINT CK_AR_ENTITY CHECK (ENTITY_TYPE IN ('STEP','LOOP','TOOL'))
);
CREATE INDEX IF NOT EXISTS IDX_AR_STATUS ON APPROVAL_REQUESTS(APPROVAL_STATUS, CREATED_AT DESC);
CREATE INDEX IF NOT EXISTS IDX_AR_ENTITY ON APPROVAL_REQUESTS(ENTITY_TYPE, ENTITY_ID);
