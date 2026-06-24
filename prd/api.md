# API PRD - AI 学习卡片系统

## 1. API 总原则

后端使用 Django Ninja 提供 REST API 和 SSE 流式 API。前端只访问 Django 后端，不直接访问 Ollama、OpenRouter、OpenAI Compatible API、vLLM 或 SGLang。

所有数据库访问必须通过 Django ORM。所有写操作必须经过 CSRF 校验。所有 AI 输出都必须经过结构化校验后再保存。

基础路径：

```txt
/api
```

推荐响应时间格式：

```txt
ISO 8601 UTC
```

推荐 ID：

```txt
UUID
```

## 2. 通用响应

### 2.1 成功响应

普通 JSON API 直接返回资源对象或列表。

示例：

```json
{
  "id": "uuid",
  "title": "SQL 学习",
  "created_at": "2026-06-24T14:00:00Z"
}
```

### 2.2 错误响应

统一格式：

```json
{
  "error": {
    "code": "validation_error",
    "message": "输入内容不能为空",
    "details": {}
  }
}
```

常见错误码：

- `validation_error`
- `not_found`
- `csrf_failed`
- `provider_unavailable`
- `generation_failed`
- `permission_denied`
- `conflict`
- `rate_limited`

## 3. Health / CSRF

### 3.1 服务健康检查

```txt
GET /api/health
```

响应：

