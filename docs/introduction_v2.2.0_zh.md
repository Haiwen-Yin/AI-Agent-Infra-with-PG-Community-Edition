# PostgreSQL 18 AI 数据库记忆系统 v2.2.0

> **统一 AI 智能体记忆系统** — 基于知识图谱、多智能体协作、任务规划、Harness 模板引擎、属性图 API、工作空间与上下文恢复，及 Web 可视化,构建于 PostgreSQL 18 之上。

**版本**: v2.2.0 | **日期**: 2026-05-23 | **作者**: 尹海文 | **许可**: Apache License 2.0

---

## 一、项目概述

PostgreSQL 18 AI 数据库记忆系统是一个面向 AI 智能体（Agent）的企业级记忆管理平台，旨在为 AI 应用提供结构化的长期记忆、知识图谱、多智能体协作与任务编排能力。系统以 PostgreSQL 18 数据库为核心存储，利用 pgvector 向量检索、Apache AGE 属性图（Property Graph）、JSONB 原生 JSON 存储和 BIGINT IDENTITY 自增主键等特性，实现了一个统一、高效、可扩展的智能体记忆基础设施。

**技术栈核心特性**：

| 维度 | 技术选型 |
|------|---------|
| 数据库驱动 | psycopg2 ThreadedConnectionPool |
| 主键策略 | BIGINT GENERATED ALWAYS AS IDENTITY |
| 属性图查询 | Apache AGE Cypher |
| 表分区 | 无（通过索引策略弥补，57 个索引覆盖高频查询） |
| 视图 | 标准 SQL 视图（只读投影） |
| 服务端语言 | PL/pgSQL |
| 参数占位符 | %s 位置参数（防 SQL 注入） |
| 时间戳 | NOW() / TIMESTAMPTZ |
| 幂等写入 | ON CONFLICT DO NOTHING |
| 调度 | pg_cron 1.6（9 个自动化作业） |
| 向量检索 | pgvector 0.8.2 HNSW（vector(1024)） |
| JSON 存储 | JSONB（GIN 索引） |
| 嵌入生成 | pg-embedding-gen-by-yhw 扩展（COPY FROM PROGRAM + Python 代理） |
| 连接方式 | localhost 时自动使用 Unix socket，远端 TCP |

**v2.2.0 是 v2.1.0 的重大升级**，引入工作空间管理、上下文链、智能体交接、Web 可视化与工作空间 API，与 v2.1.0 不兼容，无就地升级路径，需全新部署。
---

## 二、v2.2.0 核心变更 — 工作空间与上下文恢复

| v2.1 痛点 | v2.2 方案 | 效果 |
|-----------|----------|------|
| 无工作空间概念，多任务上下文混乱 | WORKSPACES 表 + 生命周期管理 | 按工作空间隔离上下文，支持多任务并行 |
| 智能体会话无交接机制 | PREDECESSOR_SESSION_ID + create_handoff_session() | 上下文无缝传递，支持跨智能体协作 |
| 上下文无版本化，无法恢复 | WORKSPACE_CONTEXT + PARENT_CONTEXT_ID 版本链 | 支持检查点、交接、摘要、错误恢复、自动保存 |
| 子表删除需逐行清理 | ON DELETE CASCADE 替代 NO ACTION | 级联删除支持嵌套删除 |
| 实体无工作空间归属 | ENTITIES 新增 WORKSPACE_ID 列 | 按工作空间隔离实体，支持 SHARED/ISOLATED 模式 |

### 2.1 工作空间（WORKSPACES）
工作空间是 v2.2 的核心概念，为智能体提供上下文隔离和生命周期管理:
- **生命周期**: ACTIVE → PAUSED → ARCHIVED
- **隔离模式**: SHARED（共享工作空间，多智能体可见）/ ISOLATED（隔离工作空间，仅归属智能体可见）
- **归属**: OWNER_USER_ID 可空，支持系统创建的共享工作空间
- **工作空间任务**: WORKSPACE_TASKS 关联 TASK_PLANS 到工作空间

### 2.2 上下文链（WORKSPACE_CONTEXT）
上下文链为工作空间提供版本化的上下文恢复能力:
- **6 种上下文类型**:  - SNAPSHOT — 快照  - CHECKPOINT — 检查点，可恢复的关键状态快照  - HANDOFF — 交接点，智能体切换时传递上下文  - SUMMARY — 摘要，工作空间阶段总结  - ERROR_STATE — 错误状态，异常发生时的上下文快照  - AUTO_SAVE — 自动保存，定期自动保存的上下文
- **版本链**: PARENT_CONTEXT_ID 指向父上下文，形成版本链，支持历史回溯和分支
- **上下文数据**: CONTEXT_DATA 为 JSONB 类型，灵活存储各类上下文负载

