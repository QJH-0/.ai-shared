# Skills 目录索引

> 最后更新：2026-09-24 | Skills 总数：**59**（不含 `.system/`，后者另见下文）
>
> 本文件是 skill 花名册的**唯一维护源**；`HARDLINK_INVENTORY.md` 只保留链接治理信息，不重复列举清单。

## Skills 清单

按名称字典序排列，便于与 `ls skills/` 实测结果逐行核对（`.system/` 与 6 个非目录条目除外，见后文）。「来源」列中 `GitHub: owner/repo` 为可核验的远端地址（`git -C skills/<name> remote get-url origin`）。

| # | Skill | 类别 | 说明 | 来源 |
|---|-------|------|------|------|
| 1 | `ai-code-review` | 开发与质量 | AI 生成代码审查：幻觉 API/依赖、安全漏洞、逻辑错误、供应链风险、可维护性 | 主仓库 |
| 2 | `ai-config-sharing` | 环境治理 | 多 AI 工具 skills/agents/AGENTS.md 配置统一管理（Junction + HardLink 单点维护） | 主仓库 |
| 3 | `ai-fast-learning-loop` | 学术科研 | 十步 AI 学习闭环：五视角 STORM → 矛盾图谱 → 综合简报 → 同行评审 → 资源筛选 → 能力阶梯 → 十次课计划 → 分级考试 → 费曼循环 → 一页速查表 | 主仓库 |
| 4 | `arxiv-paper-downloader` | 学术科研 | arXiv 论文批量下载，逐篇用首页标题校验并纠正错误 ID | 主仓库 |
| 5 | `automate` | 工具链 | 创建 Codex 自动化（一次性 / 周期性任务） | 主仓库 |
| 6 | `awesome-ai-research-writing` | 学术科研 | 中英双语学术写作工具包：起草、翻译、润色、缩写、扩写、逻辑检查 | 主仓库（社区来源已展平） |
| 7 | `babysit` | 开发与质量 | 保持 PR 可合并：分诊评论、解决明确冲突、循环修复 CI | 主仓库 |
| 8 | `browser-automation` | 浏览器与联网 | 统一浏览器自动化套件：Playwright 网页操作 / Web 应用可复跑 E2E 测试 | 主仓库（多来源合并） |
| 9 | `canvas` | 工具链 | 生成与对话并排的实时 React 分析画布（数据密集型独立产物） | 主仓库 |
| 10 | `claude-deep-research-skill` | 学术科研 | 多源深度研究、引用追踪、证据留存、结构化报告 | GitHub: 199-biotechnologies/claude-deep-research-skill |
| 11 | `code-to-interview-docs` | 文档与 Office | 按最新代码重写项目 README 与简历面试准备文档，用实测数字替换过时表述 | 主仓库 |
| 12 | `create-hook` | 工具链 | 创建 Codex hooks：hooks.json 与钩子脚本，自动化 agent 事件行为 | 主仓库 |
| 13 | `create-rule` | 工具链 | 创建 Codex rules：编码标准、项目约定、按文件类型的规则 | 主仓库 |
| 14 | `create-skill` | 工具链 | 编写 Codex Agent Skill（SKILL.md 结构与组织方式） | 主仓库 |
| 15 | `create-subagent` | 工具链 | 创建面向特定任务的子代理（自定义 prompt 与职责） | 主仓库 |
| 16 | `doc-coauthoring` | 文档与 Office | 文档协作写作工作流：文档、提案、技术规格、决策文档 | 主仓库 |
| 17 | `feishu-job-import` | 文档与 Office | 秋招投递管理：飞书岗位汇总表 → 自建投递管理表批量补全 / 新建 | 主仓库 |
| 18 | `fireworks-tech-graph` | 绘图可视化 | 手写 SVG 技术图：几何安全校验（边交叉/碰撞/标签位置）+ PNG 回读 + GIF 动效；12 种风格、14 类 UML；含 showcase 版式补遗 `references/showcase-layout.md` | GitHub: yizhiyanhua-ai/fireworks-tech-graph |
| 19 | `framework-migration-verification` | 开发与质量 | 迁回框架官方 API 或升级版本前，核实官方 API 在当前版本与调用通道下的真实行为 | 主仓库 |
| 20 | `frontend-design` | 绘图可视化 | 前端视觉设计指导：设计方向、排版、反模板化默认观感（含 50+ 风格库） | 主仓库 |
| 21 | `git-branch-diff-merge` | 开发与质量 | 双分支双向合并融合，冲突取新；AI 只读分析，Git 写操作由用户执行 | 主仓库 |
| 22 | `git-commit` | 开发与质量 | Conventional Commits 规范提交（type/scope/subject） | 主仓库 |
| 23 | `humanizer-zh` | 学术科研 | 中文去 AI 味写作助手：检测并修复 AI 写作特征模式 | GitHub: op7418/Humanizer-zh |
| 24 | `kaggle-modularize` | 开发与质量 | 单体 `.ipynb` ↔ Python 模块双向拆分 / 合并 | 主仓库 |
| 25 | `kaggle-notebook-to-cloud-jupyter` | 开发与质量 | Kaggle notebook 迁移到云 GPU JupyterLab：单源参数化、两级存储、依赖安装 | 主仓库 |
| 26 | `loop` | 工具链 | 按固定或可变间隔重复执行某个 prompt / skill | 主仓库 |
| 27 | `markitdown` | 文档与 Office | 多格式文档转 Markdown：PDF / Office / 图片 / 音频 / HTML / CSV / EPUB / ZIP / URL | 主仓库 |
| 28 | `mermaid-master` | 绘图可视化 | Mermaid 技术文档图表：流程图、架构图、时序图、状态图、ER 图、甘特图 | 主仓库 |
| 29 | `migrate-to-skills` | 工具链 | 把 rules（`.mdc`）与 slash commands 迁移为 Agent Skills 格式 | 主仓库 |
| 30 | `morph-ppt` | 文档与 Office | PowerPoint Morph 跨页平滑过渡动画幻灯片 | 主仓库 |
| 31 | `morph-ppt-3d` | 文档与 Office | 3D Morph PPT：GLB 模型插入 + 电影摄影机 + 模型内容版式 | 主仓库 |
| 32 | `multi-agent` | 开发与质量 | 多代理任务规划与可审计的子代理任务简报生成 | 主仓库 |
| 33 | `nature-skills` | 学术科研 | Nature 级学术工作流：写作、引用、绘图、检索、统计、润色、审稿回复 | GitHub: Yuan1z0825/nature-skills |
| 34 | `officecli` | 文档与 Office | Office 文档 CLI 工具：创建、分析、校对、修改 `.docx` / `.xlsx` / `.pptx` | 主仓库 |
| 35 | `officecli-academic-paper` | 文档与 Office | 学术论文 `.docx`：APA / Chicago / IEEE / MLA 引用、编号公式、交叉引用 | 主仓库 |
| 36 | `officecli-data-dashboard` | 文档与 Office | Excel 多元素仪表板：KPI 卡、多图表、sparkline、条件格式 | 主仓库 |
| 37 | `officecli-docx` | 文档与 Office | Word 文档创建、解析与编辑 | 主仓库 |
| 38 | `officecli-financial-model` | 文档与 Office | Excel 财务模型：3-statement、DCF、LBO、SaaS 单位经济、敏感性分析 | 主仓库 |
| 39 | `officecli-pitch-deck` | 文档与 Office | 投资者融资 Pitch Deck（种子轮至 C 轮、可转债、SAFE） | 主仓库 |
| 40 | `officecli-pptx` | 文档与 Office | PowerPoint 演示文稿创建、解析与编辑 | 主仓库 |
| 41 | `officecli-word-form` | 文档与 Office | 可填充 Word 表单：Content Controls + 旧式 FormField + MERGEFIELD | 主仓库 |
| 42 | `officecli-xlsx` | 文档与 Office | Excel 电子表格创建、解析与编辑 | 主仓库 |
| 43 | `plan-premise-verification` | 开发与质量 | 实施「借鉴型」优化计划前，逐条核实每条措施在本代码库的前提是否成立 | 主仓库 |
| 44 | `project-handover-docs` | 文档与 Office | 生成结构化交接文档包（对比矩阵 + 资料索引 + 进度待办 + 风险缺口），先用源码/数据实测校正口径再动笔 | 主仓库 |
| 45 | `repo-wiki` | 文档与 Office | 生成完整多页项目 Wiki（含内置模板，输出语言跟随提问语言） | GitHub: devin2255/repo-wiki-skill |
| 46 | `resume-tech-interview-decompose` | 文档与 Office | 简历技术点拆解为面试准备文档：速记表、双版本口述稿、深度答案、自评清单 | 主仓库 |
| 47 | `review` | 开发与质量 | 用 Bugbot 或 Security Review 子代理审查代码改动 | 主仓库 |
| 48 | `review-bugbot` | 开发与质量 | 用 Bugbot 子代理审查代码改动 | 主仓库 |
| 49 | `review-security` | 开发与质量 | 用 Security Review 子代理审查代码改动 | 主仓库 |
| 50 | `sdk` | 工具链 | 基于 Codex SDK（TypeScript `@cursor/sdk` / Python `cursor-sdk`）开发应用与自动化 | 主仓库 |
| 51 | `shell` | 工具链 | 把 `/shell` 之后的文本当作字面 shell 命令执行 | 主仓库 |
| 52 | `skill-creator` | 工具链 | 创建、修改、评测与优化 Skills | 主仓库（社区来源已展平） |
| 53 | `split-to-prs` | 开发与质量 | 把当前工作拆成若干小而可审查的 PR | 主仓库 |
| 54 | `statusline` | 工具链 | 配置 CLI 自定义状态栏 | 主仓库 |
| 55 | `superpowers` | 开发与质量 | 开发流程技能库：头脑风暴、系统化调试、TDD、计划编写、代码审查等 | GitHub: obra/superpowers |
| 56 | `update-cli-config` | 工具链 | 查看与修改 Codex CLI 配置（`~/.cursor/cli-config.json`） | 主仓库 |
| 57 | `update-cursor-settings` | 工具链 | 修改编辑器用户设置（`settings.json`） | 主仓库 |
| 58 | `web-access` | 浏览器与联网 | 统一联网操作：搜索、网页抓取、登录后操作、动态渲染页面 | GitHub: eze-is/web-access |
| 59 | `workbuddy-auto-credits` | 工具链 | WorkBuddy 自动领积分：每日签到 + 派猫猫旅行 | 主仓库 |

