# memory-pg18-by-yhw v0.3.2 Release Notes

**Release Date**: 2026-05-04  
**Version**: v0.3.2  
**Author**: Haiwen Yin (胖头鱼 🐟) - Database Expert  
**License**: Apache License 2.0

---

## 🆕 Summary of Changes

v0.3.2 introduces the **Task Plan Persistence System**. This release enables AI Agents to:

- ✅ Persist task execution state across session boundaries
- ✅ Recover exactly where interrupted after failures (breakpoint recovery)
- ✅ Learn from historical task patterns and completed executions
- ✅ Audit all tool calls during task execution

---

## ✨ New Features

### 1. Task Plan Persistence System

Five new database tables for comprehensive task tracking:

| Table | Purpose |
|-------|---------|
| `task_plans` | Core task plan (status, goals, priority) |
| `task_steps` | Step-by-step execution tracking |
| `task_context_snapshots` | Critical state snapshots for recovery |
| `task_tool_calls` | Complete tool call audit trail |
| `task_dependencies` | Task dependency graph |

### 2. Breakpoint Recovery API

```python
from scripts.task_plan_api import resume_task

# Resume exactly where interrupted
context = resume_task(plan_id=123)
# Returns: {"restored_context": {...}, "incomplete_steps": [...]}
```

**How it works:**
- Automatic snapshot on every tool call
- Mark latest snapshot with `is_latest = true` flag
- Restore agent_state, conversation_history, next_action
- Identify incomplete steps by checking status

### 3. Task Plan Python API

Three core functions for AI Agent integration:

```python
# Create new task plan with auto-snapshot
create_task_plan(
    plan_name="Deploy Database",
    plan_type="deployment",
    goal={"objective": "Migrate schema changes"}
)

# Resume from breakpoint
resume_task(plan_id=123)

# Search completed tasks for pattern learning
search_completed_tasks({"status": "SUCCESS"})
```

### 4. PostgreSQL Optimizations

- **JSONB over TEXT**: Native JSON indexing capabilities
- **SERIAL primary keys**: Auto-increment without sequences
- **TIMESTAMPTZ**: Timezone-aware timestamps
- **Proper indexes**: Optimized for common query patterns

---

## 📋 Feature Comparison: v0.3.1 vs v0.3.2

| Feature | v0.3.1 | **v0.3.2** |
|---------|--------|------------|
| Task Plan Storage | ❌ Not included | ✅ Complete System (5 tables) |
| Breakpoint Recovery | ❌ None | ✅ Auto Snapshot + Resume API |
| Historical Learning | ❌ Limited | ✅ Pattern Recognition |
| Status Tracking | ❌ Basic | ✅ Detailed Step-by-Step Audit |
| Tool Call Logging | ❌ No audit trail | ✅ Full tool call tracking |

---

## 📁 Files Added/Modified in v0.3.2

### New Files:
- `scripts/init_task_plan_system.sql` - Task Plan DDL schema
- `scripts/task_plan_api.py` - Python API functions (create/resume/search)
- `RELEASE_NOTES_v0.3.2.md` - This file

### Modified Files:
- `VERSION` - Updated to 0.3.2
- `SKILL.md` - Added Task Plan System documentation
- `README.md` - Updated feature comparison and quick start
- `CHANGELOG.md` - Added v0.3.2 entry

---

## 🧪 Testing Recommendations

Before deploying v0.3.2 to production:

1. **Verify schema creation:**
   ```sql
   SELECT count(*) FROM information_schema.tables 
   WHERE table_name IN ('task_plans', 'task_steps', 'task_context_snapshots');
   -- Should return 5
   ```

2. **Test API functions:**
   ```python
   from scripts.task_plan_api import create_task_plan, resume_task
   
   # Create and verify
   plan = create_task_plan("Test Plan", "test")
   
   # Resume (should work even without interruption)
   context = resume_task(plan['plan_id'])
   print(f"Restored: {len(context.get('incomplete_steps', []))} incomplete steps")
   ```

3. **Verify indexes:**
   ```sql
   SELECT indexname FROM pg_indexes WHERE tablename LIKE 'task%';
   -- Should show idx_* indexes for all 5 tables
   ```

---

## 📝 Migration Notes (from v0.3.1)

No migration required - new tables are created with `IF NOT EXISTS`. Existing memory system functions remain unchanged.

**Recommended next steps:**
1. Deploy schema to your PostgreSQL 18 instance
2. Configure TaskPlanAPI connection parameters
3. Integrate into your AI Agent workflow
4. Monitor task patterns for optimization opportunities

---

**Enjoy using memory-pg18-by-yhw v0.3.2!** 🚀
