# Web Visualization - AI Agent Infra v3.7.5 (2026-06-18) - PG Community Edition

## Server

`server.py` provides a web interface for browsing entities, relationships, agents, task plans, and graph data.

## Pages

| Page | Route | Description |
|------|-------|-------------|
| Knowledge Graph | `/knowledge` | Interactive vis.js graph of KNOWLEDGE entities and edges |
| Memory Content | `/memory` | Interactive vis.js graph of MEMORY entities and edges |
| Agent Collaboration | `/agents` | 3-tab dashboard: Agent Registry, Active Sessions, Collaboration Requests |
| Task Plans | `/tasks` | Status filter, keyword search, accordion plan list with expandable step tables |
| Property Graph | `/graph` | Graph API explorer for entity context, paths, and communities (Apache AGE) |

All pages share: bilingual UI (zh/en), session auth with auto-logout timer, `/api/stats` sidebar.

## API Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/api/health` | GET | Health check (no auth required) |
| `/api/knowledge` | GET | Knowledge graph JSON (nodes + edges) |
| `/api/knowledge/refresh` | GET | Force refresh knowledge cache |
| `/api/memory` | GET | Memory graph JSON (nodes + edges) |
| `/api/memory/refresh` | GET | Force refresh memory cache |
| `/api/agents` | GET | Agent registry, sessions, collaborations JSON |
| `/api/tasks` | GET | Task plans + steps JSON (query params: `status`, `keyword`) |
| `/api/stats` | GET | Entity counts by type + edge count |
| `/api/login` | POST | Authenticate (form: username + password) |
| `/api/logout` | GET | Clear session cookie, redirect to login |
| `/api/graph/neighbors` | GET | Graph neighbors for entity (param: `entity_id`, `direction`) |
| `/api/graph/path` | GET | Shortest path between entities (params: `source_id`, `target_id`) |
| `/api/graph/context` | GET | Entity context with grouped neighbors (param: `entity_id`) |
| `/api/graph/stats` | GET | Graph statistics (vertex/edge counts, distributions) |
| `/api/graph/search` | GET | Graph-aware search (params: `keyword`, `entity_type`, `category`) |
| `/api/graph/subgraph` | GET | Subgraph extraction (param: `entity_ids`, `include_intermediate`) |
| `/api/graph/communities` | GET | Community detection (params: `entity_type`, `min_connections`) |

## UI Column Updates

New columns displayed:
- **Summary**: Entity summary text
- **Source Agent**: Creating agent ID
- **Retrieval Count**: Access counter
- **Execution Mode**: On harness templates (SEQUENTIAL/PARALLEL/CONDITIONAL)

## Agent Collaboration Page

Three tabbed sections:

- **Agent Registry** — Table with Agent ID, Name, Type, Status (colored badge), Active Sessions count, Last Seen, Created timestamp
- **Active Sessions** — Recent 50 sessions with Session ID (truncated), Agent Name, Active (Y/N badge), Start Time
- **Collaboration Requests** — Recent 50 requests with From/To agent names, Type, Entity ID, Strength, Created timestamp

Status badges: ACTIVE=green, INACTIVE=gray, SUSPENDED=orange, DECOMMISSIONED=red.

## Quick Start

```bash
./start_web_server.sh start    # Start (daemon mode)
./start_web_server.sh status   # Show status + config
./start_web_server.sh stop     # Stop server

# Open http://localhost:18080 in browser
# Login: admin / admin123
```

## Configuration

Via `config.json` or environment variables:
- `MEMORY_SERVER_HOST` (default: 0.0.0.0)
- `MEMORY_SERVER_PORT` (default: 18080)
- `MEMORY_SESSION_TIMEOUT` (default: 300 seconds)
