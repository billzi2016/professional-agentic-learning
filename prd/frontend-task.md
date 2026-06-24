# Frontend Task - AI 学习卡片系统

## 1. 目标

前端使用 Vue 3 + Vite + TypeScript 实现 ChatGPT 风格的学习卡片界面。核心能力包括历史对话、可拖拽侧边栏、可拖拽输入框、Markdown 卡片渲染、SSE 流式生成、Provider 健康状态、选择题答题和答对烟花效果。

## 2. 阶段一：项目初始化

### 任务

- [ ] 初始化 `frontend/` Vue 项目。
- [ ] 配置 TypeScript。
- [ ] 配置 Vite。
- [ ] 配置 Tailwind CSS。
- [ ] 配置 Vue Router。
- [ ] 配置 Pinia。
- [ ] 配置基础目录结构。

### 推荐依赖

```txt
vue
vite
typescript
pinia
vue-router
tailwindcss
postcss
autoprefixer
lucide-vue-next
```

### 验收

- [ ] `npm run dev` 可以启动。
- [ ] 默认页面加载正常。
- [ ] `src/` 目录结构清晰。
- [ ] 无暗色主题默认样式。

## 3. 阶段二：API Client 与 CSRF

### 任务

- [ ] 创建 `src/api/client.ts`。
- [ ] 配置 API base URL。
- [ ] 配置 `withCredentials`。
- [ ] 实现 CSRF 初始化请求。
- [ ] 写 Axios 或 ky 拦截器，自动带 `X-CSRFToken`。
- [ ] 统一错误处理。

### 推荐依赖

```txt
axios
```

或：

```txt
ky
```

### 验收

- [ ] 页面启动后能调用 `GET /api/csrf`。
- [ ] POST、PATCH、DELETE 请求自动带 CSRF token。
- [ ] API 错误能展示可读提示。

## 4. 阶段三：应用布局

### 任务

- [ ] 实现 `AppShell.vue`。
- [ ] 实现左侧历史对话栏 `Sidebar.vue`。
- [ ] 实现主聊天区 `ChatThread.vue`。
- [ ] 实现底部输入区 `ChatInput.vue`。
- [ ] 实现右上角 `ProviderStatus.vue`。

### 视觉要求

- [ ] 白色浅色主题。
- [ ] 首屏就是可用聊天学习界面。
- [ ] 不做 landing page。
- [ ] 不使用暗色背景。
- [ ] 不使用大面积渐变装饰。

### 验收

- [ ] 页面布局接近 ChatGPT。
- [ ] 左侧是历史对话。
- [ ] 中间是聊天内容。
- [ ] 底部是输入框。
- [ ] 右上角显示 provider 和健康灯。

## 5. 阶段四：侧边栏对话列表

### 任务

- [ ] 实现对话列表 API 对接。
- [ ] 支持新建对话。
- [ ] 支持切换对话。
- [ ] 支持当前对话高亮。
- [ ] 支持对话置顶。
- [ ] 支持取消置顶。
- [ ] 支持删除对话。
- [ ] 置顶对话显示在列表上方。

### API

```txt
GET    /api/conversations
POST   /api/conversations
PATCH  /api/conversations/{conversation_id}
DELETE /api/conversations/{conversation_id}
POST   /api/conversations/{conversation_id}/pin
POST   /api/conversations/{conversation_id}/unpin
```

### 验收

- [ ] 可以新建对话。
- [ ] 可以进入历史对话。
- [ ] 置顶后对话出现在上方。
- [ ] 删除后对话从列表消失。
- [ ] 删除前有确认弹窗。

## 6. 阶段五：可拖拽尺寸

### 任务

- [ ] 实现左侧栏宽度拖拽。
- [ ] 实现输入框高度拖拽。
- [ ] 保存尺寸到 `localStorage`。
- [ ] 页面刷新后恢复尺寸。

### 建议范围

侧边栏：

- 默认：280px
- 最小：220px
- 最大：420px

输入框：

- 默认：120px
- 最小：80px
- 最大：320px

### 验收

- [ ] 用户可以拖拽左侧栏宽度。
- [ ] 用户可以拖拽输入框高度。
- [ ] 拖拽不会导致内容重叠。
- [ ] 刷新后尺寸保持。

## 7. 阶段六：聊天输入

### 任务

- [ ] 实现多行输入。
- [ ] Enter 换行。
- [ ] Shift + Enter 发送。
- [ ] 点击按钮发送。
- [ ] 发送中禁用重复提交。
- [ ] 生成中支持停止。

