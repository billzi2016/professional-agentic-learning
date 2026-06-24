# Backend PRD - AI 学习卡片系统

## 1. 产品定位

后端使用 Django 作为 API 与数据库层，提供会话、消息、学习卡片、选择题、Provider 配置、健康检查和 AI 流式生成能力。

数据库使用 SQLite，所有数据库访问必须通过 Django ORM，不允许手写 SQL 作为业务数据访问方式。

AI 接入通过 provider 抽象层实现。初始 provider 为 Ollama，默认模型为 GPT OSS 120B。后续需要支持 OpenRouter、任意 OpenAI API Compatible 服务、vLLM、SGLang。

## 2. 技术栈

### 2.1 核心框架

- Python 3.11+
- Django 5.x
- Django Ninja
- SQLite
- Django ORM

### 2.2 流式输出

使用 Django SSE 实现 AI 生成流。

可选方案：

- Django `StreamingHttpResponse`
- `django-eventstream`

推荐初期使用 `StreamingHttpResponse`，因为接口少、控制直接、依赖较轻。

SSE 返回格式必须标准化：

```txt
event: card_delta
data: {"delta": "..."}

event: card_done
data: {"card_id": "..."}
```

### 2.3 AI 客户端

不要为每个 provider 手写完整 HTTP 调用逻辑。优先使用官方或成熟 SDK。

推荐：

- OpenAI Compatible：`openai` Python SDK
- Ollama：`ollama` Python SDK，或使用 OpenAI compatible endpoint 时走 `openai` SDK
- OpenRouter：`openai` Python SDK + OpenRouter base URL
- vLLM：OpenAI compatible endpoint + `openai` SDK
- SGLang：OpenAI compatible endpoint + `openai` SDK

Provider 抽象层只负责：

- 读取配置
- 选择 SDK client
- 统一 chat completion 请求结构
- 统一 streaming delta 输出
- 健康检查

### 2.4 中文注释与可读性

Django 后端代码必须有详细中文注释，重点解释业务意图、边界条件和长难句逻辑。注释不是为了重复代码，而是为了让后来维护的人快速理解为什么这样写。

必须写中文注释的位置：

- Provider 抽象层，例如为什么 OpenRouter、vLLM、SGLang 可以复用 OpenAI-compatible client。
- SSE 生成逻辑，例如 `card_delta`、`card_done`、错误事件的发送顺序。
- 最近一轮限制逻辑，例如为什么只能修改最近输入，为什么更早卡片不能重新生成。
- Prompt 组装逻辑，例如如何避免模型输出空泛内容，如何约束它每次只讲一个小知识点。
- CSRF、CORS、XSS、API key 隐藏等安全逻辑。
- 长条件判断、事务、状态流转、异常恢复逻辑。

注释要求：

- 使用中文短句。
- 长难句必须拆开说明。
- 复杂函数顶部写一段说明输入、输出、副作用。
- 不要给 ORM 字段赋值、普通 return、简单 if 写无意义注释。

示例：

```python
# 只允许重写最近一张 active 学习卡片。
# 如果它后面已经有题目或下一张卡片，重写会让后续内容失去依据。
if not last_turn_policy.can_regenerate_card(card):
    raise ConflictError("只能重新生成最近一轮内容")
```

## 3. Django 项目结构

后端必须单独放在一个文件夹，例如：

```txt
backend/
  manage.py
  pyproject.toml
  backend/
    settings.py
    urls.py
    asgi.py
    wsgi.py
  apps/
    accounts/
    conversations/
    learning/
    providers/
    api/
```

说明：

- `backend/` 是 Django 项目根。
- `apps/conversations/` 管理对话和消息。
- `apps/learning/` 管理学习卡片、学习进度、选择题。
- `apps/providers/` 管理 AI provider 配置与健康检查。
- `apps/api/` 汇总 Django Ninja router。

## 4. 数据模型

### 4.1 Conversation

字段：

- `id`: UUID
- `title`: string
- `created_at`: datetime
- `updated_at`: datetime
- `archived_at`: datetime nullable

用途：

- 表示一次学习对话。
- 标题可由用户首条消息或 AI 自动生成。

### 4.2 Message

字段：

- `id`: UUID
- `conversation`: FK Conversation
- `role`: enum `user | assistant | system | tool`
- `content`: text
- `message_type`: enum `plain | learning_card | quiz | action`
- `metadata`: JSONField
- `created_at`: datetime

用途：

- 保存用户和 AI 的对话历史。
- AI 卡片也可作为 message 保存，便于统一展示。

### 4.3 LearningCard

字段：

- `id`: UUID
- `conversation`: FK Conversation
- `message`: OneToOne Message nullable
- `title`: string
- `topic`: string
- `level`: enum `beginner | intermediate | advanced`
- `markdown`: text
- `order_index`: integer
- `summary`: text
- `created_at`: datetime

