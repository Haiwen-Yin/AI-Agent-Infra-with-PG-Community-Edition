"""AI Agent Infra v3.7.1 - PG Community Edition - Loop Engineering API

Loop Engineering: design goal-driven autonomous feedback loops for AI agents.
Each Loop definition is stored as an ENTITY (entity_type='LOOP_DEFINITION')
with metadata in loop_meta. Runs and iterations track execution state.
"""

import json
import subprocess
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional

from .connection import (
    execute, execute_query, execute_query_one, execute_insert_returning_id,
)
from .config import get_config


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    return dict(row)


# -- Loop Definition CRUD --

def create_loop(
    title: str,
    goal_definition: Dict[str, Any],
    stop_conditions: Dict[str, Any],
    evaluation_config: Dict[str, Any],
    summary: Optional[str] = None,
    trigger_config: Optional[Dict[str, Any]] = None,
    harness_template_id: Optional[int] = None,
    workspace_id: Optional[int] = None,
    branch_id: Optional[int] = None,
    owned_by_agent: Optional[str] = None,
    visibility: str = "PRIVATE",
    spec_id: Optional[str] = None,
    parent_loop_id: Optional[int] = None,
    collab_group_id: Optional[str] = None,
) -> int:
    entity_id = execute_insert_returning_id("""
        INSERT INTO entities (entity_type, title, summary, status,
                              owned_by_agent, source_agent, visibility,
                              importance, retrieval_count, workspace_id, created_at, updated_at)
        VALUES ('LOOP_DEFINITION', %s, %s, 'ACTIVE', %s, %s, %s, 5, 0, %s, NOW(), NOW())
        RETURNING entity_id
    """, [title, summary, owned_by_agent, owned_by_agent, visibility, workspace_id])
    execute("""
        INSERT INTO loop_meta (entity_id, entity_type, loop_version,
                               goal_definition, stop_conditions, evaluation_config,
                               trigger_config, harness_template_id, workspace_id, branch_id,
                               spec_id, parent_loop_id, collab_group_id)
        VALUES (%s, 'LOOP_DEFINITION', '1.0', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, [entity_id, json.dumps(goal_definition), json.dumps(stop_conditions),
          json.dumps(evaluation_config),
          json.dumps(trigger_config) if trigger_config else None,
          harness_template_id, workspace_id, branch_id,
          spec_id, parent_loop_id, collab_group_id])
    return entity_id


def get_loop(loop_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one("""
        SELECT e.entity_id AS loop_id, e.title, e.summary, e.status, e.visibility,
               e.owned_by_agent, e.workspace_id, e.created_at, e.updated_at,
               m.loop_version, m.goal_definition, m.stop_conditions,
               m.evaluation_config, m.trigger_config,
               m.harness_template_id, m.branch_id,
               m.spec_id, m.parent_loop_id, m.collab_group_id
        FROM entities e JOIN loop_meta m ON e.entity_id = m.entity_id
        WHERE e.entity_id = %s AND e.entity_type = 'LOOP_DEFINITION'
    """, [loop_id])
    return _row_to_dict(row) if row else None


def update_loop(loop_id: int, **kwargs: Any) -> bool:
    count = 0
    entity_fields = {"title": "title", "summary": "summary", "visibility": "visibility"}
    sets, params = [], []
    for k, v in kwargs.items():
        if k in entity_fields and v is not None:
            sets.append(f"{entity_fields[k]} = %s")
            params.append(v)
    if sets:
        params.append(loop_id)
        execute(f"UPDATE entities SET {', '.join(sets)}, updated_at = NOW() "
                f"WHERE entity_id = %s AND entity_type = 'LOOP_DEFINITION'", params)
        count += 1
    meta_fields = {"goal_definition", "stop_conditions", "evaluation_config", "trigger_config"}
    msets, mparams = [], []
    for k, v in kwargs.items():
        if k in meta_fields and v is not None:
            msets.append(f"{k} = %s")
            mparams.append(json.dumps(v) if isinstance(v, dict) else v)
    if msets:
        mparams.append(loop_id)
        execute(f"UPDATE loop_meta SET {', '.join(msets)} WHERE entity_id = %s", mparams)
        count += 1
    return count > 0


def delete_loop(loop_id: int) -> bool:
    execute("DELETE FROM loop_iterations WHERE run_id IN (SELECT run_id FROM loop_runs WHERE loop_id = %s)", [loop_id])
    execute("DELETE FROM loop_runs WHERE loop_id = %s", [loop_id])
    execute("DELETE FROM loop_hooks WHERE loop_id = %s", [loop_id])
    execute("DELETE FROM task_loop_binding WHERE loop_id = %s", [loop_id])
    execute("DELETE FROM loop_meta WHERE entity_id = %s", [loop_id])
    execute("DELETE FROM entities WHERE entity_id = %s AND entity_type = 'LOOP_DEFINITION'", [loop_id])
    return True


def list_loops(status: Optional[str] = None, agent_id: Optional[str] = None,
               parent_loop_id: Optional[int] = None,
               collab_group_id: Optional[str] = None,
               spec_id: Optional[str] = None,
               limit: int = 50) -> List[Dict[str, Any]]:
    sql = """SELECT e.entity_id AS loop_id, e.title, e.summary, e.status, e.visibility,
               e.owned_by_agent, e.workspace_id, e.created_at,
               m.loop_version, m.goal_definition
            FROM entities e JOIN loop_meta m ON e.entity_id = m.entity_id
            WHERE e.entity_type = 'LOOP_DEFINITION'"""
    params: List[Any] = []
    if status:
        sql += " AND e.status = %s"; params.append(status)
    if agent_id:
        sql += " AND e.owned_by_agent = %s"; params.append(agent_id)
    if parent_loop_id:
        sql += " AND m.parent_loop_id = %s"; params.append(parent_loop_id)
    if collab_group_id:
        sql += " AND m.collab_group_id = %s"; params.append(collab_group_id)
    if spec_id:
        sql += " AND m.spec_id = %s"; params.append(spec_id)
    sql += " ORDER BY e.created_at DESC LIMIT %s"
    params.append(limit)
    return [_row_to_dict(r) for r in execute_query(sql, params)]


# -- Run Management --

def start_run(loop_id: int, agent_id: str,
              trigger_type: str = "MANUAL",
              trigger_source: Optional[str] = None,
              parent_run_id: Optional[int] = None) -> int:
    return execute_insert_returning_id("""
        INSERT INTO loop_runs (loop_id, agent_id, trigger_type, trigger_source,
                               status, iteration_count, total_tokens, started_at,
                               parent_run_id)
        VALUES (%s, %s, %s, %s, 'RUNNING', 0, 0, NOW(), %s)
        RETURNING run_id
    """, [loop_id, agent_id, trigger_type, trigger_source, parent_run_id], id_column="run_id")


def get_run(run_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one("""
        SELECT run_id, loop_id, agent_id, trigger_type, trigger_source,
               status, iteration_count, total_tokens, final_result,
               error_message, started_at, completed_at, parent_run_id
        FROM loop_runs WHERE run_id = %s
    """, [run_id])
    return dict(row) if row else None


def list_runs(loop_id: Optional[int] = None, status: Optional[str] = None,
              limit: int = 50) -> List[Dict[str, Any]]:
    sql = """SELECT run_id, loop_id, agent_id, trigger_type, trigger_source,
                    status, iteration_count, total_tokens, final_result,
                    started_at, completed_at
             FROM loop_runs WHERE 1=1"""
    params: List[Any] = []
    if loop_id:
        sql += " AND loop_id = %s"; params.append(loop_id)
    if status:
        sql += " AND status = %s"; params.append(status)
    sql += " ORDER BY started_at DESC LIMIT %s"
    params.append(limit)
    return [dict(r) for r in execute_query(sql, params)]


def pause_run(run_id: int) -> bool:
    return execute("UPDATE loop_runs SET status = 'PAUSED' "
                   "WHERE run_id = %s AND status = 'RUNNING'", [run_id]) > 0


def resume_run(run_id: int) -> bool:
    return execute("UPDATE loop_runs SET status = 'RUNNING' "
                   "WHERE run_id = %s AND status = 'PAUSED'", [run_id]) > 0


def stop_run(run_id: int, reason: Optional[str] = None) -> bool:
    result = execute("UPDATE loop_runs SET status = 'STOPPED', final_result = %s, "
                     "completed_at = NOW() WHERE run_id = %s AND status IN ('RUNNING','PAUSED')",
                     [reason, run_id]) > 0
    if result:
        on_loop_run_completed(run_id)
    return result


def fail_run(run_id: int, error_message: str) -> bool:
    return execute("UPDATE loop_runs SET status = 'FAILED', error_message = %s, "
                   "completed_at = NOW() WHERE run_id = %s",
                   [error_message, run_id]) > 0


def complete_run(run_id: int, final_result: Optional[str] = None) -> bool:
    result = execute("UPDATE loop_runs SET status = 'COMPLETED', final_result = %s, "
                     "completed_at = NOW() WHERE run_id = %s "
                     "AND status IN ('RUNNING','PAUSED')",
                     [final_result, run_id]) > 0
    if result:
        on_loop_run_completed(run_id)
    return result


# -- Collaborative & Spec-Driven Loop Features --

def create_loop_from_spec(spec_id: str, agent_id: str, **kwargs: Any) -> int:
    from .spec_api import get_spec
    spec = get_spec(spec_id)
    if not spec:
        raise ValueError(f"Spec {spec_id} not found")
    acceptance = spec.get("acceptance_criteria") or {}
    if isinstance(acceptance, str):
        acceptance = json.loads(acceptance)
    goal_definition = {"type": "SPEC_VALIDATION", "spec_id": spec_id,
                       "criteria": acceptance}
    stop_conditions = kwargs.pop("stop_conditions", {"max_iterations": 10})
    evaluation_config = {"type": "SPEC_VALIDATION", "spec_id": spec_id}
    return create_loop(
        title=kwargs.pop("title", f"Loop for spec: {spec.get('title', spec_id)}"),
        goal_definition=goal_definition,
        stop_conditions=stop_conditions,
        evaluation_config=evaluation_config,
        owned_by_agent=agent_id,
        spec_id=spec_id,
        **kwargs,
    )


def create_collab_loop(group_id: str, parent_loop_id: Optional[int],
                       agent_id: str, **kwargs: Any) -> int:
    if parent_loop_id:
        parent = get_loop(parent_loop_id)
        if not parent:
            raise ValueError(f"Parent loop {parent_loop_id} not found")
        if parent.get("parent_loop_id"):
            raise ValueError("2-level nesting limit: parent_loop_id is already a child loop")
    from .collab_api import get_collab_members
    members = get_collab_members(group_id)
    if not members:
        raise ValueError(f"Collaboration group {group_id} has no members")
    return create_loop(
        title=kwargs.pop("title", f"Collab loop for group {group_id}"),
        goal_definition=kwargs.pop("goal_definition", {"type": "COLLABORATIVE", "group_id": group_id}),
        stop_conditions=kwargs.pop("stop_conditions", {"max_iterations": 10}),
        evaluation_config=kwargs.pop("evaluation_config", {"type": "CONSENSUS"}),
        owned_by_agent=agent_id,
        collab_group_id=group_id,
        parent_loop_id=parent_loop_id,
        **kwargs,
    )


def create_sub_loops_for_group(parent_loop_id: int, group_id: str,
                               agent_ids: List[str]) -> List[int]:
    parent = get_loop(parent_loop_id)
    if not parent:
        raise ValueError(f"Parent loop {parent_loop_id} not found")
    if parent.get("parent_loop_id"):
        raise ValueError("Parent loop is already a sub-loop; 2-level nesting limit exceeded")
    sub_loop_ids = []
    for aid in agent_ids:
        lid = create_loop(
            title=f"Sub-loop for agent {aid}",
            goal_definition=parent.get("goal_definition", {}),
            stop_conditions=parent.get("stop_conditions", {}),
            evaluation_config=parent.get("evaluation_config", {}),
            owned_by_agent=aid,
            parent_loop_id=parent_loop_id,
            collab_group_id=group_id,
        )
        sub_loop_ids.append(lid)
    return sub_loop_ids


def aggregate_child_runs(parent_run_id: int) -> Dict[str, Any]:
    rows = execute_query("""
        SELECT run_id, status, final_result
        FROM loop_runs WHERE parent_run_id = %s
    """, [parent_run_id])
    total = len(rows)
    completed = sum(1 for r in rows if r["status"] == "COMPLETED")
    failed = sum(1 for r in rows if r["status"] in ("FAILED", "STOPPED", "TIMEOUT"))
    running = sum(1 for r in rows if r["status"] in ("RUNNING", "PAUSED"))
    results = [{"run_id": r["run_id"], "status": r["status"],
                "final_result": r["final_result"]} for r in rows]
    return {"total": total, "completed": completed, "failed": failed,
            "running": running, "results": results}


def bind_loop_to_step(loop_id: int, step_id: str,
                      binding_type: str = 'COMPLETION',
                      auto_start: str = 'N') -> int:
    binding_id = execute_insert_returning_id("""
        INSERT INTO task_loop_binding (loop_id, step_id, binding_type,
                                       auto_start, created_at)
        VALUES (%s, %s, %s, %s, NOW())
        RETURNING binding_id
    """, [loop_id, step_id, binding_type, auto_start], id_column="binding_id")
    execute("UPDATE task_steps SET loop_id = %s, step_completion_type = 'LOOP' "
            "WHERE step_id = %s",
            [loop_id, step_id])
    if auto_start == 'Y':
        loop = get_loop(loop_id)
        start_run(loop_id, loop.get("owned_by_agent") if loop else None)
    return binding_id


def get_step_loop(step_id: str) -> Optional[Dict[str, Any]]:
    row = execute_query_one("""
        SELECT b.binding_id, b.loop_id, b.step_id, b.binding_type,
               b.auto_start, b.created_at
        FROM task_loop_binding b WHERE b.step_id = %s
    """, [step_id])
    if not row:
        return None
    result = dict(row)
    loop = get_loop(result["loop_id"])
    if loop:
        result["loop"] = loop
    return result


def on_loop_run_completed(run_id: int) -> List[str]:
    run = get_run(run_id)
    if not run:
        return []
    loop_id = run["loop_id"]
    rows = execute_query("""
        SELECT step_id, binding_type FROM task_loop_binding
        WHERE loop_id = %s AND binding_type = 'COMPLETION'
    """, [loop_id])
    updated = []
    for r in rows:
        execute("UPDATE task_steps SET status = 'SUCCESS', completed_at = NOW() "
                "WHERE step_id = %s", [r["step_id"]])
        updated.append(r["step_id"])
    return updated


def create_validation_loop_for_skill(skill_id: int, agent_id: str) -> Optional[int]:
    from .skill_api import get_skill
    skill = get_skill(skill_id)
    if not skill:
        return None
    metadata = skill.get("metadata") or skill.get("skill_metadata") or {}
    if isinstance(metadata, str):
        metadata = json.loads(metadata)
    validation_loop = metadata.get("validation_loop")
    if not validation_loop:
        return None
    if isinstance(validation_loop, str):
        validation_loop = json.loads(validation_loop)
    return create_loop(
        title=validation_loop.get("title", f"Validation loop for skill {skill_id}"),
        goal_definition=validation_loop.get("goal_definition", {"type": "SKILL_VALIDATION", "skill_id": skill_id}),
        stop_conditions=validation_loop.get("stop_conditions", {"max_iterations": 5}),
        evaluation_config=validation_loop.get("evaluation_config", {"type": "TEST"}),
        owned_by_agent=agent_id,
    )


# -- Iteration Management --

def record_iteration(
    run_id: int,
    plan_data: Optional[Dict[str, Any]] = None,
    actions: Optional[Dict[str, Any]] = None,
    observations: Optional[Dict[str, Any]] = None,
    evaluation_result: Optional[Dict[str, Any]] = None,
    evaluation_passed: bool = False,
    adjustment: Optional[Dict[str, Any]] = None,
    token_usage: int = 0,
) -> int:
    run = get_run(run_id)
    if not run:
        raise ValueError(f"Run {run_id} not found")
    iter_id = execute_insert_returning_id("""
        INSERT INTO loop_iterations (run_id, iteration_order, plan_data, actions,
                                     observations, evaluation_result, evaluation_passed,
                                     adjustment, token_usage, started_at, completed_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        RETURNING iteration_id
    """, [run_id, run["iteration_count"] + 1,
          json.dumps(plan_data) if plan_data else None,
          json.dumps(actions) if actions else None,
          json.dumps(observations) if observations else None,
          json.dumps(evaluation_result) if evaluation_result else None,
          "Y" if evaluation_passed else "N",
          json.dumps(adjustment) if adjustment else None,
          token_usage], id_column="iteration_id")
    execute("UPDATE loop_runs SET iteration_count = iteration_count + 1, "
            "total_tokens = total_tokens + %s WHERE run_id = %s",
            [token_usage, run_id])
    if evaluation_passed:
        execute("UPDATE loop_runs SET status = 'COMPLETED', completed_at = NOW(), "
                "final_result = 'Goal achieved at iteration ' || iteration_count::text "
                "WHERE run_id = %s", [run_id])
    return iter_id


def get_iteration(iteration_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one("""
        SELECT iteration_id, run_id, iteration_order, plan_data, actions,
               observations, evaluation_result, evaluation_passed,
               adjustment, token_usage, started_at, completed_at
        FROM loop_iterations WHERE iteration_id = %s
    """, [iteration_id])
    return _row_to_dict(row) if row else None


def list_iterations(run_id: int, limit: int = 50) -> List[Dict[str, Any]]:
    rows = execute_query("""
        SELECT iteration_id, run_id, iteration_order, evaluation_passed,
               token_usage, started_at, completed_at
        FROM loop_iterations WHERE run_id = %s
        ORDER BY iteration_order ASC LIMIT %s
    """, [run_id, limit])
    return [dict(r) for r in rows]


# -- Hooks --

def add_hook(loop_id: int, hook_event: str, hook_type: str,
             hook_config: Optional[Dict[str, Any]] = None,
             priority: int = 5) -> int:
    return execute_insert_returning_id("""
        INSERT INTO loop_hooks (loop_id, hook_event, hook_type, hook_config,
                                priority, enabled, created_at)
        VALUES (%s, %s, %s, %s, %s, 'Y', NOW())
        RETURNING hook_id
    """, [loop_id, hook_event, hook_type,
          json.dumps(hook_config) if hook_config else None,
          priority], id_column="hook_id")


def remove_hook(hook_id: int) -> bool:
    return execute("DELETE FROM loop_hooks WHERE hook_id = %s", [hook_id]) > 0


def list_hooks(loop_id: int) -> List[Dict[str, Any]]:
    rows = execute_query("""
        SELECT hook_id, loop_id, hook_event, hook_type, hook_config,
               priority, enabled, created_at
        FROM loop_hooks WHERE loop_id = %s ORDER BY priority ASC, created_at ASC
    """, [loop_id])
    return [_row_to_dict(r) for r in rows]


# -- Stats & Operations --

def get_loop_stats(loop_id: int) -> Dict[str, Any]:
    row = execute_query_one("""
        SELECT
            (SELECT COUNT(*) FROM loop_runs WHERE loop_id = %s) AS total_runs,
            (SELECT COUNT(*) FROM loop_runs WHERE loop_id = %s AND status = 'COMPLETED') AS completed,
            (SELECT COUNT(*) FROM loop_runs WHERE loop_id = %s AND status IN ('FAILED','STOPPED','TIMEOUT')) AS failed,
            (SELECT COUNT(*) FROM loop_runs WHERE loop_id = %s AND status IN ('RUNNING','PAUSED')) AS running,
            (SELECT COUNT(*) FROM loop_iterations li JOIN loop_runs lr ON li.run_id = lr.run_id
             WHERE lr.loop_id = %s) AS total_iterations,
            (SELECT COALESCE(SUM(total_tokens), 0) FROM loop_runs WHERE loop_id = %s) AS total_tokens
    """, [loop_id, loop_id, loop_id, loop_id, loop_id, loop_id])
    return dict(row) if row else {}


def check_stop_conditions(run_id: int) -> str:
    run = get_run(run_id)
    if not run:
        return "STOP"
    loop = get_loop(run["loop_id"])
    if not loop:
        return "STOP"
    stop = loop.get("stop_conditions") or {}
    if isinstance(stop, str):
        stop = json.loads(stop)
    max_iter = stop.get("max_iterations")
    if max_iter and run["iteration_count"] >= max_iter:
        return "STOP"
    max_tokens = stop.get("max_tokens")
    if max_tokens and run["total_tokens"] >= max_tokens:
        return "STOP"
    max_dur = stop.get("max_duration_seconds")
    if max_dur and run.get("started_at"):
        started = run["started_at"]
        if hasattr(started, 'tzinfo') and started.tzinfo:
            started = started.replace(tzinfo=None)
        elapsed = (datetime.now() - started).total_seconds()
        if elapsed >= max_dur:
            return "TIMEOUT"
    return "CONTINUE"


def cleanup_old_runs(days_threshold: int = 90) -> int:
    return execute("""
        DELETE FROM loop_iterations
        WHERE run_id IN (
            SELECT run_id FROM loop_runs
            WHERE status IN ('COMPLETED','STOPPED','FAILED','TIMEOUT')
              AND completed_at < NOW() - (%s || ' days')::interval
        )
    """, [days_threshold]) + execute("""
        DELETE FROM loop_runs
        WHERE status IN ('COMPLETED','STOPPED','FAILED','TIMEOUT')
          AND completed_at < NOW() - (%s || ' days')::interval
    """, [days_threshold])


# -- Evaluation Engine --

def evaluate_iteration(run_id: int, iteration_id: int) -> Dict[str, Any]:
    """Evaluate an iteration using the configured evaluation method."""
    run = get_run(run_id)
    if not run:
        return {"passed": False, "error": "Run not found"}
    loop = get_loop(run["loop_id"])
    if not loop:
        return {"passed": False, "error": "Loop definition not found"}
    eval_cfg = loop.get("evaluation_config") or {}
    if isinstance(eval_cfg, str):
        eval_cfg = json.loads(eval_cfg)
    eval_type = eval_cfg.get("eval_type", "MANUAL")
    iter_data = get_iteration(iteration_id) or {}
    if eval_type == "TEST":
        return _eval_test(eval_cfg, iter_data)
    elif eval_type == "DIFF":
        return _eval_diff(eval_cfg, iter_data)
    elif eval_type == "LLM_JUDGE":
        return _eval_llm_judge(eval_cfg, iter_data)
    elif eval_type == "SPEC_VALIDATION":
        return _eval_spec_validation(eval_cfg, iter_data)
    elif eval_type == "AGGREGATE":
        return _eval_aggregate(eval_cfg, iter_data)
    else:
        return _eval_manual(eval_cfg, iter_data)


def _eval_test(cfg, iter_data):
    cmd = cfg.get("eval_command")
    if not cmd:
        return {"passed": False, "error": "No eval_command configured"}
    timeout = cfg.get("eval_timeout", 120)
    success_code = cfg.get("success_exit_code", 0)
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        passed = result.returncode == success_code
        details = {"exit_code": result.returncode,
                   "stdout": result.stdout[-2000:] if result.stdout else "",
                   "stderr": result.stderr[-2000:] if result.stderr else ""}
        criteria = cfg.get("success_criteria", {})
        if passed and criteria.get("min_pass_rate"):
            output = result.stdout + result.stderr
            pass_match = output.count("passed")
            fail_match = output.count("failed")
            total = pass_match + fail_match
            if total > 0:
                rate = pass_match / total
                details["pass_rate"] = rate
                if rate < criteria["min_pass_rate"]:
                    passed = False
        return {"passed": passed, "eval_type": "TEST", "details": details}
    except subprocess.TimeoutExpired:
        return {"passed": False, "eval_type": "TEST", "error": f"Timeout after {timeout}s"}
    except Exception as e:
        return {"passed": False, "eval_type": "TEST", "error": str(e)}


def _eval_diff(cfg, iter_data):
    diff_cmd = cfg.get("diff_command", "git diff --stat")
    max_files = cfg.get("max_files_changed")
    max_lines = cfg.get("max_lines_changed")
    try:
        result = subprocess.run(diff_cmd, shell=True, capture_output=True, text=True, timeout=60)
        output = result.stdout
        file_count = output.count(" | ") if output else 0
        line_count = 0
        for line in output.split("\n"):
            if "+" in line or "-" in line:
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        line_count += abs(int(parts[-1]))
                    except ValueError:
                        pass
        passed = True
        if max_files and file_count > max_files:
            passed = False
        if max_lines and line_count > max_lines:
            passed = False
        return {"passed": passed, "eval_type": "DIFF",
                "details": {"files_changed": file_count, "lines_changed": line_count,
                            "diff_summary": output[-1000:] if output else ""}}
    except Exception as e:
        return {"passed": False, "eval_type": "DIFF", "error": str(e)}


def _eval_llm_judge(cfg, iter_data):
    config = get_config()
    judge_cfg = config.get("llm_judge", {})
    if not judge_cfg.get("enabled", False):
        return {"passed": False, "eval_type": "LLM_JUDGE", "error": "LLM_JUDGE not enabled"}
    api_url = judge_cfg.get("api_url", "http://10.10.10.1:12345/v1/chat/completions")
    model = judge_cfg.get("model", "gpt-4o")
    timeout = judge_cfg.get("timeout", 60)
    min_score = judge_cfg.get("min_score", 7)
    prompt_template = cfg.get("eval_prompt",
        "Rate this AI agent output from 1-10. Return JSON: {\"score\": int, \"reasoning\": string}.\n\nOutput:\n{output}")
    output_text = ""
    if iter_data.get("observations"):
        obs = iter_data["observations"]
        if isinstance(obs, str):
            obs = json.loads(obs)
        output_text = json.dumps(obs, indent=2)[:4000]
    prompt = prompt_template.replace("{output}", output_text)
    try:
        payload = json.dumps({"model": model,
            "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}).encode()
        req = urllib.request.Request(api_url, data=payload, method="POST")
        req.add_header("Content-Type", "application/json")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp_data = json.loads(resp.read().decode())
        content = resp_data.get("choices", [{}])[0].get("message", {}).get("content", "")
        try:
            judge_result = json.loads(content)
        except json.JSONDecodeError:
            import re
            score_match = re.search(r'"score"\s*:\s*(\d+)', content)
            judge_result = {"score": int(score_match.group(1)) if score_match else 0, "reasoning": content}
        score = judge_result.get("score", 0)
        passed = score >= min_score
        return {"passed": passed, "eval_type": "LLM_JUDGE",
                "details": {"score": score, "min_score": min_score,
                            "reasoning": judge_result.get("reasoning", "")}}
    except Exception as e:
        return {"passed": False, "eval_type": "LLM_JUDGE", "error": str(e)}


def _eval_manual(cfg, iter_data):
    return {"passed": False, "eval_type": "MANUAL",
            "details": {"status": "AWAITING_REVIEW", "message": "Manual review required"}}


# -- Loop Execution Engine --

def execute_loop_iteration(run_id, agent_id, plan_data=None, actions=None,
                           observations=None, token_usage=0):
    stop_check = check_stop_conditions(run_id)
    if stop_check != "CONTINUE":
        if stop_check == "TIMEOUT":
            execute("UPDATE loop_runs SET status='TIMEOUT', completed_at=NOW() WHERE run_id=%s", [run_id])
        return {"iteration_id": None, "evaluation": None, "stop_status": stop_check, "run_status": stop_check}
    iter_id = record_iteration(run_id=run_id, plan_data=plan_data, actions=actions,
                               observations=observations, token_usage=token_usage)
    eval_result = evaluate_iteration(run_id, iter_id)
    passed = eval_result.get("passed", False)
    execute("UPDATE loop_iterations SET evaluation_result=%s, evaluation_passed=%s, adjustment=%s WHERE iteration_id=%s",
            [json.dumps(eval_result), "Y" if passed else "N",
             json.dumps({"next_action": "done" if passed else "continue"}), iter_id])
    if passed:
        execute("UPDATE loop_runs SET status='COMPLETED', completed_at=NOW(), final_result='Goal achieved' WHERE run_id=%s", [run_id])
        on_loop_run_completed(run_id)
        return {"iteration_id": iter_id, "evaluation": eval_result, "stop_status": "STOP", "run_status": "COMPLETED"}
    stop_check = check_stop_conditions(run_id)
    if stop_check != "CONTINUE":
        if stop_check == "TIMEOUT":
            execute("UPDATE loop_runs SET status='TIMEOUT', completed_at=NOW() WHERE run_id=%s", [run_id])
        else:
            execute("UPDATE loop_runs SET status='STOPPED', completed_at=NOW() WHERE run_id=%s", [run_id])
    return {"iteration_id": iter_id, "evaluation": eval_result, "stop_status": stop_check,
            "run_status": "TIMEOUT" if stop_check == "TIMEOUT" else ("STOPPED" if stop_check == "STOP" else "RUNNING")}
