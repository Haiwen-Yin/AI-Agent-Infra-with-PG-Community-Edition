"""AI Agent Infra v3.5.0 - PG Community Edition - Skill Package Parser

Parse skill packages (zip archives containing SKILL.md) and extract metadata + files.
Supports three metadata sources by priority:
1. _meta.json (ClawHub standard: slug + version)
2. SKILL.md YAML frontmatter (name + description)
3. SKILL.md ## Metadata section (existing format)
"""

import io
import json
import re
import zipfile
from pathlib import Path
from typing import Any, Dict, Tuple


def _parse_yaml_frontmatter(content: str) -> Dict[str, str]:
    result: Dict[str, str] = {}
    if not content.startswith("---"):
        return result
    end = content.find("---", 3)
    if end == -1:
        return result
    fm = content[3:end].strip()
    for line in fm.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"(\w+)\s*:\s*(.+)", line)
        if m:
            key = m.group(1).strip().lower()
            val = m.group(2).strip().strip('"').strip("'")
            result[key] = val
    return result


def _parse_meta_json(raw: bytes) -> Dict[str, Any]:
    try:
        data = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return {}
    result: Dict[str, Any] = {}
    if "slug" in data:
        result["skill_name"] = data["slug"]
    if "version" in data:
        result["skill_version"] = str(data["version"])
    if "publishedAt" in data:
        import time
        result["published_at"] = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(data["publishedAt"] / 1000))
    return result


def parse_skill_md(content: str) -> Dict[str, Any]:
    meta: Dict[str, Any] = {
        "title": "",
        "skill_name": "",
        "skill_version": "1.0.0",
        "skill_type": "CUSTOM",
        "skill_format": "TEXT",
        "runtime": "PYTHON",
        "text_content": "",
        "skill_description": "",
        "parameters": None,
        "dependencies": None,
        "category": None,
        "owned_by_agent": None,
        "visibility": "SHARED",
    }

    fm = _parse_yaml_frontmatter(content)
    if "name" in fm:
        meta["skill_name"] = fm["name"]
        if not meta["title"]:
            meta["title"] = fm["name"]
    if "description" in fm:
        meta["skill_description"] = fm["description"]
    if "runtime" in fm:
        meta["runtime"] = fm["runtime"].upper()
    if "format" in fm:
        meta["skill_format"] = fm["format"].upper()

    yaml_end = 0
    if content.startswith("---"):
        end = content.find("---", 3)
        if end != -1:
            yaml_end = end + 3

    body = content[yaml_end:].lstrip("\n")

    current_section = None
    text_lines: list = []

    for line in body.splitlines():
        stripped = line.strip()

        if stripped.startswith("# ") and not meta["title"]:
            meta["title"] = stripped[2:].strip()
            continue

        if stripped.startswith("## "):
            section_name = stripped[3:].strip().lower()
            if section_name in ("metadata", "\u5143\u6570\u636e"):
                current_section = "metadata"
                continue
            elif section_name in ("content", "\u6587\u672c\u5185\u5bb9", "description"):
                current_section = "content"
                continue
            else:
                current_section = "other"
                continue

        if current_section == "metadata":
            m = re.match(r"[-*]\s+\*\*([^*]+)\*\*\s*[:：]\s*(.+)", stripped)
            if m:
                key = m.group(1).strip().lower().replace(" ", "_")
                val = m.group(2).strip()
                key_map = {
                    "name": "skill_name", "skill_name": "skill_name",
                    "version": "skill_version", "skill_version": "skill_version",
                    "type": "skill_type", "skill_type": "skill_type",
                    "format": "skill_format", "skill_format": "skill_format",
                    "runtime": "runtime", "category": "category",
                    "visibility": "visibility", "parameters": "parameters",
                    "dependencies": "dependencies",
                }
                mapped = key_map.get(key)
                if mapped:
                    if mapped in ("parameters", "dependencies"):
                        try:
                            meta[mapped] = json.loads(val)
                        except (json.JSONDecodeError, TypeError):
                            meta[mapped] = val
                    else:
                        meta[mapped] = val
            continue

        if current_section == "content":
            text_lines.append(line)

    if text_lines:
        meta["text_content"] = "\n".join(text_lines).strip()

    if not meta["skill_name"]:
        name_from_title = meta["title"].lower().replace(" ", "_")
        meta["skill_name"] = re.sub(r"[^a-z0-9_]", "", name_from_title) or "unnamed_skill"

    return meta


def parse_skill_zip(zip_bytes: bytes) -> Tuple[Dict[str, Any], Dict[str, bytes]]:
    bio = io.BytesIO(zip_bytes)
    if not zipfile.is_zipfile(bio):
        raise ValueError("Not a valid ZIP archive")

    bio.seek(0)
    with zipfile.ZipFile(bio, "r") as zf:
        names = zf.namelist()

        skill_md_name = None
        meta_json_name = None
        for n in names:
            basename = Path(n).name
            if basename == "SKILL.md":
                skill_md_name = n
            elif basename == "_meta.json":
                meta_json_name = n

        if skill_md_name is None:
            raise ValueError("SKILL.md not found in archive. The zip must contain a SKILL.md file.")

        skill_md_content = zf.read(skill_md_name).decode("utf-8")
        meta = parse_skill_md(skill_md_content)

        if meta_json_name is not None:
            meta_json_data = _parse_meta_json(zf.read(meta_json_name))
            if "skill_name" in meta_json_data:
                meta["skill_name"] = meta_json_data["skill_name"]
            if "skill_version" in meta_json_data:
                meta["skill_version"] = meta_json_data["skill_version"]
            if "published_at" in meta_json_data:
                meta["published_at"] = meta_json_data["published_at"]

        has_script = False
        resource_files: Dict[str, bytes] = {}
        for n in names:
            if n == skill_md_name or n == meta_json_name:
                continue
            if n.endswith("/"):
                continue
            basename = Path(n).name
            if basename.startswith(".") or basename.startswith("__"):
                continue
            data = zf.read(n)
            resource_files[n] = data
            ext = Path(n).suffix.lower()
            if ext in (".py", ".sh", ".bash", ".js", ".ts", ".rb", ".go"):
                has_script = True

        if has_script and meta["skill_format"] == "TEXT":
            meta["skill_format"] = "SCRIPT" if not meta["text_content"] else "HYBRID"

    return meta, resource_files


def validate_skill_structure(zip_bytes: bytes) -> Dict[str, Any]:
    errors = []
    try:
        bio = io.BytesIO(zip_bytes)
        if not zipfile.is_zipfile(bio):
            return {"valid": False, "errors": ["Not a valid ZIP archive"]}
        bio.seek(0)
        with zipfile.ZipFile(bio, "r") as zf:
            names = zf.namelist()
            has_skill_md = any(Path(n).name == "SKILL.md" for n in names)
            if not has_skill_md:
                errors.append("SKILL.md not found in archive")
            for n in names:
                if Path(n).suffix.lower() in (".exe", ".bat", ".cmd", ".msi"):
                    errors.append(f"Potentially unsafe file: {n}")
    except Exception as e:
        errors.append(f"Archive error: {e}")
    return {"valid": len(errors) == 0, "errors": errors}


def extract_skill_metadata(zip_bytes: bytes) -> Dict[str, Any]:
    meta, _ = parse_skill_zip(zip_bytes)
    return meta
