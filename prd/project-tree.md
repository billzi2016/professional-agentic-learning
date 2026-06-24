# Project Tree PRD - AI 学习卡片系统

## 1. 顶层结构

项目采用前后端分离结构。Django 和 Vue 必须分别放在独立目录中，顶层只放项目说明、运行脚本、PRD 和通用配置。

建议结构：

```txt
professional-agentic-learning/
  README.md
  run-all.sh
  .gitignore
  .env.example
  prd/
    frontend-prd.md
    backend-prd.md
    project-tree.md
  backend/
    README.md
    manage.py
    pyproject.toml
    .env.example
    backend/
      __init__.py
      settings.py
      urls.py
      asgi.py
      wsgi.py
    apps/
      api/
      conversations/
      learning/
      providers/
    tests/
  frontend/
    README.md
    package.json
    vite.config.ts
    index.html
    tsconfig.json
    src/
      main.ts
      App.vue
      router/
      stores/
      api/
      components/
      views/
      styles/
      utils/
```

## 2. 顶层文件

### 2.1 README.md

必须包含：

- 面向 GitHub 访问者的项目说明。
- 项目介绍
- 技术栈
- 本地开发依赖
- Ollama 准备方式
- 后端启动方式
- 前端启动方式
- 一键启动方式
- Provider 切换说明
- 安全说明
- 项目目录结构
- 当前功能范围
- 开发状态
- License 占位说明
- Git commit message 规范

示例内容范围：

```txt
AI 学习卡片系统

Frontend: Vue 3 + Vite + TypeScript
Backend: Django + Django Ninja + SQLite
AI: Ollama / OpenRouter / OpenAI Compatible / vLLM / SGLang
```

顶层 README 的定位：

- 给 GitHub 上第一次看到项目的人阅读。
- 说明这个项目是什么、能做什么、如何启动、如何配置 AI provider。
- 不写太多内部实现细节，细节放到 `backend/README.md` 和 `frontend/README.md`。
- 明确说明真实 `.env` 不提交，只提交 `.env.example`。

### 2.2 Git commit message 规范

项目提交信息必须写得详细，采用接近 Linus Torvalds 推崇的提交说明风格：标题简洁，正文解释“为什么改”，而不是只堆“改了什么”。

要求：

- commit 标题使用中文，概括本次变更的真实目的。
- commit 正文必须写清楚背景、问题、设计取舍、主要改动和影响范围。
- 不要只写 `update`、`fix bug`、`改文档` 这种低信息量信息。
- 如果本次变更改变 API、数据模型、安全策略、运行方式或用户交互，正文必须明确说明。
- 如果运行了测试或没有运行测试，正文必须说明。
- 一次 commit 只表达一个相对完整的主题，不把无关改动混在一起。
- 不要在 commit message 中写没有意义的情绪化描述。

推荐格式：

```txt
用 PRD 明确学习卡片系统的前后端边界

这个提交补齐产品设计阶段缺失的关键约束。项目后续会同时包含
Vue 前端、Django API、SQLite 数据库和多个 AI provider，如果没有
明确的 PRD，后续实现很容易把 provider 逻辑泄漏到前端，或者在
Markdown 渲染、SSE、PDF 导出等地方重复造轮子。

主要改动：
- 增加前端 PRD，定义 ChatGPT 风格学习界面、Markdown 渲染、SSE
  流式卡片、选择题和 PDF 导出。
- 增加后端 PRD，定义 Django Ninja API、ORM 数据模型、Provider
  抽象、Prompt 质量要求和安全边界。
- 增加项目结构和任务拆解文档，明确 backend、frontend 和顶层
  README 的职责。

影响：
- 当前提交只修改 PRD 文档，不改变运行时代码。
- 后续实现应以这些文档作为验收依据。

测试：
- 未运行测试；本次是文档变更。
```

### 2.3 backend/README.md

必须包含：

- Django 后端职责说明
- Python 版本
- 依赖安装方式
- `.env` 配置方式
- SQLite 和 migration 命令
- Django dev server 启动命令
- API 文档入口
- SSE 接口说明
- Provider 切换说明
- 测试命令
- 中文注释规范
- 安全注意事项