### 2.3 智能体交接
AGENT_SESSION 表新增 3 列支持智能体交接: 
| 新增列 | 类型 | 说明 |
|--------|------|------| 
| OWNER_USER_ID | VARCHAR(64) | 会话归属用户 |
| WORKSPACE_ID | BIGINT | 关联工作空间 |
| PREDECESSOR_SESSION_ID | VARCHAR(128) | 前任会话 ID，形成交接链 |

`create_handoff_session()` 函数:基于当前会话创建交接会话，自动设置 PREDECESSOR_SESSION_ID 和 WORKSPACE_ID，生成 HANDOFF 类型上下文条目。

### 2.4 ON DELETE CASCADE
子表外键从 NO ACTION 改为 ON DELETE CASCADE，支持级联删除:
- 删除 WORKSPACES 时自动级联删除 WORKSPACE_CONTEXT 和 WORKSPACE_TASKS
- 删除 ENTITIES 时自动级联删除 KNOWLEDGE_META、HARNESS_META、ENTITY_EMBEDDINGS、ENTITY_TAGS、ENTITY_EDGES
- 删除 TASK_PLANS 时自动级联删除 TASK_STEPS

### 2.5 ENTITIES 新增 WORKSPACE_ID
ENTITIES 表新增 WORKSPACE_ID 列（BIGINT，可空），支持按工作空间隔离实体:
- ISOLATED 模式工作空间:仅归属智能体可见该工作空间下的实体
- SHARED 模式工作空间:所有授权智能体可见该工作空间下的实体
- WORKSPACE_ID 为空时，实体为全局共享

### 2.6 WORKSPACE_MANAGER PL/pgSQL 模式

新增 WORKSPACE_MANAGER 模式（Schema），包含 10 个 PL/pgSQL 函数:

| 函数 | 功能 |
|------|------|
| create_workspace() | 创建工作空间 |
| get_workspace() | 获取工作空间详情 |
| update_workspace_status() | 更新工作空间状态（生命周期转换） |
| delete_workspace() | 删除工作空间（级联删除上下文和任务） |
| add_context_entry() | 添加上下文条目 |
| get_context_chain() | 获取上下文链 |
| create_handoff() | 创建交接会话 |
| recover_to_checkpoint() | 恢复到指定检查点 |
| get_workspace_summary() | 获取工作空间摘要 |
| cleanup_abandoned() | 清理废弃工作空间 |

### 2.7 新增调度作业

| 作业 | 调度 | 功能 |
|------|------|------|
| WORKSPACE_CLEANUP_JOB | 每天凌晨 01:00 | 清理已废弃和已完成超过 30 天的工作空间 |
| STALE_WORKSPACE_DETECT_JOB | 每小时 | 检测并暂停超过 7 天无活动的工作空间 |

### 2.8 关键设计决策 — 视图 vs 原生 JSONB 策略

v2.2 在设计工作空间与上下文功能时，采用两种互补的存储策略：

| 维度 | 原生 JSONB 存储 | 标准 SQL 视图 |
|------|---------------|-------------|
| 写入模式 | 追加型（WORKSPACE_CONTEXT 仅 INSERT） | 只读投影，写入走基础表 |
| 查询灵活性 | JSONB 操作符按需提取字段 | 标准 SQL 关系查询 |
| 一致性保障 | 应用层负责 | 数据库约束自动保障 |
| 更新能力 | 需 JSONB_SET / || 操作符 | 直接更新基础表 |
| 嵌套深度 | 无限制 | 有限（视图 JOIN 关联） |
| 适用场景 | 上下文链（追加型、版本化） | 实体视图（结构化、关系型） |

**决策**:WORKSPACE_CONTEXT 采用原生 JSONB 存储（追加型，无需更新），WORKSPACES/WORKSPACE_TASKS 采用标准表 + 视图投影（结构化关系，通过 SQL 直接操作）。创建 V_MEMORY_ENTITIES、V_KNOWLEDGE_ENTITIES、V_ACTIVE_SESSIONS、V_ENTITY_GRAPH 等 5 个标准视图提供便捷查询入口。

---

## 三、v2.1.0 核心变更 — 相对 v2.0 的突破

| v2.0 痛点 | v2.1 方案 | 效果 |
|-----------|----------|------|
| 无图遍历 Python API | graph_api.py 9 个函数 + Apache AGE Cypher | 原生图遍历、路径查找、社区检测 |
| JSON TAGS 列不可索引 | TAGS + ENTITY_TAGS 规范化表 | 标签查询可索引，支持按标签过滤 |
| 自增 ID 跨系统不唯一 | BIGINT GENERATED ALWAYS AS IDENTITY | 数据库原生自增，高效简洁 |
| 无知识复查调度 | KNOWLEDGE_REVIEW_JOB | 每日自动安排间隔复查 |
| HARNESS 元数据不表达输入输出 | INPUT_SCHEMA/OUTPUT_SCHEMA (JSONB Schema) | 模板输入输出结构化定义 |
| ACCESSIBLE_TO JSON 数组复杂 | 简化为 PRIVATE/SHARED/PUBLIC | 可见性模型更清晰，协作走 AGENT_COLLABORATION |

