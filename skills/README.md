# Skills 目录索引

> 最后更新：2026-09-17 | Skills 总数：**36**（不含 `.system`）
>
> 本文件是 skill 花名册的**唯一维护源**；`HARDLINK_INVENTORY.md` 只保留链接治理信息，不重复列举清单。

## Skills 清单

按名称字典序排列，便于与 `ls skills/` 实测结果逐行核对。「来源」列中 `GitHub: owner/repo` 为可核验的远端地址（`git -C skills/<name> remote get-url origin`）。

| # | Skill | 说明 | 来源 |
|---|-------|------|------|
| 1 | `ai-code-review` | AI 生成代码审查：幻觉 API/依赖、安全漏洞、逻辑错误、供应链风险、可维护性 | 主仓库 |
| 2 | `ai-config-sharing` | 多 AI 工具 skills/agents/AGENTS.md 配置统一管理（Junction + HardLink 单点维护） | 主仓库 |
| 3 | `arxiv-paper-downloader` | arXiv 论文批量下载，逐篇用首页标题校验并纠正错误 ID | 主仓库 |
| 4 | `awesome-ai-research-writing` | 中英双语学术写作工具包：起草、翻译、润色、缩写、扩写、逻辑检查 | 主仓库（社区来源已展平） |
| 5 | `browser-automation` | 统一浏览器自动化套件：Playwright 网页操作 / E2E 测试 / Electron 桌面探索 | 主仓库（多来源合并） |
| 6 | `claude-deep-research-skill` | 多源深度研究、引用追踪、证据留存、结构化报告 | GitHub: 199-biotechnologies/claude-deep-research-skill |
| 7 | `doc-coauthoring` | 文档协作写作工作流：文档、提案、技术规格、决策文档 | 主仓库 |
| 8 | `feishu-job-import` | 秋招投递管理：飞书岗位汇总表 → 自建投递管理表批量补全 / 新建 | 主仓库 |
| 9 | `frontend-design` | 前端视觉设计指导：设计方向、排版、反模板化默认观感 | 主仓库 |
| 10 | `git-branch-diff-merge` | 双分支双向合并融合，冲突取新；AI 只读分析，Git 写操作由用户执行 | 主仓库 |
| 11 | `git-commit` | Conventional Commits 规范提交（type/scope/subject） | 主仓库 |
| 12 | `humanizer-zh` | 中文去 AI 味写作助手：检测并修复 AI 写作特征模式 | GitHub: op7418/Humanizer-zh |
| 13 | `kaggle-modularize` | 单体 `.ipynb` ↔ Python 模块双向拆分 / 合并 | 主仓库 |
| 14 | `kaggle-notebook-to-cloud-jupyter` | Kaggle notebook 迁移到云 GPU JupyterLab：单源参数化、两级存储、依赖安装 | 主仓库 |
| 15 | `markitdown` | 多格式文档转 Markdown：PDF / Office / 图片 / 音频 / HTML / CSV / EPUB / ZIP / URL | 主仓库 |
| 16 | `mermaid-master` | Mermaid 技术文档图表：流程图、架构图、时序图、状态图、ER 图、甘特图 | 主仓库 |
| 17 | `model-architecture-diagram` | 从代码生成模型架构图（UML / 类图 / 时序图 / 组件图） | ⚠️ 见「待恢复项」 |
| 18 | `morph-ppt` | PowerPoint Morph 跨页平滑过渡动画幻灯片 | 主仓库 |
| 19 | `morph-ppt-3d` | 3D Morph PPT：GLB 模型插入 + 电影摄影机 + 模型内容版式 | 主仓库 |
| 20 | `multi-agent` | 多代理任务规划与可审计的子代理任务简报生成 | 主仓库 |
| 21 | `nature-skills` | Nature 级学术工作流：写作、引用、绘图、检索、统计、润色、审稿回复 | GitHub: Yuan1z0825/nature-skills |
| 22 | `officecli` | Office 文档 CLI 工具：创建、分析、校对、修改 `.docx` / `.xlsx` / `.pptx` | 主仓库 |
| 23 | `officecli-academic-paper` | 学术论文 `.docx`：APA / Chicago / IEEE / MLA 引用、编号公式、交叉引用 | 主仓库 |
| 24 | `officecli-data-dashboard` | Excel 多元素仪表板：KPI 卡、多图表、sparkline、条件格式 | 主仓库 |
| 25 | `officecli-docx` | Word 文档创建、解析与编辑 | 主仓库 |
| 26 | `officecli-financial-model` | Excel 财务模型：3-statement、DCF、LBO、SaaS 单位经济、敏感性分析 | 主仓库 |
| 27 | `officecli-pitch-deck` | 投资者融资 Pitch Deck（种子轮至 C 轮、可转债、SAFE） | 主仓库 |
| 28 | `officecli-pptx` | PowerPoint 演示文稿创建、解析与编辑 | 主仓库 |
| 29 | `officecli-word-form` | 可填充 Word 表单：Content Controls + 旧式 FormField + MERGEFIELD | 主仓库 |
| 30 | `officecli-xlsx` | Excel 电子表格创建、解析与编辑 | 主仓库 |
| 31 | `repo-wiki` | 生成完整多页项目 Wiki（含内置模板，输出语言跟随提问语言） | GitHub: devin2255/repo-wiki-skill |
| 32 | `resume-tech-interview-decompose` | 简历技术点拆解为面试准备文档：速记表、双版本口述稿、深度答案、自评清单 | 主仓库 |
| 33 | `skill-creator` | 创建、修改、评测与优化 Skills | 主仓库（社区来源已展平） |
| 34 | `superpowers` | 开发流程技能库：头脑风暴、系统化调试、TDD、计划编写、代码审查等 | GitHub: obra/superpowers |
| 35 | `web-access` | 统一联网操作：搜索、网页抓取、登录后操作、动态渲染页面 | GitHub: eze-is/web-access |
| 36 | `workbuddy-auto-credits` | WorkBuddy 自动领积分：每日签到 + 派猫猫旅行 | 主仓库 |

