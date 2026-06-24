# Frontend PRD - AI 学习卡片系统

## 1. 产品定位

本项目是一个前后端分离的 AI 学习卡片系统。前端使用 Vue 构建，整体交互参考 ChatGPT 聊天界面，但核心输出不是长篇回答，而是“一次一个学习卡片”的渐进式学习体验。

用户输入学习目标，例如“开始学习 SQL”，系统会从最基础知识开始，按卡片逐步教学。每张卡片结束后，系统自动给出下一步操作选项，例如“继续学习”和“出题练习”。练习题为四选一选择题，答对后展示烟花效果。

页面整体使用白色浅色主题，不使用暗色背景。

## 2. 技术栈

### 2.1 核心框架

- Vue 3
- Vite
- TypeScript
- Pinia
- Vue Router

### 2.2 UI 与样式

推荐使用：

- Tailwind CSS
- Headless UI 或 Radix Vue
- lucide-vue-next

可选：

- Bootstrap 5，仅在希望快速获得标准表单、按钮、布局时使用

约束：

- 不手写复杂 UI 组件轮子。
- 拖拽尺寸、弹窗、菜单、提示、Toast、Markdown 渲染、烟花动画等优先使用成熟库。
- 页面必须是浅色 UI，主背景为白色或接近白色。
- 不加载远程 CSS CDN，依赖应通过 npm 管理并打包。

### 2.3 Markdown 渲染

使用成熟 Markdown 渲染链路：

- `markdown-it` 或 `vue-markdown-render`
- `highlight.js` 或 `shiki` 用于代码高亮
- `DOMPurify` 用于 HTML 清洗

要求：

- AI 返回内容必须按 Markdown 渲染。
- 禁止直接使用 `v-html` 渲染未清洗内容。
- 如果必须使用 `v-html`，必须经过 DOMPurify sanitize。
- 支持代码块、表格、列表、引用、行内代码。

### 2.4 SSE 客户端

优先使用浏览器原生 `EventSource`，如果需要 POST body 或更复杂控制，则使用：

- `@microsoft/fetch-event-source`

要求：

- 支持流式显示 AI 卡片生成过程。
- 支持连接中断后的错误提示。
- 支持取消当前生成。
- 后端返回事件需要有明确类型，例如 `card_delta`、`card_done`、`quiz_delta`、`error`。

### 2.5 动画效果

正确答题后的烟花效果使用成熟库：

- `canvas-confetti`

要求：

- 答对选择题后触发短暂烟花。
- 动画不阻塞 UI。
- 动画结束后不残留 DOM。

### 2.6 中文注释与可读性

Vue 前端代码必须有中文注释，但注释目标是说明意图，不是逐行翻译代码。

必须写中文注释的位置：

- 复杂交互逻辑，例如侧边栏拖拽、输入框高度拖拽、SSE 取消、PDF 分页导出。
- 与产品规则强相关的逻辑，例如 Enter 换行、Shift + Enter 发送、最近一轮才能编辑或重新生成。
- 安全相关逻辑，例如 CSRF token 注入、Markdown sanitize、外链安全属性。
- 长难句或复杂条件判断之前，必须用中文拆成短句说明业务含义。
- 组合多个状态的 computed、watch、store action，需要说明状态之间的关系。

不建议写的注释：

- 不要给显而易见的代码写废话注释，例如“设置变量”“调用函数”。
- 不要用英文长句解释业务逻辑。
- 不要让注释和代码表达相互矛盾。

示例：

```ts
// 只允许最近一轮用户输入进入编辑态。
// 更早的输入已经参与后续卡片生成，修改它会破坏学习路径的一致性。
const canEditMessage = message.id === latestUserMessageId && !isGenerating
```

## 3. 页面结构

### 3.1 总体布局

前端首屏即为主应用，不做营销 landing page。

布局：

- 左侧：历史对话侧边栏
- 中间：聊天与学习卡片主区域
- 底部：输入框
- 右上角：Provider 与健康状态

视觉要求：

- 白色背景
- 信息密度接近 ChatGPT
- 不做暗色主题
- 不使用大面积渐变、装饰性背景图或无意义卡片堆叠

### 3.2 左侧历史对话栏

功能：

- 显示过往对话列表
- 支持新建对话
- 支持切换对话
- 支持显示对话标题
- 支持显示最近更新时间
- 支持当前对话高亮

交互：

- 左侧栏宽度可拖拽调整
- 拖拽范围建议：
  - 最小宽度：220px
  - 最大宽度：420px
  - 默认宽度：280px
- 用户调整后的宽度保存到 `localStorage`

推荐库：

- `vue-draggable-resizable`
- 或 `re-resizable` 的 Vue 等价方案
- 若使用自写 resize handler，必须保持代码简单，只做尺寸拖拽，不扩展为通用拖拽框架

### 3.3 主聊天区域

内容类型：

- 用户消息
- AI 学习卡片
- 操作选项
- 选择题
- 答题反馈

AI 学习卡片要求：

- 每次只展示一个新卡片作为 AI 回复
- 卡片内容使用 Markdown
- 卡片应包含标题、核心解释、示例、关键点
- 不要一次性倾倒完整课程
- 用户应感觉是在和 AI 对话，但 AI 的教学节奏是卡片式推进

推荐卡片数据结构：

```ts
type LearningCard = {
  id: string
  conversationId: string
  title: string
  markdown: string
  topic: string
  level: 'beginner' | 'intermediate' | 'advanced'
  orderIndex: number
  createdAt: string
}
```

### 3.4 底部输入框

功能：

- 多行输入
- 输入框高度可拖拽
- Enter 换行
- Shift + Enter 发送
- 支持点击发送按钮
- 发送中展示 loading 状态
- 当前 SSE 生成中支持停止