```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

### 3.2 初始化 CSRF

```txt
GET /api/csrf
```

用途：

- 设置 CSRF cookie。
- 前端后续 POST、PATCH、DELETE 请求带 `X-CSRFToken`。

响应：

```json
{
  "csrf": "ok"
}
```

## 4. Provider API

### 4.1 获取当前 Provider 状态

```txt
GET /api/provider/status
```

响应：

```json
{
  "provider": "ollama",
  "provider_type": "ollama",
  "model": "gpt-oss:120b",
  "base_url": "http://127.0.0.1:11434/v1",
  "status": "healthy",
  "latency_ms": 120,
  "checked_at": "2026-06-24T14:00:00Z",
  "error": null
}
```

注意：

- 不返回 API key。
- `status` 可为 `healthy`、`unhealthy`、`checking`。

### 4.2 触发 Provider 健康检查

```txt
POST /api/provider/health-check
```

响应：

```json
{
  "status": "healthy",
  "latency_ms": 120,
  "checked_at": "2026-06-24T14:00:00Z",
  "error": null
}
```

### 4.3 切换 Provider 配置

```txt
PATCH /api/provider/config
```

请求：

```json
{
  "provider_type": "openai_compatible",
  "base_url": "https://openrouter.ai/api/v1",
  "model": "openai/gpt-oss-120b",
  "api_key": "sk-..."
}
```

响应：

```json
{
  "provider": "openai_compatible",
  "model": "openai/gpt-oss-120b",
  "status": "checking"
}
```

注意：

- API key 可以写入，但不允许读回。
- 后端应保存密文或使用环境变量。

## 5. Conversation API

### 5.1 获取对话列表

```txt
GET /api/conversations
```

Query：

```txt
pinned_first=true
include_archived=false
limit=50
cursor=...
```

响应：

```json
{
  "items": [
    {
      "id": "uuid",
      "title": "SQL 学习",
      "is_pinned": true,
      "last_message_preview": "开始学习 SQL",
      "created_at": "2026-06-24T14:00:00Z",
      "updated_at": "2026-06-24T14:10:00Z"
    }
  ],
  "next_cursor": null
}
```

排序：

1. 置顶对话优先。
2. 同组内按 `updated_at` 倒序。

### 5.2 创建对话

```txt
POST /api/conversations
```

请求：

```json
{
  "title": "SQL 学习"
}
```

响应：

```json
{
  "id": "uuid",
  "title": "SQL 学习",
  "is_pinned": false,
  "created_at": "2026-06-24T14:00:00Z",
  "updated_at": "2026-06-24T14:00:00Z"
}
```

### 5.3 获取单个对话

```txt
GET /api/conversations/{conversation_id}
```

响应：

```json
{
  "id": "uuid",
  "title": "SQL 学习",
  "is_pinned": false,
  "created_at": "2026-06-24T14:00:00Z",
  "updated_at": "2026-06-24T14:10:00Z"
}
```

### 5.4 修改对话标题

```txt
PATCH /api/conversations/{conversation_id}
```

请求：

```json
{
  "title": "SQL 基础学习"
}
```

响应：

```json
{
  "id": "uuid",
  "title": "SQL 基础学习",
  "is_pinned": false,
  "updated_at": "2026-06-24T14:12:00Z"
}
```

### 5.5 置顶对话

```txt
POST /api/conversations/{conversation_id}/pin
```

响应：

```json
{
  "id": "uuid",
  "is_pinned": true,
  "updated_at": "2026-06-24T14:12:00Z"
}
```

### 5.6 取消置顶

```txt
POST /api/conversations/{conversation_id}/unpin
```

响应：

```json
{
  "id": "uuid",
  "is_pinned": false,
  "updated_at": "2026-06-24T14:12:00Z"
}
```

### 5.7 删除对话

```txt
DELETE /api/conversations/{conversation_id}
```

行为：

- 默认软删除，设置 `archived_at`。
- 不物理删除消息、卡片和题目。

响应：

```json
{
  "deleted": true
}
```

## 6. Message API

### 6.1 获取对话消息

```txt
GET /api/conversations/{conversation_id}/messages
```

Query：

```txt
limit=100
cursor=...
```

响应：

```json
{
  "items": [
    {
      "id": "uuid",
      "role": "user",
      "message_type": "plain",
      "content": "开始学习 SQL",
      "is_editable": false,
      "can_regenerate_from_here": false,
      "created_at": "2026-06-24T14:00:00Z"
    },
    {
      "id": "uuid",
      "role": "assistant",
      "message_type": "learning_card",
      "content": "## 什么是数据库",
      "learning_card_id": "uuid",
      "is_editable": false,
      "can_regenerate_from_here": true,
      "created_at": "2026-06-24T14:01:00Z"
    }
  ],
  "next_cursor": null
}
```

可编辑规则：

- 只允许修改最近一轮用户输入。
- 最近一轮指当前对话末尾最新的 user message，并且它后面最多只有一个 assistant learning card 或 quiz。
- 更早的用户输入不可修改。

重新生成规则：

- 只允许从最近一张 AI 学习卡片或最近一轮用户输入重新生成。
- 再往前的卡片和对话不允许重新生成。
- 后端必须校验，不允许只靠前端隐藏按钮。

### 6.2 创建用户消息

```txt
POST /api/conversations/{conversation_id}/messages
```

请求：

```json
{
  "content": "开始学习 SQL"
}
```

响应：

```json
{
  "id": "uuid",
  "role": "user",
  "content": "开始学习 SQL",
  "message_type": "plain",
  "created_at": "2026-06-24T14:00:00Z"
}
```

### 6.3 修改最近一轮用户输入

```txt
PATCH /api/messages/{message_id}
```

请求：

```json
{
  "content": "从零开始学习 SQL 查询"
}
```

行为：

- 仅允许修改最近一轮用户输入。
- 修改后，其后由该输入生成的最近 AI 卡片应标记为 superseded，或在重新生成时替换。
- 不允许修改更早用户消息。

响应：

```json
{
  "id": "uuid",
  "content": "从零开始学习 SQL 查询",
  "updated_at": "2026-06-24T14:15:00Z"
}
```

### 6.4 删除最近一轮用户输入

```txt
DELETE /api/messages/{message_id}
```

行为：

- 仅允许删除最近一轮用户输入。
- 如果该输入后面有最近生成的 AI 卡片，必须一起标记为 superseded 或 archived。
- 更早消息不允许删除。

响应：

```json
{
  "deleted": true
}
```

## 7. Learning Card API

### 7.1 流式生成学习卡片

```txt
POST /api/conversations/{conversation_id}/learn/stream
```

请求：

```json
{
  "user_message_id": "uuid",
  "action": "start"
}
```

`action`：

- `start`
- `continue`
- `regenerate`

规则：

- `start` 用于基于用户新输入生成第一张卡片。
- `continue` 用于基于当前学习进度生成下一张卡片。
- `regenerate` 只允许最近一张 AI 学习卡片重新生成。

SSE 事件：

```txt
event: card_start
data: {"temporary_id":"uuid"}