### 2.4 frontend/README.md

必须包含：

- Vue 前端职责说明
- Node 版本
- 依赖安装方式
- `.env` 配置方式
- Vite dev server 启动命令
- 主要页面和组件说明
- SSE 客户端说明
- Markdown 渲染和 XSS 清洗说明
- PDF 导出说明
- 测试命令
- 中文注释规范
- UI 设计约束

### 2.5 run-all.sh

用途：

- 一次性启动 Django 和 Vue。
- 使用两个 tmux 窗口或 pane。

要求：

- 不写死用户机器上的绝对路径。
- 从脚本所在目录计算项目根目录。
- 检查 tmux 是否存在。
- 检查 backend 和 frontend 目录是否存在。
- 一个 tmux session 内运行两个窗口：
  - `backend`
  - `frontend`
- backend 窗口运行 Django dev server。
- frontend 窗口运行 Vite dev server。

建议脚本逻辑：

```sh
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SESSION_NAME="agentic-learning"

command -v tmux >/dev/null 2>&1 || {
  echo "tmux is required"
  exit 1
}

tmux new-session -d -s "$SESSION_NAME" -n backend
tmux send-keys -t "$SESSION_NAME:backend" "cd '$ROOT_DIR/backend' && python manage.py runserver 127.0.0.1:8000" C-m

tmux new-window -t "$SESSION_NAME" -n frontend
tmux send-keys -t "$SESSION_NAME:frontend" "cd '$ROOT_DIR/frontend' && npm run dev -- --host 127.0.0.1" C-m

tmux attach -t "$SESSION_NAME"
```

实际实现时应补充：

- 如果 session 已存在，提示用户 attach 或 kill 后重启。
- 不自动安装依赖。
- 不自动执行 migration，除非 README 明确说明。

## 3. Backend 目录

### 3.1 目录结构

```txt
backend/
  manage.py
  pyproject.toml
  .env.example
  backend/
    __init__.py
    settings.py
    urls.py
    asgi.py
    wsgi.py
  apps/
    api/
      __init__.py
      router.py
      schemas.py
    conversations/
      __init__.py
      apps.py
      models.py
      services.py
      api.py
      admin.py
      migrations/
    learning/
      __init__.py
      apps.py
      models.py
      services.py
      prompts.py
      api.py
      admin.py
      migrations/
    providers/
      __init__.py
      apps.py
      models.py
      registry.py
      base.py
      openai_compatible.py
      ollama_provider.py
      health.py
      api.py
      admin.py
      migrations/
  tests/
    conftest.py
    test_conversations.py
    test_learning_cards.py
    test_quizzes.py
    test_providers.py
    test_sse.py
```

### 3.2 apps/api

职责：

- 汇总 Django Ninja routers。
- 定义统一错误响应。
- 提供 `/api/health` 和 `/api/csrf`。

### 3.3 apps/conversations

职责：

- Conversation 模型
- Message 模型
- 对话 CRUD
- 消息保存与查询

### 3.4 apps/learning

职责：

- LearningCard 模型
- Quiz 模型
- QuizAttempt 模型
- 学习卡片生成服务
- 选择题生成服务
- 答题判定
- 学习上下文组装

### 3.5 apps/providers

职责：

- ProviderConfig 模型
- ProviderHealthCheck 模型
- Provider registry
- OpenAI compatible client
- Ollama provider
- 健康检查

原则：

- OpenRouter、vLLM、SGLang 优先走 OpenAI compatible client。
- 只有 provider 差异确实存在时，才新增 provider 子类。

## 4. Frontend 目录

### 4.1 目录结构

```txt
frontend/
  package.json
  vite.config.ts
  index.html
  tsconfig.json
  postcss.config.js
  tailwind.config.ts
  src/
    main.ts
    App.vue
    router/
      index.ts
    stores/
      conversations.ts
      messages.ts
      provider.ts
      layout.ts
    api/
      client.ts
      conversations.ts
      learning.ts
      provider.ts
      csrf.ts
    components/
      layout/
        AppShell.vue
        Sidebar.vue
        ResizableSidebar.vue
        ProviderStatus.vue
      chat/
        ChatThread.vue
        MessageBubble.vue
        LearningCard.vue
        ChatInput.vue
        ActionBar.vue
      quiz/
        QuizCard.vue
        QuizOption.vue
      markdown/
        MarkdownRenderer.vue
      common/
        IconButton.vue
        Tooltip.vue
        StatusDot.vue
    views/
      ChatView.vue
    styles/
      main.css
    utils/
      markdown.ts
      confetti.ts
      storage.ts
      sse.ts
```

