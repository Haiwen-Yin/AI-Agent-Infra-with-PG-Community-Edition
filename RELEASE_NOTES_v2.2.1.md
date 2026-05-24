# Release Notes - memory-pg18-by-yhw v2.2.1

**Author**: Haiwen Yin (胖头鱼)
**Date**: 2026-05-24
**License**: Apache License 2.0

---

## v2.2.1 — UI Bug Fixes

v2.2.1 is a patch release fixing two UI issues discovered after v2.2.0 deployment. No database schema, API, or test changes.

### Bug Fixes

| Issue | Root Cause | Fix |
|-------|-----------|-----|
| Language toggle resets to English when navigating between pages | `data-lang` attribute set on `<html>` but lost on page load (always defaults to `en`) | All 7 HTML pages now save language to `localStorage` on toggle and restore it on page init |
| Tasks page step table and Plan Details text unreadable on dark background | `.data-table tbody td` and Plan Details values inherited `color:var(--text-primary)` (#e0e0e0) which blends with dark card background | Changed to `color:#fff` for step table cells and Plan Details grid values |

### Files Changed

| File | Change |
|------|--------|
| `scripts/visualization/server.py` | Version string: `2.2.0` → `2.2.1` |
| `scripts/visualization/templates/agents.html` | Added `localStorage` save/restore for language |
| `scripts/visualization/templates/graph.html` | Added `localStorage` save/restore for language |
| `scripts/visualization/templates/knowledge.html` | Added `localStorage` save/restore for language |
| `scripts/visualization/templates/login.html` | Added `localStorage` save/restore for language |
| `scripts/visualization/templates/memory.html` | Added `localStorage` save/restore for language |
| `scripts/visualization/templates/tasks.html` | Added `localStorage` save/restore; `.data-table tbody td{color:#fff}`; Plan Details `color:#fff` |
| `scripts/visualization/templates/workspaces.html` | Added `localStorage` save/restore; `.data-table tbody td{color:#fff}` |
| `VERSION` | `v2.2.0` → `v2.2.1` |

### Compatibility

- **Database**: No changes (compatible with v2.2.0 schema)
- **API**: No changes (115/115 tests still pass)
- **Python**: 3.14+ recommended, 3.6+ minimum
- **psycopg2-binary**: 2.8.6+

### Test Results

```
PostgreSQL Memory System v2.2.1 - Full Test Suite
============================================================
  Connection:  6/6 PASS
  Memory:     16/16 PASS
  Knowledge:  19/19 PASS
  Agent:      17/17 PASS
  Security:   19/19 PASS
  Graph:      12/12 PASS
  Harness:    12/12 PASS
  Workspace:  14/14 PASS
Overall: 115/115 ALL PASSED
```

---

**Release Date**: 2026-05-24
**Author**: Haiwen Yin (胖头鱼)
**License**: Apache License 2.0