### 来源分类小结

| 来源 | 数量 | 说明 |
|------|------|------|
| GitHub 克隆 | 6 | 各自保留独立 `.git`，由主仓库 `.gitignore` 排除，整体不入库 |
| 主仓库跟踪 | 30 | 由 `.ai-shared` 主仓库直接版本管理（含已展平的社区来源） |

## 内部系统目录（`.system/`，不上传）

`skills/.system/` 为 Codex 内部系统 skill 目录，当前为**空目录**（原始内容未恢复），由 `skills/.gitignore` 排除，不入库。

## 目录内非 skill 条目

以下文件位于 `skills/` 根下，不是 skill 目录：

| 条目 | 说明 |
|------|------|
| `.gitignore` | skills 目录的 git 忽略规则 |
| `README.md` | 本文件 |
| `.disable_to_model_invocation_migration.json` | Codex 迁移标记 |
| `.model_invocation_to_override_migration.json` | Codex 迁移标记 |
| `.user_invocable_only_to_off_migration.json` | Codex 迁移标记 |
| `_bm_skillid_migration.json` | SkillsHub 本地元数据（`skills/.gitignore` 排除） |

## 待恢复项

| Skill | 状态 | 说明 |
|-------|------|------|
| `model-architecture-diagram` | ⚠️ 占位文件（frontmatter `status: NEEDS_RECOVERY`） | 原始 SKILL.md 内容丢失，未找到对应公开仓库；需用户提供原始来源或备份 |

## 共享架构

所有 skill 通过 Windows 目录联接（Junction）共享到以下工具目录：

```
C:\Users\20448\.ai-shared\skills\  ← 唯一维护源
├── .claude\skills\       ──Junction──→ .ai-shared\skills\
├── .codex\skills\        ──Junction──→ .ai-shared\skills\
├── .cursor\skills\       ──Junction──→ .ai-shared\skills\
├── .qoder\skills\        ──Junction──→ .ai-shared\skills\
├── .workbuddy\skills\    ──Junction──→ .ai-shared\skills\
├── .workbuddy-ai\skills\ ──Junction──→ .ai-shared\skills\
├── .catpawai\skills\     ──Junction──→ .ai-shared\skills\
└── .agents\skills\       ──Junction──→ .ai-shared\skills\
```

## 更新方法

### GitHub 克隆的 Skills（6 个）

```bash
cd ~/.ai-shared/skills/<skill-name> && git pull --ff-only
```

适用于：`claude-deep-research-skill`、`humanizer-zh`、`nature-skills`、`repo-wiki`、`superpowers`、`web-access`

### 主仓库跟踪的 Skills（30 个）

无外部更新源，直接修改即可；改动经 Junction 同步到所有工具目录，并由主仓库统一版本管理。