用途：

- 保存每张学习卡片。
- 支持后续继续学习时读取上下文。

### 4.4 Quiz

字段：

- `id`: UUID
- `conversation`: FK Conversation
- `learning_card`: FK LearningCard nullable
- `question`: text
- `options`: JSONField
- `correct_option_index`: integer
- `explanation`: text
- `created_at`: datetime

`options` 格式：

```json
[
  {"label": "A", "text": "..."},
  {"label": "B", "text": "..."},
  {"label": "C", "text": "..."},
  {"label": "D", "text": "..."}
]
```

### 4.5 QuizAttempt

字段：

- `id`: UUID
- `quiz`: FK Quiz
- `selected_option_index`: integer
- `is_correct`: boolean
- `created_at`: datetime

用途：

- 保存用户答题记录。

### 4.6 ProviderConfig

字段：

- `id`: UUID
- `name`: string，例如 `ollama`
- `provider_type`: enum `ollama | openai_compatible | openrouter | vllm | sglang`
- `base_url`: string
- `model`: string
- `api_key`: string encrypted or blank
- `is_active`: boolean
- `created_at`: datetime
- `updated_at`: datetime

安全：

- API key 不应明文返回给前端。
- 本地开发可使用 `.env`。
- 如果需要存库，使用字段加密库，例如 `django-fernet-fields` 或类似成熟库。

### 4.7 ProviderHealthCheck

字段：

- `id`: UUID
- `provider_config`: FK ProviderConfig
- `status`: enum `healthy | unhealthy | checking`
- `latency_ms`: integer nullable
- `error_message`: text
- `checked_at`: datetime

用途：

- 记录最近健康检查。
- 前端展示红黄绿状态。

## 5. API 设计

### 5.1 Health

```txt
GET /api/health
```

返回：

```json
{
  "status": "ok"
}
```

### 5.2 Provider 状态

```txt
GET /api/provider/status
```

返回：

```json
{
  "provider": "ollama",
  "model": "gpt-oss:120b",
  "status": "healthy",
  "latency_ms": 120,
  "checked_at": "2026-06-24T12:00:00Z",
  "error": null
}
```

### 5.3 对话列表

```txt
GET /api/conversations
```

返回最近对话列表。

### 5.4 创建对话

```txt
POST /api/conversations
```

请求：

```json
{
  "title": "SQL 学习"
}
```

### 5.5 获取消息

```txt
GET /api/conversations/{conversation_id}/messages
```

返回该对话的消息、学习卡片和题目摘要。

### 5.6 创建用户消息

```txt
POST /api/conversations/{conversation_id}/messages
```

请求：

```json
{
  "content": "开始学习 SQL"
}
```

### 5.7 流式生成学习卡片

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

`action` 可选：

- `start`
- `continue`

SSE 事件：

- `card_start`
- `card_delta`
- `card_done`
- `error`

### 5.8 流式生成选择题

```txt
POST /api/conversations/{conversation_id}/quiz/stream
```

请求：

```json
{
  "learning_card_id": "uuid"
}
```

SSE 事件：

- `quiz_start`
- `quiz_delta`
- `quiz_done`
- `error`

### 5.9 提交答案

```txt
POST /api/quizzes/{quiz_id}/answer
```

请求：

```json
{
  "selected_option_index": 2
}
```

返回：

```json
{
  "is_correct": true,
  "correct_option_index": 2,
  "explanation": "..."
}
```

## 6. AI Provider 抽象

### 6.1 目标

后端只暴露统一学习接口，前端不感知具体模型服务。

Provider 需要支持：

- Ollama
- OpenRouter
- OpenAI API Compatible
- vLLM
- SGLang

### 6.2 Provider 接口

建议定义：

```python
class ChatProvider(Protocol):
    def stream_chat(self, messages: list[dict], *, model: str) -> Iterator[str]:
        ...

    def health_check(self) -> ProviderHealthResult:
        ...
```

### 6.3 OpenAI Compatible 优先

对于 OpenRouter、vLLM、SGLang、OpenAI Compatible API，统一使用 OpenAI Python SDK：

```python
from openai import OpenAI
```

通过不同的 `base_url` 和 `api_key` 切换 provider。

### 6.4 Ollama

Ollama 有两种可选方式：

1. 使用 Ollama SDK。
2. 如果本地 Ollama 暴露 OpenAI compatible endpoint，则走 OpenAI SDK。

建议优先走 OpenAI compatible 方式，减少 provider 分支。

默认配置：

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

## 7. Prompt 与输出约束

学习卡片生成必须要求模型返回结构化内容。

推荐让模型输出 JSON，再由后端保存并转成 Markdown。不要完全依赖模型自由文本。

