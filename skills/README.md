# Skills 目录索引

> 最后更新：2026-10-12（花名册对账完成） | Skills 总数：**28**（顶层 skill 目录，不含 `.system/`）
>
> 计数口径：只统计 `skills\` 的**顶层目录**（**28**），与 `ls skills/` 逐行对应。
>
> 另有 **38 个嵌套子技能**（`nature-skills` 20、`superpowers` 14、`frontend-design` 2、`browser-automation` 2）**不计入本表**——全目录 `SKILL.md` 合计 **66** 个。历史上出现过的「60」「80」等数字均因混用口径所致，现统一按顶层目录计数。
>
> ```bash
> ls -1 skills | grep -vE '^(README\.md|_bm_skillid_migration\.json)$' | wc -l              # 顶层，应为 28
> find skills -name SKILL.md -not -path 'skills/.system/*' | wc -l                        # 全部，应为 66
> find skills -name SKILL.md -not -path 'skills/.system/*' | grep -vcE '^skills/[^/]+/SKILL\.md$'  # 嵌套，应为 38
> ```
>
> 本文件是 skill 花名册的**唯一维护源**；`HARDLINK_INVENTORY.md` 只保留链接治理信息，不重复列举清单。
> **新增或删除 skill 必须同批更新本表**——下方「对账记录」记录了一次长期欠账及其成因。

## Skills 清单

按名称字典序排列，与 `ls skills/` 实测结果逐行核对（`.system/` 与非目录条目除外，见后文）。「来源」列：`GitHub: owner/repo` 为可核验的远端地址（`git -C skills/<name> remote get-url origin`）；已展平、未保留独立 `.git` 的克隆计入「主仓库」。

| # | Skill | 类别 | 说明 | 来源 |
|---|-------|------|------|------|
| 1 | `ai-code-review` | 开发与质量 | AI 生成代码审查：幻觉 API/依赖、安全漏洞、逻辑错误、供应链风险、可维护性 | 主仓库 |
| 2 | `ai-config-sharing` | 环境治理 | 多 AI 工具 skills/agents/AGENTS.md 配置统一管理（Junction + HardLink 单点维护） | 主仓库 |
| 3 | `ai-fast-learning-loop` | 学术科研 | 十步 AI 学习闭环：五视角 STORM → 矛盾图谱 → 综合简报 → 同行评审 → 资源筛选 → 能力阶梯 → 十次课计划 → 分级考试 → 费曼循环 → 一页速查表 | 主仓库 |
| 4 | `ai-output-readability` | 输出表达 | AI 输出可读性四级路由：规范文本（ASD-STE100）→ 图表 → 交互网页 → 讲解视频；含触发条件、提示词模板与反模式 | 主仓库 |
| 5 | `archify` | 绘图可视化 | 架构 / 工作流 / 时序 / 数据流 / 生命周期图：类型化 JSON IR → 可探索单文件 HTML（内联 SVG、深浅主题、可选追踪动效、PNG/JPEG/WebP/SVG/WebM 导出），`finalize` 含真实 Chrome browser-check；可读仓库取证 | 主仓库（来源 GitHub: tt-a1i/archify v3.0.1，已展平） |
| 6 | `arxiv-paper-downloader` | 学术科研 | arXiv 论文批量下载，逐篇用首页标题校验并纠正错误 ID | 主仓库 |
| 7 | `awesome-ai-research-writing` | 学术科研 | 中英双语学术写作工具包：起草、翻译、润色、缩写、扩写、逻辑检查 | 主仓库（社区来源已展平） |
| 8 | `browser-automation` | 浏览器与联网 | 统一浏览器自动化套件：Playwright 网页操作 / Web 应用可复跑 E2E 测试 | 主仓库（多来源合并） |
| 9 | `claude-deep-research-skill` | 学术科研 | 多源深度研究、引用追踪、证据留存、结构化报告 | GitHub: 199-biotechnologies/claude-deep-research-skill |
| 10 | `doc-coauthoring` | 文档与 Office | 文档协作写作工作流：文档、提案、技术规格、决策文档 | 主仓库 |
| 11 | `explainer-video` | 输出表达 | 3b1b 风格讲解视频：脚本 → 程序化动画 → TTS 配音 → 合成 MP4 | 主仓库 |
| 12 | `find-skills` | 工具链 | 场景驱动 + 关键词双模式的技能发现：官方内置 / 本地已安装 / SkillHub / 虾评 / GitHub / ClawHub 六层联合搜索并推荐，支持一键安装（取代官方原 `find-skills` 插件） | 主仓库（SkillsHub 安装，frontmatter `slug: guipi-find-skills`） |
| 13 | `fireworks-tech-graph` | 绘图可视化 | 手写 SVG 技术图：几何安全校验（边交叉/碰撞/标签位置）+ PNG 回读 + GIF 动效；12 种风格、14 类 UML；含 showcase 版式补遗 `references/showcase-layout.md` | GitHub: yizhiyanhua-ai/fireworks-tech-graph |
| 14 | `frontend-design` | 绘图可视化 | 前端视觉设计指导：设计方向、排版、反模板化默认观感（含 50+ 风格库） | 主仓库 |
| 15 | `git-branch-diff-merge` | 开发与质量 | 双分支双向合并融合，冲突取新；AI 只读分析，Git 写操作由用户执行 | 主仓库 |
| 16 | `git-commit` | 开发与质量 | Conventional Commits 规范提交（type/scope/subject） | 主仓库 |
| 17 | `grilling` | 开发与质量 | 用设计树 + 分轮提问把计划 / 决策拷问到没有未决假设：每轮列出当前可问的全部问题并给出推荐答案，事实自行查证、决策交用户裁决 | 主仓库 |
| 18 | `humanizer-zh` | 学术科研 | 中文去 AI 味写作助手：检测并修复 AI 写作特征模式 | GitHub: op7418/Humanizer-zh |
| 19 | `kaggle-modularize` | 开发与质量 | 单体 `.ipynb` ↔ Python 模块双向拆分 / 合并 | 主仓库 |
| 20 | `kaggle-notebook-to-cloud-jupyter` | 开发与质量 | Kaggle notebook 迁移到云 GPU JupyterLab：单源参数化、两级存储、依赖安装 | 主仓库 |
| 21 | `markitdown` | 文档与 Office | 多格式文档转 Markdown：PDF / Office / 图片 / 音频 / HTML / CSV / EPUB / ZIP / URL | 主仓库 |
| 22 | `mermaid-master` | 绘图可视化 | Mermaid 技术文档图表：流程图、架构图、时序图、状态图、ER 图、甘特图 | 主仓库 |
| 23 | `multi-agent` | 开发与质量 | 多代理任务规划与可审计的子代理任务简报生成 | 主仓库 |
| 24 | `nature-skills` | 学术科研 | Nature 级学术工作流：写作、引用、绘图、检索、统计、润色、审稿回复 | GitHub: Yuan1z0825/nature-skills |
| 25 | `repo-wiki` | 文档与 Office | 生成完整多页项目 Wiki（含内置模板，输出语言跟随提问语言） | GitHub: devin2255/repo-wiki-skill |
| 26 | `superpowers` | 开发与质量 | 开发流程技能库：头脑风暴、系统化调试、TDD、计划编写、代码审查等 | GitHub: obra/superpowers |
| 27 | `web-access` | 浏览器与联网 | 统一联网操作：搜索、网页抓取、登录后操作、动态渲染页面 | GitHub: eze-is/web-access |
| 28 | `workbuddy-auto-credits` | 工具链 | WorkBuddy 自动领积分：每日签到 + 派猫猫旅行 | 主仓库 |

### 来源分类小结

| 来源 | 数量 | 说明 |
|------|------|------|
| GitHub 克隆 | 7 | 各自保留独立 `.git`，由主仓库 `.gitignore` 排除，整体不入库 |
| 主仓库跟踪 | 21 | 由 `.ai-shared` 主仓库直接版本管理（含已展平的社区 / SkillsHub 来源） |

### 类别分布

| 类别 | 数量 |
|------|------|
| 开发与质量 | 8 |
| 学术科研 | 6 |
| 绘图可视化 | 4 |
| 文档与 Office | 3 |
| 工具链 | 2 |
| 浏览器与联网 | 2 |
| 输出表达 | 2 |
| 环境治理 | 1 |

## 对账记录（2026-10-12 完成）

结果：花名册 **28** 行 = 磁盘 **28** 个顶层 skill 目录；三条复核命令均命中预期值。

本次修正：

- **删除 17 行**「登记了但磁盘不存在」的历史条目——**经用户确认是其手动删除**，不是丢失，因此不列为待恢复项：`canvas`、`code-to-interview-docs`、`feishu-job-import`、`migrate-to-skills`、`morph-ppt`、`morph-ppt-3d`、`officecli` 及其 8 个变体（`-academic-paper`、`-data-dashboard`、`-docx`、`-financial-model`、`-pitch-deck`、`-pptx`、`-word-form`、`-xlsx`）、`resume-tech-interview-decompose`、顶层 `skill-creator`。
- **补登记 2 项**此前漏登的：`find-skills`、`grilling`。
- **新增 1 项**：`archify`（替换 `project-chain-atlas`，边界见「已知功能重叠」）。
- **悬空引用检查**：全仓 grep 上述 17 个名字，除本文件自身的登记行外无命中；尤其 `agents/*.md` 的 Skills 路由表未引用它们。`project-chain-atlas` 仅在其自身目录内自引用，已随目录一并移入 `.trash`。
- **同批发现**：`fireworks-tech-graph` 克隆内被上游跟踪的嵌套副本（`skills/fireworks-tech-graph/`，140 文件）在本地工作区**已被删除且未提交**，本表旧文「重复 140 文件 / 9.0MB」已失效，按现状改写（见「已知重名」）。另：本表此前引用的 `.agent_docs/audits/2026-09-24-skills-audit.md` 在磁盘上不存在，属悬空引用，本次一并清除。

欠账成因：手动删除 skill 后未同批更新本表，而本表此前长期只增不删。**此后删除 skill 必须同批删行**；批量核对走 `ai-config-sharing` 的「清单盘点：花名册与实测目录对账」三步法。

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
| `skill-creator` | 顶层 `skills/skill-creator` 已于 2026-10-12 随用户手动删除一并移除登记；现存仅 `.system/skill-creator` | 创建 / 改进 / 评测 skill 走 `.system/skill-creator`（Codex 内置，随 Junction 分发且被 `.gitignore` 排除，**不改**） |
| `fireworks-tech-graph` 克隆内的上游发布副本 | 上游 HEAD 跟踪嵌套目录 `skills/fireworks-tech-graph/`（140 文件）；本地工作区**已删除**该副本（未提交，`git status` 显示 140 个 `D`） | **保持删除**：它是上游发布包，与本体重名且不是发现路径（加载只认顶层 `skills/fireworks-tech-graph/SKILL.md`）。`git pull` 会把它恢复，属预期——恢复后按需再删，不影响加载 |
| `claude-deep-research-skill` 命名不一致 | 目录名与 frontmatter `name: deep-research` 不一致 | **以目录名 `claude-deep-research-skill` 为准**（`agents/analyst.md`、`agents/researcher.md` 均按此引用）；该 skill 是干净克隆，未改 `name:` 以免 `git pull` 冲突 |
| `web-access` 触发声明过宽 | 其 description 声称「所有联网操作必须通过此 skill 处理」，与 `browser-automation` 重叠 | 边界已在**主仓库侧**的 `browser-automation` description 中写明（搜索 / 登录态抓取 / 社交媒体 → `web-access`）；`web-access` 是干净克隆，未改动以免 `git pull` 冲突 |

### 已知功能重叠（保留，未合并）

`ai-output-readability` 与 `mermaid-master` / `archify` / `fireworks-tech-graph` / `explainer-video` 是**路由与执行的分工**：前者只决定「该用哪一级表达」，具体画图 / 出视频交给后者，不重复定义绘图规则。

绘图类的边界（2026-10-12 补充）：需要交互探索、多格式导出，且要求「读仓库取证 + 自动校验」的架构 / 流程 / 时序 / 数据流 / 生命周期图 → `archify`；单张手绘 SVG 且要几何安全校验 → `fireworks-tech-graph`；文档内嵌 Mermaid 源码 → `mermaid-master`。`project-chain-atlas`（代码库可点击链路手册）已于 2026-10-12 移除，其用途由 `archify` 承接。

## 待恢复项

当前无待恢复项。2026-10-12 对账确认：此前 17 行登记属用户手动删除，不构成待恢复项。

`model-architecture-diagram` 曾登记为占位 skill（frontmatter `status: NEEDS_RECOVERY`），2026-09-23 核对时确认磁盘上已不存在（全盘搜索无结果），故从清单移除。该技能原本的用途（从代码生成模型架构图）已由 `fireworks-tech-graph` 与 `archify` 覆盖，不再单独恢复。

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
└── .agents\skills\       ──Junction──→ .ai-shared\skills\
```

> `.catpawai`（CatPaw AI）已被用户删除并决定不再保留，其 `skills\` 联接与 `agents\` 联接一并移除。若日后重新纳入 CatPaw，按 `HARDLINK_INVENTORY.md` §八「新增 AI 工具目录」重建。

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
- **`fireworks-tech-graph`**：含**本地功能扩展**，不是噪声，**被 pull 覆盖会直接丢失**；本地还删除了上游跟踪的嵌套副本 `skills/fireworks-tech-graph/`（140 文件，未提交），pull 会一并恢复：
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

### 主仓库跟踪的 Skills（21 个）

无外部更新源，直接修改即可；改动经 Junction 同步到所有工具目录，并由主仓库统一版本管理。

其中 `archify` 的原版来自 `github.com/tt-a1i/archify`（v3.0.1，已展平为顶层 skill 且未保留 `.git`）。需要跟随上游时按官方方式取材：

```bash
npx -y skills add tt-a1i/archify --list --full-depth   # 先确认源内技能数与名字（应恰为 1 个 archify）
npx -y skills add tt-a1i/archify --skill archify --agent cursor --global --copy --yes
```

> 本机注意（2026-10-12 实测）：IDE 给 Node 注入了 `node-language-shim.cjs`（经 `NODE_OPTIONS`），
> 会让 archify 的原子写入判定 `nlink` 异常，`finalize` 直接报
> `finalize-receipt-hardlinked` 之类的假失败。跑 archify 前先清空该环境变量：
> PowerShell 用 `$env:NODE_OPTIONS=''`。
