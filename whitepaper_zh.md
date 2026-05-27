# PostgreSQL 18 AI 数据库记忆系统 v2.3.1

## 产品白皮书

| 项目 | 详情 |
|------|------|
| **产品名称** | PostgreSQL 18 AI 数据库记忆系统 (PG18 AI Database Memory System) |
| **版本** | 2.3.1 |
| **发布日期** | 2026年5月 |
| **作者** | 尹海文 |
| **许可证** | Apache 2.0 |
| **数据库** | PostgreSQL 18.3 + pgvector 0.8 + Apache AGE 1.7 + pg_cron 1.6 + pg-embedding-gen-by-yhw 1.0 |
| **Python** | 3.14 / psycopg2-binary 2.9+ |

---

## 目录

1. [执行摘要](#1-执行摘要)
2. [产品定位与核心价值](#2-产品定位与核心价值)
3. [系统架构](#3-系统架构)
4. [统一实体模型](#4-统一实体模型)
5. [记忆引擎](#5-记忆引擎)
6. [知识图谱](#6-知识图谱)
7. [规格驱动开发](#7-规格驱动开发)
8. [智能体弹性管理](#8-智能体弹性管理)
9. [协作组](#9-协作组)
10. [工作空间与上下文连续性](#10-工作空间与上下文连续性)
11. [任务规划引擎](#11-任务规划引擎)
12. [Harness模板系统](#12-harness模板系统)
13. [属性图API](#13-属性图api)
14. [向量检索引擎](#14-向量检索引擎)
15. [安全体系](#15-安全体系)
16. [数据架构](#16-数据架构)
17. [自动化运维](#17-自动化运维)
18. [可视化控制台](#18-可视化控制台)
19. [API参考](#19-api参考)
20. [部署与运维](#20-部署与运维)
21. [版本演进](#21-版本演进)
22. [术语表](#22-术语表)

---

## 1. 执行摘要

PostgreSQL 18 AI 数据库记忆系统是一款面向AI智能体的企业级记忆与知识管理平台，基于PostgreSQL 18数据库构建，为AI代理提供持久化记忆、结构化知识管理、规格驱动开发、弹性智能体调度与多智能体协作等核心能力。

传统AI代理面临记忆遗忘、知识孤岛、协作困难等根本性挑战。本系统通过统一实体模型、pgvector向量检索、Apache AGE属性图、JSONB原生JSON存储等PostgreSQL 18原生特性，构建了一套完整的企业级解决方案。

**v2.3.1版本核心升级：**

- **嵌入Python API**：embedding_api.py（12个函数），基于pgvector + pg-embedding-gen-by-yhw实现向量嵌入生成、存储、相似性搜索、混合搜索与跨类型搜索
- **EMBEDDING_GENERATION_JOB**：pg_cron调度作业，每2小时自动为新增MEMORY/KNOWLEDGE实体生成嵌入向量
- **19项嵌入测试**：覆盖生成、存储、检索、向量搜索、实体搜索、混合搜索、跨类型搜索、批量处理、维度检测、统计与清理

**系统规模一览：**

| 指标 | 数值 |
|------|------|
| 数据库表 | 27 |
| PL/pgSQL模式 | 7 |
| 调度作业 | 13 |
| Python模块 | 13 |
| API函数 | 110+ |
| 测试通过率 | 162/162 (100%) |
| 可视化页面 | 9 |
| REST端点 | 16 |
---

## 2. 产品定位与核心价值

### 2.1 AI Agent记忆的核心痛点

当前AI智能体在实际生产环境中，不仅面临基本的功能缺失，更深层次的问题源于**纯文本存储架构**的固有缺陷。AI Agent的记忆并非简单的文本信息堆砌，还涵盖上下文关联、元数据属性等多维信息；且单条记忆并非孤立存在，而是嵌套在完整的记忆链路与知识图谱体系之中。

#### 2.1.1 纯文本存储架构的底层缺陷

| 缺陷 | 描述 |
|------|------|
| **容量与维护瓶颈** | 当单条记忆文本容量过大，或记忆文件数量累积到一定规模后，AI Agent难以快速检索匹配有效信息，同时记忆文件的日常管理与维护成本大幅攀升 |
| **关联检索能力薄弱** | 无法建立标准化索引体系，难以实现关联记忆的高效精准检索 |
| **Token资源消耗过高** | 冗余繁杂的记忆读写操作直接增加Token消耗量，频繁的记忆调度还会挤占上下文窗口资源，造成上下文信息冗余与污染 |
| **规模化场景适配性不足** | 在多Agent协同、企业级落地场景中，记忆来源维度更多样、读写调用频次更高，纯文本文件的存储与调用架构无法承载高并发、高负载的记忆存取需求 |

#### 2.1.2 生产环境中的六大挑战

| 痛点 | 描述 |
|------|------|
| **记忆遗忘** | AI代理的对话记忆随会话结束而丢失，无法形成长期经验积累 |
| **知识孤岛** | 不同代理、不同项目间的知识无法互通，形成信息壁垒 |
| **规格缺失** | AI代理缺乏行为规格约束，输出质量不可控、不可验证 |
| **资源浪费** | 空闲代理持续占用资源，无法弹性伸缩，运维成本居高不下 |
| **协作困难** | 多代理间缺乏结构化协作机制，任务交接混乱 |
| **上下文断裂** | 会话切换或代理变更时，上下文丢失，工作连续性被破坏 |

#### 2.1.3 数据库架构的根本性优势

引入数据库架构重构AI Agent记忆存储体系，是解决纯文本记忆短板的最优路径：

| 优势 | 说明 |
|------|------|
| **多模态一体化存储** | PostgreSQL 18不仅支持传统关系型标量数据存储，还兼容AI Agent所需的长文本（TEXT）、JSONB结构化数据，并能依托Apache AGE属性图搭建完整的记忆链路与知识图谱 |
| **多维度数据互补增强** | 借助标量业务数据为pgvector向量检索做辅助标注，弥补向量检索精准度不足的短板，提升记忆匹配准确率 |
| **统一接口与混合查询能力** | 通过SQL语句实现多模态数据联合混合查询，以最简操作流程高效调取所需记忆数据 |
| **高性能与高可用保障** | PostgreSQL原生支持高并发读写能力（MVCC），搭配成熟的流复制高可用架构，提供稳定、高效的底层支撑 |

### 2.2 六大核心能力

| 能力 | 描述 |
|------|------|
| **持久化记忆** | 跨会话的记忆存储与检索，支持强化、衰减、融合与归档的完整生命周期 |
| **结构化知识** | 领域知识的结构化管理，支持间隔复习、知识溯源与矛盾检测 |
| **向量检索引擎** | pgvector HNSW向量相似性检索 + 混合搜索 + 跨类型搜索，pg-embedding-gen-by-yhw服务端嵌入生成 |
| **规格驱动开发** | 规格为一等实体，驱动计划生成与验证闭环，确保输出符合规格约束 |
| **弹性智能体管理** | DORMANT休眠与POOL池化双模式，配合凭据体系实现资源弹性调度 |
| **协作组** | 组级共享+个人隔离的双层工作空间，三级共享策略满足不同协作场景 |
| **上下文连续性** | 基于工作空间的追加式上下文链，支持检查点、交接、摘要等多类型上下文 |

### 2.3 技术优势

| 优势 | 说明 |
|------|------|
| **原生PostgreSQL 18** | 充分利用JSONB、BIGINT IDENTITY、Apache AGE Cypher、pgvector HNSW、pg_cron等特性 |
| **统一实体模型** | 7种实体类型共享单表，消除数据孤岛，统一访问接口 |
| **psycopg2连接池** | ThreadedConnectionPool(min=2, max=5)，4500x加速于psql子进程，Python 3.6+兼容 |
| **pg-embedding-gen-by-yhw** | 自研PG18扩展，COPY FROM PROGRAM + Python代理，无需C编译 |
| **Apache AGE Cypher** | 属性图Cypher查询，跨类型图遍历，SQL回退保障 |
| **162/162测试覆盖** | 全量测试通过，12套测试覆盖所有核心能力路径 |
| **4阶段SQL部署** | schema→api→jobs→harness，幂等部署，ON CONFLICT DO NOTHING |
---

## 3. 系统架构

### 3.1 四层架构

```
+---------------------------------------------------------------------+
|                    可视化层 (Visualization)                         |
|      Knowledge | Memory | Agents | Tasks | Workspaces | ...         |
|                    9 页面 · 暗色主题 · 中英双语 · 分页30/页         |
+---------------------------------------------------------------------+
|                  Python API 层 (Business Logic)                     |
|      memory_api | knowledge_api | agent_api | spec_api | ...        |
|                     13 模块 · 110+ API 函数 · psycopg2-binary       |
+---------------------------------------------------------------------+
|                  PostgreSQL 18 层 (Data & Logic)                    |
|   27 Tables | 7 PL/pgSQL Schemas | AGE Graph | pgvector HNSW        |
|              JSONB · BIGINT IDENTITY · 标准视图 · CHECK约束         |
+---------------------------------------------------------------------+
|                     调度层 (pg_cron Scheduler)                      |
|      MEMORY_FUSION_JOB | EMBEDDING_GENERATION_JOB | ...             |
|                    13 调度作业 · 自动化运维                         |
+---------------------------------------------------------------------+
```

### 3.2 数据流

```
+------------+    +-----------+    +-----------+    +------------+    +-----------+
|  Agent     |--->|  Memory   |--->|  Fusion   |--->| Knowledge  |--->|  Graph    |
| Interaction|    |  Store    |    |  Engine   |    | Extraction |    |  Building |
+------------+    +-----------+    +-----------+    +------------+    +-----------+
      |                 |                |                |                 |
      v                 v                v                v                 v
  SESSION          ENTITIES        memory_fusion    KNOWLEDGE_META    ENTITY_EDGES
  ENTITIES         (MEMORY)        schema           ENTITIES(KNOW)    Apache AGE
                    WORKSPACE                                         memory_graph
                    CONTEXT
```

**数据流说明：**

1. **智能体交互**：Agent通过Python API创建会话，产生交互数据
2. **记忆存储**：交互内容作为MEMORY类型实体存入ENTITIES表
3. **记忆融合**：memory_fusion schema定期执行相似记忆融合、衰减与知识提取
4. **知识提取**：高重要性记忆（IMPORTANCE>7）自动提取为KNOWLEDGE实体
5. **图谱构建**：实体间关系通过ENTITY_EDGES建立，Apache AGE属性图memory_graph

### 3.3 部署架构

```
+------------------+     HTTP/REST      +------------------+
|                  | <----------------> |                  |
|   Browser        |     :8000          |  Python App      |
|   (Dashboard)    |                    |  Server          |
|                  |                    |  (server.py)     |
+------------------+                    +--------+---------+
                                                |
                                         psycopg2-binary
                                         ThreadedConnPool
                                                |
                                       +--------v---------+
                                       |                  |
                                       |  PostgreSQL 18   |
                                       |  10.10.10.131    |
                                       |  :5432           |
                                       +------------------+
```

**部署特点：**

- Web服务器运行在**本地**（10.10.10.136），通过psycopg2 TCP连接远程PostgreSQL 18
- 数据库主机（10.10.10.131）不运行Web服务器
- localhost配置时自动切换为Unix socket（/tmp）连接


---



---

## 4. 统一实体模型

### 4.1 设计理念

统一实体模型是本系统的核心设计范式。通过单表多态（Single-Table Polymorphism），将7种实体类型统一存储于ENTITIES表中，终结数据孤岛，提供统一的访问接口与关系构建基础。

```
+---------------------------------------------------------------+
|                          ENTITIES                             |
|                                                               |
|  MEMORY ----------+                                           |
|  KNOWLEDGE -------+                                           |
|  TASK_OUTPUT -----+--- 共享列 + 类型专属扩展列 + JSONB          |
|  EXPERIENCE ------+                                           |
|  HARNESS_TEMPLATE +                                           |
|  SPEC ------------+                                           |
+---------------------------------------------------------------+
        |
        | BIGINT IDENTITY PK + ON DELETE CASCADE
        +--> KNOWLEDGE_META
        +--> HARNESS_META
        +--> SPEC_META
        +--> ENTITY_EMBEDDINGS
        +--> ENTITY_TAGS
        +--> ENTITY_EDGES
```

### 4.2 核心表结构

**ENTITIES表完整列定义：**

| 列名 | 类型 | 说明 |
|------|------|------|
| ENTITY_ID | BIGINT GENERATED ALWAYS AS IDENTITY | 实体唯一标识，数据库自动分配 |
| ENTITY_TYPE | VARCHAR(32) | 实体类型：MEMORY/KNOWLEDGE/TASK_OUTPUT/EXPERIENCE/HARNESS_TEMPLATE/SPEC |
| TITLE | VARCHAR(500) | 实体标题 |
| CONTENT | TEXT | 实体内容 |
| SUMMARY | VARCHAR(2000) | 实体摘要 |
| CATEGORY | VARCHAR(100) | 分类 |
| STATUS | VARCHAR(32) | 状态：ACTIVE/ARCHIVED/DELETED/DRAFT |
| IMPORTANCE | INT | 重要性评分 (1-10) |
| OWNED_BY_AGENT | VARCHAR(64) | 归属智能体 |
| SOURCE_AGENT | VARCHAR(64) | 创建智能体 |
| VISIBILITY | VARCHAR(16) | 可见性：PRIVATE/SHARED/PUBLIC |
| RETRIEVAL_COUNT | INT | 访问计数 |
| WORKSPACE_ID | BIGINT | 所属工作空间 |
| CREATED_AT | TIMESTAMPTZ | 创建时间 |
| UPDATED_AT | TIMESTAMPTZ | 更新时间 |
| EXPIRES_AT | TIMESTAMPTZ | 过期时间 |

**主键策略：** BIGINT GENERATED ALWAYS AS IDENTITY — 数据库原生自增，无需显式序列管理，高效简洁。

### 4.3 七种实体类型

| 实体类型 | 说明 | 扩展表 |
|---------|------|--------|
| MEMORY | 短期智能体记忆 | - |
| KNOWLEDGE | 长期验证知识 | KNOWLEDGE_META |
| TASK_OUTPUT | 任务执行输出 | - |
| EXPERIENCE | 学习经验与启发式规则 | - |
| HARNESS_TEMPLATE | 可复用智能体执行蓝图 | HARNESS_META |
| SPEC | 规格驱动开发 | SPEC_META |

### 4.4 反规范化ENTITY_TYPE

ENTITY_TYPE列反规范化到所有引用ENTITIES的子表，支持按类型索引和过滤：

| 子表 | 主键 | 外键 | 反规范化列 |
|------|------|------|-----------|
| ENTITY_EDGES | EDGE_ID BIGINT IDENTITY | SOURCE_ID -> ENTITIES | SOURCE_TYPE |
| KNOWLEDGE_META | ENTITY_ID BIGINT | ENTITY_ID -> ENTITIES | ENTITY_TYPE |
| ENTITY_EMBEDDINGS | (ENTITY_ID, ENTITY_TYPE) | ENTITY_ID -> ENTITIES | ENTITY_TYPE |
| HARNESS_META | ENTITY_ID BIGINT | ENTITY_ID -> ENTITIES | ENTITY_TYPE |
| ENTITY_TAGS | (ENTITY_ID, ENTITY_TYPE, TAG_ID) | ENTITY_ID -> ENTITIES | ENTITY_TYPE |

### 4.5 无表分区架构

PostgreSQL 18版本不使用表分区，通过索引策略实现高性能查询：

- 69个索引覆盖所有高频查询路径
- HNSW向量索引（idx_emb_hnsw）实现向量相似性检索
- B-tree复合索引覆盖类型+归属、类型+分类等组合查询
- 如需未来引入分区，可在LIST/RANGE分区基础上逐步演进

**索引策略亮点：**

| 索引 | 类型 | 用途 |
|------|------|------|
| idx_entities_type | B-tree | 按实体类型过滤 |
| idx_entities_type_owner | B-tree 复合 | 类型+归属组合查询 |
| idx_entities_type_cat | B-tree 复合 | 类型+分类组合查询 |
| idx_entities_workspace | B-tree | 工作空间隔离查询 |
| idx_emb_hnsw | HNSW (vector_cosine_ops) | 向量相似性检索，m=16, ef_construction=64 |
| idx_edges_source_type | B-tree 复合 | 边源+类型组合查询 |
| idx_km_next_review | B-tree | 知识复查调度 |

### 4.6 JSONB灵活扩展

WORKSPACE_CONTEXT.CONTEXT_DATA和ENTITY_EDGES.METADATA使用PostgreSQL原生JSONB类型，提供灵活的半结构化扩展能力：

```python
# 写入时使用 json.dumps()
context_data = json.dumps({
    "progress": "Step 3 of 7 complete",
    "pending_actions": ["Run validation", "Generate report"]
})

# 读取时自动转为 dict
data = row['context_data']  # -> dict

# 更新时使用 JSONB 操作符 -> 和 ->>
value = row['metadata']['status']  # 使用 ->> 获取文本值
```

### 4.7 可见性模型

```
+----------------------------------------------+
|              VISIBILITY 模型                 |
|                                              |
|  PRIVATE  -- 仅 OWNED_BY_AGENT 可见          |
|  SHARED   -- 所有注册智能体可见              |
|  PUBLIC   -- 无限制                          |
|                                              |
|  访问控制检查：                              |
|  1. PUBLIC -> 直接允许                       |
|  2. SHARED  -> 验证 WORKSPACE_ID 匹配        |
|  3. PRIVATE -> 验证 OWNED_BY_AGENT 匹配      |
+----------------------------------------------+
```

### 4.8 标签系统

标签使用规范化表TAGS + ENTITY_TAGS替代JSON数组，实现可索引、可查询的标签管理：

- **TAGS表**：TAG_ID BIGINT IDENTITY, TAG_NAME VARCHAR(100) UNIQUE, TAG_GROUP VARCHAR(50), USAGE_COUNT INT
- **ENTITY_TAGS表**：复合主键(ENTITY_ID, ENTITY_TYPE, TAG_ID)，FK到TAGS ON DELETE CASCADE
- 使用 ON CONFLICT DO NOTHING 确保幂等注册

### 4.9 边关系类型

ENTITY_EDGES定义10种边关系类型：

| 边类型 | 说明 | 属性 |
|------|------|------|
| DEPENDS_ON | 依赖关系 | STRENGTH (0-1), CONFIDENCE (0-1) |
| RELATED_TO | 相关知识 | STRENGTH, CONFIDENCE |
| DERIVED_FROM | 知识溯源 | STRENGTH, CONFIDENCE |
| CAUSES | 因果关系 | STRENGTH, CONFIDENCE |
| ENABLES | 使能关系 | STRENGTH, CONFIDENCE |
| PREVENTS | 阻止关系 | STRENGTH, CONFIDENCE |
| SIMILAR_TO | 相似关系 | STRENGTH, CONFIDENCE |
| EVOLVED_FROM | 版本演化 | STRENGTH, CONFIDENCE |
| CONTRADICTS | 知识矛盾 | STRENGTH, CONFIDENCE |
| SUPPORTS | 知识支撑 | STRENGTH, CONFIDENCE |

每种边携带STRENGTH（关系强度，0-1）和CONFIDENCE（信心度，0-1）两个属性，用于衡量关系的可靠度与确定度。

---

## 5. 记忆引擎

### 5.1 记忆生命周期

记忆引擎是系统的核心运行机制，管理从记忆创建到归档的完整生命周期。记忆经历5个阶段的状态变迁：

```
+----------+     强化    +----------+     衰减    +----------+
|  Create  | ----------> | Reinforce| ----------> |  Decay   |
| (创建)   |  retrieval++|  (强化)  | importance↓ |  (衰减)  |
+----------+             +----------+             +----------+
                                                     |
                                                     v
                          +----------+     归档    +----------+
                          |  Archive | <---------- |  Fuse    |
                          | (归档)   |  status=    |  (融合)  |
                          | ARCHIVED |  ARCHIVED   | 合并相似 |
                          +----------+             +----------+
```

**生命周期各阶段说明：**

| 阶段 | 触发条件 | 行为 |
|------|---------|------|
| **Create** | Agent通过memory_api.create_memory()创建 | 插入ENTITIES表，ENTITY_TYPE='MEMORY'，STATUS='ACTIVE'，IMPORTANCE默认5 |
| **Reinforce** | 每次检索访问（search_memories / get_memory） | RETRIEVAL_COUNT递增，高检索频率的记忆获得更高IMPORTANCE |
| **Decay** | memory_fusion.decay_old_memories()定时执行 | 超过阈值天数（默认90天）的活跃记忆，IMPORTANCE按衰减因子（默认0.5）降低 |
| **Fuse** | memory_fusion.fuse_similar_memories()定时执行 | 相似度≥0.85的记忆对：建立SIMILAR_TO边，次记忆STATUS→ARCHIVED |
| **Archive** | session_cleanup.archive_old_entities()定时执行 | IMPORTANCE≥3且超过180天的活跃记忆，STATUS→ARCHIVED |

### 5.2 memory_fusion PL/pgSQL

记忆融合引擎通过PL/pgSQL函数实现，部署在`memory_fusion` schema下：

**核心函数：**

| 函数 | 返回 | 说明 |
|------|------|------|
| fuse_similar_memories(p_category, p_min_similarity, p_dry_run) | TABLE(source_id, target_id, similarity, action) | 检测并融合相似记忆，支持dry_run模式 |
| extract_knowledge_from_memories(p_category, p_min_count) | TABLE(category, memory_count, knowledge_entity_id) | 从同类别记忆中提取KNOWLEDGE实体 |
| decay_old_memories(p_days_threshold, p_decay_factor) | INT | 衰减过期记忆的优先级，返回受影响行数 |
| get_fusion_stats() | JSONB | 返回融合统计信息 |

**融合算法流程：**

```sql
-- fuse_similar_memories 核心逻辑
SELECT e1.entity_id AS src, e2.entity_id AS tgt,
       similarity(e1.title, e2.title) AS sim
FROM entities e1
JOIN entities e2 ON e1.entity_id < e2.entity_id
                AND e1.entity_type = 'MEMORY'
                AND e2.entity_type = 'MEMORY'
                AND e1.status = 'ACTIVE'
                AND e2.status = 'ACTIVE'
WHERE similarity(e1.title, e2.title) >= p_min_similarity
```

融合执行时：
1. 在两个相似记忆间建立`SIMILAR_TO`边，STRENGTH=similarity值，CONFIDENCE=0.9
2. 将次记忆（tgt）的STATUS设为`ARCHIVED`
3. 主记忆（src）保留为活跃状态

### 5.3 search_memories

记忆检索通过Python API实现，支持多维度条件组合：

```python
results = search_memories(
    keyword="数据库优化",        # ILIKE模糊匹配 TITLE和CONTENT
    category="performance",     # 精确匹配CATEGORY
    visibility="SHARED",        # 可见性过滤
    owned_by_agent="agent-001", # 归属智能体过滤
    workspace_id="42",          # 工作空间隔离
    isolation_mode="ISOLATED",  # SHARED=无工作空间 / ISOLATED=指定工作空间
    limit=100,                  # LIMIT分页
    offset=0,                   # 偏移量
)
```

**检索权限模型：**

```sql
-- 记忆可见性过滤核心逻辑
WHERE entity_type = 'MEMORY'
  AND (
    visibility = 'SHARED'
    OR visibility = 'PUBLIC'
    OR owned_by_agent = %s
  )
```

### 5.4 可见性模型

记忆引擎继承统一实体模型的可见性控制，通过`agent_perm.check_entity_access()` PL/pgSQL函数实现细粒度访问控制：

```
+---------------------------------------------------+
|            记忆访问控制流程                       |
|                                                   |
|  请求访问(entity_id, agent_id, access_type)       |
|       |                                           |
|       v                                           |
|  VISIBILITY = PUBLIC?  ----是----> GRANTED        |
|       |否                                         |
|       v                                           |
|  VISIBILITY = SHARED?  ----是----> GRANTED        |
|       |否                                         |
|       v                                           |
|  VISIBILITY = PRIVATE?                            |
|   且 owned_by_agent = agent_id?                   |
|       |是                |否                      |
|       v                   v                       |
|    GRANTED           DENIED:PRIVATE               |
+---------------------------------------------------+
```

### 5.5 标签与分类

记忆支持通过规范化标签系统进行多维标注：

```python
# 添加标签
add_memory_tags(entity_id, ["postgresql", "性能优化", "索引策略"])

# 查询标签
tags = get_memory_tags(entity_id)
# [{"tag_id": 1, "tag_name": "postgresql", "tag_group": None}, ...]

# 移除标签
remove_memory_tag(entity_id, tag_id)
```

标签写入流程：
1. INSERT INTO tags ON CONFLICT DO NOTHING — 幂等注册
2. INSERT INTO entity_tags ON CONFLICT DO NOTHING — 关联实体与标签
3. session_cleanup.update_tag_counts() — 定期更新USAGE_COUNT，清理零引用标签

### 5.6 调度作业

记忆引擎相关的pg_cron调度作业：

| 作业名 | 调度周期 | 函数 | 说明 |
|--------|---------|------|------|
| memory_fusion_job | 每日02:00 | memory_fusion.fuse_similar_memories(p_dry_run:=false) | 执行相似记忆融合 |
| knowledge_extraction_job | 每日03:00 | memory_fusion.extract_knowledge_from_memories() | 从记忆模式提取知识 |
| entity_archive_job | 每周日05:00 | session_cleanup.archive_old_entities(180) | 归档180天以上的低优先级记忆 |

---

## 6. 知识图谱

### 6.1 KNOWLEDGE_META扩展表

知识实体通过KNOWLEDGE_META扩展表承载领域属性，与ENTITIES表形成一对一关系：

| 列名 | 类型 | 说明 |
|------|------|------|
| ENTITY_ID | BIGINT PK | FK → ENTITIES(ENTITY_ID) ON DELETE CASCADE |
| ENTITY_TYPE | VARCHAR(32) | 反规范化，默认'KNOWLEDGE' |
| DOMAIN | VARCHAR(100) | 知识领域（如：数据库、安全、算法） |
| TOPIC | VARCHAR(200) | 知识主题 |
| DIFFICULTY | VARCHAR(32) | 难度级别：BEGINNER/INTERMEDIATE/ADVANCED/EXPERT |
| REVIEW_COUNT | INT | 复习次数，默认0 |
| LAST_REVIEWED | TIMESTAMPTZ | 最近复习时间 |
| NEXT_REVIEW | TIMESTAMPTZ | 下次复习时间，默认NOW() + 7 days |

**难度级别体系：**

```
+-----------+------------------------------------------+
| BEGINNER  | 入门级 -- 基础概念，无需前置知识         |
+-----------+------------------------------------------+
|INTERMEDIATE| 中级 -- 需要领域基础，可独立应用        |
+-----------+------------------------------------------+
| ADVANCED  | 高级 -- 需要深厚领域经验，可解决复杂问题 |
+-----------+------------------------------------------+
| EXPERT    | 专家级 -- 前沿研究级，需要创新性思维     |
+-----------+------------------------------------------+
```

### 6.2 间隔复习机制

知识图谱内置基于艾宾浩斯遗忘曲线的间隔复习算法，通过2^n天数间隔递增：

```
复习次数    间隔(天)    累计(天)    复习函数
--------   ---------   ---------   ------------------------------
   0          2^1=2       2       NEXT = NOW() + 2天
   1          2^2=4       6       NEXT = NOW() + 4天
   2          2^3=8      14       NEXT = NOW() + 8天
   3          2^4=16     30       NEXT = NOW() + 16天
   4+        min(2^5,30) 60+      NEXT = NOW() + 30天(上限)
```

**PL/pgSQL实现：**

```sql
CREATE OR REPLACE FUNCTION knowledge_api.record_review(p_entity_id BIGINT)
RETURNS BOOLEAN AS $$
BEGIN
    UPDATE knowledge_meta
    SET review_count = review_count + 1,
        last_reviewed = now(),
        next_review = now() + LEAST(POWER(2, review_count + 1), 30) * INTERVAL '1 day'
    WHERE entity_id = p_entity_id;
    RETURN FOUND;
END;
$$ LANGUAGE plpgsql;
```

**关键设计决策：**
- 间隔上限30天，避免知识长时间无人复查
- LEAST(POWER(2, review_count+1), 30) 确保间隔不超过30天
- 复习次数越多的知识，复习间隔越长，符合认知科学原理

**到期复习查询：**

```sql
SELECT e.entity_id, e.title, km.domain, km.next_review
FROM entities e
JOIN knowledge_meta km ON e.entity_id = km.entity_id
WHERE km.next_review <= now()
  AND e.status = 'ACTIVE'
  AND e.entity_type = 'KNOWLEDGE'
ORDER BY km.next_review ASC
LIMIT 50;
```

### 6.3 边关系类型与知识图谱

知识图谱通过ENTITY_EDGES建立实体间的关系网络，10种边类型构成完整的知识拓扑：

```
+------------------+       DERIVED_FROM       +------------------+
|   MEMORY实体     | -----------------------> |  KNOWLEDGE实体   |
| (短期经验)       |       EVOLVED_FROM       | (长期知识)       |
+------------------+ <----------------------- +------------------+
                         SIMILAR_TO
                    +------------------+
                    |  KNOWLEDGE实体   |
                    |  (相似知识)      |
                    +------------------+
                    SUPPORTS / CONTRADICTS
                    +------------------+
                    |  KNOWLEDGE实体   |
                    |  (关联知识)      |
                    +------------------+
```

**知识图谱核心边类型：**

| 边类型 | 语义 | 典型场景 |
|--------|------|---------|
| DERIVED_FROM | 知识溯源 | MEMORY→KNOWLEDGE，知识从哪些记忆中提取 |
| EVOLVED_FROM | 版本演化 | KNOWLEDGE_v1→KNOWLEDGE_v2，知识版本迭代 |
| SIMILAR_TO | 相似关系 | 同类知识间的关联，由融合引擎自动建立 |
| CONTRADICTS | 知识矛盾 | 互相冲突的知识点，触发矛盾检测 |
| SUPPORTS | 知识支撑 | 一条知识为另一条提供证据 |
| DEPENDS_ON | 依赖关系 | 前置知识依赖 |
| ENABLES | 使能关系 | 掌握某知识后可学习的新领域 |

### 6.4 矛盾检测

知识图谱通过CONTRADICTS边实现矛盾检测与标记：

```python
# 标记知识矛盾
knowledge_api.add_edge(
    source_id=101, source_type="KNOWLEDGE",
    target_id=202, edge_type="CONTRADICTS",
    strength=0.9, confidence=0.85,
    metadata={"reason": "性能建议冲突", "context": "索引策略"}
)
```

**矛盾检测流程：**

1. 当新知识插入时，通过向量相似性检索已有知识
2. 若新知识与已有知识语义相似但结论矛盾，标记CONTRADICTS边
3. CONTRADICTS边的CONFIDENCE反映矛盾的确信度
4. 待人工或高优先级Agent审查，决定保留哪条知识

### 6.5 知识版本演化

通过knowledge_api PL/pgSQL实现知识的版本化迭代：

```sql
-- 创建知识新版本
knowledge_api.create_concept_version(p_entity_id, p_new_content)

-- 内部流程：
-- 1. 旧版本 is_current = FALSE
-- 2. 创建新实体 + 新 knowledge_meta (version + 1, is_current = TRUE)
-- 3. 建立 EVOLVED_FROM 边：旧版本 -> 新版本
```

```
KNOWLEDGE_v1 --EVOLVED_FROM--> KNOWLEDGE_v2 --EVOLVED_FROM--> KNOWLEDGE_v3
  is_current=F                  is_current=F                  is_current=T
  version=1                     version=2                     version=3
```

### 6.6 调度作业

| 作业名 | 调度周期 | 函数 | 说明 |
|--------|---------|------|------|
| knowledge_review_job | 每日06:00 | knowledge_api.record_review() | 自动执行到期知识复习 |
| embedding_generation_job | 每2小时 | memory.generate_embedding() | 为新增KNOWLEDGE实体生成嵌入向量 |

---

## 7. 规格驱动开发

### 7.1 SPEC实体

规格（SPEC）是一等实体，在统一实体模型中与MEMORY、KNOWLEDGE等享有同等地位。规格驱动开发确保AI智能体的输出符合预定义的行为约束。

```
+-----------------------------------------------------------+
|                    SPEC 实体定位                          |
|                                                           |
|  传统模式：Agent -> 任务 -> 输出（无约束）                |
|  规格驱动：Agent -> 规格 -> 计划 -> 输出（受约束）        |
|                                                           |
|  SPEC = 行为契约 + 验收标准 + 约束条件                    |
+-----------------------------------------------------------+
```

### 7.2 SPEC_META扩展表

| 列名 | 类型 | 说明 |
|------|------|------|
| ENTITY_ID | BIGINT PK | FK → ENTITIES(ENTITY_ID) ON DELETE CASCADE |
| SPEC_VERSION | INT | 规格版本号，默认1 |
| SPEC_STATUS | VARCHAR(32) | 规格状态：DRAFT/REVIEWED/APPROVED/IMPLEMENTED/DEPRECATED |
| ACCEPTANCE_CRITERIA | JSONB | 验收标准（JSON结构化定义） |
| SPEC_CONSTRAINTS | JSONB | 规格约束（如blocked、max_retries等） |
| SPEC_SCOPE | VARCHAR(64) | 规格作用域 |
| COMPLEXITY | VARCHAR(16) | 复杂度：LOW/MEDIUM/HIGH/CRITICAL |
| PARENT_SPEC_ID | BIGINT | 父规格ID，FK → ENTITIES(ENTITY_ID) |

### 7.3 规格生命周期

```
+--------+    审查   +----------+    批准   +----------+   实现    +------------+
| DRAFT  | --------> | REVIEWED | --------> | APPROVED | --------> | IMPLEMENTED|
| (草稿) |           | (已审查) |           | (已批准) |           | (已实现)   |
+--------+           +----------+           +----------+           +------------+
     |                                                                  |
     |                       废弃                                       v
     +-----------------------------------------------------------> +-----------+
                                                                   | DEPRECATED|
                                                                   | (已废弃)  |
                                                                   +-----------+
```

**生命周期状态约束：**

| 当前状态 | 允许转换 | 条件 |
|---------|---------|------|
| DRAFT | REVIEWED | 需定义ACCEPTANCE_CRITERIA |
| REVIEWED | APPROVED | 需通过spec_manager.validate_spec()验证 |
| APPROVED | IMPLEMENTED | 需关联至少一个plan且plan状态为SUCCESS |
| IMPLEMENTED | DEPRECATED | 由derive_spec产生新版本后可废弃 |
| 任意 | DRAFT | 仅限PARENT_SPEC_ID非空的派生规格 |

### 7.4 spec_plan_links关联表

规格与计划通过SPEC_PLAN_LINKS表建立多对多关联，4种关联类型定义不同的约束语义：

| 列名 | 类型 | 说明 |
|------|------|------|
| LINK_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 关联ID |
| SPEC_ID | BIGINT FK → ENTITIES | 规格实体ID |
| PLAN_ID | BIGINT | 计划ID |
| LINK_TYPE | VARCHAR(32) | 关联类型：DRIVES/VALIDATES/CONSTRAINS/EXTENDS |
| LINK_STRENGTH | NUMERIC(5,4) | 关联强度 (0-1)，默认1.0000 |
| CREATED_AT | TIMESTAMPTZ | 创建时间 |

**UNIQUE约束：(SPEC_ID, PLAN_ID, LINK_TYPE)** — 同一规格-计划对在同一关联类型下唯一。

**四种关联类型语义：**

```
+----------+     DRIVES      +----------+     VALIDATES     +----------+
|   SPEC   | --------------> |   PLAN   | <---------------  |   SPEC   |
|  (驱动)  | 规格驱动计划生成|          |  计划验证规格达成 | (验证)   |
+----------+                 +----------+                   +----------+
                                   |
                      CONSTRAINS   |   EXTENDS
                   +---------------+---------------+
                   |                               |
             +----------+                     +----------+
             |   SPEC   |                     |   SPEC   |
             | (约束)   |                     | (扩展)   |
             +----------+                     +----------+
```

| 关联类型 | 语义 | 使用场景 |
|---------|------|---------|
| DRIVES | 规格驱动计划生成 | create_plan_from_spec()自动创建DRIVES关联 |
| VALIDATES | 计划验证规格达成 | 计划完成后验证是否满足验收标准 |
| CONSTRAINS | 规格约束计划行为 | 限制计划执行范围、禁止特定操作 |
| EXTENDS | 规格扩展计划能力 | 在原规格基础上增加新能力 |

### 7.5 create_plan_from_spec

从规格自动生成计划，建立DRIVES关联：

```python
# Python API：从规格创建计划
plan_id = create_plan_from_spec(
    spec_id=42,
    plan_title="实现API网关认证模块",
    plan_description="基于SPEC-42的验收标准实现认证功能"
)

# 内部流程：
# 1. get_spec(spec_id) 获取规格详情
# 2. INSERT INTO task_plans (goal, agent_id, priority, status, workspace_id)
# 3. INSERT INTO spec_plan_links (spec_id, plan_id, 'DRIVES', 1.0)
# 4. 返回 plan_id
```

### 7.6 validate_plan_against_spec

计划完成后，验证是否满足规格的验收标准与约束：

```python
# Python API：验证计划是否符合规格
result = validate_plan_against_spec(spec_id=42, plan_id=101)

# 返回结构：
# {
#     "valid": True/False,
#     "errors": ["Spec status is DRAFT but must be APPROVED"],
#     "warnings": ["Spec complexity is CRITICAL but plan priority is below 8"]
# }
```

**验证逻辑：**

1. 规格状态必须为APPROVED或IMPLEMENTED，否则报错
2. 验收标准非空时，计划必须有goal字段
3. 规格约束中blocked标记与计划RUNNING状态冲突检测
4. 规格与计划必须有显式spec_plan_links关联
5. CRITICAL复杂度规格要求计划priority≥8

### 7.7 derive_spec

规格支持派生继承，通过PARENT_SPEC_ID和DERIVES_FROM边建立规格链：

```python
# Python API：派生规格
new_spec_id = derive_spec(
    parent_spec_id=42,
    entity_data={"title": "认证模块v2 - 支持OAuth2"},
    spec_meta={"complexity": "HIGH", "spec_scope": "auth-v2"}
)

# 内部流程：
# 1. get_spec(parent_spec_id) 获取父规格
# 2. 合并元数据：parent_spec_id、version自动递增、complexity继承
# 3. create_spec(entity_data, merged_meta)
# 4. INSERT INTO entity_edges (source_id, target_id, 'DERIVES_FROM', 1.0, 1.0)
```

### 7.8 spec_manager PL/pgSQL

规格管理通过`spec_manager` schema提供PL/pgSQL函数：

| 函数 | 返回 | 说明 |
|------|------|------|
| create_spec(p_title, p_content, ...) | BIGINT | 创建规格实体+spec_meta |
| get_spec(p_entity_id) | JSONB | 获取规格完整信息（ENTITIES+SPEC_META联合） |
| update_spec_status(p_entity_id, p_new_status) | BOOLEAN | 更新规格状态 |
| validate_spec(p_entity_id) | JSONB | 验证规格完整性（验收标准、约束条件） |
| link_spec_to_plan(p_spec_id, p_plan_id, p_link_type, p_link_strength) | BIGINT | 创建规格-计划关联，ON CONFLICT DO NOTHING |
| get_spec_plan_links(p_spec_id) | JSONB | 获取规格关联的所有计划 |


---

## 8. 智能体弹性管理

### 8.1 DORMANT与POOL双模式

v2.3.0版本为AGENT_REGISTRY引入两种弹性状态：DORMANT（休眠）和POOL（池化），实现智能体资源的弹性调度。

```
+-----------------------------------------------------------+
|              智能体弹性状态体系                           |
|                                                           |
|  ACTIVE ──── 休眠 ────> DORMANT ──── 唤醒 ────> ACTIVE    |
|  (活跃)     (超过阈值)    (休眠)   (wake_agent) (活跃)    |
|                                                           |
|  POOL ──── 分配 ────> ACTIVE ──── 回收 ────> POOL         |
|  (池化) (assign_pool)  (活跃) (手动/超时)   (池化)        |
+-----------------------------------------------------------+
```

**状态转换条件：**

| 转换 | 触发 | 说明 |
|------|------|------|
| ACTIVE → DORMANT | dormant_agent_job（每30min） | last_active_at超过dormant_timeout_min阈值 |
| DORMANT → ACTIVE | wake_agent() | 手动唤醒，last_active_at更新 |
| POOL → ACTIVE | assign_pool_agent() | 按技能匹配分配给用户 |
| ACTIVE → POOL | 手动/超时回收 | 归还池化资源 |

### 8.2 agent_credentials与scope JSONB

凭据体系为弹性智能体提供临时访问授权，scope字段使用JSONB定义细粒度权限范围：

| 列名 | 类型 | 说明 |
|------|------|------|
| CREDENTIAL_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 凭据ID |
| AGENT_ID | VARCHAR(64) FK → AGENT_REGISTRY | 持有凭据的智能体 |
| USER_ID | VARCHAR(64) | 关联用户 |
| CREDENTIAL_TYPE | VARCHAR(32) | 凭据类型：ACCESS_TOKEN/SESSION_KEY/PASSWORD_HASH/API_KEY/SESSION/TEMP/assignment |
| CREDENTIAL_VALUE | TEXT | 凭据值（UUID自动生成） |
| SCOPE | JSONB | 权限范围定义 |
| EXPIRES_AT | TIMESTAMPTZ | 过期时间 |
| IS_ACTIVE | BOOLEAN | 是否活跃 |
| CREATED_AT | TIMESTAMPTZ | 创建时间 |

**scope JSONB示例：**

```python
# assignment类型凭据的scope定义
scope = {
    "access_level": "FULL",
    "restricted_domains": [],
    "max_clearance": "CONFIDENTIAL"
}

# 写入时使用 json.dumps()
scope_val = json.dumps(scope)

# 读取时自动转为 dict
scope = row['scope']  # -> dict
```

### 8.3 凭据生命周期

```
+----------+     issue_credential     +----------+     verify_credential    +----------+
|  未创建  | -----------------------> |  ACTIVE  | -----------------------> | 验证通过 |
|          |  (UUID生成, scope定义)   |  (活跃)  |  (检查is_active+expires) |          |
+----------+                          +----------+                          +----------+
                                              |                                |
                                              | 过期/撤销                      | 失效
                                              v                                v
                                        +----------+                     +----------+
                                        | INACTIVE |                     | INACTIVE |
                                        | (失效)   |                     | (失效)   |
                                        +----------+                     +----------+
                                              |                                |
                                              v                                v
                                         credential_cleanup_job          credential_cleanup_job
                                         (删除过期+7天inactive)          (删除过期+7天inactive)
```

**凭据管理函数：**

| 函数 | 说明 |
|------|------|
| issue_credential(agent_id, user_id, cred_type, scope, expires_hours=24) | 发放凭据，UUID自动生成，默认24小时过期 |
| verify_credential(credential_id) | 验证凭据：检查is_active和expires_at，失效时自动标记INACTIVE |
| revoke_credential(credential_id) | 撤销凭据：is_active → FALSE |
| get_credentials_for_user(user_id) | 查询用户活跃凭据 |
| hibernate_agent(agent_id) | 休眠智能体：status→DORMANT，所有凭据is_active→FALSE |

### 8.4 dormant_agent_job调度

休眠智能体检测作业每30分钟执行一次，自动将超时未活跃的智能体转为DORMANT状态：

```sql
-- dormant_agent_job (pg_cron: */30 * * * *)
UPDATE agent_registry
SET status = 'DORMANT', updated_at = now()
WHERE status = 'ACTIVE'
  AND last_active_at < now() - (
      SELECT config_value::INT
      FROM system_config
      WHERE config_key = 'dormant_timeout_min'
  ) * interval '1 minute';

-- 同步停用凭据
UPDATE agent_credentials
SET is_active = FALSE
WHERE agent_id IN (SELECT agent_id FROM agent_registry WHERE status = 'DORMANT')
  AND is_active = TRUE;
```

### 8.5 credential_cleanup_job调度

凭据清理作业每日02:00执行，清除过期和长期失效凭据：

```sql
-- credential_cleanup_job (pg_cron: 0 2 * * *)
DELETE FROM agent_credentials
WHERE (expires_at IS NOT NULL AND expires_at < now())
   OR (is_active = FALSE AND created_at < now() - interval '7 days');
```

### 8.6 池化智能体技能匹配

池化智能体通过pool_config JSONB中的skills_tags实现技能匹配分配：

```python
# 注册池化智能体（带技能标签）
agent_id = register_pool_agent(
    agent_name="通用代码助手",
    capabilities={"code_analysis": True, "refactoring": True},
    skills_tags=["python", "sql", "postgresql"]
)

# 分配池化智能体（按技能匹配）
agent_id = assign_pool_agent(
    user_id="user-001",
    required_skills=["postgresql", "sql"]
)
# 返回技能匹配度最高的POOL状态智能体
# 自动：status -> ACTIVE, issue_credential(assignment类型)
```

**技能匹配SQL：**

```sql
-- 按skills_tags匹配度排序
SELECT agent_id FROM agent_registry
WHERE status = 'POOL'
ORDER BY (
    SELECT COUNT(*)
    FROM jsonb_array_elements_text(
        COALESCE(pool_config->'skills_tags', '[]'::jsonb)
    ) AS tag
    WHERE tag = ANY(%s)
) DESC, created_at ASC
LIMIT 1;
```

### 8.7 状态转换图

```
+-----------------------------------------------------------+
|                AGENT_REGISTRY 状态转换图                  |
|                                                           |
|  +---------+    register     +---------+                  |
|  | (新)    | --------------> | ACTIVE  |                  |
|  +---------+                 +---------+                  |
|       |                          |                        |
|       | register_pool_agent      | dormant_agent_job      |
|       v                          v                        |
|  +---------+                 +---------+                  |
|  |  POOL   |                 | DORMANT |                  |
|  +---------+                 +---------+                  |
|       |                          |                        |
|       | assign_pool_agent        | wake_agent             |
|       v                          v                        |
|  +---------+                 +---------+                  |
|  | ACTIVE  |                 | ACTIVE  |                  |
|  +---------+                 +---------+                  |
|       |                          |                        |
|       | decommission_agent       | decommission_agent     |
|       v                          v                        |
|  +--------------+            +--------------+             |
|  |DECOMMISSIONED|            |DECOMMISSIONED|             |
|  +--------------+            +--------------+             |
|                                                           |
|  INACTIVE: 暂停状态（可手动激活回到ACTIVE）               |
|  SUSPENDED: 挂起状态（违规暂停，需管理员恢复）            |
+-----------------------------------------------------------+
```


---

## 9. 协作组

### 9.1 协作组模型

协作组（collab_groups）为多智能体协作提供结构化的组织单元，支持组级共享工作空间与个人隔离工作空间的双层架构。

```
+-----------------------------------------------------------+
|                 协作组双层工作空间架构                    |
|                                                           |
|  +-----------------------+  共享工作空间                  |
|  |  COLLAB_GROUP WS      |  TYPE=COLLAB_GROUP             |
|  |  ISOLATION=SHARED     |  所有成员可见                  |
|  +-----------------------+                                |
|                                                           |
|  +----------+ +----------+ +----------+  个人工作空间     |
|  |LEAD WS   | |CONTRIB WS| |LEAD WS   |  TYPE=PERSONAL_   |
|  |ISOLATED  | |ISOLATED  | |ISOLATED  |  IN_GROUP         |
|  +----------+ +----------+ +----------+  仅自己可见       |
|     LEAD      CONTRIBUTOR     LEAD                        |
+-----------------------------------------------------------+
```

### 9.2 协作组表结构

**COLLAB_GROUPS表：**

| 列名 | 类型 | 说明 |
|------|------|------|
| GROUP_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 组ID |
| GROUP_NAME | VARCHAR(256) | 组名称 |
| GROUP_TYPE | VARCHAR(32) | 组类型：PROJECT/TEAM/AD_HOC/PIPELINE |
| DESCRIPTION | TEXT | 描述 |
| WORKSPACE_ID | BIGINT FK → WORKSPACES | 关联的共享工作空间 |
| COORDINATOR_AGENT_ID | VARCHAR(64) FK → AGENT_REGISTRY | 协调智能体 |
| SHARING_POLICY | VARCHAR(32) | 共享策略：OPEN/MODERATED/RESTRICTED |
| STATUS | VARCHAR(32) | 状态：ACTIVE/PAUSED/ARCHIVED/SUSPENDED |
| METADATA | JSONB | 扩展元数据 |

**COLLAB_GROUP_MEMBERS表：**

| 列名 | 类型 | 说明 |
|------|------|------|
| MEMBER_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 成员ID |
| GROUP_ID | BIGINT FK → COLLAB_GROUPS | 组ID |
| AGENT_ID | VARCHAR(64) FK → AGENT_REGISTRY | 智能体ID |
| ROLE | VARCHAR(32) | 角色：LEAD/CONTRIBUTOR/OBSERVER/MEMBER |
| PERSONAL_WORKSPACE_ID | BIGINT FK → WORKSPACES | 个人工作空间ID |
| JOINED_AT | TIMESTAMPTZ | 加入时间 |
| STATUS | VARCHAR(16) | 成员状态：ACTIVE/LEFT/REMOVED |

**UNIQUE约束：(GROUP_ID, AGENT_ID)** — 同一智能体在同一组中唯一。

### 9.3 成员角色

```
+-----------------------------------------------------------+
|                 协作组成员角色体系                        |
|                                                           |
|  LEAD (负责人)                                            |
|  ├── 管理组成员（添加/移除）                              |
|  ├── 修改共享策略                                         |
|  ├── 自动创建 PERSONAL_IN_GROUP 工作空间                  |
|  └── 可发布到共享工作空间                                 |
|                                                           |
|  CONTRIBUTOR (贡献者)                                     |
|  ├── 读写共享工作空间                                     |
|  ├── 自动创建 PERSONAL_IN_GROUP 工作空间                  |
|  └── 可发布到共享工作空间                                 |
|                                                           |
|  MEMBER (成员)                                            |
|  ├── 读写共享工作空间                                     |
|  └── 自动创建 PERSONAL_IN_GROUP 工作空间                  |
|                                                           |
|  OBSERVER (观察者)                                        |
|  ├── 只读共享工作空间                                     |
|  └── 不创建 PERSONAL_IN_GROUP 工作空间                    |
+-----------------------------------------------------------+
```

### 9.4 共享策略

| 策略 | 说明 | 记忆共享行为 |
|------|------|-------------|
| OPEN | 开放策略 | 组内任意成员可直接将个人记忆发布到共享工作空间 |
| MODERATED | 审核策略 | 成员发布记忆需LEAD审核后进入共享工作空间 |
| RESTRICTED | 限制策略 | 仅LEAD可发布记忆到共享工作空间 |

### 9.5 collab_group_manager PL/pgSQL

协作组管理通过`collab_group_manager` schema提供PL/pgSQL函数：

| 函数 | 返回 | 说明 |
|------|------|------|
| create_group(p_group_name, p_group_type, p_description, p_sharing_policy, p_coordinator_agent_id) | BIGINT | 创建协作组+共享工作空间(COLLAB_GROUP) |
| get_group(p_group_id) | JSONB | 获取组信息（含成员计数） |
| update_group(p_group_id, p_status, p_sharing_policy) | BOOLEAN | 更新组状态/策略 |
| add_member(p_group_id, p_agent_id, p_role) | BIGINT | 添加成员，LEAD/CONTRIBUTOR自动创建PERSONAL_IN_GROUP工作空间 |
| remove_member(p_group_id, p_agent_id) | BOOLEAN | 移除成员（status→REMOVED） |
| get_group_members(p_group_id) | JSONB | 获取组内活跃成员列表 |
| cleanup_groups() | INT | 归档无活跃成员的组 |

**成员添加核心逻辑：**

```sql
-- add_member: LEAD/CONTRIBUTOR自动创建个人工作空间
IF p_role IN ('LEAD', 'CONTRIBUTOR') THEN
    INSERT INTO workspaces (workspace_name, workspace_type, isolation_mode)
    VALUES (group_name || ' - ' || p_agent_id, 'PERSONAL_IN_GROUP', 'ISOLATED')
    RETURNING workspace_id INTO v_ws_id;
END IF;

INSERT INTO collab_group_members (group_id, agent_id, role, personal_workspace_id)
VALUES (p_group_id, p_agent_id, p_role, v_ws_id)
ON CONFLICT (group_id, agent_id) DO UPDATE
    SET status = 'ACTIVE', role = EXCLUDED.role;
```

### 9.6 组内记忆共享

通过Python API实现组内记忆共享：

```python
# 将记忆共享到组
collab_id = share_memory_to_group(
    group_id=1,
    memory_id=42,
    shared_by="agent-001"
)

# 查询组内共享记忆
memories = get_group_shared_memories(group_id=1)
```

**共享记录存储在agent_collaboration表中，col_type='GROUP_SHARE'，context包含group_id。**

### 9.7 调度作业

| 作业名 | 调度周期 | 函数 | 说明 |
|--------|---------|------|------|
| collab_group_cleanup_job | 每日03:00 | collab_group_manager.cleanup_groups() | 归档无活跃成员的协作组 |
| collab_expiry_job | 每日00:30 | agent_perm.process_collaboration_requests() | 过期7天的PENDING协作请求标记EXPIRED |


---

## 10. 工作空间与上下文连续性

### 10.1 5种工作空间类型

v2.3.0版本支持5种工作空间类型，覆盖从单智能体对话到多智能体协作的全部场景：

| 工作空间类型 | 隔离模式 | 使用场景 | 说明 |
|-------------|---------|---------|------|
| CONVERSATION | SHARED | 单智能体对话 | 默认类型，共享上下文，Agent可访问所有历史记忆 |
| AUTONOMOUS | ISOLATED | 自主执行任务 | 隔离上下文，Agent仅可见工作空间内实体 |
| PIPELINE | SHARED | 流式任务处理 | 多步骤顺序执行，共享中间结果 |
| COLLAB_GROUP | SHARED | 协作组共享层 | 组内所有成员共享的记忆与知识空间 |
| PERSONAL_IN_GROUP | ISOLATED | 组内个人空间 | 组成员的私有草稿区，发布后进入共享层 |

```
+-----------------------------------------------------------+
|              工作空间类型与隔离模式                       |
|                                                           |
|  CONVERSATION  ─── SHARED ─── Agent可访问所有记忆         |
|  AUTONOMOUS    ─── ISOLATED ── 仅工作空间内实体可见       |
|  PIPELINE      ─── SHARED ─── 步骤间共享中间结果          |
|  COLLAB_GROUP  ─── SHARED ─── 组内全员共享                |
|  PERSONAL_IN_GROUP ── ISOLATED ── 个人私有草稿区          |
|                                                           |
|  共享模式(ISOLATED=SHARED): workspace_id匹配即可见        |
|  隔离模式(ISOLATED=ISOLATED): 仅entities.workspace_id匹配 |
+-----------------------------------------------------------+
```

### 10.2 上下文链

工作空间通过追加式上下文链（Context Chain）实现会话间的上下文连续性。每个上下文条目通过PARENT_CONTEXT_ID形成链式结构：

```
+-----------------------------------------------------------+
|                上下文链结构                               |
|                                                           |
|  CHECKPOINT ──> HANDOFF ──> SUMMARY ──> CHECKPOINT        |
|       |             |           |             |           |
|       v             v           v             v           |
| parent_id=NULL   parent=CK1   parent=HF1  parent=SM1      |
|                                                           |
|  每个上下文条目：                                         |
|  context_id | workspace_id | agent_id | session_id        |
|  context_type | context_data(JSONB) | parent_context_id   |
+-----------------------------------------------------------+
```

**上下文类型定义：**

| 上下文类型 | 说明 | 使用场景 |
|-----------|------|---------|
| CHECKPOINT | 检查点 | 关键步骤完成时保存进度，用于恢复 |
| HANDOFF | 交接 | 智能体切换时传递上下文，确保连续性 |
| SUMMARY | 摘要 | 定期压缩长上下文链，减少Token消耗 |
| ERROR_STATE | 错误状态 | 异常发生时保存错误上下文，用于故障分析 |
| AUTO_SAVE | 自动保存 | 系统定期自动保存，防止上下文丢失 |

### 10.3 智能体交接

当工作空间需要从一个智能体切换到另一个智能体时，通过HANDOFF类型的上下文条目实现无缝交接：

```python
# Python API：创建交接会话
new_session_id = create_handoff_session(
    workspace_id=42,
    new_agent_id="agent-002",
    handoff_data={
        "progress": "Step 3 of 7 complete",
        "pending_actions": ["Run validation", "Generate report"],
        "decisions": ["Use B-tree index for range queries"]
    }
)

# 内部流程：
# 1. 创建新agent_session，predecessor_session_id指向旧会话
# 2. 保存HANDOFF上下文到workspace_context
# 3. 更新workspaces.current_agent_id和current_session_id
```

**PL/pgSQL实现：**

```sql
-- workspace_manager.create_handoff()
-- 1. 创建新会话
INSERT INTO agent_session (session_id, agent_id, workspace_id,
                           predecessor_session_id, is_active, context)
VALUES (v_session_id, p_new_agent_id, p_workspace_id,
        v_ws.current_session_id, TRUE, p_handoff_data);

-- 2. 保存HANDOFF上下文
INSERT INTO workspace_context (workspace_id, agent_id, session_id, context_type, context_data)
VALUES (p_workspace_id, p_new_agent_id, v_session_id, 'HANDOFF', p_handoff_data);

-- 3. 更新工作空间
UPDATE workspaces
SET current_agent_id = p_new_agent_id,
    current_session_id = v_session_id;
```

### 10.4 recover_workspace

工作空间恢复功能将上下文链、活跃任务、最近会话和实体信息打包为完整的恢复快照：

```python
# Python API：恢复工作空间
recovery_data = recover_workspace(workspace_id=42)

# 返回结构：
# {
#     "workspace": {...},             # 工作空间基本信息
#     "context_chain": [...],         # 最近5条上下文条目
#     "active_tasks": [...],          # PENDING/RUNNING/BLOCKED任务
#     "recent_sessions": [...],       # 最近5个会话
#     "recent_entities": [...]        # ISOLATED模式下最近10个实体
# }
```

**恢复逻辑：**
- ISOLATED模式：额外返回工作空间内最近10个实体
- SHARED模式：不返回实体列表（全局可见）
- 仅包含PENDING/RUNNING/BLOCKED状态的任务

### 10.5 workspace_manager PL/pgSQL

工作空间管理通过`workspace_manager` schema提供PL/pgSQL函数：

| 函数 | 返回 | 说明 |
|------|------|------|
| create_workspace(p_name, p_workspace_type, p_isolation_mode, p_owner_user_id) | BIGINT | 创建工作空间 |
| get_workspace(p_workspace_id) | JSONB | 获取工作空间完整信息 |
| update_workspace_status(p_workspace_id, p_new_status) | BOOLEAN | 更新状态（仅ACTIVE/PAUSED可变更） |
| delete_workspace(p_workspace_id) | BOOLEAN | 删除工作空间 |
| add_context_entry(p_workspace_id, p_agent_id, p_context_type, p_session_id, p_context_data) | BIGINT | 添加上下文条目 |
| get_context_chain(p_workspace_id, p_limit) | TABLE | 获取上下文链 |
| create_handoff(p_workspace_id, p_new_agent_id, p_handoff_data) | VARCHAR | 创建交接会话 |
| recover_to_checkpoint(p_workspace_id) | JSONB | 恢复到最近检查点 |
| get_workspace_summary(p_workspace_id) | JSONB | 工作空间概要（含上下文/任务计数） |
| cleanup_abandoned() | INT | 归档30天无活跃会话的工作空间 |

### 10.6 调度作业

| 作业名 | 调度周期 | 函数 | 说明 |
|--------|---------|------|------|
| workspace_cleanup_job | 每日01:00 | workspace_manager.cleanup_abandoned() | 归档废弃工作空间 |
| stale_workspace_detect_job | 每小时 | UPDATE workspaces SET status='PAUSED' | 7天无活跃会话的工作空间自动暂停 |
| session_cleanup_job | 每30分钟 | agent_perm.cleanup_expired_sessions() | 清理超过300分钟的过期会话 |


---

## 11. 任务规划引擎

### 11.1 核心表结构

任务规划引擎通过4张核心表实现完整的计划-步骤-工具调用-依赖关系管理：

```
+-----------------------------------------------------------+
|                 任务规划引擎表关系                        |
|                                                           |
|  task_plans (计划)                                        |
|    ├── task_steps (步骤) ──── plan_id FK                  |
|    ├── task_tool_calls (工具调用) ── plan_id FK           |
|    │       └── step_id FK (可选)                          |
|    ├── task_context_snapshots (上下文快照) ── plan_id FK  |
|    └── task_dependencies (依赖) ── source/target plan_id  |
|                                                           |
|  workspace_tasks (工作空间-计划关联)                      |
|       workspace_id + plan_id 复合主键                     |
+-----------------------------------------------------------+
```

**TASK_PLANS表：**

| 列名 | 类型 | 说明 |
|------|------|------|
| PLAN_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 计划ID |
| AGENT_ID | VARCHAR(64) | 执行智能体 |
| GOAL | TEXT | 计划目标 |
| STATUS | VARCHAR(32) | 状态：PENDING/RUNNING/BLOCKED/SUCCESS/FAILED/CANCELLED |
| PRIORITY | INT | 优先级，默认5 |
| STRATEGY | VARCHAR(200) | 执行策略 |
| RESULT_SUMMARY | TEXT | 结果摘要 |
| CREATED_AT | TIMESTAMPTZ | 创建时间 |
| UPDATED_AT | TIMESTAMPTZ | 更新时间 |
| COMPLETED_AT | TIMESTAMPTZ | 完成时间 |

**TASK_STEPS表：**

| 列名 | 类型 | 说明 |
|------|------|------|
| STEP_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 步骤ID |
| PLAN_ID | BIGINT FK → TASK_PLANS ON DELETE CASCADE | 所属计划 |
| PLAN_STATUS | VARCHAR(32) | 计划状态快照 |
| STEP_ORDER | INT | 步骤顺序 |
| DESCRIPTION | TEXT | 步骤描述 |
| TOOL_NAME | VARCHAR(100) | 工具名称 |
| TOOL_INPUT | JSONB | 工具输入参数 |
| TOOL_OUTPUT | JSONB | 工具输出结果 |
| STATUS | VARCHAR(32) | 步骤状态：PENDING/RUNNING/SUCCESS/FAILED/SKIPPED |
| STARTED_AT | TIMESTAMPTZ | 开始时间 |
| COMPLETED_AT | TIMESTAMPTZ | 完成时间 |

### 11.2 上下文快照

任务执行过程中可保存上下文快照，支持断点恢复：

| 列名 | 类型 | 说明 |
|------|------|------|
| SNAPSHOT_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 快照ID |
| PLAN_ID | BIGINT FK → TASK_PLANS ON DELETE CASCADE | 所属计划 |
| SNAPSHOT_TYPE | VARCHAR(32) | 快照类型：MANUAL/AUTO/CHECKPOINT/RECOVERY |
| CONTEXT_DATA | JSONB | 快照数据 |
| CREATED_AT | TIMESTAMPTZ | 创建时间 |

```python
# 保存快照
snapshot_id = save_snapshot(
    plan_id=1,
    snapshot_type="CHECKPOINT",
    context_data={"step": 3, "variables": {"x": 42}}
)

# 快照类型说明：
# MANUAL: 手动保存
# AUTO: 自动保存（系统定时触发）
# CHECKPOINT: 检查点（关键步骤完成时）
# RECOVERY: 恢复点（用于故障恢复）
```

### 11.3 工具调用审计

所有工具调用通过task_tool_calls表进行完整审计：

| 列名 | 类型 | 说明 |
|------|------|------|
| CALL_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 调用ID |
| PLAN_ID | BIGINT FK → TASK_PLANS ON DELETE CASCADE | 所属计划 |
| STEP_ID | BIGINT FK → TASK_STEPS | 关联步骤（可选） |
| TOOL_NAME | VARCHAR(100) | 工具名称 |
| TOOL_INPUT | JSONB | 工具输入 |
| TOOL_OUTPUT | JSONB | 工具输出 |
| STATUS | VARCHAR(32) | 调用状态：PENDING/RUNNING/SUCCESS/FAILED |
| DURATION_MS | INT | 执行耗时（毫秒） |

```python
# 记录工具调用
call_id = log_tool_call(
    plan_id=1, step_id=5,
    tool_name="search_memories",
    tool_input={"keyword": "数据库优化", "limit": 10},
    tool_output={"results": [...], "count": 5},
    status="SUCCESS", duration_ms=230
)
```

### 11.4 依赖关系

计划间通过task_dependencies表建立依赖关系，支持3种依赖类型：

| 列名 | 类型 | 说明 |
|------|------|------|
| DEP_ID | BIGINT GENERATED ALWAYS AS IDENTITY PK | 依赖ID |
| SOURCE_PLAN_ID | BIGINT FK → TASK_PLANS ON DELETE CASCADE | 源计划 |
| TARGET_PLAN_ID | BIGINT FK → TASK_PLANS ON DELETE CASCADE | 目标计划 |
| DEP_TYPE | VARCHAR(32) | 依赖类型：HARD/SOFT/CONDITIONAL |

**依赖类型语义：**

```
+-----------------------------------------------------------+
|                任务依赖关系图                             |
|                                                           |
|  Plan A ──── BLOCKS ────> Plan B                          |
|  (A必须先完成，B才能开始)                                 |
|                                                           |
|  Plan C ──── ENABLES ────> Plan D                         |
|  (C完成后D才具备执行条件，但D不一定会执行)                |
|                                                           |
|  Plan E ──── RELATES_TO ──> Plan F                        |
|  (E与F有关联，无强制依赖)                                 |
|                                                           |
|  Plan G ──── CONFLICTS ──> Plan H                         |
|  (G与H互斥，不可同时执行)                                 |
+-----------------------------------------------------------+
```

| 依赖类型 | 说明 | 调度行为 |
|---------|------|---------|
| HARD | 硬依赖 | 目标计划必须完成后源计划才能开始 |
| SOFT | 软依赖 | 建议等待，但不强制阻塞 |
| CONDITIONAL | 条件依赖 | 仅在特定条件满足时生效 |

### 11.5 计划状态机

```
+---------+     开始    +---------+     阻塞    +---------+
| PENDING | ----------> | RUNNING | ----------> | BLOCKED |
| (待执行)|             | (执行中)|             | (阻塞)  |
+---------+             +---------+             +---------+
               ┌──────────────┤                      |
               v              v                      v
        +---------+    +---------+            +---------+
        | SUCCESS |    | FAILED  |            |CANCELLED|
        | (成功)  |    | (失败)  |            | (取消)  |
        +---------+    +---------+            +---------+

终态: SUCCESS / FAILED / CANCELLED
进入终态时自动设置 completed_at = NOW()
```

### 11.6 步骤状态机

```
+---------+    开始     +---------+
| PENDING | ----------> | RUNNING |
+---------+             +---------+
                             |
              ┌──────────────┼──────────────┐
              v              v              v
        +---------+    +---------+    +---------+
        | SUCCESS |    | FAILED  |    | SKIPPED |
        +---------+    +---------+    +---------+

RUNNING进入时: started_at = NOW()
终态进入时: completed_at = NOW()
```


---

## 12. Harness模板系统

### 12.1 HARNESS_META扩展表

Harness模板是可复用的智能体执行蓝图，存储为ENTITIES表中ENTITY_TYPE='HARNESS_TEMPLATE'的实体，通过HARNESS_META扩展表定义输入输出规格与执行模式：

| 列名 | 类型 | 说明 |
|------|------|------|
| ENTITY_ID | BIGINT PK | FK → ENTITIES(ENTITY_ID) ON DELETE CASCADE |
| ENTITY_TYPE | VARCHAR(32) | 反规范化，默认'HARNESS_TEMPLATE' |
| TEMPLATE_VERSION | INT | 模板版本号，默认1 |
| INPUT_SCHEMA | JSONB | 输入参数JSON Schema定义 |
| OUTPUT_SCHEMA | JSONB | 输出结果JSON Schema定义 |
| EXECUTION_MODE | VARCHAR(32) | 执行模式：SEQUENTIAL/PARALLEL/CONDITIONAL |

### 12.2 模板生命周期

```
+---------+     发布    +-----------+    废弃     +-----------+
|  DRAFT  | ----------> | PUBLISHED | ----------> | DEPRECATED|
| (草稿)  |             | (已发布)  |             | (已废弃)  |
+---------+             +-----------+             +-----------+

DRAFT: 模板仅创建者可见，可编辑修改
PUBLISHED: 模板对所有智能体可见（visibility=SHARED），可实例化
DEPRECATED: 模板不再推荐使用，已有实例仍可运行
```

模板生命周期通过ENTITIES表的STATUS字段控制：

| STATUS | 语义 | 可见性 |
|--------|------|--------|
| ACTIVE | PUBLISHED（活跃可用） | 默认SHARED |
| DRAFT | DRAFT（草稿编辑） | PRIVATE |
| ARCHIVED | DEPRECATED（已废弃） | 仅归档查询 |

### 12.3 模板继承

Harness模板支持通过ENTITY_EDGES的DERIVES_FROM边实现继承扩展：

```
Base Template ──── DERIVES_FROM ────> Extended Template
(基础模板)                            (扩展模板)
input_schema: {role, objective}       input_schema: {role, objective, policies}
output_schema: {report}               output_schema: {report, risk_level}
execution_mode: SEquential            execution_mode: CONDITIONAL
```

**模板实例化流程：**

```python
# 实例化模板
instance_id = instantiate_harness_template(
    entity_id=1,               # 模板实体ID
    variable_values={"role": "security analyst", "objective": "audit"},
    agent_id="agent-001"
)

# 内部流程：
# 1. get_harness_template(entity_id) 获取模板
# 2. CONTENT中的{variable}占位符替换为variable_values
# 3. 创建TASK_OUTPUT实体（实例化产物）
# 4. 建立USES_HARNESS边：instance -> template
```

### 12.4 执行模式

| 执行模式 | 说明 | 适用场景 |
|---------|------|---------|
| SESEQUENTIAL | 步骤按顺序依次执行 | 研究分析、代码生成、安全审计 |
| PARALLEL | 步骤并行执行 | 数据分析、多源检索 |
| CONDITIONAL | 根据条件选择执行路径 | 任务规划、复杂决策 |

### 12.5 5个内置模板

系统预装5个内置Harness模板，覆盖主要智能体工作流场景：

| 模板名称 | 分类 | 执行模式 | 输入参数 | 输出结果 |
|---------|------|---------|---------|---------|
| Research Analyst | research | SESEQUENTIAL | role, domain, objective, query | report, sources |
| Code Assistant | development | SESEQUENTIAL | role, language, guidelines, task | code, explanation |
| Data Analyst | analytics | PARALLEL | role, focus_area, data_query | analysis, visualizations |
| Task Planner | orchestration | CONDITIONAL | role, constraints, objective | plan, status |
| Security Auditor | security | SESEQUENTIAL | role, policies, action | findings, risk_level |

**内置模板输入Schema示例（Research Analyst）：**

```json
{
    "type": "object",
    "properties": {
        "role": {"type": "string", "description": "Agent role"},
        "domain": {"type": "string", "description": "Research domain"},
        "objective": {"type": "string", "description": "Research objective"},
        "query": {"type": "string", "description": "Search query"}
    },
    "required": ["role", "objective"]
}
```

### 12.6 Harness API函数

| 函数 | 说明 |
|------|------|
| create_harness_template(title, summary, content, category, input_schema, output_schema, execution_mode, ...) | 创建模板实体+harness_meta |
| get_harness_template(entity_id) | 获取模板完整信息 |
| update_harness_template(entity_id, **kwargs) | 更新实体/harness_meta字段 |
| delete_harness_template(entity_id) | 删除模板（先删harness_meta再删entity） |
| list_harness_templates(category, execution_mode, limit, offset) | 列表查询模板 |
| get_template_with_variables(entity_id) | 从input_schema解析变量列表 |
| instantiate_harness_template(entity_id, variable_values, agent_id) | 实例化模板，变量替换+USES_HARNESS边 |
| count_harness_templates(category) | 统计模板数量 |



---

## 13. 属性图API

### 13.1 概述

本系统基于Apache AGE扩展构建实体关系网络，使用Cypher查询语言实现图查询。单一属性图以ENTITIES为顶点、ENTITY_EDGES为边，支持邻居遍历、路径查找、社区检测等图分析能力。

### 13.2 Apache AGE配置

每次使用AGE Cypher查询前，必须加载扩展并设置search_path：

```sql
LOAD 'age';
SET search_path = ag_catalog, "$user", public;
```

### 13.3 Cypher查询模式

**邻居遍历：**

```sql
SELECT * FROM cypher('memory_graph', $$
    MATCH (a)-[e]->(b)
    WHERE a.entity_id = 42
    RETURN b.entity_id, b.title, type(e)
$$) AS (target_id agtype, title agtype, edge_type agtype);
```

### 13.4 graph_api.py

graph_api.py提供9个Python函数：

| 函数 | 参数 | 返回类型 | 说明 |
|------|------|------|------|
| get_neighbors | entity_id, direction, edge_type, min_strength | list | 获取邻居节点 |
| get_reachable | entity_id, max_depth | list | 获取可达节点 |
| get_shortest_path | from_id, to_id | list | 最短路径查找 |
| find_similar_entities | entity_id, top_k | list | 相似实体推荐 |
| get_entity_context | entity_id | dict | 实体上下文信息 |
| get_subgraph | entity_ids, depth | dict | 获取子图 |
| graph_search | keyword, entity_type, min_importance | list | 图关键词搜索 |
| find_communities | entity_id, max_depth | list | 社区检测 |
| get_graph_stats | - | dict | 图统计信息 |

**SQL回退机制：** 当AGE查询失败时，自动回退到ENTITY_EDGES表的SQL查询。

### 13.5 典型使用场景

| 场景 | 说明 | 使用函数 |
|------|------|------|
| 知识遍历 | 沿关系边遍历知识网络 | get_neighbors, get_shortest_path |
| 相似度搜索 | 查找结构相似的实体 | find_similar_entities |
| 社区检测 | 识别知识社区 | find_communities |
| 路径查找 | 发现实体间隐含关系 | get_shortest_path |


---

## 14. 向量检索引擎

### 14.1 概述

v2.3.1新增embedding_api.py模块，提供12个Python函数，实现向量嵌入的生成、存储、检索与批量处理。底层使用pgvector扩展的`<=>`余弦距离算子和`::vector`类型转换，配合pg-embedding-gen-by-yhw扩展和memory.generate_embedding() PL/pgSQL函数。

### 14.2 pgvector基础

```sql
-- 存储向量
INSERT INTO entity_embeddings (entity_id, entity_type, embedding, embed_model, embedded_at)
VALUES (123, 'MEMORY', '[0.1, 0.2, ...]'::vector, 'text-embedding-bge-m3', NOW());

-- 余弦距离检索（<=> 算子，值越小越相似）
SELECT e.entity_id, e.title,
       (ee.embedding <=> '[0.1, 0.2, ...]'::vector) AS distance
FROM entity_embeddings ee
JOIN entities e ON e.entity_id = ee.entity_id
ORDER BY distance ASC
LIMIT 10;
```

**pgvector关键特性：**

| 特性 | 说明 |
|------|------|
| VECTOR(1024) | 1024维向量类型 |
| <=> 算子 | 余弦距离（0=完全相同，2=完全相反） |
| HNSW索引 | 高性能近似最近邻索引 |
| ::vector cast | 从JSON字符串转换为向量类型 |

**与Oracle VECTOR_DISTANCE的区别：**

| 特性 | PG18 pgvector | Oracle VECTOR_DISTANCE |
|------|--------------|----------------------|
| 距离算子 | `<=>` (中缀) | VECTOR_DISTANCE(COSINE, a, b) (函数) |
| 类型转换 | `::vector` | TO_VECTOR() |
| 绑定方式 | `%s` 位置绑定 | `:named` 命名绑定 |
| 模糊匹配 | ILIKE | UPPER() + LIKE |
| 分页 | LIMIT/OFFSET | FETCH FIRST N ROWS ONLY |

### 14.3 HNSW索引

```sql
CREATE INDEX idx_entity_embeddings_hnsw ON entity_embeddings
USING hnsw (embedding vector_cosine_ops)
WITH (M = 32, ef_construction = 128);
```

### 14.4 pg-embedding-gen-by-yhw扩展

自研PostgreSQL扩展，通过COPY FROM PROGRAM机制调用Python代理生成嵌入向量：

```
+------------------+    COPY FROM PROGRAM    +------------------+
| PostgreSQL 18    | ----------------------> | Python 3.x 代理  |
| memory.generate  |   传入文本行            | 调用embedding API|
| _embedding()     | <---------------------- | 返回向量行       |
+------------------+    返回向量结果         +------------------+
```

核心优势：纯SQL调用、无需C编译、自动降级、PL/pgSQL封装。

### 14.5 embedding_api.py

12个Python函数完整签名：

| 函数 | 参数 | 返回类型 | 说明 |
|------|------|------|------|
| generate_embedding | text, api_url, model, timeout | list[float] | 调用API生成向量 |
| store_embedding | entity_id, entity_type, text, api_url, model | bool | 生成+存储嵌入 |
| store_embedding_vector | entity_id, entity_type, embedding, model | bool | 存储预计算向量 |
| get_embedding | entity_id, entity_type | dict | 获取嵌入元数据 |
| delete_embedding | entity_id, entity_type | bool | 删除嵌入 |
| search_similar | text, top_k, entity_type, workspace_id, api_url, model | list[dict] | 向量相似搜索 |
| search_by_entity_id | entity_id, entity_type, top_k, workspace_id | list[dict] | 基于已有实体搜索 |
| search_hybrid | text, keyword, top_k, entity_type, workspace_id, vector_weight | list[dict] | 向量+关键词混合检索 |
| search_multi_type | text, entity_types, top_k, workspace_id | dict[str,list] | 跨类型向量检索 |
| generate_embeddings_batch | entity_type, limit, api_url, model | dict | 批量生成嵌入 |
| get_embedding_stats | - | dict | 嵌入统计 |
| get_model_dimension | model | int | 获取/检测模型维度 |

### 14.6 混合检索（search_hybrid）

向量+关键词双信号混合，返回三维评分：

```python
results = search_hybrid(
    text="database architecture",
    keyword="architecture",
    top_k=10,
    vector_weight=0.7
)

for r in results:
    print(f"{r['title']}: vec={r['vector_score']:.3f} "
          f"kw={r['keyword_score']:.3f} hybrid={r['hybrid_score']:.3f}")
```

评分计算：

```
vector_score = max(0, 1 - cosine_distance) * vector_weight
keyword_score = (1 - vector_weight)  [if keyword ILIKE matches]
hybrid_score = vector_score + keyword_score
```

### 14.7 跨类型检索（search_multi_type）

同时检索MEMORY、KNOWLEDGE、SPEC三种类型，按类型分组返回。

### 14.8 EMBEDDING_GENERATION_JOB

pg_cron调度作业，每2小时自动为缺少向量的MEMORY和KNOWLEDGE实体生成嵌入。增量处理（NOT EXISTS）、批量限制（LIMIT 100）、NULL安全、幂等执行。


---

## 15. 安全体系

### 15.1 DataMaskingService

数据脱敏服务支持7种敏感模式的上下文感知脱敏：

| 模式 | 正则表达式 | 脱敏规则 | 示例 |
|------|----------|----------|------|
| credit_card | \d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4} | 仅保留后4位 | ****-****-****-1234 |
| ssn | \d{3}-\d{2}-\d{4} | 仅保留后4位 | ***-**-5678 |
| jwt_token | eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+ | 完全脱敏 | [REDACTED_JWT] |
| api_key | [A-Za-z0-9]{32,} | 仅保留前4位 | sk-1***[REDACTED] |
| email | [\w.+-]+@[\w-]+\.[\w.]+ | 遮掩用户名 | j***@example.com |
| ip_address | \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3} | 遮掩后2段 | 10.10.***.*** |
| phone | \d{3}[-.]?\d{3}[-.]?\d{4} | 仅保留后4位 | ***-***-5678 |

### 15.2 ReversibleEncryption

基于AES的可逆加密，用于凭证存储。密钥自动生成并存储在system_config表中。

### 15.3 密码哈希

```python
def hash_password(password: str) -> str:
    return "SHA256:" + hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, password_hash: str) -> bool:
    return hash_password(password) == password_hash
```

SHA256:前缀为7个字符。

### 15.4 可见性访问控制

| 可见性 | 访问规则 |
|--------|---------|
| PUBLIC | 全局可见 |
| SHARED | 同工作空间内可见 |
| PRIVATE | 仅创建者可见 |

### 15.5 agent_permission_manager PL/pgSQL

agent_perm schema提供：check_entity_access, check_workspace_access, log_access, cleanup_expired_sessions, process_collaboration_requests。

---

## 16. 数据架构

### 16.1 表分类概览

系统共27张表，按功能分为6类：

| 类别 | 表名 | 说明 |
|------|------|------|
| **核心表** (7) | entities, entity_edges, knowledge_meta, entity_embeddings, spec_meta, harness_meta, entity_tags | 统一实体模型及扩展元数据 |
| **系统表** (3) | system_users, system_config, tags | 用户认证、配置、标签 |
| **智能体表** (5) | agent_registry, agent_credentials, agent_session, entity_access_log, agent_permission_log | 智能体注册、凭证、会话、审计 |
| **协作表** (3) | agent_collaboration, collab_groups, collab_group_members | 协作请求、协作组 |
| **工作空间表** (3) | workspaces, workspace_context, workspace_tasks | 工作空间与上下文 |
| **任务表** (5) | task_plans, task_steps, task_context_snapshots, task_tool_calls, task_dependencies | 任务规划全生命周期 |

### 16.2 BIGINT主键策略

所有主键使用PostgreSQL 18的BIGINT GENERATED ALWAYS AS IDENTITY：

```sql
entity_id  BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
plan_id    BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
group_id   BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY
```

| 特性 | PG18 BIGINT IDENTITY | Oracle VARCHAR2(64) |
|------|---------------------|---------------------|
| 类型 | 8字节整数 | 32字符十六进制字符串 |
| 生成 | 数据库自动递增 | RAWTOHEX(SYS_GUID()) |
| 存储 | 8字节 | 64字节 |
| 索引效率 | 高（整数比较） | 低（字符串比较） |
| JOIN性能 | 快 | 慢 |

### 16.3 JSONB策略

| 操作 | 方法 | 说明 |
|------|------|------|
| 写入 | json.dumps() -> %s绑定 | Python端序列化为字符串 |
| 读取 | 自动转dict | psycopg2自动反序列化JSONB列 |
| 查询 | column ->> 'key' | JSONB文本提取运算符 |
| 过滤 | column @> '{"key":"val"}'::jsonb | JSONB包含运算符 |

### 16.4 索引策略

系统共69个索引：

| 索引类型 | 数量 | 说明 |
|---------|------|------|
| 主键索引 | 27 | 所有IDENTITY列自动创建 |
| 外键索引 | 20+ | 所有FK列索引 |
| HNSW索引 | 1 | entity_embeddings.embedding向量索引 |
| GIN索引 | 1 | 知识全文搜索 |
| 业务索引 | 20+ | 复合查询优化 |

### 16.5 标签规范化设计

```
+----------+     +-------------+     +--------+
| entities |---->| entity_tags |<----| tags   |
| entity_id|     | entity_id   |     |tag_id  |
|          |     | entity_type |     |tag_name|
|          |     | tag_id      |     +--------+
+----------+     +-------------+
```

### 16.6 无表分区架构

PostgreSQL 18版本不使用表分区，通过69个索引覆盖所有高频查询路径。如需未来引入分区，可在LIST/RANGE分区基础上逐步演进。

### 16.7 无JRD Duality Views

PG18版本不提供Oracle JRD (JSON Relational Duality) 视图。所有CRUD操作通过Python API + PL/pgSQL函数实现，功能等价但架构不同。


---

## 17. 自动化运维

### 17.1 13个pg_cron调度作业

| 作业名 | 调度 | 说明 |
|---------|------|------|
| memory_fusion_job | 每日 02:00 | 融合相似记忆 |
| knowledge_extraction_job | 每日 03:00 | 从记忆提取知识 |
| knowledge_review_job | 每日 06:00 | 标记待复习知识 |
| session_cleanup_job | 每30分钟 | 清理过期会话 |
| access_log_purge_job | 每周日 04:00 | 清理90天前访问日志 |
| entity_archive_job | 每周日 05:00 | 归档180天前实体 |
| collab_expiry_job | 每日 00:30 | 处理协作过期 |
| workspace_cleanup_job | 每日 01:00 | 清理废弃工作空间 |
| stale_workspace_detect_job | 每小时 | 检测7天不活跃工作空间 |
| dormant_agent_job | 每30分钟 | 休眠超时智能体 |
| credential_cleanup_job | 每日 02:00 | 清理过期凭证 |
| collab_group_cleanup_job | 每日 03:00 | 归档无成员协作组 |
| embedding_generation_job | 每2小时 | 自动生成缺失的嵌入向量 |

### 17.2 作业设计模式

**幂等部署：** 所有作业使用DO $$ ... IF NOT EXISTS ... $$块：

```sql
DO $$
BEGIN
    PERFORM cron.schedule('dormant_agent_job', '*/30 * * * *', $JOB$
        UPDATE agent_registry SET status = 'DORMANT', updated_at = now()
        WHERE status = 'ACTIVE'
          AND last_active_at < now() - (
              SELECT config_value::INT FROM system_config WHERE config_key = 'dormant_timeout_min'
          ) * interval '1 minute';
    $JOB$);
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'dormant_agent_job already exists: %', SQLERRM;
END;
$$;
```

**SYSTEM_CONFIG驱动：** 关键参数存储在system_config表中，作业运行时动态读取。

---

## 18. 可视化控制台

### 18.1 9页面仪表盘

| 页面 | 路由 | 功能 |
|------|------|------|
| Login | /login | PBKDF2-SHA256认证，5分钟自动注销，中英双语 |
| Knowledge | /knowledge | 图/List双视图，内联详情展开，粘性表头 |
| Memory | /memory | 图/List双视图，内联详情展开，粘性表头 |
| Agents | /agents | 注册表/会话/协作三标签页 |
| Tasks | /tasks | 手风琴步骤详情，计划信息面板 |
| Workspaces | /workspaces | 可展开详情行，上下文时间线 |
| Graph Explorer | /graph | vis-network交互式图可视化 |
| Specs | /specs | 规格管理，spec-plan关联 |
| Collab | /collab | 协作组管理，成员列表 |

### 18.2 技术架构

```
+-------------------+
|    server.py      |  主服务器，路由分发 (VERSION="2.3.1")
+-------------------+
        |
        +--> templates/          9 HTML模板文件
        +--> static/style.css    暗色主题样式
        +--> static/vis-network.min.js  图可视化库 (702KB UMD, 本地服务)
```

### 18.3 16个REST端点

| 端点 | 方法 | 说明 |
|------|------|------|
| /api/knowledge | GET | 获取知识列表 |
| /api/memory | GET | 获取记忆列表 |
| /api/agents | GET | 获取代理列表 |
| /api/tasks | GET | 获取任务列表 |
| /api/workspaces | GET | 获取工作空间列表 |
| /api/specs | GET | 获取规格列表 |
| /api/collab | GET | 获取协作组列表 |
| /api/stats | GET | 获取系统统计 |
| /api/graph/neighbors | GET | 获取图邻居节点 |
| /api/graph/context | GET | 获取图上下文 |
| /api/graph/stats | GET | 获取图统计 |
| /api/graph/search | GET | 图搜索 |
| /api/graph/all | GET | 获取全图数据 |
| /api/entity/detail | GET | 获取实体详情 |
| /api/search | GET | 统一搜索 |
| /api/login | POST | 用户认证 |

### 18.4 暗色主题CSS变量

```css
:root {
    --bg-primary: #1a1a2e;
    --bg-secondary: #16213e;
    --bg-card: #0f3460;
    --text-primary: #e6e6e6;
    --text-secondary: #a8a8a8;
    --accent: #e94560;
    --success: #4ecca3;
    --warning: #ffd369;
    --danger: #ff6b6b;
}
```

### 18.5 粘性表头实现

v2.3.1修复了全部7个列表页的粘性表头问题，核心CSS：

```css
/* 必须使用 border-collapse:separate 而非 collapse */
.data-table { border-collapse: separate; border-spacing: 0; }

/* thead th 粘性定位 */
.data-table thead th {
    position: sticky;
    top: 0;
    z-index: 2;
    background: var(--bg-card);
    box-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* 滚动容器去除上下padding防止内容穿透 */
.content-area { padding: 0 20px; }
```

### 18.6 分页

所有列表页统一PAGE_SIZE=30，renderPagination()分页控件：

- Knowledge: 42条 -> 2页
- Memory: 35条 -> 2页
- Workspaces: 146条 -> 5页

### 18.7 双语界面

采用data-zh/data-en属性实现中英双语界面，语言偏好存储在localStorage。

### 18.8 安全特性

| 特性 | 说明 |
|------|------|
| 5分钟自动登出 | 带倒计时器，超时自动返回登录页 |
| Session认证 | 基于SHA256密码验证的会话认证 |
| 默认凭证 | admin/admin123 |

### 18.9 图表颜色

| 实体类型 | 颜色 | 色值 |
|---------|------|------|
| KNOWLEDGE | 蓝色 | #4a90d9 |
| MEMORY | 浅蓝 | #4fc3f7 |
| TASK_OUTPUT | 橙色 | #ffb74d |
| EXPERIENCE | 红色 | #e57373 |
| HARNESS_TEMPLATE | 紫色 | #ba68c8 |
| SPEC | 绿色 | #81c784 |


---

## 19. API参考

### 19.1 connection.py (4函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| get_connection | - | psycopg2 connection |
| close_connection | connection | None |
| execute_query | sql, params, connection | list[dict] |
| execute_dml | sql, params, connection | int |

ThreadedConnectionPool(min=2, max=5)，localhost自动切换Unix socket。

### 19.2 memory_api.py (8函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_memory | title, content, category, importance, visibility, workspace_id, created_by | dict |
| get_memory | memory_id | dict |
| update_memory | memory_id, **kwargs | dict |
| delete_memory | memory_id | dict |
| search_memories | keyword, category, visibility, workspace_id, importance_min, limit, offset | list |
| reinforce_memory | memory_id | dict |
| get_memories_by_workspace | workspace_id, limit | list |
| get_memory_tags | memory_id | list |

### 19.3 knowledge_api.py (7函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_knowledge | title, content, domain, topic, difficulty, importance, visibility, workspace_id, created_by | dict |
| get_knowledge | knowledge_id | dict |
| update_knowledge | knowledge_id, **kwargs | dict |
| delete_knowledge | knowledge_id | dict |
| search_knowledge | keyword, domain, topic, difficulty, validation_status, limit, offset | list |
| add_knowledge_edge | source_id, target_id, edge_type, strength, confidence | dict |
| get_knowledge_edges | knowledge_id, edge_type | list |

### 19.4 agent_api.py (22函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_agent | name, agent_type, description, skills_tags, config | dict |
| get_agent | agent_id | dict |
| update_agent | agent_id, **kwargs | dict |
| delete_agent | agent_id | dict |
| list_agents | status, agent_type | list |
| create_session | agent_id, user_id, workspace_id | dict |
| get_session | session_id | dict |
| update_session | session_id, **kwargs | dict |
| end_session | session_id | dict |
| get_agent_sessions | agent_id, limit | list |
| get_sessions_by_user | user_id | list |
| issue_credential | agent_id, user_id, scope, expires_hours | dict |
| verify_credential | credential_id | dict |
| get_credentials_for_user | user_id | list |
| revoke_credential | credential_id | dict |
| hibernate_agent | agent_id | dict |
| wake_agent | agent_id | dict |
| register_pool_agent | name, skills_tags, description | dict |
| assign_pool_agent | required_skills, user_id | dict |
| get_agent_by_id | agent_id | dict |
| get_all_agents | - | list |
| get_active_agents | - | list |

### 19.5 task_plan_api.py (6函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_task_plan | title, description, steps, created_by | dict |
| get_task_plan | plan_id | dict |
| update_step_status | step_id, new_status, tool_output | dict |
| add_task_dependency | source_step_id, target_step_id, dependency_type | dict |
| get_plan_steps | plan_id | list |
| create_context_snapshot | plan_id, step_id, context_type, context_data | dict |

### 19.6 security.py (4函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| mask_sensitive_data | text | str |
| encrypt_value | plaintext | str |
| decrypt_value | ciphertext | str |
| verify_password | password, password_hash | bool |

### 19.7 harness_api.py (8函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_harness_template | title, summary, content, category, input_schema, output_schema, execution_mode | dict |
| get_harness_template | entity_id | dict |
| update_harness_template | entity_id, **kwargs | dict |
| delete_harness_template | entity_id | dict |
| list_harness_templates | category, execution_mode, limit, offset | list |
| get_template_with_variables | entity_id | dict |
| instantiate_harness_template | entity_id, variable_values, agent_id | dict |
| count_harness_templates | category | int |

### 19.8 graph_api.py (9函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| get_neighbors | entity_id, direction, edge_type, min_strength | list |
| get_reachable | entity_id, max_depth | list |
| get_shortest_path | from_id, to_id | list |
| find_similar_entities | entity_id, top_k | list |
| get_entity_context | entity_id | dict |
| get_subgraph | entity_ids, depth | dict |
| graph_search | keyword, entity_type, min_importance | list |
| find_communities | entity_id, max_depth | list |
| get_graph_stats | - | dict |

### 19.9 workspace_api.py (14函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_workspace | name, ws_type, isolation, description, created_by | dict |
| get_workspace | workspace_id | dict |
| update_workspace | workspace_id, **kwargs | dict |
| list_workspaces | ws_type, status | list |
| archive_workspace | workspace_id | dict |
| add_context | workspace_id, session_id, context_type, content_snapshot | dict |
| get_context_chain | workspace_id | list |
| get_latest_context | workspace_id | dict |
| create_handoff_session | predecessor_session_id, agent_id, workspace_id | dict |
| recover_workspace | workspace_id | dict |
| pause_workspace | workspace_id | dict |
| resume_workspace | workspace_id | dict |
| get_workspace_entities | workspace_id, entity_type | list |
| search_workspace_contexts | workspace_id, context_type | list |

### 19.10 spec_api.py (10函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_spec | entity_data, spec_meta | dict |
| get_spec | spec_id | dict |
| update_spec | spec_id, **kwargs | dict |
| update_spec_status | spec_id, new_status | dict |
| list_specs | status, scope, workspace_id | list |
| link_spec_to_plan | spec_id, plan_id, link_type, link_strength | dict |
| get_spec_plans | spec_id | list |
| create_plan_from_spec | spec_id, plan_title | dict |
| validate_plan_against_spec | spec_id, plan_id | dict |
| derive_spec | parent_spec_id, title, additional_criteria, additional_constraints | dict |

### 19.11 collab_api.py (10函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| create_collab_group | group_name, group_type, sharing_policy, creator_agent_id | dict |
| get_collab_group | group_id | dict |
| update_collab_group | group_id, **kwargs | dict |
| add_group_member | group_id, agent_id, role | dict |
| remove_group_member | group_id, agent_id | dict |
| get_group_members | group_id | list |
| share_memory_to_group | group_id, memory_id, from_workspace_id | dict |
| get_group_shared_memories | group_id | list |
| list_collab_groups | agent_id | list |
| delete_collab_group | group_id | dict |

### 19.12 embedding_api.py (12函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| generate_embedding | text, api_url, model, timeout | list[float] |
| store_embedding | entity_id, entity_type, text, api_url, model | bool |
| store_embedding_vector | entity_id, entity_type, embedding, model | bool |
| get_embedding | entity_id, entity_type | dict |
| delete_embedding | entity_id, entity_type | bool |
| search_similar | text, top_k, entity_type, workspace_id | list[dict] |
| search_by_entity_id | entity_id, entity_type, top_k, workspace_id | list[dict] |
| search_hybrid | text, keyword, top_k, entity_type, workspace_id, vector_weight | list[dict] |
| search_multi_type | text, entity_types, top_k, workspace_id | dict[str,list] |
| generate_embeddings_batch | entity_type, limit, api_url, model | dict |
| get_embedding_stats | - | dict |
| get_model_dimension | model | int |

### 19.13 config.py (3函数)

| 函数 | 参数 | 返回类型 |
|------|------|------|
| get_config | key | str |
| set_config | key, value | bool |
| load_config | - | dict |


---

## 20. 部署与运维

### 20.1 部署流程

4阶段SQL部署，按顺序执行：

```
+----------------+    +------------+    +-----------+    +---------------------+
| 1_schema.sql   |--->| 2_api.sql  |--->| 3_jobs.sql|--->| 4_harness_templates |
| 创建27张表、   |    | 创建7个    |    | 创建13个  |    | 创建5个内置模板     |
| 69个索引、     |    | PL/pgSQL   |    | pg_cron   |    | (可选)              |
| CHECK约束      |    | schemas    |    | 调度作业  |    |                     |
+----------------+    +------------+    +-----------+    +---------------------+
```

### 20.2 前置条件

| 组件 | 版本要求 |
|------|----------|
| PostgreSQL | 18.3+（需pgvector, Apache AGE, pg_cron, pg-embedding-gen-by-yhw） |
| Python | 3.6+（本地推荐3.14，远程兼容3.6） |
| psycopg2-binary | 2.9+ |
| pg_cron | 1.6+ |
| pgvector | 0.8+ |
| Apache AGE | 1.7+ |
| pg-embedding-gen-by-yhw | 1.0+ |

### 20.3 配置方式

支持两种配置方式：

**环境变量：**

```bash
export DB_HOST=<your_db_host>
export DB_PORT=5432
export DB_NAME=memory
export DB_USER=memory_user
export DB_PASSWORD=<your_password>
export WEB_PORT=8000
```

**config.json：**

```json
{
    "db_host": "<your_db_host>",
    "db_port": 5432,
    "db_name": "memory",
    "db_user": "memory_user",
    "db_password": "<your_password>",
    "web_port": 8000,
    "session_timeout": 300
}
```

localhost配置时自动切换为Unix socket连接。

### 20.4 测试执行

```bash
cd scripts && python -m tests.test_all
```

测试结果：162/162通过，100%通过率（12套测试）。

### 20.5 服务器控制

```bash
# 启动
./start_web_server.sh start

# 停止
./start_web_server.sh stop

# 重启
./start_web_server.sh restart

# 状态
./start_web_server.sh status
```

### 20.6 从 v2.2.x 升级

```sql
-- v2.3.0新增表
CREATE TABLE IF NOT EXISTS spec_meta (...);
CREATE TABLE IF NOT EXISTS spec_plan_links (...);
CREATE TABLE IF NOT EXISTS agent_credentials (...);
CREATE TABLE IF NOT EXISTS collab_groups (...);
CREATE TABLE IF NOT EXISTS collab_group_members (...);

-- v2.3.1新增表
CREATE TABLE IF NOT EXISTS entity_embeddings (...);

-- 更新PL/pgSQL
-- 执行 2_api.sql (ON CONFLICT DO NOTHING / OR REPLACE)

-- 更新pg_cron作业
-- 执行 3_jobs.sql (EXCEPTION WHEN OTHERS处理)
```

### 20.7 已知问题与解决方案

| 问题 | 解决方案 |
|------|----------|
| Apache AGE search_path | 每次连接需LOAD 'age' + SET search_path |
| pgvector NULL向量 | generate_embedding失败返回NULL，需过滤 |
| psycopg2 JSONB绑定 | 使用json.dumps()序列化后%s绑定 |
| vis-network容器高度 | 需明确height:calc(100vh - Npx) |
| border-collapse:collapse | 破坏sticky表头，必须用separate;border-spacing:0 |
| body min-height vs height | 列表页必须用height:100vh而非min-height:100vh |
| 滚动容器上下padding | 导致sticky表头内容穿透，必须用0 20px |


---

## 21. 版本演进

### 21.1 版本历史

| 版本 | 日期 | 核心特性 |
|------|------|----------|
| **v2.3.1** | 2026-05-27 | embedding_api.py（12函数）、EMBEDDING_GENERATION_JOB、19项嵌入测试、Web UI粘性表头+分页修复 |
| **v2.3.0** | 2026-05-24 | 规格驱动开发（SDD）、弹性智能体管理（DORMANT/POOL）、协作组 |
| **v2.2.1** | 2026-05-23 | 语言切换持久化、任务页面文本对比度 |
| **v2.2.0** | 2026-05-20 | 工作空间与上下文连续性、vis-network图可视化 |
| **v2.1.0** | 2026-05-19 | Apache AGE属性图、pgvector向量检索 |
| **v2.0.0** | 2026-05-15 | 统一架构重写、psycopg2-binary驱动 |
| **v1.0** | 2026-04-10 | 基础记忆+知识+代理管理 |
| **v0.5** | 2026-04-05 | 初始原型 |

### 21.2 各版本详解

**v2.3.1 (2026-05-27) — 向量嵌入引擎 + Web UI修复**

- 新增embedding_api.py（12函数），基于pgvector <=>余弦距离
- 新增EMBEDDING_GENERATION_JOB（pg_cron每2小时自动生成嵌入）
- 新增19项嵌入测试，总计162项全部通过
- Web UI：粘性表头修复（border-collapse:separate）、分页（PAGE_SIZE=30）、滚动修复（height:100vh）
- 登录页+全部9个HTML页面版本号统一为v2.3.1
- 演示数据补充：Knowledge 42条、Memory 35条

**v2.3.0 (2026-05-24) — 规格驱动 + 弹性管理 + 协作**

- 新增SPEC实体类型与SPEC_META表
- 新增SPEC_PLAN_LINKS规格-计划关联表（DRIVES/VALIDATES/CONSTRAINS/EXTENDS）
- 新增spec_manager PL/pgSQL schema（6函数）
- 新增spec_api.py（10函数）
- 新增DORMANT/POOL智能体状态
- 新增AGENT_CREDENTIALS凭证表
- 新增dormant_agent_job和credential_cleanup_job
- 新增agent_api.py +8函数
- 新增COLLAB_GROUPS和COLLAB_GROUP_MEMBERS表
- 新增collab_api.py（10函数）和collab_group_manager PL/pgSQL schema

**v2.2.1 (2026-05-23) — UI增强**

- 语言切换持久化（localStorage）
- 任务页面文本对比度修复

**v2.2.0 (2026-05-20) — 工作空间与图可视化**

- 工作空间与上下文连续性系统
- vis-network图可视化（Graph Explorer页面）
- 代理交接机制

**v2.1.0 (2026-05-19) — 属性图与向量检索**

- Apache AGE属性图支持
- pgvector向量检索
- AGE Cypher查询

**v2.0.0 (2026-05-15) — 架构重写**

- 统一实体模型重写
- 迁移至psycopg2-binary驱动
- Python API层重构

**v1.0 (2026-04-10) — 初始版本**

- 基础记忆存储
- 简单知识管理
- 基本代理管理


---

## 22. 术语表

| 术语 | 英文 | 定义 |
|------|--------|------|
| ENTITIES | Entities | 统一实体表，存储7种类型的实体数据 |
| BIGINT IDENTITY | BIGINT GENERATED ALWAYS AS IDENTITY | PostgreSQL 18自增8字节整数主键 |
| PL/pgSQL | Procedural Language/PostgreSQL | PostgreSQL原生过程语言 |
| pgvector | pgvector extension | PostgreSQL向量扩展，支持VECTOR类型和余弦距离检索 |
| Apache AGE | Apache AGE | PostgreSQL属性图扩展，支持Cypher查询语言 |
| pg_cron | pg_cron extension | PostgreSQL定时任务调度扩展 |
| pg-embedding-gen-by-yhw | Custom PG Extension | 自研嵌入生成扩展，COPY FROM PROGRAM + Python代理 |
| HNSW | Hierarchical Navigable Small World | 高性能近似最近邻向量索引算法 |
| SDD | Specification-Driven Development | 规格驱动开发，将规格说明作为一等公民实体驱动开发流程 |
| DORMANT | Dormant State | 智能体休眠状态，保留身份与配置，临时停用以节约资源 |
| POOL | Pool State | 智能体池化状态，无状态空闲，按需技能匹配分配 |
| JSONB | JSON Binary | PostgreSQL原生二进制JSON存储格式，高性能读写 |
| psycopg2-binary | psycopg2 Binary Package | PostgreSQL Python驱动预编译包 |
| ThreadedConnectionPool | Threaded Connection Pool | psycopg2线程安全连接池 |
| agtype | AGE Data Type | Apache AGE通用数据类型 |
| Cypher | Cypher Query Language | 属性图声明式查询语言 |
| 规格驱动开发 | Spec-Driven Development | 以规格为一等实体驱动计划生成与验证的开发范式 |
| 间隔复习 | Spaced Review | 基于艾宾浩斯遗忘曲线的知识复习机制，复习间隔随复习次数指数递增 |
| 记忆融合 | Memory Fusion | 相似记忆的自动合并与知识提取过程 |
| 记忆衰减 | Memory Decay | 记忆重要性随时间指数衰减的机制 |
| 工作空间 | Workspace | 隔离的工作环境，包含实体、上下文与会话 |
| 上下文链 | Context Chain | 追加式上下文序列，支持代理交接与恢复 |
| 属性图 | Property Graph | Apache AGE原生图数据结构，支持顶点和边的属性 |
| 规格 | Specification (SPEC) | 系统行为规范的正式定义，作为ENTITIES的SPEC子类型 |
| 协作组 | Collaboration Group | 多智能体协作的组织形式，包含共享与个人工作空间 |
| 凭证体系 | Credential System | 基于加密凭证的智能体访问授权机制 |
| 单表多态 | Single-Table Polymorphism | 将多种类型实体存储在同一张表中的设计模式 |
| Embedding | Vector Embedding | 文本的向量嵌入表示，用于语义相似度计算 |
| ILIKE | Case-Insensitive LIKE | PostgreSQL不区分大小写的模式匹配运算符 |
| vis-network | vis-network.js | JavaScript网络图可视化库 |
| 粘性表头 | Sticky Table Header | position:sticky实现的表头固定效果 |

---

*本白皮书由尹海文编写，PostgreSQL 18 AI 数据库记忆系统 v2.3.1，2026年5月发布，Apache 2.0许可证。*