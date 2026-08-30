# Skills 目录索引

> 最后更新：2026-08-30 | Skills 总数：31（不含 `.system`）

## Skills 清单

### 自建 Skills（21 个）

| # | Skill | 说明 |
|---|-------|------|
| 1 | `ai-code-review` | AI 生成代码审查（幻觉 API、安全漏洞、逻辑错误） |
| 2 | `ai-config-sharing` | 统一管理多个 AI 编程助手的 skills/agents/AGENTS.md 配置 |
| 3 | `algorithmic-art` | p5.js 生成艺术、粒子系统、流场 |
| 4 | `doc-coauthoring` | 文档协作写作工作流 |
| 5 | `frontend-design` | 前端设计：设计哲学 + 50+ 风格 + 161 配色 + 57 字体搭配 |
| 6 | `git-commit` | Conventional Commits 规范提交 |
| 7 | `kaggle-notebookify` | Markdown → Kaggle Jupyter Notebook |
| 8 | `markitdown` | 多格式文档转 Markdown（PDF/Office/HTML/CSV） |
| 9 | `mermaid-master` | Mermaid 技术文档图表生成 |
| 10 | `morph-ppt` | PowerPoint Morph 过渡动画幻灯片 |
| 11 | `morph-ppt-3d` | 3D Morph PPT（GLB 模型插入 + 电影摄影机） |
| 12 | `multi-agent` | 多代理任务规划与子代理简报生成 |
| 13 | `officecli` | Office 文档 CLI 工具（.docx/.xlsx/.pptx） |
| 14 | `officecli-academic-paper` | 学术论文 .docx 生成（APA/IEEE/MLA 引用样式） |
| 15 | `officecli-data-dashboard` | Excel 多元素仪表板生成 |
| 16 | `officecli-docx` | Word 文档创建与编辑 |
| 17 | `officecli-financial-model` | Excel 财务模型（3-statement/DCF/LBO） |
| 18 | `officecli-pitch-deck` | 投资者融资 Pitch Deck 生成 |
| 19 | `officecli-pptx` | PowerPoint 演示文稿创建与编辑 |
| 20 | `officecli-word-form` | 可填充 Word 表单（Content Controls + Mail Merge） |
| 21 | `officecli-xlsx` | Excel 电子表格创建与编辑 |

### 社区 Skills（10 个）

| # | Skill | 来源 | 说明 |
|---|-------|------|------|
| 22 | `superpowers` | [obra/superpowers](https://github.com/obra/superpowers) | 核心技能库：TDD、调试、协作模式等 14 个子技能 |
| 23 | `web-access` | [eze-is/web-access](https://github.com/eze-is/web-access) | 统一联网操作：搜索、抓取、登录后操作 |
| 24 | `nature-skills` | [Yuan1z0825/nature-skills](https://github.com/Yuan1z0825/nature-skills) | Nature 级别学术工作流（16 个子技能） |
| 25 | `claude-deep-research-skill` | [199-biotechnologies/claude-deep-research-skill](https://github.com/199-biotechnologies/claude-deep-research-skill) | 多源深度研究、引用追踪、结构化报告 |
| 26 | `awesome-ai-research-writing` | [zengrong233/awesome-ai-research-writing-skill](https://github.com/zengrong233/awesome-ai-research-writing-skill) | 通用学术写作工具包（中英双语） |
| 27 | `humanizer-zh` | [deedeekong07-alt/humanizer-zh](https://github.com/deedeekong07-alt/humanizer-zh) | 中文去 AI 味写作助手 |
| 28 | `repo-wiki` | [dark4scope/claude-skill-repo-wiki](https://github.com/dark4scope/claude-skill-repo-wiki) | 生成 OpenDeepWiki 风格的仓库文档 |
| 29 | `arxiv-paper-downloader` | 自建 | arXiv 论文批量下载与首页标题校验 |
| 30 | `browser-automation` | 合并 | 统一浏览器自动化：网页操作 / E2E 测试 / Electron |
| 31 | `skill-creator` | [anthropics/claude-plugins-official](https://github.com/anthropics/claude-plugins-official) | 创建、修改和测试 Skills |

### 内部系统 Skills（`.system/`，不上传）

| Skill | 说明 |
|-------|------|
| `imagegen` | AI 位图生成 |
| `openai-docs` | OpenAI 产品/API 文档查询 |
| `plugin-creator` | Codex 插件目录脚手架 |
| `review-agent` | 只读代码审查 |
| `skill-creator` | Skill 创建（系统版本） |
| `skill-installer` | Skill 安装器 |

## 共享架构

所有 skill 通过 Windows Junction 共享到以下工具目录：

```
C:\Users\20448\.ai-shared\skills\  ← 唯一维护点
├── .claude\skills\     ──Junction──→ .ai-shared\skills\
├── .codex\skills\      ──Junction──→ .ai-shared\skills\
├── .cursor\skills\     ──Junction──→ .ai-shared\skills\
├── .qoder\skills\      ──Junction──→ .ai-shared\skills\
├── .workbuddy\skills\  ──Junction──→ .ai-shared\skills\
├── .catpawai\skills\   ──Junction──→ .ai-shared\skills\
└── .agents\skills\     ──Junction──→ .ai-shared\skills\
```

## 更新方法

### 有 git 信息的 Skills（6 个）

```bash
cd ~/.ai-shared/skills/<skill-name> && git pull --ff-only
```

适用于：superpowers, web-access, nature-skills, claude-deep-research-skill, awesome-ai-research-writing, humanizer-zh, repo-wiki

### 自建 Skills（21 个）

无外部更新源，根据需要手动修改。在 `~/.ai-shared/skills/` 中修改即可同步到所有工具。
