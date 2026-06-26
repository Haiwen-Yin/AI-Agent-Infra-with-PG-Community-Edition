"""AI Agent Infra v3.7.4 - PG Community Edition - Deployment Check API

Pre-deployment safety checks for AI Agents.
Agents MUST call check_deployment() before running any deploy scripts.
"""

import json
import logging
from typing import Any, Dict

from .connection import execute_query

logger = logging.getLogger(__name__)


def check_deployment() -> Dict[str, Any]:
    row = execute_query_one(
        "SELECT deploy_api.check_deployment() AS result"
    )
    if row and row.get("result"):
        val = row["result"]
        if isinstance(val, str):
            return json.loads(val)
        return val
    return {
        "deployed": False,
        "schema_version": None,
        "table_count": 0,
        "edition": None,
        "agent_count": 0,
        "user_count": 0,
        "recommendation": "Unable to check deployment status.",
    }