---

## 四、核心架构

### 4.1 统一实体模型

ENTITIES 表以 BIGINT GENERATED ALWAYS AS IDENTITY 作为主键:

```
ENTITIES（统一实体表，PK: ENTITY_ID BIGINT IDENTITY）
  ├── MEMORY          — 短期智能体记忆
  ├── KNOWLEDGE       — 长期验证知识（扩展: KNOWLEDGE_META）
  ├── TASK_OUTPUT     — 任务执行输出
  ├── EXPERIENCE      — 学习经验与启发式规则
  ├── HARNESS_TEMPLATE — 可复用智能体执行蓝图（扩展: HARNESS_META）
```

**v2.1 列变更**:

| v2.0 列 | v2.1 列 | 说明 |
|---------|---------|------|
| NAME | TITLE | 重命名 |
| PRIORITY | IMPORTANCE | 重命名，范围 1-10 |
| TAGS (JSON) | *(移除)* | 拆分为 TAGS + ENTITY_TAGS 表 |
| METADATA (JSON) | *(移除)* | 仅保留在 ENTITY_EDGES |
| ACCESSIBLE_TO (JSON) | *(移除)* | 简化为 PRIVATE/SHARED/PUBLIC |
| DESCRIPTION | *(移除)* | 由 SUMMARY 替代 |
| *(新增)* | SUMMARY | VARCHAR(2000) 实体摘要 |
| *(新增)* | SOURCE_AGENT | VARCHAR(64) 创建智能体 |
| *(新增)* | RETRIEVAL_COUNT | INT 访问计数 |
| *(新增)* | IMPORTANCE | INT 1-10 重要度 |
| *(新增)* | WORKSPACE_ID | BIGINT 工作空间归属（v2.2） |

### 4.2 统一边模型（SOURCE_TYPE 反规范化）

ENTITY_EDGES 表保留 SOURCE_TYPE 反规范化列，支持按类型过滤:

- FK: SOURCE_ID 引用 ENTITIES(ENTITY_ID) ON DELETE CASCADE
- TARGET_ID 引用 ENTITIES(ENTITY_ID) ON DELETE CASCADE
- 10 种边类型:DEPENDS_ON, RELATED_TO, DERIVED_FROM, CAUSES, ENABLES, PREVENTS, SIMILAR_TO, EVOLVED_FROM, CONTRADICTS, SUPPORTS
- STRENGTH (0-1) 和 CONFIDENCE (0-1) 支持加权图遍历
- METADATA (JSONB) 仅保留在边表

### 4.3 反规范化 ENTITY_TYPE

ENTITY_TYPE 列反规范化到所有引用 ENTITIES 的子表，支持按类型索引和过滤:

| 子表 | 主键 | 外键 | 反规范化列 |
|------|------|------|-----------|
| ENTITY_EDGES | EDGE_ID BIGINT IDENTITY | SOURCE_ID → ENTITIES | SOURCE_TYPE |
| KNOWLEDGE_META | ENTITY_ID BIGINT | ENTITY_ID → ENTITIES | ENTITY_TYPE |
| ENTITY_EMBEDDINGS | (ENTITY_ID, ENTITY_TYPE) | ENTITY_ID → ENTITIES | ENTITY_TYPE |
| HARNESS_META | ENTITY_ID BIGINT | ENTITY_ID → ENTITIES | ENTITY_TYPE |
| ENTITY_TAGS | (ENTITY_ID, ENTITY_TYPE, TAG_ID) | ENTITY_ID → ENTITIES | ENTITY_TYPE |

### 4.4 无表分区架构

### 4.4 索引策略（无表分区）

PostgreSQL 18 版本不使用表分区，通过索引策略实现高性能查询：

- 57 个索引覆盖所有高频查询路径
- HNSW 向量索引（idx_emb_hnsw）实现向量相似性检索
- B-tree 复合索引覆盖类型+归属、类型+分类等组合查询
- 如需未来引入分区，可在 LIST/RANGE 分区基础上逐步演进

**索引策略亮点**:

| 索引 | 类型 | 用途 |
|------|------|------|
| idx_entities_type | B-tree | 按实体类型过滤 |
| idx_entities_type_owner | B-tree 复合 | 类型+归属组合查询 |
| idx_entities_type_cat | B-tree 复合 | 类型+分类组合查询 |
| idx_entities_workspace | B-tree | 工作空间隔离查询 |
| idx_emb_hnsw | HNSW (vector_cosine_ops) | 向量相似性检索，m=16, ef_construction=64 |
| idx_edges_source_type | B-tree 复合 | 边源+类型组合查询 |
| idx_km_next_review | B-tree | 知识复查调度 |