### 来源分类小结

| 来源 | 数量 | 说明 |
|------|------|------|
| GitHub 克隆 | 7 | 各自保留独立 `.git`，由主仓库 `.gitignore` 排除，整体不入库 |
| 主仓库跟踪 | 53 | 由 `.ai-shared` 主仓库直接版本管理（含已展平的社区来源） |

### 类别分布

| 类别 | 数量 |
|------|------|
| 文档与 Office | 18 |
| 工具链 | 15 |
| 开发与质量 | 14 |
| 学术科研 | 6 |
| 绘图可视化 | 4 |
| 浏览器与联网 | 2 |
| 环境治理 | 1 |

## 内部系统目录（`.system/`）

`skills/.system/` 是 Codex 内部系统 skill 目录，**不为空**，含 6 个 skill（由 `skills/.gitignore` 的 `.system/` 规则排除，不入主仓库；但会随 Junction 分发到各工具目录）：

| Skill | 说明 |
|-------|------|
| `imagegen` | 生成或编辑位图图像（照片、插画、纹理、mockup 等） |
| `openai-docs` | Codex 模型/定价、定时任务、skills、设置、故障排查、自动化等自助查询 |
| `plugin-creator` | 生成 Codex 插件目录骨架与 `plugin.json` |
| `review-agent` | 只读、缺陷优先的代码变更审查 |
| `skill-creator` | 创建/更新 Codex skill 及其配套资源 |
| `skill-installer` | 从精选清单或 GitHub 仓库安装 Codex skill |

