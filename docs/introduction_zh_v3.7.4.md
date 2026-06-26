# AI Agent Infra with PostgreSQL — 社区版 v3.7.4

**版本**: v3.7.4 | **日期**: 2026-06-26 | **作者**: 尹海文 | **许可**: Apache License 2.0

> v3.7.4 引入6大扩展方向：Agent通信协议(COLLAB_MESSAGES)、多Agent编排(DAG引擎/fan-out/in)、事件驱动(publish/subscribe/LOOP_HOOKS)、高级记忆管理(consolidation/merge/reindex)、可观察性(TRACE_ID/health dashboard/drift detection)、工具生态(OpenAPI导入/TOOL_REGISTRY)。基于v3.7.0 引入的循环工程（Loop Engineering）——第4代 AI 工程方法论，构建完整的 AI Agent 基础设施。适配 PostgreSQL 18.3 生态：psycopg2 驱动、pgvector 向量搜索、Apache AGE 属性图、pg_cron 定时任务、PL/Python3u 存储过程、pgcrypto 数据库加密、Row Security Policies 行级安全。

---

## 一、项目简介

**AI Agent Infra with PostgreSQL** 是一套面向 AI Agent 的基础设施架构，基于 PostgreSQL 18.3 数据库构建，为 AI Agent 提供记忆、知识、Agent 管理、Skill 分发、身份认证、加密存储、上下文分支等完整能力。

本项目的核心设计理念是：**将 AI Agent 运行所需的一切基础设施——记忆、知识、身份、技能、安全、分支——统一收敛于一个数据库内核之中**，利用 PostgreSQL 的分区、JSONB、属性图（Apache AGE）、向量搜索（pgvector）、行级安全策略（RLS）等原生能力，在数据库层实现基础设施的完整闭环。

### 核心能力矩阵

| 能力域 | 说明 |
|--------|------|
| 记忆与知识 | 5信号统一混合搜索、向量嵌入、知识图谱、记忆融合 |
| Agent 管理 | 弹性池化管理、会话生命周期、凭证加密、协作组 |
| 工作空间 | 上下文连续性、Agent 交接、会话恢复 |
| 上下文分支 | fork/merge/abandon/resume 分支、冲突检测、学习提取 |
| 规格驱动 | Spec 文档管理、计划关联、验证与派生 |
| Skill 分发 | ZIP 包解析、Agent 自动获取 |
| 身份认证 | 本地用户认证、自动注册 |
| 加密存储 | PBKDF2+流密码、pgcrypto 数据库原生加密、主密钥管理、自动加密 |
| 数据库访问安全 | 规范约束 + 最小权限用户 + SECURITY DEFINER + Row Security Policies + 审计 + 脱敏 |
| 循环工程 | 6种评估类型、生命周期钩子、协同集成（Spec-Driven/Task-Loop/Collaborative Loop） |

---

## 二、与 Oracle 版本的核心差异

本项目从 Oracle 社区版 v3.6.1 移植而来，功能完全对标，但适配了 PostgreSQL 生态：

| Oracle | PostgreSQL | 说明 |
|--------|-----------|------|
| oracledb 4.0.1+ | psycopg2 2.9+ | Python 数据库驱动 |
| `:name` 命名绑定 | `%s` 位置绑定 | SQL 参数绑定 |
| PL/SQL | PL/pgSQL + PL/Python3u | 存储过程 |
| DBMS_CRYPTO | pgcrypto (`encrypt_iv`/`decrypt_iv`) | 数据库内加密 |
| VECTOR_DISTANCE | pgvector `<=>` 运算符 | 向量相似度搜索 |
| CONTAINS + SCORE | ts_vector + ts_rank | 全文搜索 |
| GRAPH_TABLE (SQL/PGQ) | Apache AGE `cypher()` | 属性图查询 |
| Data Grants | Row Security Policies (RLS) | 行级访问控制 |
| Oracle Scheduler | pg_cron | 定时任务 |
| JRD 对偶视图 | 视图 + INSTEAD OF 触发器 | 可更新文档视图 |
| RAWTOHEX(SYS_GUID()) | encode(gen_random_bytes(16), 'hex') | ID 生成 |
| JSON_OBJECT / JSON_ARRAYAGG | jsonb_build_object / jsonb_agg | JSON 构建 |
| VARCHAR2 | VARCHAR | 字符串类型 |
| CLOB | TEXT | 大文本类型 |
| NUMBER | INTEGER / NUMERIC | 数值类型 |
| DSN `host:port/service` | host + port + dbname | 连接参数 |

---

## 三、版本历史