### 4.5 辅助表体系

| 表名 | 用途 |
|------|------|
| ENTITIES | 统一实体表 |
| ENTITY_EDGES | 统一有向边表 |
| KNOWLEDGE_META | 知识扩展元数据（领域、主题、难度、间隔复查） |
| ENTITY_EMBEDDINGS | 语义向量嵌入 VECTOR(1024) |
| HARNESS_META | 模板版本、输入/输出模式、执行模式 |
| TAGS | 标签定义（TAG_ID BIGINT IDENTITY, TAG_NAME, TAG_GROUP） |
| ENTITY_TAGS | 实体-标签关联（规范化替代 JSON TAGS） |
| AGENT_REGISTRY | 智能体身份、能力、配置 |
| AGENT_SESSION | 会话追踪与上下文（含交接链） |
| ENTITY_ACCESS_LOG | 实体访问审计日志 |
| AGENT_PERMISSION_LOG | 权限变更审计（GRANT/REVOKE/DENY） |
| AGENT_COLLABORATION | 跨智能体协作链接 |
| TASK_PLANS | 多步骤任务定义 |
| TASK_STEPS | 计划步骤与状态追踪（含 PLAN_STATUS） |
| TASK_CONTEXT_SNAPSHOTS | 断点/恢复快照 |
| TASK_TOOL_CALLS | 工具调用审计 |
| TASK_DEPENDENCIES | 跨计划依赖图 |
| SYSTEM_CONFIG | 系统配置 |
| SYSTEM_USERS | 系统用户与角色 |
| WORKSPACES | 工作空间生命周期、隔离模式、归属 |
| WORKSPACE_CONTEXT | 上下文版本链（6 种类型，PARENT_CONTEXT_ID） |
| WORKSPACE_TASKS | 工作-任务关联 |

### 4.6 属性图与视图

- **MEMORY_GRAPH**:Apache AGE 属性图，使用 ag_catalog.create_graph() 创建，支持 Cypher 查询语言跨类型图遍历
- **V_MEMORY_ENTITIES**:记忆实体视图（JOIN ENTITY_EMBEDDINGS）
- **V_KNOWLEDGE_ENTITIES**:知识实体视图（JOIN KNOWLEDGE_META + ENTITY_EMBEDDINGS）
- **V_ACTIVE_SESSIONS**:活跃会话视图（JOIN AGENT_REGISTRY）
- **V_ENTITY_GRAPH**:实体图视图（边 + 源/目标实体信息）

---

## 五、属性图 Python API（graph_api.py）

v2.1 新增 9 个图遍历函数，全部基于 Apache AGE Cypher 查询:

| 函数 | 功能 | Cypher 模式 |
|------|------|------------|
| get_neighbors() | 获取邻居节点 | MATCH (a)-[r]->(b) 单跳遍历 |
| get_reachable() | 多跳可达性 | MATCH (a)-[r*1..N]->(v) 多跳模式 |
| get_shortest_path() | 最短路径 | shortestPath() + SQL 回溯（最多 6 跳） |
| find_similar_entities() | 图近邻相似 | 基于图距离的相似性发现 |
| get_entity_context() | 实体上下文 | 直接 SQL + 邻居分组 |
| get_graph_stats() | 图统计 | 顶点/边计数、度分布、类型分布 |
| get_subgraph() | 子图提取 | 按实体 ID 列表提取，含中间节点 |
| find_communities() | 社区检测 | 高连接度实体聚类 |
| graph_search() | 图感知搜索 | 条件过滤 + 重要度排序 |

**AGE Cypher 调用方式**:

```python
# 内部通过 ag_catalog.age_query() 执行 Cypher
sql = """
    SET search_path = 'ag_catalog', "$user", public;
    SELECT * FROM ag_catalog.age_query(
        'memory_graph',
        'memory_graph',
        $${cypher_query}$$
    )
"""
```

---

## 六、4 阶段 SQL 部署

### Phase 1: 1_schema.sql — 模式层
- 22 张表
- BIGINT GENERATED ALWAYS AS IDENTITY 主键
- 全部外键 ON DELETE CASCADE
- 57 个索引（含 HNSW 向量索引）
- 5 个标准视图
- Apache AGE 属性图（MEMORY_GRAPH）
- pgvector + age 扩展自动创建
- **破坏性**:自动删除所有已有表（CASCADE）
- 所有枚举列加 CHECK 约束
- 种子数据:SYSTEM_CONFIG（版本 2.2.0）、SYSTEM_USERS（admin 账户）
- pg-embedding-gen-by-yhw 扩展用于服务端嵌入生成
- memory.generate_embedding() 函数调用 embedding_generate()