event: card_delta
data: {"delta":"## 什么是 SQL\n"}

event: card_done
data: {"card_id":"uuid","message_id":"uuid"}

event: error
data: {"code":"generation_failed","message":"模型生成失败"}
```

完成后保存：

- Message
- LearningCard
- Conversation updated_at

### 7.2 获取学习卡片

```txt
GET /api/learning-cards/{card_id}
```

响应：

```json
{
  "id": "uuid",
  "conversation_id": "uuid",
  "title": "什么是 SQL",
  "topic": "SQL",
  "level": "beginner",
  "markdown": "## 什么是 SQL\n...",
  "summary": "介绍 SQL 的用途和基本概念",
  "order_index": 1,
  "created_at": "2026-06-24T14:01:00Z"
}
```

### 7.3 重新生成最近学习卡片

```txt
POST /api/learning-cards/{card_id}/regenerate
```

行为：

- 仅允许最近一张 active 学习卡片。
- 原卡片标记为 superseded。
- 通过 SSE 重新返回新卡片。

建议也可以统一走：

```txt
POST /api/conversations/{conversation_id}/learn/stream
```

并传：

```json
{
  "action": "regenerate",
  "learning_card_id": "uuid"
}
```

## 8. Quiz API

### 8.1 流式生成选择题

```txt
POST /api/conversations/{conversation_id}/quiz/stream
```

请求：

```json
{
  "learning_card_id": "uuid"
}
```

规则：

- 题目基于当前最近学习卡片生成。
- 题目必须是四选一。
- 只能有一个正确答案。
- 干扰项必须合理，不能明显胡编。

SSE 事件：

```txt
event: quiz_start
data: {"temporary_id":"uuid"}

event: quiz_delta
data: {"delta":"..."}

event: quiz_done
data: {"quiz_id":"uuid"}

