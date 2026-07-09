"""AI Agent Infra v3.10.0 - PG Community Edition - Skill Storage & Distribution API

Supports direct database access and Admin API mode for Business Agents.
"""

import json
from typing import Any, Dict, List, Optional

from .connection import (
    execute,
    execute_query,
    execute_query_one,
    execute_insert_returning_id,
    sanitize_row,
)
from .skill_storage import store_skill_resource, delete_skill_resource, get_skill_resource_path

_JSON_COLUMNS = {"input_schema", "output_schema", "dependencies"}
_ALLOWED_UPDATE_FIELDS = {
    "skill_name", "skill_version", "description", "skill_type",
    "category", "visibility", "input_schema", "output_schema",
    "dependencies", "resource_path", "status",
}


def _row_to_dict(row: Dict[str, Any]) -> Dict[str, Any]:
    result = sanitize_row(row)
    for col in _JSON_COLUMNS:
        val = result.get(col)
        if isinstance(val, str):
            try:
                result[col] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def register_skill(
    skill_name: str,
    skill_version: str = "1.0.0",
    description: Optional[str] = None,
    skill_type: str = "TOOL",
    category: Optional[str] = None,
    visibility: str = "SHARED",
    owned_by_agent: Optional[str] = None,
    input_schema: Optional[Any] = None,
    output_schema: Optional[Any] = None,
    dependencies: Optional[Any] = None,
    resource_path: Optional[str] = None,
) -> int:
    row = execute_query_one(
        """SELECT skill_manager.register(
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        ) AS skill_id""",
        [skill_name, skill_version, description, skill_type, category,
         visibility, owned_by_agent,
         json.dumps(input_schema) if input_schema and not isinstance(input_schema, str) else input_schema,
         json.dumps(output_schema) if output_schema and not isinstance(output_schema, str) else output_schema,
         json.dumps(dependencies) if dependencies and not isinstance(dependencies, str) else dependencies,
         resource_path],
    )
    return row["skill_id"] if row else -1


def update_skill(skill_id: int, **kwargs: Any) -> bool:
    title = kwargs.get("title")
    updates: Dict[str, Any] = {}
    for k, v in kwargs.items():
        lk = k.lower()
        if lk in _ALLOWED_UPDATE_FIELDS and v is not None:
            if lk in _JSON_COLUMNS and not isinstance(v, str):
                updates[lk] = json.dumps(v)
            else:
                updates[lk] = v

    if not updates:
        return False

    row = execute_query_one(
        "SELECT skill_manager.update(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) AS result",
        [skill_id,
         updates.get("skill_name"), updates.get("skill_version"),
         updates.get("description"), updates.get("skill_type"),
         updates.get("category"), updates.get("visibility"),
         updates.get("input_schema"), updates.get("output_schema"),
         updates.get("dependencies"), updates.get("resource_path"),
         updates.get("status")],
    )
    return row is not None and row.get("result", False)


def delete_skill(skill_id: int) -> bool:
    delete_skill_resource(skill_id)
    row = execute_query_one(
        "SELECT skill_manager.delete(%s) AS result",
        [skill_id],
    )
    return row is not None and row.get("result", False)


def get_skill(skill_id: int) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        "SELECT skill_manager.get(%s) AS sj",
        [skill_id],
    )
    if row and row.get("sj"):
        val = row["sj"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return None


def list_skills(
    skill_type: Optional[str] = None,
    category: Optional[str] = None,
    skill_status: str = "ACTIVE",
    limit: int = 50,
) -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM skill_manager.list(%s, %s, %s, %s)",
        [skill_type, category, skill_status, limit],
    )
    return [sanitize_row(r) for r in rows]


