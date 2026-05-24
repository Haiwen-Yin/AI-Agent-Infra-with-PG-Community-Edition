"""PostgreSQL Memory System v2.2.1 - Configuration"""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class DatabaseConfig:
    host: str = '10.10.10.131'
    port: int = 5432
    database: str = 'memory_graph'
    user: str = 'pgsql'
    password: str = ''
    min_conn: int = 2
    max_conn: int = 5


@dataclass
class ServerConfig:
    host: str = '0.0.0.0'
    port: int = 8000
    session_timeout: int = 300


@dataclass
class EmbeddingConfig:
    api_url: str = 'http://10.10.10.1:12345/v1/embeddings'
    model: str = 'text-embedding-bge-m3'
    dimension: int = 1024


@dataclass
class SecurityConfig:
    masking_enabled: bool = True
    pbkdf2_iterations: int = 100000
    max_login_attempts: int = 5
    lockout_minutes: int = 15


@dataclass
class Config:
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    server: ServerConfig = field(default_factory=ServerConfig)
    embedding: EmbeddingConfig = field(default_factory=EmbeddingConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    project_root: str = field(default_factory=lambda: str(Path(__file__).resolve().parent.parent.parent))

    def __post_init__(self):
        self._load_config_file()
        self._load_env_overrides()

    def _load_config_file(self):
        config_path = Path(self.project_root) / 'config.json'
        if not config_path.exists():
            return
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        section_map = {
            'database': self.database,
            'server': self.server,
            'embedding': self.embedding,
            'security': self.security,
        }
        for section_key, section_obj in section_map.items():
            if section_key in data:
                for k, v in data[section_key].items():
                    if hasattr(section_obj, k):
                        setattr(section_obj, k, v)

    def _load_env_overrides(self):
        env_map = {
            'MEMORY_DB_HOST': (self.database, 'host', None),
            'MEMORY_DB_PORT': (self.database, 'port', int),
            'MEMORY_DB_NAME': (self.database, 'database', None),
            'MEMORY_DB_USER': (self.database, 'user', None),
            'MEMORY_DB_PASSWORD': (self.database, 'password', None),
            'MEMORY_SERVER_PORT': (self.server, 'port', int),
            'MEMORY_EMBEDDING_API': (self.embedding, 'api_url', None),
        }
        for env_var, (obj, attr, converter) in env_map.items():
            val = os.environ.get(env_var)
            if val is not None:
                setattr(obj, attr, converter(val) if converter else val)


_config_instance = None


def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = Config()
    return _config_instance
