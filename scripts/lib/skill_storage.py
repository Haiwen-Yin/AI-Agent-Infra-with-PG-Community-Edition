"""AI Agent Infra v3.10.2 - PG Community Edition - Skill Resource Storage Abstraction Layer"""

import hashlib
import mimetypes
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from .connection import execute, execute_query_one

SKILL_RESOURCE_BASE_DIR = Path(__file__).parent.parent.parent / "data" / "skill_resources"


def _ensure_base_dir() -> Path:
    SKILL_RESOURCE_BASE_DIR.mkdir(parents=True, exist_ok=True)
    return SKILL_RESOURCE_BASE_DIR


def _get_skill_dir(skill_id) -> Path:
    return _ensure_base_dir() / str(skill_id)


def _compute_checksum(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _guess_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"


def create_skill_directory(skill_id) -> Path:
    skill_dir = _get_skill_dir(skill_id)
    skill_dir.mkdir(parents=True, exist_ok=True)
    return skill_dir


def store_skill_resource(skill_id, filename: str, content: bytes) -> Dict[str, Any]:
    skill_dir = _get_skill_dir(skill_id)
    skill_dir.mkdir(parents=True, exist_ok=True)

    safe_filename = Path(filename).name
    file_path = skill_dir / safe_filename

    file_path.write_bytes(content)

    checksum = _compute_checksum(content)
    size = len(content)
    mime_type = _guess_mime_type(safe_filename)
    relative_uri = f"skill_resources/{skill_id}/{safe_filename}"

    execute(
        """UPDATE skill_meta SET
              resource_path = %s
           WHERE skill_id = %s""",
        [relative_uri, skill_id],
    )

    return {
        "path": str(file_path),
        "relative_uri": relative_uri,
        "filename": safe_filename,
        "size": size,
        "mime_type": mime_type,
        "checksum": checksum,
    }


def get_skill_resource_path(skill_id) -> Optional[str]:
    row = execute_query_one(
        "SELECT resource_path FROM skill_meta WHERE skill_id = %s",
        [skill_id],
    )
    if row is None or not row.get("resource_path"):
        return None

    relative_uri = row["resource_path"]
    file_path = SKILL_RESOURCE_BASE_DIR.parent / relative_uri
    if file_path.exists():
        return str(file_path)
    return None


def delete_skill_resource(skill_id) -> bool:
    skill_dir = _get_skill_dir(skill_id)
    deleted = False

    if skill_dir.exists():
        for f in skill_dir.iterdir():
            f.unlink()
            deleted = True
        skill_dir.rmdir()

    execute(
        "UPDATE skill_meta SET resource_path = NULL WHERE skill_id = %s",
        [skill_id],
    )

    return deleted


def list_skill_resources(skill_id) -> List[Dict[str, Any]]:
    skill_dir = _get_skill_dir(skill_id)
    if not skill_dir.exists():
        return []
    results = []
    for f in sorted(skill_dir.iterdir()):
        if f.is_file():
            results.append({
                "filename": f.name,
                "size": f.stat().st_size,
                "path": str(f),
            })
    return results


def calculate_checksum(content: bytes) -> str:
    return _compute_checksum(content)


def get_resource_filename(skill_id) -> Optional[str]:
    row = execute_query_one(
        "SELECT resource_path FROM skill_meta WHERE skill_id = %s",
        [skill_id],
    )
    if row and row.get("resource_path"):
        path = Path(row["resource_path"])
        return path.name
    return None


def get_resource_size(skill_id) -> Optional[int]:
    path = get_skill_resource_path(skill_id)
    if path:
        return Path(path).stat().st_size
    return None


def verify_resource_integrity(skill_id) -> Dict[str, Any]:
    skill_dir = _get_skill_dir(skill_id)
    if not skill_dir.exists():
        return {"skill_id": skill_id, "valid": False, "error": "resource directory not found"}

    total_size = 0
    file_count = 0
    for f in skill_dir.iterdir():
        if f.is_file():
            total_size += f.stat().st_size
            file_count += 1

    return {
        "skill_id": skill_id,
        "valid": True,
        "file_count": file_count,
        "total_size": total_size,
    }


def cleanup_skill_resources(max_age_days: int = 90) -> int:
    import time
    cutoff = time.time() - (max_age_days * 86400)
    count = 0
    if not SKILL_RESOURCE_BASE_DIR.exists():
        return 0
    for skill_dir in SKILL_RESOURCE_BASE_DIR.iterdir():
        if skill_dir.is_dir():
            mtime = skill_dir.stat().st_mtime
            if mtime < cutoff:
                for f in skill_dir.iterdir():
                    if f.is_file():
                        f.unlink()
                skill_dir.rmdir()
                count += 1
    return count


def backup_skill(skill_id, backup_dir: Optional[str] = None) -> Optional[str]:
    import shutil
    skill_dir = _get_skill_dir(skill_id)
    if not skill_dir.exists():
        return None
    backup_base = Path(backup_dir) if backup_dir else SKILL_RESOURCE_BASE_DIR.parent / "skill_backups"
    backup_base.mkdir(parents=True, exist_ok=True)
    backup_path = backup_base / str(skill_id)
    if backup_path.exists():
        shutil.rmtree(backup_path)
    shutil.copytree(skill_dir, backup_path)
    return str(backup_path)


def restore_skill(skill_id, backup_dir: Optional[str] = None) -> bool:
    import shutil
    backup_base = Path(backup_dir) if backup_dir else SKILL_RESOURCE_BASE_DIR.parent / "skill_backups"
    backup_path = backup_base / str(skill_id)
    if not backup_path.exists():
        return False
    skill_dir = _get_skill_dir(skill_id)
    if skill_dir.exists():
        shutil.rmtree(skill_dir)
    shutil.copytree(backup_path, skill_dir)
    return True