学习卡片 schema：

```json
{
  "title": "...",
  "topic": "...",
  "level": "beginner",
  "markdown": "...",
  "summary": "..."
}
```

选择题 schema：

```json
{
  "question": "...",
  "options": ["...", "...", "...", "..."],
  "correct_option_index": 0,
  "explanation": "..."
}
```

建议使用：

- Pydantic 校验模型输出
- `json_repair` 作为容错解析工具

不要手写脆弱的字符串切割解析。

## 8. 记忆与上下文

系统必须有对话记忆。

上下文来源：

- 当前 Conversation 的用户消息
- 已生成 LearningCard 的 summary
- 最近 Quiz 和 QuizAttempt
- 当前学习主题与进度

上下文策略：

- 不把完整历史无限塞入 prompt。
- 使用最近 N 条消息 + 卡片 summary。
- 每张卡片生成后保存 summary。
- 当历史过长时，后端生成 conversation summary。

## 9. 安全要求

### 9.1 CSRF

- Django 启用 CSRF Middleware。
- 前端所有 POST 请求带 `X-CSRFToken`。
- 提供初始化 CSRF cookie 的 API，例如：

```txt
GET /api/csrf
```

### 9.2 XSS

后端不信任 AI 输出。

要求：

- 后端保存原始 Markdown，但不得保存或返回未标记的可执行 HTML。
- 前端负责最终 Markdown sanitize。
- 后端可以使用 `bleach` 对允许的 HTML 做二次清洗，尤其当支持 HTML Markdown 时。

### 9.3 ORM

- 所有数据库读写必须使用 Django ORM。
- 禁止业务代码手写 SQL。
- 如未来确实需要 raw SQL，必须单独说明原因并写测试。

### 9.4 CORS

前后端分离开发时使用：

- `django-cors-headers`

开发配置：

- 允许 Vite dev server origin，例如 `http://localhost:5173`

生产配置：

- 只允许明确域名。

### 9.5 API Key

- API key 不返回给前端。
- `.env` 不提交 git。
- Provider status 只返回 provider 名称、模型、健康状态、错误摘要。

### 9.6 输入限制

- 用户输入长度限制，例如 8000 字符。
- Quiz answer 必须校验 index 范围为 0 到 3。
- UUID 参数必须通过 schema 校验。

## 10. 后台任务

早期不引入 Celery，除非健康检查和总结任务变复杂。

可选：

- `django-q2`
- Celery + Redis

初期建议：

- Provider 健康检查按请求触发或轻量缓存。
- 长任务通过 SSE 请求同步流式返回。

## 11. 配置管理

使用：

- `django-environ`
- `.env`

示例：

```env
DJANGO_SECRET_KEY=dev-secret
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173

AI_PROVIDER=ollama
AI_BASE_URL=http://localhost:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

## 12. 测试要求

使用：

- `pytest`
- `pytest-django`
- `factory_boy`

测试范围：

- Conversation CRUD
- Message 保存
- LearningCard 保存
- Quiz answer 判定
- Provider config 选择
- Provider health status API
- SSE event 格式
- CSRF 行为
- XSS 危险内容不会被直接执行或原样标记为安全 HTML

AI provider 测试：

- 使用 mock client。
- 不在单元测试中真实调用 Ollama/OpenRouter/OpenAI。

## 13. 验收标准

- Django 项目单独位于 `backend/`。
- API 使用 Django Ninja。
- 数据库使用 SQLite。
- 所有数据库访问使用 ORM。
- 支持 SSE 流式学习卡片。
- 支持 SSE 流式选择题生成。
- 支持 provider 抽象。
- 默认 provider 为 Ollama，模型为 GPT OSS 120B。
- 可通过 base URL 和 API key 切换 OpenRouter、OpenAI Compatible、vLLM、SGLang。
- 前端无法直接访问 API key。
- CSRF 生效。
- CORS 配置明确。
- 对 AI 输出有结构化校验。
- 对选择题答案有后端校验。

## 14. 不造轮子原则

必须优先使用成熟库：

- API：Django Ninja
- ORM：Django ORM
- 配置：`django-environ`
- CORS：`django-cors-headers`
- AI OpenAI compatible：`openai`
- Ollama：`ollama` SDK 或 OpenAI compatible endpoint
- 数据校验：Pydantic / Django Ninja Schema
- 测试：pytest、pytest-django、factory_boy
- Markdown / HTML 清洗：`bleach`
- JSON 容错：`json_repair`
- 加密字段：成熟 Django 字段加密库

禁止自行实现：

- Web 框架
- ORM
- SSE 协议解析器
- OpenAI compatible HTTP SDK
- Markdown parser
- HTML sanitizer
- 后台任务框架
- 表单和 schema 校验框架
