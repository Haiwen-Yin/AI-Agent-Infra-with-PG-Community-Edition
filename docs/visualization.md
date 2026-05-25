# Web Visualization - PostgreSQL Memory System v2.3.0

## Status

Web visualization is **implemented**. Run locally with `python3.14 scripts/visualization/server.py`.

## Architecture

The visualization server runs **locally** (Agent side), connecting to the remote PostgreSQL 18 database on 10.10.10.131 via psycopg2 over TCP. No web server runs on the database host.

```
[Local Machine]                    [10.10.10.131]
+------------------+               +------------------+
| python3.14       |  TCP 5432     | PostgreSQL 18    |
| server.py :8000  |-------------->| memory_graph DB  |
| vis.js (local)   |               |                  |
+------------------+               +------------------+
```

## Starting

```bash
cd /root/memory-pg18-by-yhw
python3.14 scripts/visualization/server.py
# Open http://localhost:8000 in browser
# Login: admin / admin123 (or any system_users account)
```

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Knowledge Graph | `/knowledge` | Interactive vis.js graph of KNOWLEDGE entities and edges; domain-colored nodes, importance-sized, click for detail panel |
| Memory Graph | `/memory` | Interactive vis.js graph of MEMORY entities and edges; category-colored nodes, search/filter bar |
| Agent Dashboard | `/agents` | 3-tab dashboard: Agent Registry, Active Sessions, Collaboration Requests; status badges |
| Task Plans | `/tasks` | Status filter, keyword search, Bootstrap accordion with expandable step tables; status-colored badges |
| Workspaces | `/workspaces` | Workspace table with expandable context chain timeline and linked tasks; context_data JSON modal |
| Graph Explorer | `/graph` | Stats cards, keyword/type search, click result to load vis.js network (center + neighbors grouped by type), detail panel |

## API Routes

| Route | Method | Auth | Description |
|-------|--------|------|-------------|
| `/api/health` | GET | No | `{status: "ok", version: "2.2.1"}` |
| `/api/login` | POST | No | `{username, password}` → `{success, session_id}` |
| `/api/logout` | GET | Yes | Clear session cookie |
| `/api/knowledge` | GET | Yes | `{nodes: [...], edges: [...]}` for vis.js |
| `/api/memory` | GET | Yes | `{nodes: [...], edges: [...]}` for vis.js |
| `/api/agents` | GET | Yes | `{agents: [...], sessions: [...], collaborations: [...]}` |
| `/api/tasks` | GET | Yes | `{plans: [{...steps...}]}` |
| `/api/workspaces` | GET | Yes | `{workspaces: [...]}` |
| `/api/stats` | GET | Yes | `{entity_counts: {...}, edge_count, workspace_count, agent_count}` |
| `/api/graph/neighbors` | GET | Yes | `?entity_id=X` — neighbor data |
| `/api/graph/context` | GET | Yes | `?entity_id=X` — entity context with grouped neighbors |
| `/api/graph/stats` | GET | Yes | Graph statistics JSON |
| `/api/graph/search` | GET | Yes | `?q=X` — search results JSON |
| `/api/graph/all` | GET | Yes | All entities + edges for full graph rendering |

## Tech Stack

- **Server**: Python `http.server` (standard library only, no Flask/Django)
- **Graph Rendering**: vis.js Network (served as local static file `/static/vis-network.min.js`)
- **CSS Framework**: Bootstrap 5 from CDN
- **Auth**: Session-based via cookies, passwords from `system_users` table (PBKDF2-SHA256)
- **i18n**: Bilingual (Chinese/English) toggle with `data-zh`/`data-en` attributes
- **Theme**: Dark theme (CSS variables)
- **DB Connection**: psycopg2 ThreadedConnectionPool via `scripts/lib/connection.py`
