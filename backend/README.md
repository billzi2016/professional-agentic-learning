# Backend

Django 后端负责 API、SQLite 数据库、SSE 流式生成、AI Provider 抽象和安全边界。

## 技术栈

- Django
- Django Ninja
- SQLite
- Django ORM
- OpenAI Python SDK
- django-cors-headers

## 启动

本项目按用户要求使用 conda/base Python，不创建虚拟环境。

```sh
cd backend
/opt/anaconda3/bin/python3.13 manage.py migrate
/opt/anaconda3/bin/python3.13 manage.py runserver 127.0.0.1:8000
```

## 环境变量

复制 `.env.example` 为 `.env`，或直接在 shell 中导出变量。

默认 provider 是 Ollama：

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

OpenRouter、vLLM、SGLang 和其他 OpenAI-compatible 服务通过 `AI_BASE_URL`、`AI_MODEL`、`AI_API_KEY` 切换。

## 注释规范

复杂业务逻辑必须写中文注释。注释解释意图和边界，不逐行翻译代码。

重点包括：

- Provider 抽象
- SSE 事件顺序
- 最近一轮编辑限制
- Prompt 质量约束
- CSRF、CORS、XSS 和 API key 隐藏

## 测试

测试文件落在 `backend/tests/`。

```sh
cd backend
/opt/anaconda3/bin/python3.13 -m pytest
```

注意：`tests/test_provider_real.py` 会真实调用当前 env 配置的 AI provider，不使用 mock。如果 Ollama、OpenRouter、vLLM 或 SGLang 没有启动，或者模型不存在，这个测试应该失败。
