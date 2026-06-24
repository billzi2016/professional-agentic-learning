# Env PRD - AI 学习卡片系统

## 1. 目标

项目必须通过环境变量配置 AI Provider。默认使用 Ollama，但可以通过 `.env` 切换到 OpenRouter、任意 OpenAI API Compatible 服务、vLLM 或 SGLang。

项目需要提供：

- 顶层 `.env.example`
- `backend/.env.example`
- 可选 `frontend/.env.example`

真实 `.env` 文件只用于本地开发，不提交 git。

## 2. 顶层 .env.example

顶层 `.env.example` 用来说明整个项目的关键配置，方便开发者复制后拆分到 backend/frontend。

建议路径：

```txt
professional-agentic-learning/.env.example
```

内容：

```env
# Django
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

# Frontend
VITE_API_BASE_URL=http://127.0.0.1:8000

# AI Provider
# 可选值：ollama, openrouter, openai_compatible, vllm, sglang
AI_PROVIDER=ollama

# 默认 Ollama OpenAI-compatible endpoint
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama

# OpenRouter 示例
# AI_PROVIDER=openrouter
# AI_BASE_URL=https://openrouter.ai/api/v1
# AI_MODEL=openai/gpt-oss-120b
# AI_API_KEY=sk-or-v1-your-key

# OpenAI Compatible 示例
# AI_PROVIDER=openai_compatible
# AI_BASE_URL=https://api.example.com/v1
# AI_MODEL=your-model-name
# AI_API_KEY=your-api-key

# vLLM 示例
# AI_PROVIDER=vllm
# AI_BASE_URL=http://127.0.0.1:8001/v1
# AI_MODEL=gpt-oss-120b
# AI_API_KEY=EMPTY

# SGLang 示例
# AI_PROVIDER=sglang
# AI_BASE_URL=http://127.0.0.1:30000/v1
# AI_MODEL=gpt-oss-120b
# AI_API_KEY=EMPTY
```

## 3. Backend .env.example

建议路径：

```txt
backend/.env.example
```

内容：

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5173,http://localhost:5173

# SQLite
DATABASE_URL=sqlite:///db.sqlite3

# AI Provider
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama

# OpenRouter
# AI_PROVIDER=openrouter
# AI_BASE_URL=https://openrouter.ai/api/v1
# AI_MODEL=openai/gpt-oss-120b
# AI_API_KEY=sk-or-v1-your-key

# OpenAI Compatible
# AI_PROVIDER=openai_compatible
# AI_BASE_URL=https://api.example.com/v1
# AI_MODEL=your-model-name
# AI_API_KEY=your-api-key

# vLLM
# AI_PROVIDER=vllm
# AI_BASE_URL=http://127.0.0.1:8001/v1
# AI_MODEL=gpt-oss-120b
# AI_API_KEY=EMPTY

# SGLang
# AI_PROVIDER=sglang
# AI_BASE_URL=http://127.0.0.1:30000/v1
# AI_MODEL=gpt-oss-120b
# AI_API_KEY=EMPTY
```

## 4. Frontend .env.example

建议路径：

```txt
frontend/.env.example
```

内容：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

注意：

- 前端 `.env` 不放 AI Provider API key。
- 前端不直接访问 OpenRouter、Ollama、vLLM、SGLang。
- Provider 信息由后端 `/api/provider/status` 返回。

## 5. Provider 切换规则

### 5.1 Ollama 默认配置

默认：

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

要求：

- Ollama 必须可以从 env 文件修改。
- 不允许把 Ollama base URL、model 写死在代码里。
- 如果 Ollama 提供 OpenAI-compatible endpoint，后端优先通过 OpenAI SDK 调用。

### 5.2 OpenRouter 配置

切换到 OpenRouter：

```env
AI_PROVIDER=openrouter
AI_BASE_URL=https://openrouter.ai/api/v1
AI_MODEL=openai/gpt-oss-120b
AI_API_KEY=sk-or-v1-your-key
```

要求：

- 使用 OpenAI Python SDK。
- 通过 `base_url` 切换到 OpenRouter。
- API key 只存在后端 env 或后端安全存储中。
- 前端不得读取或展示 API key。

### 5.3 OpenAI Compatible 配置

适用于任何兼容 OpenAI Chat Completions API 的服务：

```env
AI_PROVIDER=openai_compatible
AI_BASE_URL=https://api.example.com/v1
AI_MODEL=your-model-name
AI_API_KEY=your-api-key
```

### 5.4 vLLM 配置

本地 vLLM OpenAI-compatible server 示例：

```env
AI_PROVIDER=vllm
AI_BASE_URL=http://127.0.0.1:8001/v1
AI_MODEL=gpt-oss-120b
AI_API_KEY=EMPTY
```

### 5.5 SGLang 配置

本地 SGLang OpenAI-compatible server 示例：

```env
AI_PROVIDER=sglang
AI_BASE_URL=http://127.0.0.1:30000/v1
AI_MODEL=gpt-oss-120b
AI_API_KEY=EMPTY
```

## 6. 后端读取方式

后端使用 `django-environ` 读取配置。

示例：

```python
AI_PROVIDER = env("AI_PROVIDER", default="ollama")
AI_BASE_URL = env("AI_BASE_URL", default="http://127.0.0.1:11434/v1")
AI_MODEL = env("AI_MODEL", default="gpt-oss:120b")
AI_API_KEY = env("AI_API_KEY", default="ollama")
```

要求：

- 所有 Provider 配置从 env 或数据库 ProviderConfig 读取。
- env 优先用于本地开发。
- 不允许在业务代码中写死 provider、base URL、model、API key。
- API key 不写入日志。
- API key 不返回前端。

## 7. .gitignore 要求

`.gitignore` 必须包含：

```gitignore
.env
backend/.env
frontend/.env
*.sqlite3
db.sqlite3
```

允许提交：

```txt
.env.example
backend/.env.example
frontend/.env.example
```

## 8. 验收标准

- [ ] 项目包含顶层 `.env.example`。
- [ ] Backend 包含 `backend/.env.example`。
- [ ] Frontend 包含 `frontend/.env.example`。
- [ ] Ollama 默认配置写在 env example 中。
- [ ] OpenRouter 示例配置写在 env example 中。
- [ ] OpenAI Compatible 示例配置写在 env example 中。
- [ ] vLLM 示例配置写在 env example 中。
- [ ] SGLang 示例配置写在 env example 中。
- [ ] 后端通过 env 读取 `AI_PROVIDER`、`AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY`。
- [ ] 前端 env 只包含后端 API 地址，不包含 AI Provider key。
- [ ] 真实 `.env` 不提交 git。
