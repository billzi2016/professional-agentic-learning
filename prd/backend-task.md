# Backend Task - AI 学习卡片系统

## 1. 目标

后端使用 Django + Django Ninja + SQLite 实现 API、数据库、SSE 流式生成、AI Provider 抽象、对话记忆、学习卡片、选择题、最近一轮编辑限制、CSRF、CORS 和基础安全能力。

## 2. 阶段一：项目初始化

### 任务

- [ ] 初始化 `backend/` Django 项目。
- [ ] 配置 Python 依赖管理。
- [ ] 配置 SQLite。
- [ ] 配置 `.env`。
- [ ] 配置 Django Ninja。
- [ ] 配置基础 settings。

### 推荐依赖

```txt
django
django-ninja
django-environ
```

### 验收

- [ ] `python manage.py runserver` 可以启动。
- [ ] `GET /api/health` 返回正常。
- [ ] SQLite 配置可用。

## 3. 阶段二：安全基础配置

### 任务

- [ ] 启用 Django CSRF Middleware。
- [ ] 实现 `GET /api/csrf`。
- [ ] 配置 `django-cors-headers`。
- [ ] 配置允许的前端 origin。
- [ ] 配置安全 cookie 选项。

### 推荐依赖

```txt
django-cors-headers
```

### 验收

- [ ] 前端能获取 CSRF cookie。
- [ ] POST、PATCH、DELETE 没有 CSRF token 时被拒绝。
- [ ] CORS 只允许配置中的 origin。

## 4. 阶段三：Django App 结构

### 任务

- [ ] 创建 `apps/api`。
- [ ] 创建 `apps/conversations`。
- [ ] 创建 `apps/learning`。
- [ ] 创建 `apps/providers`。
- [ ] 注册 app。
- [ ] 建立统一 router。

### 验收

- [ ] `backend/apps/` 结构清晰。
- [ ] 所有 API 都通过 Ninja router 汇总。
- [ ] URL 前缀为 `/api`。

## 5. 阶段四：数据模型

### 任务

- [ ] 实现 Conversation。
- [ ] 实现 Message。
- [ ] 实现 LearningCard。
- [ ] 实现 Quiz。
- [ ] 实现 QuizAttempt。
- [ ] 实现 ProviderConfig。
- [ ] 实现 ProviderHealthCheck。
- [ ] 创建 migrations。

### 关键字段

Conversation：

- `id`
- `title`
- `is_pinned`
- `archived_at`
- `created_at`
- `updated_at`

Message：

- `id`
- `conversation`
- `role`
- `message_type`
- `content`
- `metadata`
- `status`
- `created_at`
- `updated_at`

LearningCard：

- `id`
- `conversation`
- `message`
- `title`
- `topic`
- `level`
- `markdown`
- `summary`
- `order_index`
- `status`
- `created_at`

Quiz：

- `id`
- `conversation`
- `learning_card`
- `question`
- `options`
- `correct_option_index`
- `explanation`
- `status`
- `created_at`

ProviderConfig：

- `id`
- `name`
- `provider_type`
- `base_url`
- `model`
- `api_key`
- `is_active`

### 验收

- [ ] migrations 能正常执行。
- [ ] 所有数据库访问走 ORM。
- [ ] 不出现业务 raw SQL。

## 6. 阶段五：Conversation API

### 任务

- [ ] 实现对话列表。
- [ ] 实现创建对话。
- [ ] 实现获取单个对话。
- [ ] 实现修改标题。
- [ ] 实现置顶。
- [ ] 实现取消置顶。
- [ ] 实现软删除。

### API

```txt
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{conversation_id}
PATCH  /api/conversations/{conversation_id}
DELETE /api/conversations/{conversation_id}
POST   /api/conversations/{conversation_id}/pin
POST   /api/conversations/{conversation_id}/unpin
```

### 验收

- [ ] 对话列表按置顶和更新时间排序。
- [ ] 删除为软删除。
- [ ] archived 对话默认不返回。

## 7. 阶段六：Message API

### 任务

- [ ] 实现获取对话消息。
- [ ] 实现创建用户消息。
- [ ] 实现修改最近一轮用户输入。
- [ ] 实现删除最近一轮用户输入。
- [ ] 返回 `is_editable`。
- [ ] 返回 `can_regenerate_from_here`。

### API