### 注意

本项目要求 Enter 是换行，Shift + Enter 是发送，这与很多聊天产品相反，必须明确测试。

### 验收

- [ ] Enter 只换行。
- [ ] Shift + Enter 发送。
- [ ] 空内容不可发送。
- [ ] 发送后用户消息出现在聊天区。
- [ ] 生成中可以取消。

## 8. 阶段七：Markdown 渲染

### 任务

- [ ] 实现 `MarkdownRenderer.vue`。
- [ ] 使用成熟 Markdown 库。
- [ ] 接入代码高亮。
- [ ] 使用 DOMPurify 清洗 HTML。
- [ ] 给外链加安全属性。

### 推荐依赖

```txt
markdown-it
dompurify
highlight.js
```

### 验收

- [ ] 支持标题、列表、代码块、表格、引用。
- [ ] AI 内容不会直接用未清洗 `v-html` 渲染。
- [ ] 恶意 script 不会执行。

## 9. 阶段八：SSE 学习卡片

### 任务

- [ ] 实现 `src/utils/sse.ts`。
- [ ] 使用 `@microsoft/fetch-event-source`。
- [ ] 支持 `card_start`、`card_delta`、`card_done`、`error`。
- [ ] 支持 AbortController 取消。
- [ ] 流式更新当前 AI 卡片。

### API

```txt
POST /api/conversations/{conversation_id}/learn/stream
```

### 验收

- [ ] 用户发送“开始学习 SQL”后，AI 卡片流式显示。
- [ ] 每次只出现一张新卡片。
- [ ] 生成完成后显示“继续学习”和“出题练习”。
- [ ] 出错时显示错误状态。

## 10. 阶段九：继续学习与出题

### 任务

- [ ] 实现卡片底部操作栏 `ActionBar.vue`。
- [ ] 点击“继续学习”生成下一张卡片。
- [ ] 点击“出题练习”生成四选一题。
- [ ] 题目生成支持 SSE。

### API

```txt
POST /api/conversations/{conversation_id}/learn/stream
POST /api/conversations/{conversation_id}/quiz/stream
GET  /api/quizzes/{quiz_id}
```

### 验收

- [ ] 卡片完成后自动出现两个操作按钮。
- [ ] 继续学习会生成下一张卡片。
- [ ] 出题练习会显示四个选项。

## 11. 阶段十：选择题答题

### 任务

- [ ] 实现 `QuizCard.vue`。
- [ ] 实现 `QuizOption.vue`。
- [ ] 用户点击选项后提交答案。
- [ ] 显示正确或错误。
- [ ] 错误时显示正确答案和解释。
- [ ] 正确时触发烟花。

### 推荐依赖

```txt
canvas-confetti
```

### API

```txt
POST /api/quizzes/{quiz_id}/answer
```

### 验收

- [ ] 题目有四个选项。
- [ ] 用户只能选择一个。
- [ ] 答题后显示结果。
- [ ] 答对后有烟花效果。
- [ ] 答题后不允许重复提交，除非后端明确允许。

## 12. 阶段十一：导出学习记录 PDF

### 任务

- [ ] 在聊天主界面增加导出按钮，建议放在顶部工具区或对话标题旁。
- [ ] 点击导出后生成当前完整对话过程的 PDF。
- [ ] PDF 内容包含用户输入、AI 学习卡片、选择题、用户答案、正确/错误状态和解释。
- [ ] PDF 使用当前 Markdown 渲染后的可读内容，不导出原始 Markdown 符号堆叠。
- [ ] 导出前隐藏输入框、操作按钮、Provider 状态灯等不属于学习记录的 UI。
- [ ] 导出过程中显示 loading 状态，避免重复点击。
- [ ] 导出完成后自动下载文件。
- [ ] 文件名包含对话标题和日期，例如 `SQL-学习-2026-06-24.pdf`。

### 推荐依赖

```txt
html2canvas
jspdf
```

可选方案：

```txt
pdfmake
```

### 实现建议

- 优先使用现成库，不手写 PDF 渲染引擎。
- 如果使用 `html2canvas` + `jspdf`，应准备一个专门的导出 DOM 容器，避免直接截取带滚动条的聊天窗口。
- 长对话需要分页，不能只导出当前可视区域。
- 代码块、表格、选择题选项需要保持可读排版。
- 导出内容应使用浅色背景，适合打印。