### Phase 2: 2_api.sql — PL/pgSQL API 层
5 个 PL/pgSQL Schema，使用 JSONB 构造函数、BIGINT IDENTITY ID、%s 参数占位符:

| Schema | 功能 |
|------|------|
| memory_fusion | 合并相似记忆、提取知识、衰减重要度 |
| knowledge_api | 间隔复查调度/记录、知识血统查询 |
| agent_perm | 访问控制、会话清理、协作处理 |
| session_cleanup | 清除日志、归档实体、标签计数 |
| workspace_manager | 工作空间生命周期、上下文链、交接、恢复 |

### Phase 3: 3_jobs.sql — 调度层
9 个自动化调度作业（pg_cron，v2.2 新增 WORKSPACE_CLEANUP_JOB、STALE_WORKSPACE_DETECT_JOB）:

| 作业 | 调度 | 功能 |
|------|------|------|
| MEMORY_FUSION_JOB | 每天 02:00 | 融合相似记忆 + 重要度衰减 |
| KNOWLEDGE_EXTRACTION_JOB | 每天 03:00 | 从记忆模式提取知识 |
| KNOWLEDGE_REVIEW_JOB | 每天 06:00 | 安排知识间隔复查 |
| SESSION_CLEANUP_JOB | 每 30 分钟 | 清理过期会话 |
| ACCESS_LOG_PURGE_JOB | 每周日 04:00 | 清除 90 天以上日志 |
| ENTITY_ARCHIVE_JOB | 每周日 05:00 | 归档 180 天以上低重要度记忆 |
| COLLAB_EXPIRY_JOB | 每天 00:30 | 处理协作请求 |
| WORKSPACE_CLEANUP_JOB | 每天凌晨 01:00 | 清理已废弃和已完成超过 30 天的工作空间 |
| STALE_WORKSPACE_DETECT_JOB | 每小时 | 检测并暂停超过 7 天无活动的工作空间 |

### Phase 4: 4_harness_templates.sql — Harness 模板层
- 种子化 5 个内置模板
- HARNESS_META 含 INPUT_SCHEMA/OUTPUT_SCHEMA (JSONB Schema) 和 EXECUTION_MODE
- 使用 ON CONFLICT DO NOTHING 确保幂等

---

## 七、Python API 库

### 7.1 模块结构（10 个模块）

| 模块 | 功能 |
|------|------|
| config.py | 统一配置数据类，支持环境变量覆盖 |
| connection.py | psycopg2 连接池管理（延迟初始化、线程安全、Unix socket） |
| memory_api.py | 记忆 CRUD + 标签管理（ENTITIES, ENTITY_TYPE=MEMORY） |
| knowledge_api.py | 知识 CRUD + 边操作 + 间隔复查 + 标签 |
| graph_api.py | **v2.1 新增** 属性图遍历（9 个函数，Apache AGE Cypher） |
| agent_api.py | 智能体注册、会话、协作、访问日志 |
| task_plan_api.py | 任务计划、步骤（含 PLAN_STATUS）、快照、工具调用、依赖 |
| security.py | 数据脱敏、可逆加密、密码哈希 |
| harness_api.py | 模板 CRUD、实例化、变量提取（8 个公开函数） |
| workspace_api.py | **v2.2 新增** 工作空间生命周期、上下文链、智能体交接、恢复（11 个函数） |

### 7.2 ID 生成策略

所有 ID 均为 BIGINT GENERATED ALWAYS AS IDENTITY，由 PostgreSQL 数据库自动分配:

| 表 | ID 列 | 类型 |
|------|------|------|
| ENTITIES | ENTITY_ID | BIGINT IDENTITY |
| ENTITY_EDGES | EDGE_ID | BIGINT IDENTITY |
| ENTITY_ACCESS_LOG | LOG_ID | BIGINT IDENTITY |
| AGENT_COLLABORATION | COLLAB_ID | BIGINT IDENTITY |
| TASK_PLANS | PLAN_ID | BIGINT IDENTITY |
| TASK_STEPS | STEP_ID | BIGINT IDENTITY |
| TAGS | TAG_ID | BIGINT IDENTITY |
| WORKSPACES | WORKSPACE_ID | BIGINT IDENTITY |
| WORKSPACE_CONTEXT | CONTEXT_ID | BIGINT IDENTITY |

AGENT_SESSION.SESSION_ID 和 AGENT_REGISTRY.AGENT_ID 为 VARCHAR 类型，由应用层生成。

### 7.3 代码示例