```txt
GET    /api/conversations/{conversation_id}/messages
POST   /api/conversations/{conversation_id}/messages
PATCH  /api/messages/{message_id}
DELETE /api/messages/{message_id}
```

### 验收

- [ ] 只能修改最近一轮用户输入。
- [ ] 只能删除最近一轮用户输入。
- [ ] 更早消息返回 conflict。
- [ ] 后端不依赖前端隐藏按钮来保证规则。

## 8. 阶段七：Provider 抽象

### 任务

- [ ] 定义 `ChatProvider` 协议。
- [ ] 实现 OpenAI Compatible provider。
- [ ] 实现 Ollama provider 或 Ollama OpenAI compatible 配置。
- [ ] 实现 provider registry。
- [ ] 实现 provider config 读取。
- [ ] 实现 health check。

### 推荐依赖

```txt
openai
ollama
```

### API

```txt
GET   /api/provider/status
POST  /api/provider/health-check
PATCH /api/provider/config
```

### 验收

- [ ] 默认 provider 是 Ollama。
- [ ] 默认模型是 GPT OSS 120B。
- [ ] OpenRouter、OpenAI Compatible、vLLM、SGLang 能通过 base URL 切换。
- [ ] API key 不返回给前端。

## 9. 阶段八：Prompt 与结构化输出

### 任务

- [ ] 编写学习卡片 system prompt。
- [ ] 编写选择题 system prompt。
- [ ] 定义 Pydantic schema。
- [ ] 实现 JSON 解析和校验。
- [ ] 实现不合格内容重试。

### 推荐依赖

```txt
pydantic
json-repair
```

### Prompt 要求

- [ ] 每次只讲一个小知识点。
- [ ] 从前置概念开始。
- [ ] 给出具体例子。
- [ ] 有常见误解。
- [ ] 有检查点。
- [ ] 禁止空泛鼓励和漂亮废话。
- [ ] 内容必须让用户真的学到东西。

### 验收

- [ ] 学习卡片有标题、主题、级别、Markdown、summary。
- [ ] 选择题有四个选项且只有一个正确答案。
- [ ] 结构不合法时不会直接保存。

## 10. 阶段九：学习卡片生成

### 任务

- [ ] 实现学习上下文组装。
- [ ] 实现 `start` 生成。
- [ ] 实现 `continue` 生成。
- [ ] 实现 `regenerate` 生成。
- [ ] 保存 Message 和 LearningCard。
- [ ] 更新 Conversation `updated_at`。

### API

```txt
POST /api/conversations/{conversation_id}/learn/stream
GET  /api/learning-cards/{card_id}
POST /api/learning-cards/{card_id}/regenerate
```

### SSE 事件

```txt
card_start
card_delta
card_done
error
```

### 验收

- [ ] 每次只生成一张学习卡片。
- [ ] 生成过程流式返回。
- [ ] 完成后数据保存到数据库。
- [ ] 只能重新生成最近一张 active 卡片。

## 11. 阶段十：选择题生成与答题

### 任务

- [ ] 基于最近学习卡片生成选择题。
- [ ] 题目通过结构化 schema 校验。
- [ ] 保存 Quiz。
- [ ] 实现答题接口。
- [ ] 保存 QuizAttempt。
- [ ] 答题前不返回正确答案。
- [ ] 答题后返回正确答案和解释。

### API

```txt
POST   /api/conversations/{conversation_id}/quiz/stream
GET    /api/quizzes/{quiz_id}
POST   /api/quizzes/{quiz_id}/answer
DELETE /api/quizzes/{quiz_id}
```

### SSE 事件

```txt
quiz_start
quiz_delta
quiz_done
error
```

### 验收

- [ ] 题目必须四选一。
- [ ] 只有一个正确答案。
- [ ] 答案 index 必须在 0 到 3。
- [ ] 删除只允许最近一轮题目。

## 12. 阶段十一：最近一轮限制服务

### 任务

- [ ] 实现统一的最近一轮判定服务。
- [ ] 判断消息是否可编辑。
- [ ] 判断卡片是否可重新生成。
- [ ] 判断题目是否可删除。
- [ ] 所有相关 API 复用该服务。

### 规则

允许：

- 修改最近一条用户输入。
- 删除最近一条用户输入。
- 重新生成最近一张 AI 学习卡片。
- 删除最近一道题目。

不允许：

