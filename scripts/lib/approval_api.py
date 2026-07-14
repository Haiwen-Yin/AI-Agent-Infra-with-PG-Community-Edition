"""AI Agent Infra v3.10.1 - Community Edition - Approval API

Unified approval management for Human-in-the-Loop workflows.
Supports three entity types: STEP (orchestrator), LOOP (loop runs), TOOL (tool calls).

Table: APPROVAL_REQUESTS
"""

import json
import logging
from typing import Any, Dict, List, Optional

from .connection import (
    execute,
    execute_query,
    execute_query_one,
    execute_insert_returning_id,
    sanitize_row,
)

logger = logging.getLogger(__name__)


def create_request(entity_type: str, entity_id: str, requested_by: str) -> Optional[str]:
    try:
        from .event_bus import publish_event
    except ImportError:
        publish_event = None

    approval_id = execute_insert_returning_id(
        """INSERT INTO APPROVAL_REQUESTS (APPROVAL_ID, ENTITY_TYPE, ENTITY_ID, REQUESTED_BY)
           VALUES (gen_random_uuid()::text, %s, %s, %s)
           RETURNING APPROVAL_ID""",
        (entity_type, entity_id, requested_by),
    )

    if approval_id and publish_event:
        try:
            publish_event(
                event_type="APPROVAL_REQUIRED",
                source_id=requested_by,
                source_type="AGENT",
                payload={"approval_id": approval_id, "entity_type": entity_type, "entity_id": entity_id},
            )
        except Exception:
            pass

    logger.info("Approval request created: %s for %s:%s", approval_id, entity_type, entity_id)
    return approval_id


def approve(approval_id: str, approver: str) -> bool:
    result = execute(
        """UPDATE APPROVAL_REQUESTS
           SET APPROVAL_STATUS = 'APPROVED', APPROVED_BY = %s, APPROVED_AT = NOW()
           WHERE APPROVAL_ID = %s AND APPROVAL_STATUS = 'PENDING'""",
        (approver, approval_id),
    )
    if result > 0:
        _notify_entity_approval(approval_id, "APPROVED")
        logger.info("Approval %s approved by %s", approval_id, approver)
    return result > 0


def reject(approval_id: str, approver: str, reason: str = "") -> bool:
    result = execute(
        """UPDATE APPROVAL_REQUESTS
           SET APPROVAL_STATUS = 'REJECTED', APPROVED_BY = %s, APPROVED_AT = NOW(),
               REJECT_REASON = %s
           WHERE APPROVAL_ID = %s AND APPROVAL_STATUS = 'PENDING'""",
        (approver, reason, approval_id),
    )
    if result > 0:
        _notify_entity_approval(approval_id, "REJECTED")
        logger.info("Approval %s rejected by %s: %s", approval_id, approver, reason)
    return result > 0


def get_request(approval_id: str) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        """SELECT APPROVAL_ID, ENTITY_TYPE, ENTITY_ID, REQUESTED_BY,
                  APPROVAL_STATUS, APPROVED_BY, APPROVED_AT, REJECT_REASON, CREATED_AT
           FROM APPROVAL_REQUESTS WHERE APPROVAL_ID = %s""",
        (approval_id,),
    )
    return sanitize_row(row) if row else None


def list_pending(entity_type: Optional[str] = None, limit: int = 50) -> List[Dict[str, Any]]:
    if entity_type:
        rows = execute_query(
            """SELECT APPROVAL_ID, ENTITY_TYPE, ENTITY_ID, REQUESTED_BY,
                      APPROVAL_STATUS, CREATED_AT
               FROM APPROVAL_REQUESTS
               WHERE APPROVAL_STATUS = 'PENDING' AND ENTITY_TYPE = %s
               ORDER BY CREATED_AT DESC
               LIMIT %s""",
            (entity_type, limit),
        )
    else:
        rows = execute_query(
            """SELECT APPROVAL_ID, ENTITY_TYPE, ENTITY_ID, REQUESTED_BY,
                      APPROVAL_STATUS, CREATED_AT
               FROM APPROVAL_REQUESTS
               WHERE APPROVAL_STATUS = 'PENDING'
               ORDER BY CREATED_AT DESC
               LIMIT %s""",
            (limit,),
        )
    return [sanitize_row(r) for r in rows] if rows else []


def list_all(limit: int = 100) -> List[Dict[str, Any]]:
    rows = execute_query(
        """SELECT APPROVAL_ID, ENTITY_TYPE, ENTITY_ID, REQUESTED_BY,
                  APPROVAL_STATUS, APPROVED_BY, APPROVED_AT, REJECT_REASON, CREATED_AT
           FROM APPROVAL_REQUESTS
           ORDER BY CREATED_AT DESC
           LIMIT %s""",
        (limit,),
    )
    return [sanitize_row(r) for r in rows] if rows else []


def check_approval_needed(entity_type: str, entity_id: str) -> bool:
    if entity_type == "STEP":
        row = execute_query_one(
            "SELECT REQUIRES_APPROVAL FROM STEP_EXECUTION_PLAN WHERE PLAN_ID = %s",
            (entity_id,),
        )
        return row and row.get("requires_approval") == "Y"
    elif entity_type == "LOOP":
        row = execute_query_one(
            "SELECT REQUIRE_APPROVAL FROM LOOP_META WHERE LOOP_ID = %s",
            (entity_id,),
        )
        return row and row.get("require_approval") == "Y"
    elif entity_type == "TOOL":
        row = execute_query_one(
            "SELECT REQUIRES_APPROVAL FROM TOOL_REGISTRY WHERE TOOL_ID = %s",
            (entity_id,),
        )
        return row and row.get("requires_approval") == "Y"
    return False


def get_pending_for_entity(entity_type: str, entity_id: str) -> Optional[Dict[str, Any]]:
    row = execute_query_one(
        """SELECT APPROVAL_ID, APPROVAL_STATUS, REQUESTED_BY, CREATED_AT
           FROM APPROVAL_REQUESTS
           WHERE ENTITY_TYPE = %s AND ENTITY_ID = %s
             AND APPROVAL_STATUS = 'PENDING'
           ORDER BY CREATED_AT DESC
           LIMIT 1""",
        (entity_type, entity_id),
    )
    return sanitize_row(row) if row else None


def _notify_entity_approval(approval_id: str, decision: str):
    try:
        from .event_bus import publish_event
        req = get_request(approval_id)
        if req:
            publish_event(
                event_type="APPROVAL_DECIDED",
                source_id=req.get("approved_by", "system"),
                source_type="AGENT",
                payload={
                    "approval_id": approval_id,
                    "entity_type": req.get("entity_type"),
                    "entity_id": req.get("entity_id"),
                    "decision": decision,
                },
            )
    except Exception:
        pass


def get_stats() -> Dict[str, Any]:
    rows = execute_query(
        """SELECT APPROVAL_STATUS, COUNT(*) AS cnt
           FROM APPROVAL_REQUESTS
           GROUP BY APPROVAL_STATUS""",
        (),
    )
    stats = {"total": 0, "pending": 0, "approved": 0, "rejected": 0}
    if rows:
        for r in rows:
            status = r.get("approval_status", "").lower()
            count = r.get("cnt", 0)
            stats[status] = count
            stats["total"] += count
    return stats
