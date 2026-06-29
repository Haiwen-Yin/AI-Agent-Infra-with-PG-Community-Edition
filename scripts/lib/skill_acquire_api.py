"""AI Agent Infra v3.7.5 - PG Community Edition - Skill Acquisition API

Agent-facing interface for discovering and acquiring skills.
- Community Edition: direct access, no token required
- Admin API mode: Business Agent acquires skills via Admin Agent HTTP API
"""

import io
import json
import zipfile
from typing import Any, Dict, List, Optional

from .connection import execute_query, execute_query_one
from .skill_api import get_skill, list_skills, search_skills
from .skill_storage import get_skill_resource_path, _get_skill_dir

from pathlib import Path


def discover_skills(
    skill_type: Optional[str] = None,
    runtime: Optional[str] = None,
    skill_format: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conditions = ["s.status = 'ACTIVE'"]
    params: List[Any] = []
    params.append(50)

    if skill_type:
        conditions.append("s.skill_type = %s")
        params.insert(len(params) - 1, skill_type)
    if runtime:
        conditions.append("s.category = %s")
        params.insert(len(params) - 1, runtime)
    if skill_format:
        conditions.append("s.visibility = %s")
        params.insert(len(params) - 1, skill_format)
    if keyword:
        conditions.append("(s.skill_name ILIKE %s OR s.description ILIKE %s)")
        params.insert(len(params) - 1, f"%{keyword}%")
        params.insert(len(params) - 1, f"%{keyword}%")

    where = " AND ".join(conditions)
    sql = f"""
        SELECT s.skill_id, s.skill_name, s.skill_version, s.skill_type,
               s.description, s.category, s.visibility, s.owned_by_agent,
               s.status, s.resource_path, s.download_count, s.rating
        FROM skill_meta s
        WHERE {where}
        ORDER BY s.created_at DESC
        LIMIT %s
    """
    rows = execute_query(sql, params)
    return rows


def acquire_skill_text(skill_id: int) -> Optional[Dict[str, Any]]:
    skill = get_skill(skill_id)
    if skill is None:
        return None
    if skill.get("status") != "ACTIVE":
        return None

    return {
        "skill_id": skill_id,
        "skill_name": skill.get("skill_name"),
        "skill_version": skill.get("skill_version"),
        "skill_type": skill.get("skill_type"),
        "description": skill.get("description"),
        "category": skill.get("category"),
        "visibility": skill.get("visibility"),
        "owned_by_agent": skill.get("owned_by_agent"),
        "input_schema": skill.get("input_schema"),
        "output_schema": skill.get("output_schema"),
        "dependencies": skill.get("dependencies"),
        "has_resource": bool(skill.get("resource_path")),
        "resource_path": skill.get("resource_path"),
    }


def acquire_skill_resource(skill_id: int, agent_id: Optional[str] = None, session_id: Optional[int] = None) -> Optional[bytes]:
    skill = get_skill(skill_id)
    if skill is None or not skill.get("resource_path"):
        return None

    skill_dir = _get_skill_dir(skill_id)
    if not skill_dir.exists():
        p = get_skill_resource_path(skill_id)
        if p:
            return Path(p).read_bytes()
        return None

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in sorted(skill_dir.iterdir()):
            if f.is_file():
                zf.write(f, f.name)
    return buf.getvalue()


def acquire_skill_full(skill_id: int, agent_id: Optional[str] = None, session_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
    text_result = acquire_skill_text(skill_id)
    if text_result is None:
        return None

    resource_zip = None
    if text_result.get("has_resource"):
        resource_zip = acquire_skill_resource(skill_id, agent_id, session_id)

    result = {**text_result, "resource_zip": resource_zip}

    # v3.7.5: Auto-trigger validation loop if defined in skill metadata
    try:
        from .loop_api import create_validation_loop_for_skill
        validation_loop_id = create_validation_loop_for_skill(skill_id, agent_id or 'system')
    except Exception:
        pass

    return result


def discover_skills_via_admin(
    admin_url: str,
    admin_token: str,
    skill_type: Optional[str] = None,
    runtime: Optional[str] = None,
    keyword: Optional[str] = None,
) -> List[Dict[str, Any]]:
    from urllib.request import Request as _Request, urlopen as _urlopen
    from urllib.error import HTTPError as _HTTPError, URLError as _URLError

    url = f"{admin_url.rstrip('/')}/api/admin/skill/list?admin_token={admin_token}"
    if skill_type:
        url += f"&type={skill_type}"
    if runtime:
        url += f"&runtime={runtime}"
    if keyword:
        url += f"&keyword={keyword}"
    req = _Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with _urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("skills", [])
    except Exception:
        return []


def acquire_skill_via_admin(
    admin_url: str,
    admin_token: str,
    skill_id: int,
    include_resource: bool = False,
) -> Optional[Dict[str, Any]]:
    from urllib.request import Request as _Request, urlopen as _urlopen

    url = f"{admin_url.rstrip('/')}/api/admin/skill/{skill_id}/acquire?admin_token={admin_token}"
    if include_resource:
        url += "&resource=1"
    req = _Request(url, headers={"Accept": "application/json"}, method="GET")
    try:
        with _urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        if "error" in result:
            return None
        if include_resource and result.get("resource_encoding") == "base64" and result.get("resource_zip"):
            import base64
            result["resource_zip"] = base64.b64decode(result["resource_zip"])
            result.pop("resource_encoding", None)

        # v3.7.5: Auto-trigger validation loop if defined in skill metadata
        try:
            from .loop_api import create_validation_loop_for_skill
            validation_loop_id = create_validation_loop_for_skill(skill_id, 'system')
        except Exception:
            pass

        return result
    except Exception:
        return None


def check_skill_access(skill_id: int, agent_id: Optional[str] = None) -> Dict[str, Any]:
    skill = get_skill(skill_id)
    if skill is None:
        return {"accessible": False, "reason": "Skill not found"}
    visibility = skill.get("visibility", "SHARED")
    owner = skill.get("owned_by_agent")
    if visibility == "PUBLIC":
        return {"accessible": True, "visibility": visibility}
    if visibility == "SHARED":
        return {"accessible": True, "visibility": visibility}
    if visibility == "PRIVATE":
        if agent_id and agent_id == owner:
            return {"accessible": True, "visibility": visibility}
        return {"accessible": False, "reason": "Private skill, not owned by this agent"}
    return {"accessible": True, "visibility": visibility}
