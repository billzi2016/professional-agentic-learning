# Professional Agentic Learning

AI 学习卡片系统。项目采用前后端分离架构：Vue 前端提供 ChatGPT 风格学习界面，Django 后端提供 API、SQLite 数据库、SSE 流式生成和 AI Provider 抽象。

## 功能范围

- 多轮学习对话
- 每次生成一张学习卡片
- 继续学习和出题练习
- 四选一选择题
- 答对烟花效果
- Markdown 安全渲染
- 整个对话导出 PDF
- Provider 健康状态
- Ollama / OpenRouter / OpenAI-compatible / vLLM / SGLang 可切换
- `cl100k_base` 100k token 上下文预算

## 目录

```txt
professional-agentic-learning/
  backend/             Django + Django Ninja + SQLite
  frontend/            Vue 3 + Vite + TypeScript + pnpm
  prd/                 产品和工程 PRD
  run-all.sh           本地同时启动前后端
  Dockerfile           多阶段容器构建
  docker-compose.yml   容器编排
```

## 本地启动

本项目按当前机器约定使用 conda/base Python，不创建 Python 虚拟环境。

后端：

```sh
cd backend
/opt/anaconda3/bin/python3.13 manage.py migrate
/opt/anaconda3/bin/python3.13 manage.py runserver 127.0.0.1:8000
```

前端：

```sh
cd frontend
pnpm install
pnpm dev --host 127.0.0.1
```

一键启动：

```sh
./run-all.sh
```

停止本项目的两个 tmux session：

```sh
./stop-all.sh
```

## 环境变量

后端默认使用 Ollama OpenAI-compatible endpoint：

```env
AI_PROVIDER=ollama
AI_BASE_URL=http://127.0.0.1:11434/v1
AI_MODEL=gpt-oss:120b
AI_API_KEY=ollama
```

前端只配置后端地址：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

真实 `.env` 不提交。示例见：

- `backend/.env.example`
- `frontend/.env.example`

## 测试

后端测试包含真实 AI Provider 测试，不是 mock-only。

```sh
cd backend
/opt/anaconda3/bin/python3.13 -m pytest -q
```

前端构建：

```sh
cd frontend
pnpm build
```

## Docker Compose

```sh
docker compose up --build
```

默认端口：

- Backend: `http://127.0.0.1:8000`
- Frontend: `http://127.0.0.1:5173`

容器内的 Ollama/OpenRouter/vLLM/SGLang 地址需要通过环境变量配置。macOS Docker 访问宿主机 Ollama 时通常使用：

```env
AI_BASE_URL=http://host.docker.internal:11434/v1
```

## 提交规范

commit message 使用中文，标题简洁，正文写清楚背景、原因、主要改动、影响范围和测试结果。不要使用 `update`、`fix`、`改一下` 这类低信息量提交。