目录内另有 `.codex-system-skills.marker` 标记文件。

## 目录内非 skill 条目

以下条目位于 `skills/` 根下，不是 skill 目录：

| 条目 | 说明 |
|------|------|
| `.gitignore` | skills 目录的 git 忽略规则 |
| `README.md` | 本文件 |
| `.disable_to_model_invocation_migration.json` | Codex 迁移标记 |
| `.model_invocation_to_override_migration.json` | Codex 迁移标记 |
| `.user_invocable_only_to_off_migration.json` | Codex 迁移标记 |
| `_bm_skillid_migration.json` | SkillsHub 本地元数据（`skills/.gitignore` 排除） |

## 已知重名与命名不一致（加载说明）

以下情况已逐项核对过，属**预期状态**，不是缺陷。列在此处，避免下次审查重复排查。

| 情况 | 说明 | 处置 |
|------|------|------|
| `frontend-design` 重名 | 顶层 `SKILL.md` 是**容器索引**（正文写「This is a skill collection」并列出子技能），`skills/frontend-design/SKILL.md` 才是正文；第三个 `ui-ux-data/` 即 `ui-ux-pro-max` | 保持现状，**加载以顶层为准**；嵌套路径非标准发现路径 |
| `skill-creator` 重名 | `.system/skill-creator` 与顶层 `skills/skill-creator` 同名 | `.system` 由 Codex 内置、随 Junction 分发且被 `.gitignore` 排除，**不改**；创建 / 改进 / 评测 skill 以顶层为准 |
| `fireworks-tech-graph` 重名 | 克隆内含上游发布目录 `skills/fireworks-tech-graph/`，与本体重名，重复 140 文件 / 9.0MB | **预期状态，不动**：该副本是上游跟踪内容（在克隆的 HEAD 中），删除会留下永久脏路径；判定依据见 `.agent_docs/audits/2026-09-24-skills-audit.md` §2.1 |
| `claude-deep-research-skill` 命名不一致 | 目录名与 frontmatter `name: deep-research` 不一致 | **以目录名 `claude-deep-research-skill` 为准**（`agents/analyst.md`、`agents/researcher.md` 均按此引用）；该 skill 是干净克隆，未改 `name:` 以免 `git pull` 冲突 |
| `web-access` 触发声明过宽 | 其 description 声称「所有联网操作必须通过此 skill 处理」，与 `browser-automation` 重叠 | 边界已在**主仓库侧**的 `browser-automation` description 中写明（搜索 / 登录态抓取 / 社交媒体 → `web-access`）；`web-access` 是干净克隆，未改动以免 `git pull` 冲突 |