```python
from scripts.lib.memory_api import create_memory, get_memory, add_memory_tags
from scripts.lib.knowledge_api import create_knowledge, add_edge
from scripts.lib.graph_api import get_neighbors, get_shortest_path, graph_search
from scripts.lib.agent_api import register_agent, create_session
from scripts.lib.harness_api import create_harness_template, instantiate_harness_template

# 创建记忆
mid = create_memory("会议纪要", "讨论了 v2.1 索引方案", category="meeting", importance=8)

# 添加标签
add_memory_tags(mid, ["架构", "索引", "v2.1"])

# 创建知识概念
kid = create_knowledge("索引架构模式", "HNSW 向量索引 + B-tree 复合索引", domain="architecture", importance=9)

# 建立关联（需要 source_type 参数）
eid = add_edge(mid, 'MEMORY', kid, 'DERIVED_FROM', strength=0.9)

# 图遍历
neighbors = get_neighbors(kid, direction="both", min_strength=0.5)

# 图搜索
results = graph_search(keyword="索引", entity_type="KNOWLEDGE", min_importance=7)

# Harness 模板
tpl_id = create_harness_template(
    title="数据分析师",
    content="你是{role}，请分析{data}",
    execution_mode="PARALLEL",
)
instance_id = instantiate_harness_template(tpl_id, {"role": "金融分析师", "data": "Q3财报"}, "agent-1")
```

### 7.4 设计模式

- 所有查询使用 %s 参数占位符（防 SQL 注入）
- INSERT...RETURNING 返回 BIGINT ID
- execute_query 返回 List[Dict[str, Any]]（列名作键）
- ON CONFLICT 实现幂等注册
- _row_to_dict() 处理 psycopg2 返回的各类数据类型（bytes、内存视图等）
- JSONB 列自动序列化/反序列化
- composite FK 操作需要 ENTITY_TYPE/SOURCE_TYPE/PLAN_STATUS 参数
- localhost 连接自动使用 Unix socket（/tmp），远端使用 TCP

---

## 八、Harness 模板系统

### 8.1 HARNESS_META（v2.1 重构）

| 列 | 类型 | 说明 |
|----|------|------|
| ENTITY_ID | BIGINT | FK 到 ENTITIES |
| ENTITY_TYPE | VARCHAR(32) | 反规范化，固定 HARNESS_TEMPLATE |
| TEMPLATE_VERSION | INT | 模板版本号 |
| INPUT_SCHEMA | JSONB | JSON Schema 定义输入变量 |
| OUTPUT_SCHEMA | JSONB | JSON Schema 定义输出格式 |
| EXECUTION_MODE | VARCHAR(32) | SEQUENTIAL / PARALLEL / CONDITIONAL |

**v2.1 移除**:VARIABLES (JSON)、TEMPLATE_STATUS、CHANGELOG (JSON)

### 8.2 关键能力

| 能力 | 说明 |
|------|------|
| **JSONB Schema 输入/输出** | INPUT_SCHEMA 定义变量（类型、默认值、必填），OUTPUT_SCHEMA 定义输出格式 |
| **3 种执行模式** | SEQUENTIAL（顺序）、PARALLEL（并行）、CONDITIONAL（条件分支） |
| **变量替换** | {variable} 在实例化时解析替换 |
| **实例化** | 创建 TASK_OUTPUT 实体 + USES_HARNESS 边 |
| **模板验证** | get_template_with_variables() 从 INPUT_SCHEMA 提取变量定义 |
| **5 个内置模板** | Research Analyst, Code Assistant, Data Analyst, Task Planner, Security Auditor |

### 8.3 内置模板

| 模板 | 类别 | 执行模式 | 输入变量 |
|------|------|---------|---------|
| Research Analyst | research | SEQUENTIAL | role, domain, objective, query |
| Code Assistant | development | SEQUENTIAL | role, language, guidelines, task |
| Data Analyst | analytics | PARALLEL | role, focus_area, data_query |
| Task Planner | orchestration | CONDITIONAL | role, constraints, objective |
| Security Auditor | security | SEQUENTIAL | role, policies, action |

### 8.4 Python API（8 个函数）

| 函数 | 功能 |
|------|------|
| create_harness_template() | 创建模板（含 INPUT_SCHEMA/OUTPUT_SCHEMA/EXECUTION_MODE） |
| get_harness_template() | 获取模板完整元数据 + HARNESS_META |
| update_harness_template() | 更新实体字段和模板元数据 |
| delete_harness_template() | 删除模板 + HARNESS_META |
| list_harness_templates() | 列表（支持类别/执行模式过滤） |
| get_template_with_variables() | 从 INPUT_SCHEMA 提取变量定义 |
| instantiate_harness_template() | 实例化模板（变量替换 + 创建实例实体） |
| count_harness_templates() | 计数 |

---

## 九、安全模块

### 9.1 数据脱敏（DataMaskingService）

- **7 种模式类型**:email、phone、credit_card、ssn、api_key、ip_address、jwt_token
- **4 种上下文级别**:LOGGING、DEBUGGING、ANALYTICS、SHARING
- 确定性匹配顺序（credit_card 优先于 phone，避免误匹配）