| 版本 | 日期 | 里程碑 |
|------|------|--------|
| **v3.7.3** | 2026-06-23 | 部署修复：建表外键顺序、DEFINE SCHEMA_OWNER、配置优先级、Embedding模型提示 |
| **v3.7.4** | 2026-06-26 |  6大扩展：Agent通信协议(COLLAB_MESSAGES)、多Agent编排(DAG引擎/fan-out/in)、事件驱动(publish/subscribe/LOOP_HOOKS)、高级记忆管理(consolidation/merge/reindex)、可观察性(TRACE_ID/health dashboard/drift detection)、工具生态(OpenAPI导入/TOOL_REGISTRY)  |
| **v3.7.2** | 2026-06-26 | 文档一致性修正：loop_manager ~33→~22、loop_api 32公共函数、LOOP_CLEANUP Weekly Sunday 06:00、PL/SQL→PL/pgSQL、ENTITIES 分区7→8、评估类型4→6、架构图对齐 |
| **v3.7.1** | 2026-06-26 | 循环工程协同集成：Spec-Driven Loop、Task-Loop Binding、Collaborative Loop、SPEC_VALIDATION/AGGREGATE 评估类型、Skill-Triggered Loop；会话持久化与认证修复 |
| **v3.7.0** | 2026-06-18 | 循环工程（第4代AI方法论）：4/5张循环表、loop_manager schema、loop_api.py、6种评估类型、生命周期钩子、3个 pg_cron 作业 |
| **v3.6.2** | 2026-06-18 | Portal 聊天发送/切换修复、15 个 PG Bug 修复 |
| **v3.6.1** | 2026-06-16 | PostgreSQL 社区版初始发布，功能对标 Oracle 社区版 v3.6.1 |
| Oracle v3.6.1 | 2026-06-14 | Bug fix：Portal 登录修复、图谱交互改进、文档一致性修正 |
| Oracle v3.6.0 | 2026-06-13 | Admin/Agent 分离架构、Recovery Code、Agent 恢复、私有 Skill 备份 |
| Oracle v3.4.0 | 2026-06-11 | Oracle Deep Data Security 深度数据安全 |
| Oracle v3.0.0 | 2026-05-30 | Skill 系统、Portal 用户系统、多 Agent 协作 |

---

## 四、核心架构

### PostgreSQL 18.3 数据库基础

| PostgreSQL 能力 | 应用场景 |
|----------------|---------|
| **LIST 分区** | ENTITIES 按 ENTITY_TYPE 分区，实现类型裁剪 |
| **引用分区** | 8 个子表继承 ENTITIES 分区策略，确保父子行物理同位 |
| **JSONB** | 上下文数据、元数据等半结构化存储，GIN 索引加速查询 |
| **pgvector** | ENTITY_EMBEDDINGS 存储 VECTOR 类型嵌入，支持 `<=>` 余弦相似度检索 |
| **Apache AGE** | pg_memory_graph 统一属性图，支持 cypher() 查询 |
| **ts_vector / ts_query** | 全文索引与检索，ts_rank 相关性评分 |
| **Row Security Policies** | 25+ 个 RLS 策略，行级/列级访问控制 |
| **pgcrypto** | encrypt_iv/decrypt_iv 数据库内 AES-CBC 加密 |
| **pg_cron** | 16 个定时调度作业 |
| **PL/Python3u** | 不可信 Python 存储过程，用于 embedding 生成等 |
| **HNSW 向量索引** | entity_embeddings 上 1024 维 pgvector HNSW 索引 |

### 分层架构

| Layer | Components |
|-------|-----------|
| **可视化层** (Visualization) | Portal（用户）+ Dashboard（管理）+ Graph Explorer · server.py · templates/ · static/ |
| **Python API 层** (API Layer) | 23 模块 · 330+ 函数 · %s 位置绑定 · memory_api · knowledge_api · agent_api · ... |
| **数据库层** (Database Layer) | 35 表 · 22 PL/pgSQL 基础函数 + 78 API 函数 · 14 模式 · 16 pg_cron 作业 · 分区 · 视图 · AGE 属性图 · pgvector · 全文索引 |

---

## 五、功能体系

### 5.1 记忆与知识系统

5信号加权融合检索是本项目的核心检索能力：

| 信号 | 默认权重 | 数据源 | PostgreSQL 实现 |
|------|---------|--------|----------------|
| **vector** | 0.40 | ENTITY_EMBEDDINGS | pgvector `<=>` 余弦距离 |
| **fulltext** | 0.25 | ts_vector 索引 | ts_rank 相关性评分 |
| **relational** | 0.20 | KNOWLEDGE_META / ENTITIES | 属性匹配评分 |
| **tag** | （含在 relational） | ENTITY_TAGS | 标签交集比例 |
| **graph** | 0.15 | ENTITY_EDGES | BFS 邻居扩散评分 |

**单 SQL 融合检索（推荐）**：`search_unified_sql()` 通过一条 CTE SQL 语句完成五信号融合，延迟降低 70-85%。