### 已知功能重叠（保留，未合并）

以下重叠已确认，属**有意保留**：`create-skill` 的能力是 `skill-creator` 的真子集，但保留以维持 `create-hook` / `create-rule` / `create-skill` / `create-subagent` 四件套的对称性；`officecli` 基座与 `officecli-docx/xlsx/pptx` 的触发边界已写入各自 description。完整清单与处置建议见 `.agent_docs/audits/2026-09-24-skills-audit.md`。

## 待恢复项

当前无待恢复项。

`model-architecture-diagram` 曾登记为占位 skill（frontmatter `status: NEEDS_RECOVERY`），2026-09-23 核对时确认**磁盘上已不存在**（全盘搜索无结果），故从清单移除。该技能原本的用途（从代码生成模型架构图）已由 `fireworks-tech-graph` 覆盖，不再单独恢复。

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

### GitHub 克隆的 Skills（7 个）

克隆状态分三类，**不能统一用 `git pull --ff-only`**（2026-09-24 实测）：

| 类别 | 克隆 | 更新方式 |
|------|------|----------|
| 干净 | `claude-deep-research-skill`、`humanizer-zh`、`web-access` | 可直接 `cd ~/.ai-shared/skills/<name> && git pull --ff-only` |
| 仅新增根 `SKILL.md` | `nature-skills`、`superpowers` | 上游顶层无 `SKILL.md`，新增文件不与 pull 冲突；pull 后确认根 `SKILL.md` 仍在，不在则从子目录重建索引 |
| **有本地改动，禁止直接 pull** | `repo-wiki`、`fireworks-tech-graph` | 先备份本地改动再 pull；改动内容见下 |

#### 本地改动的具体内容（更新前必读）

- **`repo-wiki`**：已**展平**——删除了上游跟踪的 `repo-wiki/SKILL.md`，把内容提到克隆根目录（让加载器能在 `skills/repo-wiki/SKILL.md` 找到它）。上游若更新 `repo-wiki/*`，`git pull` 会冲突，或把展平结果改回去。
- **`fireworks-tech-graph`**：含**本地功能扩展**，不是噪声，**被 pull 覆盖会直接丢失**：
  - 改动文件：`scripts/generate-from-template.py`、`CHANGELOG.md`（2 文件 / +31 行）
  - 内容：rect 节点新增可选 `body: [line, ...]` 多行字段，每行渲染为独立的 `data-text-role="body"` 文本行（首选 11.5px / 最小 10.5px），标题 / 副标题 / 正文按 `NODE_LINE_HEIGHT = 17` 整块居中；无 `body` 的节点与上游逐字节一致
  - 动机：架构图源规格常给组件三到六行文字（名称、形状、参数、职责），原 `label` + `sublabel` 两行被迫压缩
  - CHANGELOG 中自标 `Local extension — 2026-09-23 (not upstream)`
  - 契约侧布局必须同步 `NODE_LINE_HEIGHT`，否则按 N 行定高的节点会裁掉最后一行基线
  - 另含 3 个本地新增内容（2026-09-25 合并自原 `fireworks-showcase-layout` skill）：`SKILL.md` 新增
    「Hand-placed coordinates and showcase grade」节与对应 description、`references/showcase-layout.md`、
    `references/fwg_layout.py`（543 行版式模块，`SKILL_ROOT` 已硬编码为本机路径）

> **本机 TLS 注意事项**（2026-09-23 实测）：默认 schannel 后端会因证书吊销服务不可达而报
> `schannel: failed to receive handshake`。改用 openssl 后端并跳过吊销校验即可正常 clone/pull：
>
> ```bash
> GIT_SSL_NO_VERIFY=1 git -c http.sslBackend=openssl clone --depth 1 <url> <dir>
> ```
>
> 若 `git clone` 完全不通，退路是下载 tarball（`codeload.github.com` 可达，用 `curl -L --ssl-no-revoke`），
> 但那样会丢失独立 `.git`，后续无法 `git pull`。

### 主仓库跟踪的 Skills（53 个）

无外部更新源，直接修改即可；改动经 Junction 同步到所有工具目录，并由主仓库统一版本管理。
