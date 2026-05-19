"""PostgreSQL Memory System v2.0.0 - Configuration"""

import json
import os
from pathlib import Path


class DatabaseConfig:
    def __init__(self, host='10.10.10.131', port=5432, database='memory_graph',
                 user='pgsql', password='', min_conn=2, max_conn=5):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.min_conn = min_conn
        self.max_conn = max_conn


class ServerConfig:
    def __init__(self, host='0.0.0.0', port=8000, session_timeout=300):
        self.host = host
        self.port = port
        self.session_timeout = session_timeout


class EmbeddingConfig:
    def __init__(self, api_url='http://10.10.10.1:12345/v1/embeddings',
                 model='text-embedding-bge-m3', dimension=1024):
        self.api_url = api_url
        self.model = model
        self.dimension = dimension


class SecurityConfig:
    def __init__(self, masking_enabled=True, pbkdf2_iterations=100000,
                 max_login_attempts=5, lockout_minutes=15):
        self.masking_enabled = masking_enabled
        self.pbkdf2_iterations = pbkdf2_iterations
        self.max_login_attempts = max_login_attempts
        self.lockout_minutes = lockout_minutes


class Config:
    def __init__(self):
        self.database = DatabaseConfig()
        self.server = ServerConfig()
        self.embedding = EmbeddingConfig()
        self.security = SecurityConfig()
        self.project_root = Path(__file__).resolve().parent.parent.parent
        self._load_config_file()

    def _load_config_file(self):
        config_path = self.project_root / 'config.json'
        if not config_path.exists():
            return
        try:
            with open(config_path, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        if 'database' in data:
            for k, v in data['database'].items():
                if hasattr(self.database, k):
                    setattr(self.database, k, v)
        if 'server' in data:
            for k, v in data['server'].items():
                if hasattr(self.server, k):
                    setattr(self.server, k, v)
        if 'embedding' in data:
            for k, v in data['embedding'].items():
                if hasattr(self.embedding, k):
                    setattr(self.embedding, k, v)
        if 'security' in data:
            for k, v in data['security'].items():
                if hasattr(self.security, k):
                    setattr(self.security, k, v)


def load_config():
    config = Config()

    env_map = {
        'MEMORY_DB_HOST': ('database', 'host'),
        'MEMORY_DB_PORT': ('database', 'port', int),
        'MEMORY_DB_NAME': ('database', 'database'),
        'MEMORY_DB_USER': ('database', 'user'),
        'MEMORY_DB_PASSWORD': ('database', 'password'),
        'MEMORY_SERVER_PORT': ('server', 'port', int),
        'MEMORY_EMBEDDING_API': ('embedding', 'api_url'),
    }

    for env_var, spec in env_map.items():
        val = os.environ.get(env_var)
        if val is not None:
            section = getattr(config, spec[0])
            attr = spec[1]
            converter = spec[2] if len(spec) > 2 else None
            setattr(section, attr, converter(val) if converter else val)

    return config


_config_instance = None


def get_config():
    global _config_instance
    if _config_instance is None:
        _config_instance = load_config()
    return _config_instance
