# Frontend

Vue 前端负责 AI 学习卡片系统的聊天式学习界面。

## 技术栈

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router
- pnpm

## 启动

```sh
cd frontend
pnpm install
pnpm dev
```

默认后端地址：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## 功能

- 左侧历史对话
- 侧边栏宽度拖拽
- 输入框高度拖拽
- Enter 换行，Shift + Enter 发送
- Markdown 安全渲染
- SSE 流式学习卡片
- 继续学习和出题练习
- 四选一答题反馈
- 答对烟花效果
- Provider 健康状态
- 导出整个对话为 PDF

## 注释规范

复杂交互必须写中文注释，解释业务意图和边界。不要给显而易见的代码写逐行翻译。