### 验收

- [ ] 点击导出按钮后可以下载 PDF。
- [ ] PDF 包含整个当前对话过程，不只包含当前屏幕。
- [ ] PDF 中 Markdown 内容排版清晰。
- [ ] PDF 中选择题和答题结果可读。
- [ ] 导出时不会把输入框、继续学习按钮、出题按钮、Provider 状态导入正文。
- [ ] 长对话可以正常分页。

## 13. 阶段十二：最近一轮编辑与重新生成

### 任务

- [ ] 在最近一条用户输入上显示编辑入口。
- [ ] 在最近一张 AI 卡片上显示重新生成入口。
- [ ] 更早消息不显示编辑或重新生成入口。
- [ ] 调用后端校验 API。
- [ ] 如果后端拒绝，显示错误提示。

### API

```txt
PATCH /api/messages/{message_id}
DELETE /api/messages/{message_id}
POST  /api/learning-cards/{card_id}/regenerate
```

### 验收

- [ ] 最近用户输入可修改。
- [ ] 最近 AI 卡片可重新生成。
- [ ] 更早内容不可操作。
- [ ] 后端拒绝时前端能展示提示。

## 14. 阶段十三：Provider 状态

### 任务

- [ ] 实现 `providerStore`。
- [ ] 获取 provider 状态。
- [ ] 展示 provider 名称、模型、健康灯。
- [ ] 支持手动重新检查健康状态。

### API

```txt
GET  /api/provider/status
POST /api/provider/health-check
```

### 验收

- [ ] 右上角显示 `provider: ollama`。
- [ ] 健康状态绿、红、黄灯准确显示。
- [ ] 不暴露 API key。

## 15. 阶段十四：前端测试与检查

### 任务

- [ ] 测试输入快捷键。
- [ ] 测试 Markdown XSS。
- [ ] 测试 SSE 中断。
- [ ] 测试对话置顶和删除。
- [ ] 测试最近一轮编辑限制。
- [ ] 测试移动端基本布局。

### 推荐工具

```txt
vitest
@vue/test-utils
playwright
```

### 验收

- [ ] 核心交互有测试覆盖。
- [ ] 页面无明显文本重叠。
- [ ] 主要流程可完整走通。

## 16. 阶段十五：README 与中文注释

### 任务

- [ ] 编写 `frontend/README.md`。
- [ ] 在 README 中说明 Vue 前端职责、启动方式、环境变量、主要组件和测试命令。
- [ ] 在 README 中说明 Markdown 渲染、XSS 清洗、SSE 客户端和 PDF 导出方案。
- [ ] 在复杂 Vue 组件中补充中文注释，明确业务意图。
- [ ] 在复杂 store action、computed、watch 中补充中文注释。
- [ ] 对长难句和复杂条件判断，用中文短句拆开解释。
- [ ] 避免给显而易见的代码写无意义注释。

### 验收

- [ ] `frontend/README.md` 存在。
- [ ] 新开发者可以只看 `frontend/README.md` 启动前端。
- [ ] 关键复杂逻辑有中文注释。
- [ ] 注释解释“为什么这样做”，不是逐行翻译代码。

## 17. 阶段十六：提交前检查

### 任务

- [ ] 确认前端改动只包含当前任务相关内容。
- [ ] 确认复杂逻辑已有中文注释。
- [ ] 确认 README 或任务文档已同步更新。
- [ ] 准备详细中文 commit message，说明背景、原因、改动、影响和测试。
- [ ] commit message 不使用 `update`、`fix`、`改一下` 这类低信息量标题。

### 验收

- [ ] 提交信息符合项目的 Linus 风格提交说明要求。
- [ ] 提交正文说明是否运行过前端测试。

## 18. 不造轮子清单

必须使用成熟库：

- Markdown 渲染：`markdown-it`
- HTML 清洗：`dompurify`
- SSE：`@microsoft/fetch-event-source`
- 状态管理：`pinia`
- 路由：`vue-router`
- 图标：`lucide-vue-next`
- 烟花动画：`canvas-confetti`
- PDF 导出：`html2canvas` + `jspdf` 或 `pdfmake`
- 日期：`dayjs`
- 请求：`axios` 或 `ky`
- 代码高亮：`highlight.js` 或 `shiki`

禁止自行实现：

- Markdown parser
- HTML sanitizer
- SSE parser
- 粒子动画系统
- PDF 渲染引擎
- 全局状态管理框架
- 日期格式化框架