event: error
data: {"code":"generation_failed","message":"题目生成失败"}
```

### 8.2 获取题目

```txt
GET /api/quizzes/{quiz_id}
```

响应：

```json
{
  "id": "uuid",
  "question": "SQL 中 SELECT 的主要作用是什么？",
  "options": [
    {"label": "A", "text": "查询数据"},
    {"label": "B", "text": "删除数据库"},
    {"label": "C", "text": "启动服务器"},
    {"label": "D", "text": "创建操作系统用户"}
  ],
  "answered": false
}
```

注意：

- 用户答题前不返回 `correct_option_index`。

### 8.3 提交答案

```txt
POST /api/quizzes/{quiz_id}/answer
```

请求：

```json
{
  "selected_option_index": 0
}
```

响应：

```json
{
  "is_correct": true,
  "selected_option_index": 0,
  "correct_option_index": 0,
  "explanation": "SELECT 用于从表中查询数据。"
}
```

### 8.4 删除题目

```txt
DELETE /api/quizzes/{quiz_id}
```

规则：

- 仅允许删除最近一轮生成的题目。
- 更早题目不允许删除。

响应：

```json
{
  "deleted": true
}
```

## 9. 最近一轮编辑与重新生成规则

为了避免历史学习路径被任意篡改，系统只允许用户对最近一轮内容操作。

允许：

- 修改最近一条用户输入。
- 删除最近一条用户输入。
- 重新生成最近一张 AI 学习卡片。
- 删除最近一道题目。

不允许：

- 修改更早的用户输入。
- 删除更早的学习卡片。
- 从更早学习卡片重新生成。
- 修改已经形成历史依赖的中间内容。

后端判定标准：

```txt
目标对象必须属于该 conversation。
目标对象必须是 active 状态。
目标对象必须位于当前 conversation 的最后一轮或倒数第一张卡片。
如果目标对象后面存在非 superseded 的后续学习内容，则拒绝操作。
```

拒绝响应：

```json
{
  "error": {
    "code": "conflict",
    "message": "只能修改或重新生成最近一轮内容",
    "details": {}
  }
}
```

## 10. Prompt 质量要求

Prompt 的目标不是让模型输出漂亮废话，而是让用户真的学会知识。系统必须要求模型生成有信息密度、有教学顺序、有例子、有检查点的内容。

### 10.1 学习卡片系统 Prompt 要求

模型角色：

```txt
你是一个严谨、务实、循序渐进的私人教师。
你的目标是让用户真正掌握主题，而不是输出空泛鼓励、营销话术或装饰性废话。
```

必须遵守：

- 每次只讲一个小知识点。
- 从最基本的前置概念开始。
- 不跳步。
- 给出具体例子。
- 解释为什么这个知识点重要。
- 指出常见误解。
- 用简短检查问题确认用户是否理解。
- 不输出空泛鼓励。
- 不使用“这很重要”“你会变得更好”这类没有信息量的句子，除非后面立刻给出具体原因。
- 如果用户主题过大，自动拆成最小可学习单元。
- 如果用户已经有上下文，承接之前卡片，不重复讲已经学过的内容。

### 10.2 学习卡片输出结构

模型应输出 JSON：

```json
{
  "title": "什么是 SQL",
  "topic": "SQL",
  "level": "beginner",
  "markdown": "## 什么是 SQL\nSQL 是...\n\n### 例子\n```sql\nSELECT name FROM users;\n```\n\n### 常见误解\n...\n\n### 检查点\n...",
  "summary": "用户学习了 SQL 是用于查询和操作关系型数据库的语言。"
}
```

后端用 Pydantic 校验：

- `title` 不为空
- `markdown` 不为空
- `level` 在允许枚举中
- `summary` 不为空

不合格内容应触发重试或返回错误：

- 纯鸡汤
- 没有例子
- 没有实际知识点
- 和当前主题无关
- 一次讲太多内容
- JSON 结构不合法且无法修复

### 10.3 选择题 Prompt 要求

选择题必须检查刚学过的核心点，不允许考无关细节。

必须遵守：

- 四个选项。
- 只有一个正确答案。
- 错误选项要有迷惑性，但不能胡说。
- 解释必须说明为什么正确选项正确，以及为什么用户选错时容易混淆。
- 题目不能靠文字游戏。
- 题目不能依赖没有教过的知识。

输出 JSON：

```json
{
  "question": "SQL 中 SELECT 的主要作用是什么？",
  "options": [
    "从表中查询数据",
    "删除整个数据库服务",
    "创建操作系统用户",
    "启动 Web 服务器"
  ],
  "correct_option_index": 0,
  "explanation": "SELECT 用于查询数据。其他选项属于数据库管理或系统操作，不是 SELECT 的作用。"
}
```

## 11. API 权限与安全

第一版可以不做多用户账号，但仍要有安全边界。

要求：

- 所有写操作启用 CSRF。
- 所有 POST、PATCH、DELETE 校验输入 schema。
- 所有 ID 参数校验 UUID。
- AI Markdown 不直接标记为安全 HTML。
- API key 不返回前端。
- 删除默认软删除。
- 更早历史内容禁止编辑和删除。

## 12. API 清单

```txt
GET    /api/health
GET    /api/csrf

GET    /api/provider/status
POST   /api/provider/health-check
PATCH  /api/provider/config

GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{conversation_id}
PATCH  /api/conversations/{conversation_id}
DELETE /api/conversations/{conversation_id}
POST   /api/conversations/{conversation_id}/pin
POST   /api/conversations/{conversation_id}/unpin

GET    /api/conversations/{conversation_id}/messages
POST   /api/conversations/{conversation_id}/messages
PATCH  /api/messages/{message_id}
DELETE /api/messages/{message_id}

POST   /api/conversations/{conversation_id}/learn/stream
GET    /api/learning-cards/{card_id}
POST   /api/learning-cards/{card_id}/regenerate

POST   /api/conversations/{conversation_id}/quiz/stream
GET    /api/quizzes/{quiz_id}
POST   /api/quizzes/{quiz_id}/answer
DELETE /api/quizzes/{quiz_id}
```