注意：

- 用户明确要求 Enter 是换行，Shift Enter 是发送。
- 这与常见聊天工具相反，必须在实现中写清楚并测试。

输入框高度：

- 默认高度：120px
- 最小高度：80px
- 最大高度：320px
- 用户调整后的高度保存到 `localStorage`

发送按钮：

- 使用 lucide 图标，例如 `Send`
- 生成中显示 `Square` 或 `StopCircle`

### 3.5 右上角 Provider 和健康状态

显示内容：

- 当前 Provider，例如 `provider: ollama`
- 健康状态灯：
  - 绿色：可用
  - 红色：不可用
  - 黄色：检查中或降级

交互：

- 点击 provider 区域可打开 provider 设置面板
- 设置面板展示：
  - 当前 provider
  - base URL
  - model
  - 最近一次健康检查时间
  - 错误摘要

Provider 不在前端直接调用，前端只展示后端配置与健康检查结果。

## 4. 核心用户流程

### 4.1 开始学习

1. 用户进入页面。
2. 点击新建对话或使用当前对话。
3. 输入“开始学习 SQL”。
4. 用户按 Shift + Enter 发送。
5. 前端创建用户消息。
6. 前端请求后端创建 AI 学习卡片 SSE。
7. AI 卡片流式渲染。
8. 卡片完成后，前端展示操作选项：
   - 继续学习
   - 出题练习

### 4.2 继续学习

1. 用户点击“继续学习”。
2. 前端发送 `continue` action。
3. 后端基于 conversation memory 生成下一张卡片。
4. 前端流式渲染新卡片。
5. 完成后再次显示“继续学习”和“出题练习”。

### 4.3 出题练习

1. 用户点击“出题练习”。
2. 后端基于当前学习卡片生成选择题。
3. 前端展示四个选项。
4. 用户点击一个选项。
5. 前端调用答题校验 API。
6. 如果正确：
   - 显示正确状态
   - 触发 `canvas-confetti`
7. 如果错误：
   - 显示错误状态
   - 展示正确答案和简短解释

## 5. 前端路由

建议路由：

- `/`：默认重定向到最近对话或创建新对话
- `/chat/:conversationId`：聊天学习页面
- `/settings/provider`：可选，provider 设置页面

如果产品早期追求简单，也可以用单页状态面板，不单独做设置路由。

## 6. 状态管理

使用 Pinia，不使用自写全局事件总线。

Store 建议：

- `conversationStore`
  - 对话列表
  - 当前对话
  - 新建对话
  - 切换对话
- `messageStore`
  - 当前对话消息
  - AI 流式消息状态
  - 学习卡片
  - 题目
- `providerStore`
  - provider 配置展示
  - provider 健康状态
- `layoutStore`
  - 左侧栏宽度
  - 输入框高度

## 7. API 对接

前端只调用 Django API，不直接调用 Ollama、OpenRouter、OpenAI API、vLLM 或 SGLang。

建议 API：

```txt
GET    /api/health
GET    /api/provider/status
GET    /api/conversations
POST   /api/conversations
GET    /api/conversations/{id}/messages
POST   /api/conversations/{id}/messages
POST   /api/conversations/{id}/learn/stream
POST   /api/conversations/{id}/quiz/stream
POST   /api/quizzes/{id}/answer
```

SSE 接口建议使用 `@microsoft/fetch-event-source`，因为原生 EventSource 不支持 POST body。

## 8. 安全要求

### 8.1 XSS

- 所有 AI Markdown 渲染必须 sanitize。
- 禁止执行 AI 内容中的 script、iframe、onerror、onclick 等危险内容。
- 链接默认加 `rel="noopener noreferrer"`。
- 外链可选加确认提示。

### 8.2 CSRF

- Django 后端启用 CSRF。
- 前端请求带 `X-CSRFToken`。
- 启动时调用后端 CSRF 初始化接口或读取 cookie。
- 使用 Axios 拦截器统一注入 CSRF token。

### 8.3 输入校验

- 前端做基本长度限制。
- 后端仍必须做最终校验。
- 用户输入不应直接拼 HTML。

## 9. 可访问性

- 所有按钮有明确 `aria-label`
- 图标按钮必须有 tooltip 或 aria-label
- 选择题选项可用键盘选择
- 发送按钮可用键盘触发
- 健康状态不能只依赖颜色，应有文字状态

## 10. 验收标准

- 页面为浅色 ChatGPT 风格聊天界面。
- 左侧历史对话栏可拖拽调整宽度。
- 底部输入框可拖拽调整高度。
- Enter 换行，Shift + Enter 发送。
- 右上角展示 provider 与红黄绿健康状态。
- AI 回复以 Markdown 学习卡片形式流式展示。
- 每次只生成一张学习卡片。
- 卡片完成后自动显示“继续学习”和“出题练习”。
- 选择题为四选一。
- 答对后显示烟花效果。
- Markdown 渲染经过 XSS 清洗。
- 所有 API 调用走 Django 后端。

## 11. 不造轮子原则

必须优先使用成熟库：

- Markdown：`markdown-it`、`vue-markdown-render`
- XSS 清洗：`dompurify`
- SSE：`@microsoft/fetch-event-source`
- 状态管理：`pinia`
- 路由：`vue-router`
- 图标：`lucide-vue-next`
- 动画：`canvas-confetti`
- 拖拽尺寸：成熟 resize 组件库
- 日期格式化：`dayjs`
- 请求：`axios` 或 `ky`
- 表单校验：`vee-validate` + `zod`，或仅用 `zod` 做轻量校验

除非没有合适库，否则不手写通用组件、Markdown parser、SSE parser、动画系统、日期格式化、复杂表单校验或 sanitizer。
