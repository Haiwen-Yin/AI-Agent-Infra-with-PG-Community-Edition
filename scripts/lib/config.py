"""AI Agent Infra v3.7.5 - PG Community Edition - Unified Configuration Manager

Reads from config.json with environment variable fallback.
Priority: config.json > Environment Variables > Built-in defaults
Supports Admin/Agent separation modes (standalone, admin, agent).
"""

import json
import logging
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)

VERSION = "3.7.5"

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    dbname: str = "ai_agent"
    user: str = "pgsql"
    password: str = ""
    min_conn: int = 2
    max_conn: int = 5


@dataclass(frozen=True)
class ServerConfig:
    host: str = "0.0.0.0"
    port: int = 18080
    session_timeout: int = 300


@dataclass(frozen=True)
class EmbeddingConfig:
    api_url: str = ""
    model: str = ""
    dimension: int = 0


@dataclass(frozen=True)
class SecurityConfig:
    masking_enabled: bool = True
    pbkdf2_iterations: int = 210000
    max_login_attempts: int = 5
    lockout_minutes: int = 15


@dataclass(frozen=True)
class AgentModeConfig:
    mode: str = "standalone"
    admin_token: Optional[str] = None
    admin_api_url: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass(frozen=True)
class Config:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    agent: AgentModeConfig = field(default_factory=AgentModeConfig)
    project_root: Path = field(default_factory=lambda: _PROJECT_ROOT)


def _load_config_file() -> dict:
    config_path = _PROJECT_ROOT / "config.json"
    if config_path.exists():
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def load_config() -> Config:
    raw = _load_config_file()

    db_raw = raw.get("database", {})
    srv_raw = raw.get("server", {})
    emb_raw = raw.get("embedding", {})
    sec_raw = raw.get("security", {})

    # Priority: config.json > Environment Variables > Defaults
    db = DatabaseConfig(
        host=db_raw.get("host") or os.environ.get("AI_AGENT_DB_HOST", DatabaseConfig.host),
        port=int(db_raw.get("port") or os.environ.get("AI_AGENT_DB_PORT", DatabaseConfig.port)),
        dbname=db_raw.get("dbname") or os.environ.get("AI_AGENT_DB_NAME", DatabaseConfig.dbname),
        user=db_raw.get("user") or os.environ.get("AI_AGENT_DB_USER", DatabaseConfig.user),
        password=db_raw.get("password") or os.environ.get("AI_AGENT_DB_PASSWORD", DatabaseConfig.password),
        min_conn=int(db_raw.get("min_conn", DatabaseConfig.min_conn)),
        max_conn=int(db_raw.get("max_conn", DatabaseConfig.max_conn)),
    )

    srv = ServerConfig(
        host=srv_raw.get("host") or os.environ.get("AI_AGENT_SERVER_HOST", ServerConfig.host),
        port=int(srv_raw.get("port") or os.environ.get("AI_AGENT_SERVER_PORT", ServerConfig.port)),
        session_timeout=int(srv_raw.get("session_timeout") or os.environ.get("AI_AGENT_SESSION_TIMEOUT", ServerConfig.session_timeout)),
    )

    emb = EmbeddingConfig(
        api_url=emb_raw.get("api_url") or os.environ.get("AI_AGENT_EMBEDDING_API", EmbeddingConfig.api_url),
        model=emb_raw.get("model") or os.environ.get("AI_AGENT_EMBEDDING_MODEL", EmbeddingConfig.model),
        dimension=int(emb_raw.get("dimension") or os.environ.get("AI_AGENT_EMBEDDING_DIM", EmbeddingConfig.dimension)),
    )

    sec = SecurityConfig(
        masking_enabled=sec_raw.get("masking_enabled", SecurityConfig.masking_enabled),
        pbkdf2_iterations=int(sec_raw.get("pbkdf2_iterations", SecurityConfig.pbkdf2_iterations)),
        max_login_attempts=int(sec_raw.get("max_login_attempts", SecurityConfig.max_login_attempts)),
        lockout_minutes=int(sec_raw.get("lockout_minutes", SecurityConfig.lockout_minutes)),
    )

    agent_raw = raw.get("agent", {})
    agt = AgentModeConfig(
        mode=agent_raw.get("mode") or os.environ.get("AI_AGENT_MODE", AgentModeConfig.mode),
        admin_token=agent_raw.get("admin_token") or os.environ.get("AI_AGENT_ADMIN_TOKEN", AgentModeConfig.admin_token),
        admin_api_url=agent_raw.get("admin_api_url") or os.environ.get("AI_AGENT_ADMIN_API_URL", AgentModeConfig.admin_api_url),
        agent_id=agent_raw.get("agent_id") or os.environ.get("AI_AGENT_ID", AgentModeConfig.agent_id),
    )

    return Config(database=db, server=srv, embedding=emb, security=sec, agent=agt, project_root=_PROJECT_ROOT)


_config: Optional[Config] = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = load_config()
    return _config