### 9.2 可逆加密（ReversibleEncryption）

- PBKDF2 密钥派生 + XOR 加密
- 长度前缀编码（替代零字节填充）
- 安全密钥轮换:先全部解密，再用新密钥重新加密

### 9.3 密码哈希

- PBKDF2-HMAC-SHA256，可配置迭代次数（默认 100,000 次）

### 9.4 可见性模型（v2.1 简化）

| 级别 | 访问 |
|------|------|
| PRIVATE | 仅 OWNED_BY_AGENT |
| SHARED | 所有注册智能体 |
| PUBLIC | 无限制（v2.1 新增，替代 v2.0 COLLABORATIVE） |

跨智能体共享通过 AGENT_COLLABORATION 表管理。

---

## 十、测试体系

### 10.1 测试覆盖

```
PostgreSQL Memory System v2.2.0 - 全量测试套件
============================================================
  Connection:  6/6 PASS
  Memory:     16/16 PASS
  Knowledge:  19/19 PASS
  Agent:      17/17 PASS
  Graph:      12/12 PASS
  Harness:    12/12 PASS
  Security:   19/19 PASS
  Workspace:  14/14 PASS
Overall: 115/115 ALL PASSED
```

### 10.2 测试模块

| 测试文件 | 用例数 | 覆盖范围 |
|------|------|------|
| test_connection.py | 6 | 连接池创建、获取、释放、查询、异常处理 |
| test_memory.py | 16 | 创建/读取/更新/删除/搜索/标签/计数/智能体记忆 |
| test_knowledge.py | 19 | 概念创建/关系/图遍历/元数据/标签/间隔复查/计数 |
| test_agent.py | 17 | 注册/更新/心跳/会话/协作/权限/审计/交接 |
| test_graph.py | 12 | 邻居/路径/上下文/统计/搜索/子图/社区/SQL回退 |
| test_harness.py | 12 | CRUD/实例化/变量提取/计数/模式过滤 |
| test_security.py | 19 | 脱敏/加密/哈希/密钥轮换/上下文级别 |
| test_workspace.py | 14 | **v2.2 新增** 工作空间CRUD/上下文链/交接/恢复/任务关联 |


---

## 十之一、Web 可视化系统（v2.2 新增）

### 可视化架构

可视化服务器运行在**本地**（智能体侧），通过 psycopg2 TCP 连接远程 PostgreSQL 18 数据库。数据库主机上不运行 Web 服务器。

```
[本地机器]                      [10.10.10.131]
+------------------+             +------------------+
| python3.14       |  TCP 5432   | PostgreSQL 18    |
| server.py :8000  |------------>| memory_graph DB  |
| vis.js (本地)    |             |                  |
+------------------+             +------------------+
```

### 页面一览

| 页面 | 路径 | 功能 |
|------|------|------|
| 知识图谱 | `/knowledge` | vis.js 图/List 双视图切换，默认列表视图，域名/重要度/标签完整展示 |
| 记忆图谱 | `/memory` | vis.js 图/List 双视图切换，默认列表视图，分类/可见性/标签完整展示 |
| 智能体仪表板 | `/agents` | 3 标签页:注册表、活跃会话、协作请求 |
| 任务计划 | `/tasks` | 状态过滤、关键词搜索、可展开步骤详情 + 计划详情面板 |
| 工作空间 | `/workspaces` | 工作空间表 + 上下文链时间线 + 关联任务 |
| 图探索器 | `/graph` | 页面加载时渲染全图(`loadAllGraph`)，搜索/点击加载邻居网络 |
| 登录页 | `/login` | PBKDF2-SHA256 认证，5 分钟自动注销 |

### REST API（14 个端点）

| 端点 | 方法 | 认证 | 说明 |
|------|------|------|------|
| `/api/health` | GET | 无 | 服务健康检查 |
| `/api/login` | POST | 无 | 用户名/密码认证 |
| `/api/logout` | GET | 需要 | 注销会话 |
| `/api/knowledge` | GET | 需要 | 知识实体 + 边（vis.js 格式） |
| `/api/memory` | GET | 需要 | 记忆实体 + 边（vis.js 格式） |
| `/api/agents` | GET | 需要 | 智能体注册/会话/协作 |
| `/api/tasks` | GET | 需要 | 任务计划 + 步骤 |
| `/api/workspaces` | GET | 需要 | 工作空间 + 上下文链 |
| `/api/stats` | GET | 需要 | 系统统计 |
| `/api/graph/neighbors` | GET | 需要 | `?entity_id=X` 邻居数据 |
| `/api/graph/context` | GET | 需要 | `?entity_id=X` 实体上下文 |
| `/api/graph/stats` | GET | 需要 | 图统计 |
| `/api/graph/search` | GET | 需要 | `?q=X` 关键词搜索 |
| `/api/graph/all` | GET | 需要 | 全图渲染数据 |