### 5.2 Agent 弹性管理

Agent 池化状态机：`POOL → ACTIVE（分配）→ POOL（释放）`

### 5.3 工作空间与上下文

WORKSPACE_CONTEXT 版本链式上下文条目，PARENT_CONTEXT_ID 形成链表，支持 Agent 交接。

### 5.4 上下文分支

fork/merge/abandon/resume 分支操作，冲突检测，学习提取。

### 5.5 多 Agent 协同

协作组 + Branch + Spec + Task Plan + Harness 五层联动。

### 5.6 规格驱动开发

SPEC_META 引用分区子表，SPEC_PLAN_LINKS 多对多关联。

### 5.7 Portal 用户系统

Portal（用户面向）+ Dashboard（管理面向）独立页面系统。12 个页面，暗色主题，中英双语。

### 5.8 Skill 存储与分发

数据库支持的 Skill 注册中心，社区版直接访问资源。

### 5.9 加密凭证系统

**双轨加密**：connection_crypto（本地文件加密）+ pgcrypto（数据库内加密）。

| 维度 | connection_crypto | pgcrypto |
|------|-------------------|----------|
| 加密对象 | 本地文件（config.json） | 数据库内数据（AGENT CREDENTIALS） |
| 密钥存储 | `~/.pg-infra/master.key` | SYSTEM_CONFIG 表 |
| 共享范围 | 单机本地 | 所有连接同一数据库的 Agent |

### 5.10 数据库访问安全策略

| 层级 | 机制 | 防护目标 |
|------|------|----------|
| L1 规范约束 | SKILL.md 明确禁止直接 SQL/DML/DDL | 规范层面禁止绕过 API |
| L2 最小权限用户 | agent_api 受限数据库用户 | 技术层面限制 DDL/DML 能力 |
| L3 SECURITY DEFINER | PL/pgSQL 函数以属主权限执行 | 强制走 API 并执行业务逻辑 |
| L4 Row Security Policies | 25+ 个 RLS 策略 + 零信任 | 行级/列级访问控制 |
| L5 审计日志 | 直接 DML 绕过检测触发器 | 审计绕过 API 的直接操作 |
| L6 凭证过滤 | save_context() 自动脱敏 | 防止凭证泄露到上下文存储 |

---

## 六、数据库对象统计

### 6.1 表（35 张）

| 分类 | 表名 | 说明 |
|------|------|------|
| **核心** | entities | 统一实体存储（8 种类型），LIST 分区 |
| | entity_edges | 有向关系边，引用分区 |
| | knowledge_meta | 知识元数据，引用分区 |
| | entity_embeddings | 向量嵌入，引用分区，HNSW 索引 |
| | harness_meta | Harness 模板元数据，引用分区 |
| | entity_tags | 标签关联，引用分区 |
| | tags | 标签定义 |
| **系统** | system_users | 用户账户 |
| | system_config | 键值配置 |
| **智能体** | agent_registry | 智能体定义 |
| | agent_credentials | 加密凭据 |
| | agent_session | 会话 + 交接链 |
| | entity_access_log | 实体访问审计 |
| **循环工程** | loop_meta | 循环定义：名称、停止条件、评估配置 |
| | loop_runs | 循环执行实例：状态、时间、Token 用量 |
| | loop_iterations | 迭代记录：输入、输出、评估结果 |
| | loop_hooks | 生命周期钩子定义 |
| | task_loop_binding | 任务步骤-循环绑定 |

### 6.2 PL/pgSQL 函数

- 22 个基础函数
- 78 个 API 函数分布在 13 个模式中
- 3 个 PL/Python3u 嵌入函数（embedding_generate, embedding_generate_batch, embedding_status）
- 3 个 pgcrypto 封装（db_crypto.encrypt/decrypt/rotate_key）

### 6.3 pg_cron 调度作业（16 个）

| 作业 | 调度 | 说明 |
|------|------|------|
| memory_fusion_job | 每日 02:00 | 融合相似记忆 + 衰减旧记忆 |
| knowledge_extraction_job | 每日 03:00 | 从记忆提取知识 |
| knowledge_review_job | 每日 06:00 | 知识审查与验证 |
| session_cleanup_job | 每 30 分钟 | 清理过期会话 |
| dormant_agent_job | 每 30 分钟 | 超时 Agent 自动设为 POOL 状态 |
| embedding_generation_job | 每 2 小时 | 自动生成缺失的 embedding |
| branch_cleanup_job | 每日 | 归档 ABANDONED 分支 |

---

## 七、Bug 修复（v3.6.1 → v3.7.0）及 v3.7.4 新功能