### 4.2 api/client.ts

职责：

- 创建 Axios 或 ky client。
- 统一 base URL。
- 自动带 credentials。
- 自动注入 CSRF token。
- 统一错误处理。

### 4.3 utils/markdown.ts

职责：

- 初始化 Markdown renderer。
- 接入代码高亮。
- 调用 DOMPurify sanitize。
- 输出安全 HTML。

不允许：

- 手写 Markdown parser。
- 直接渲染未清洗 AI 内容。

### 4.4 utils/sse.ts

职责：

- 封装 `@microsoft/fetch-event-source`。
- 统一处理 `card_delta`、`card_done`、`quiz_delta`、`quiz_done`、`error`。
- 支持 AbortController 取消。

不允许：

- 手写复杂 SSE parser。

### 4.5 utils/confetti.ts

职责：

- 封装 `canvas-confetti`。
- 提供 `fireSuccessConfetti()`。

不允许：

- 自己实现粒子系统。

## 5. 本地开发端口

建议：

- Django API: `http://127.0.0.1:8000`
- Vue Vite: `http://127.0.0.1:5173`
- Ollama: `http://127.0.0.1:11434`

前端通过环境变量配置 API 地址：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

后端通过环境变量配置 AI provider：

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

## 6. 依赖建议

### 6.1 Backend

```txt
django
django-ninja
django-cors-headers
django-environ
openai
ollama
pydantic
json-repair
bleach
pytest
pytest-django
factory-boy
```

### 6.2 Frontend

```txt
vue
vite
typescript
pinia
vue-router
axios
@microsoft/fetch-event-source
markdown-it
dompurify
highlight.js
canvas-confetti
lucide-vue-next
dayjs
tailwindcss
@headlessui/vue
zod
```

## 7. 开发顺序建议

1. 创建顶层 README、run-all.sh、`.env.example`。
2. 初始化 Django 项目到 `backend/`。
3. 配置 Django Ninja、CORS、CSRF、SQLite。
4. 建立 Conversation、Message、LearningCard、Quiz、Provider 模型。
5. 实现 provider health API。
6. 实现非流式 mock 学习卡片 API。
7. 实现 SSE 学习卡片 API。
8. 初始化 Vue 项目到 `frontend/`。
9. 实现 ChatGPT 风格基础布局。
10. 接入对话列表和消息 API。
11. 接入 SSE 流式卡片。
12. 接入选择题与答题反馈。
13. 添加烟花动画。
14. 补充测试和 README。
15. 编写 run-all.sh。

## 8. 验收标准

- 顶层存在 `README.md`。
- `backend/` 存在 `README.md`。
- `frontend/` 存在 `README.md`。
- 顶层存在 `run-all.sh`。
- `run-all.sh` 使用 tmux 同时启动 Django 和 Vue。
- Django 项目在 `backend/`。
- Vue 项目在 `frontend/`。
- PRD 文档在 `prd/`。
- 前后端不混在同一项目目录中。
- SQLite 数据库由 Django 管理。
- 数据访问走 ORM。
- 前端不直接访问 AI provider。
- provider 可通过配置切换。
- CSRF、CORS、XSS 处理在结构上有明确落点。
- Django 和 Vue 代码中对复杂逻辑有中文注释。
- 顶层 README 面向 GitHub 读者，子项目 README 面向开发者。
- README 中包含详细 Git commit message 规范。

## 9. 明确不做

第一版不做：

- 多用户账号系统
- 支付
- 课程市场
- 移动 App
- 离线同步
- 自研 Markdown parser
- 自研 SSE parser
- 自研 ORM
- 自研 UI 组件库
- 自研烟花粒子系统
- 自研 AI HTTP SDK

这些能力以后可以扩展，但不应进入第一版基础架构。