def search_skills(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    rows = execute_query(
        "SELECT * FROM skill_manager.search(%s, %s)",
        [query, limit],
    )
    return [sanitize_row(r) for r in rows]


def validate_skill(skill_id: int) -> Dict[str, Any]:
    skill = get_skill(skill_id)
    errors: List[str] = []
    if skill is None:
        return {"valid": False, "errors": [f"Skill {skill_id} not found"]}
    if not skill.get("skill_name"):
        errors.append("SKILL_NAME is required")
    return {"valid": len(errors) == 0, "errors": errors}


def deprecate_skill(skill_id: int) -> bool:
    return update_skill(skill_id, status="DEPRECATED")


def register_skill_via_admin(
    admin_url: str,
    admin_token: str,
    title: str,
    skill_name: str,
    **kwargs,
) -> Optional[str]:
    import json as _json
    from urllib.request import Request as _Request, urlopen as _urlopen
    from urllib.error import HTTPError as _HTTPError, URLError as _URLError

    url = f"{admin_url.rstrip('/')}/api/admin/skill/create"
    payload = {
        "admin_token": admin_token,
        "title": title,
        "skill_name": skill_name,
        **kwargs,
    }
    body = _json.dumps(payload).encode("utf-8")
    req = _Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with _urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        if "error" in result:
            return None
        return result.get("skill_id")
    except Exception:
        return None


def update_skill_via_admin(
    admin_url: str,
    admin_token: str,
    skill_id: int,
    **kwargs,
) -> bool:
    import json as _json
    from urllib.request import Request as _Request, urlopen as _urlopen

    url = f"{admin_url.rstrip('/')}/api/admin/skill/update"
    payload = {"admin_token": admin_token, "skill_id": skill_id, **kwargs}
    body = _json.dumps(payload).encode("utf-8")
    req = _Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with _urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        return "skill" in result
    except Exception:
        return False


def delete_skill_via_admin(
    admin_url: str,
    admin_token: str,
    skill_id: int,
) -> bool:
    import json as _json
    from urllib.request import Request as _Request, urlopen as _urlopen

    url = f"{admin_url.rstrip('/')}/api/admin/skill/delete"
    payload = {"admin_token": admin_token, "skill_id": skill_id}
    body = _json.dumps(payload).encode("utf-8")
    req = _Request(url, data=body, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with _urlopen(req, timeout=30) as resp:
            result = _json.loads(resp.read().decode("utf-8"))
        return result.get("deleted", False)
    except Exception:
        return False


def upload_skill_resource(skill_id: int, filename: str, content: bytes) -> Optional[Dict[str, Any]]:
    skill = get_skill(skill_id)
    if skill is None:
        return None
    return store_skill_resource(skill_id, filename, content)


def get_skill_resource(skill_id: int) -> Optional[Dict[str, Any]]:
    skill = get_skill(skill_id)
    if skill is None:
        return None
    path = get_skill_resource_path(skill_id)
    return {
        "skill_id": skill_id,
        "has_resource": path is not None,
        "resource_path": path,
    }


def discover_skills(
    skill_type: Optional[str] = None,
    runtime: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    if keyword:
        return search_skills(keyword, limit=limit)
    return list_skills(skill_type=skill_type, skill_status="ACTIVE", limit=limit)


def get_skill_dependencies(skill_id: int) -> List[Dict[str, Any]]:
    skill = get_skill(skill_id)
    if skill is None:
        return []
    deps = skill.get("dependencies")
    if isinstance(deps, str):
        try:
            deps = json.loads(deps)
        except (json.JSONDecodeError, TypeError):
            return []
    if not isinstance(deps, list):
        return []
    resolved = []
    for dep_id in deps:
        dep = get_skill(dep_id)
        if dep is not None:
            resolved.append(dep)
    return resolved


def parse_skill_package(zip_bytes: bytes) -> Dict[str, Any]:
    from .skill_parser import parse_skill_zip
    meta, _ = parse_skill_zip(zip_bytes)
    return meta


def export_skill(skill_id: int) -> Optional[Dict[str, Any]]:
    skill = get_skill(skill_id)
    if skill is None:
        return None
    deps = get_skill_dependencies(skill_id)
    return {
        "skill": skill,
        "dependencies": deps,
    }