| # | 修复 | 影响 |
|---|------|------|
| 1 | 修复 conn→connection 拼写错误 | Portal 聊天无法发送消息 |
| 2 | 修复大写 SQL→小写 PG 兼容性 | PG 默认返回小写列名 |
| 3 | 修复 BIGINT .substring 错误 | BIGINT ID 导致 substring TypeError |
| 4 | 修复用户认证使用 user_manager.authenticate() + salt | 用户无法用加盐密码登录 |
| 5 | 修复 workspace owner_user_id 使用 username | 工作空间创建时拥有者引用错误 |
| 6 | 修复 CHAT_MESSAGE context_type 约束 | 聊天消息被约束拒绝 |
| 7 | 修复 Portal 注册时 Agent 池分配 | Portal 用户未获得池 Agent |
| 8 | 修复 Decimal 序列化为 float | 图 API 返回无法序列化的 Decimal 对象 |
| 9 | 修复图统计字段名（node_count, edge_count） | 图统计返回错误字段名 |
| 10 | 修复 branch_api.list_branches 和 graph_api.get_graph_stats 缺失函数 | API 端点返回 404 |
| 11 | 修复 task_plan_api 列不匹配 | 任务计划操作因列错误失败 |
| 12 | 修复 spec_api spec_plan_links 列不匹配 | Spec 计划链接操作失败 |
| 13 | 修复 Portal 聊天发送（_handle_portal_chat_send 缺失） | Portal 聊天发送端点返回 404 |
| 14 | 修复会话切换错误处理 | 会话切换可能导致未处理异常 |

---

## 八、快速开始

### 前置条件

- **PostgreSQL 18.3 或更高**
- **Python 3.8+，需安装 `psycopg2 2.9+`**
- 所需 PostgreSQL 扩展：pgvector、age、pg_cron、plpython3u、pgcrypto

### 1. 安装扩展

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE EXTENSION IF NOT EXISTS age;
CREATE EXTENSION IF NOT EXISTS pg_cron;
CREATE EXTENSION IF NOT EXISTS plpython3u;
```

### 2. 创建数据库

```bash
createdb -U postgres ai_agent
```

### 3. 部署 Schema

```bash
psql -U postgres -d ai_agent -f scripts/deploy/1_schema.sql
psql -U postgres -d ai_agent -f scripts/deploy/2_api.sql
psql -U postgres -d ai_agent -f scripts/deploy/3_jobs.sql
```

### 4. 安装 Python 依赖

```bash
pip install psycopg2-binary
```

### 5. 配置

```bash
export MASTER_DB_KEY=$(python3 -c "import base64,os; print(base64.b64encode(os.urandom(32)).decode())")
export MEMORY_DB_USER=<db_user>
export MEMORY_DB_PASSWORD=<db_password>
export MEMORY_DB_HOST=<db_host>
export MEMORY_DB_PORT=5432
export MEMORY_DB_NAME=<db_name>
```

### 6. 运行测试

```bash
cd scripts && python -m tests.test_all
```

### 7. 启动可视化服务器

```bash
./start_web_server.sh start    # 启动
# 访问 http://localhost:18080 — 登录: admin / admin123
```

---

## 九、许可证与作者

### 许可证

**社区版**：Apache License 2.0 — 详见 [LICENSE](../LICENSE)

### 网站

https://db4agent.top

### 作者

**尹海文（Haiwen Yin）**

- GitHub: [https://github.com/Haiwen-Yin](https://github.com/Haiwen-Yin)
- 博客: [https://blog.csdn.net/yhw1809](https://blog.csdn.net/yhw1809)


## 循环工程协同集成（Loop Engineering Collaborative Integration）[NEW v3.7.4]

- **Spec-Driven Loop**：从 Spec 验收标准自动派生循环，SPEC_VALIDATION 评估类型
- **Task-Loop Binding**：循环绑定任务步骤，循环成功时步骤自动完成
- **Collaborative Loop**：协作组父子循环，AGGREGATE 评估汇总子循环结果，最多2层嵌套
- **Branch-Isolated Loop**：绑定分支的循环在分支上下文中运行
- **Skill-Triggered Loop**：Skill acquire 后自动触发验证循环

## 循环工程（Loop Engineering）[NEW v3.7.4]

**循环工程**是第四代 AI 工程方法论。核心概念：

- **5 阶段循环**：Plan → Act → Observe → Evaluate → Adjust
- **4 种评估类型**：TEST、DIFF、LLM_JUDGE、MANUAL
- **生命周期钩子**：PRE_RUN、POST_ITERATION、ON_STOP、ON_FAIL、ON_TIMEOUT、ON_START
- **3 个 pg_cron 任务**：loop_trigger_job、loop_stuck_check_job、loop_cleanup_job
- **4 张新表**：loop_meta、loop_runs、loop_iterations、loop_hooks
- **loop_manager** PL/pgSQL 模式 + **loop_api.py** Python 模块
- **详情面板关闭按钮**：❌ 按钮位于详情面板右上角