- 修改更早输入。
- 删除更早卡片。
- 重新生成更早卡片。
- 修改已经产生后续依赖的内容。

### 验收

- [ ] 规则有单元测试。
- [ ] API 返回一致的 `conflict` 错误。
- [ ] 前端返回字段与后端真实判定一致。

## 13. 阶段十二：XSS 与内容安全

### 任务

- [ ] 后端保存 Markdown 原文。
- [ ] 不把 AI 输出标记为 safe HTML。
- [ ] 对支持 HTML 的 Markdown 内容可使用 bleach 做清洗或禁用 HTML。
- [ ] 对链接和代码块保持安全输出策略。

### 推荐依赖

```txt
bleach
```

### 验收

- [ ] AI 输出中的 script 不会作为 safe HTML 返回。
- [ ] API 明确返回 Markdown 字段，而不是已信任 HTML。

## 14. 阶段十三：测试

### 任务

- [ ] 配置 pytest。
- [ ] 配置 pytest-django。
- [ ] 编写 Conversation 测试。
- [ ] 编写 Message 最近一轮限制测试。
- [ ] 编写 Provider 测试。
- [ ] 编写 LearningCard 测试。
- [ ] 编写 Quiz 测试。
- [ ] 编写 SSE 格式测试。
- [ ] 编写 CSRF 测试。

### 推荐依赖

```txt
pytest
pytest-django
factory-boy
```

### 验收

- [ ] 核心 API 有测试。
- [ ] Provider 调用使用 mock。
- [ ] 测试不真实调用 Ollama 或外部 API。

## 15. 阶段十四：运行文档与脚本配合

### 任务

- [ ] 提供 backend `.env.example`。
- [ ] 编写 `backend/README.md`。
- [ ] 在 README 中写后端启动步骤。
- [ ] 在 README 中写 migration、测试、Provider 切换、SSE 接口说明。
- [ ] 确认 `run-all.sh` 能启动 Django。
- [ ] 写 migration 和启动说明。

### 验收

- [ ] 新开发者按 README 可以启动后端。
- [ ] `run-all.sh` 的 backend 窗口能运行 Django server。

## 16. 阶段十五：中文注释与可读性

### 任务

- [ ] 在 Provider 抽象层补充中文注释，说明不同 provider 复用 OpenAI-compatible client 的原因。
- [ ] 在 SSE 流式输出逻辑中补充中文注释，说明事件顺序和错误处理。
- [ ] 在最近一轮限制服务中补充中文注释，说明为什么更早内容不能修改或重新生成。
- [ ] 在 Prompt 组装逻辑中补充中文注释，说明如何保证模型输出真材实料。
- [ ] 在 CSRF、CORS、XSS、API key 隐藏相关代码中补充中文注释。
- [ ] 对长难句、复杂条件判断、事务和状态流转，用中文短句拆开解释。
- [ ] 避免给普通字段赋值、简单 return、简单 if 写无意义注释。

### 验收

- [ ] 复杂业务逻辑有中文注释。
- [ ] 注释解释业务意图和边界条件。
- [ ] 长难句逻辑已拆成容易理解的中文短句。
- [ ] 注释没有变成逐行翻译代码的噪音。

## 17. 阶段十六：提交前检查

### 任务

- [ ] 确认后端改动只包含当前任务相关内容。
- [ ] 确认复杂业务逻辑已有中文注释。
- [ ] 确认 README、API 文档或任务文档已同步更新。
- [ ] 准备详细中文 commit message，说明背景、原因、改动、影响和测试。
- [ ] 如果没有运行测试，必须在 commit message 正文里明确说明原因。

### 验收

- [ ] 提交信息符合项目的 Linus 风格提交说明要求。
- [ ] 提交正文说明是否运行过后端测试。

## 18. 不造轮子清单

必须使用成熟库：

- API：Django Ninja
- ORM：Django ORM
- 配置：`django-environ`
- CORS：`django-cors-headers`
- AI SDK：`openai`、`ollama`
- Schema：Pydantic / Django Ninja Schema
- JSON 修复：`json-repair`
- HTML 清洗：`bleach`
- 测试：pytest、pytest-django、factory-boy

禁止自行实现：

- ORM
- Web 框架
- OpenAI Compatible HTTP SDK
- Markdown parser
- HTML sanitizer
- SSE 协议解析器
- 测试框架