### 关键设计决策

- **侧边栏**: `position:fixed;height:100vh`，底部居中注销按钮 + 5 分钟倒计时 + 语言切换
- **vis.js**: 本地 `/static/vis-network.min.js`（702KB 独立 UMD 构建），不使用 CDN
- **容器高度**: vis.js Network 容器必须设置 `height:calc(100vh - Npx)`，否则渲染 0x0
- **图/List 切换**: 列表默认显示，切换到图视图时 `setTimeout(100ms)` + `destroy()` + 重建 Network
- **自动注销**: 5 分钟无操作自动注销，≤60s 红色闪烁，≤30s 标题栏警告
- **认证**: Session Cookie，密码来自 `system_users` 表（PBKDF2-SHA256）

### Bug 修复汇总

- 修复认证重定向（`_get_session()` 替代 `_require_auth()`）
- 修复 `_knowledge_to_vis()` / `_memory_to_vis()` 返回完整字段 + 标签
- 修复 `graph.html` 容器高度和 `setTimeout` 重建模式
- 修复所有 6 个页面侧边栏 `position:fixed`
- 修复 `tasks.html` JS 语法错误（重复代码块）
- 修复 `test_*.py` 中 `test_get_nonexistent` 使用字符串而非 BIGINT
- 修复 `test_security.py` 中敏感键名和 ANALYTICS 上下文测试
- 修复 `test_workspace.py` 中 PROJECT→PIPELINE 工作空间类型
- 添加 `graph_api.get_neighbors()` SQL 回退（AGE Cypher 失败时）

---

## 十一、快速开始

```bash
# 1. 克隆项目
git clone https://github.com/Haiwen-Yin/memory-pg18-by-yhw.git
cd memory-pg18-by-yhw

# 2. 部署数据库（4 阶段）
psql -h localhost -U pgsql -d memory_graph -f scripts/deploy/1_schema.sql
psql -h localhost -U pgsql -d memory_graph -f scripts/deploy/2_api.sql
psql -h localhost -U pgsql -d memory_graph -f scripts/deploy/3_jobs.sql
psql -h localhost -U pgsql -d memory_graph -f scripts/deploy/4_harness_templates.sql

# 3. 安装 Python 依赖
pip install psycopg2-binary

# 4. 配置
export MEMORY_DB_HOST=localhost
export MEMORY_DB_PORT=5432
export MEMORY_DB_NAME=memory_graph
export MEMORY_DB_USER=pgsql
export MEMORY_DB_PASSWORD=

# 5. 运行测试
cd /root/memory-pg18-by-yhw
python3.14 -m scripts.tests.test_all

# 6. 启动 Web 可视化服务器
./start_web_server.sh start
# 访问 http://10.10.10.136:8000
# 登录: admin / admin123 (仅限开发环境)
```

---

## 十二、文档索引

| 文档 | 说明 |
|------|------|
| [SKILL.md](../SKILL.md) | 精简技能概览 |
| [architecture.md](architecture.md) | 架构设计与索引策略 |
| [api-reference.md](api-reference.md) | Python + PL/pgSQL API 参考（含 graph_api） |
| [deployment.md](deployment.md) | 部署指南与 pg_cron 维护 |
| [migration.md](migration.md) | v2.1 -> v2.2 迁移指南 |
| [security.md](security.md) | 安全特性与配置 |
| [harness.md](harness.md) | Harness 模板系统指南 |
| [workspace.md](workspace.md) | 工作空间与上下文恢复 |
| [visualization.md](visualization.md) | Web 可视化架构与 API |
| [minimum-privileges.md](minimum-privileges.md) | PG18 最小数据库用户权限 |

---

## 十三、版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| **v2.2.0** | 2026-05-23 | 工作空间管理、Web 可视化、上下文链、智能体交接、Bug 修复 |
| **v2.1.0** | 2026-05-19 | BIGINT IDENTITY PK、Apache AGE Cypher 图 API、规范化标签、pgvector HNSW |
| v2.0.0 | 2026-05-15 | 完全重写:统一架构、psycopg2 驱动、4 阶段部署、Harness 模板 |
| v1.1.0 | 2026-05-12 | Web 可视化、会话安全、双语 UI |
| v1.0.0 | 2026-05-10 | 生产发布:知识库、属性图、多智能体 |
| v0.5.1 | 2026-05-08 | 增强会话管理 |
| v0.5.0 | 2026-05-06 | 多智能体协作框架 |
| v0.4.0 | 2026-05-02 | 任务计划系统 |
| v0.3.x | 2026-04-28 | 核心记忆系统 |

---

## 许可

Apache License 2.0 — Copyright (c) 2026 尹海文
