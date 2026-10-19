# Skills 目录索引

> 最后更新：2026-10-19（新增主仓库 skill `mechanism-explainer`，内容来自 `AGENTS.md` §10 的抽离） | Skills 总数：**24**（顶层 skill 目录，不含 `.system/`）
>
> 计数口径：只统计 `skills\` 的**顶层目录**（**24**），与 `ls skills/` 逐行对应。
>
> 另有 **19 个嵌套子技能**（`superpowers` 15、`frontend-design` 2、`browser-automation` 2）**不计入本表**——全目录 `SKILL.md` 合计 **43** 个。历史上出现过的「60」「80」等数字均因混用口径所致，现统一按顶层目录计数。
>
> **2026-10-16 变更**：6 个「学术科研」类 skill（`ai-fast-learning-loop`、`arxiv-paper-downloader`、`awesome-ai-research-writing`、`claude-deep-research-skill`、`humanizer-zh`、`nature-skills`）已移出本目录，归集到独立科研库 `C:\Users\20448\research-skills\`（不在本 Junction 分发范围内，工具不再自动发现）；其中 `claude-deep-research-skill` 因被更强的 `academic-research-skills/deep-research` 替代而删除（备份于 `.trash/research-dedup-2026-10-16/`）。本目录不再有「学术科研」类别。
>
> ```bash
> ls -1 skills | grep -vE '^(README\.md|_bm_skillid_migration\.json)$' | wc -l              # 顶层，应为 24
> find skills -name SKILL.md -not -path 'skills/.system/*' | wc -l                        # 全部，应为 43
> find skills -name SKILL.md -not -path 'skills/.system/*' | grep -vcE '^skills/[^/]+/SKILL\.md$'  # 嵌套，应为 19
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
| 3 | `ai-output-readability` | 输出表达 | AI 输出可读性四级路由：规范文本（ASD-STE100）→ 图表 → 交互网页 → 讲解视频；含触发条件、提示词模板与反模式 | 主仓库 |
| 4 | `anatomy` | 绘图可视化 | 把抽象技术概念翻译成真实可运转的等距机械装置图：SVG / SVG+WebGL 着色器 / 3D（beta）三档，含几何审计（穿模、端点在支座、深度顺序）与无头 Chrome 截图自检 | GitHub: wheresryan22/anatomy（MIT，约 13.7k★，克隆未展平） |
| 5 | `archify` | 绘图可视化 | 架构 / 工作流 / 时序 / 数据流 / 生命周期图：类型化 JSON IR → 可探索单文件 HTML（内联 SVG、深浅主题、可选追踪动效、PNG/JPEG/WebP/SVG/WebM 导出），`finalize` 含真实 Chrome browser-check；可读仓库取证 | GitHub: tt-a1i/archify v3.1.0（83k★，已展平 + 本地扩展） |
| 6 | `browser-automation` | 浏览器与联网 | 统一浏览器自动化套件：Playwright 网页操作 / Web 应用可复跑 E2E 测试 | 主仓库（多来源合并：`playwright/` 来自 microsoft/playwright-cli 14k★ 并本地改写为 `npx playwright cli`；`webapp-testing/` 来自 anthropics/skills） |
| 7 | `doc-coauthoring` | 文档与 Office | 文档协作写作工作流：文档、提案、技术规格、决策文档 | GitHub: anthropics/skills（181k★，已展平） |
| 8 | `explainer-video` | 输出表达 | 3b1b 风格讲解视频：脚本 → 程序化动画 → TTS 配音 → 合成 MP4 | 主仓库 |
| 9 | `find-skills` | 工具链 | 场景驱动 + 关键词双模式的技能发现：官方内置 / 本地已安装 / SkillHub / 虾评 / GitHub / ClawHub 六层联合搜索并推荐，支持一键安装（取代官方原 `find-skills` 插件） | 主仓库（SkillsHub 安装；上游 GitHub: guipi888/find-skills，0★，本地为增强版，见「上游更新记录」） |
| 10 | `fireworks-tech-graph` | 绘图可视化 | 手写 SVG 技术图：几何安全校验（边交叉/碰撞/标签位置）+ PNG 回读 + GIF 动效；12 种风格、14 类 UML；含 showcase 版式补遗 `references/showcase-layout.md` | GitHub: yizhiyanhua-ai/fireworks-tech-graph |
| 11 | `frontend-design` | 绘图可视化 | 前端视觉设计指导：设计方向、排版、反模板化默认观感（含 50+ 风格库） | GitHub: anthropics/skills（181k★，正文）+ 本地 `ui-ux-data/` 设计数据库合并 |
| 12 | `git-branch-diff-merge` | 开发与质量 | 双分支双向合并融合，冲突取新；AI 只读分析，Git 写操作由用户执行 | 主仓库 |
| 13 | `git-commit` | 开发与质量 | Conventional Commits 规范提交（type/scope/subject） | 主仓库 |
| 14 | `grilling` | 开发与质量 | 用设计树 + 分轮提问把计划 / 决策拷问到没有未决假设：每轮列出当前可问的全部问题并给出推荐答案，事实自行查证、决策交用户裁决 | 主仓库 |
| 15 | `kaggle-modularize` | 开发与质量 | 单体 `.ipynb` ↔ Python 模块双向拆分 / 合并 | 主仓库 |
| 16 | `kaggle-notebook-to-cloud-jupyter` | 开发与质量 | Kaggle notebook 迁移到云 GPU JupyterLab：单源参数化、两级存储、依赖安装 | 主仓库 |
| 17 | `markitdown` | 文档与 Office | 多格式文档转 Markdown：PDF / Office / 图片 / 音频 / HTML / CSV / EPUB / ZIP / URL | GitHub: microsoft/markitdown（190k★，v0.1.8 展平 + 本地 SKILL.md） |
| 18 | `mechanism-explainer` | 输出表达 | 理解类提问的回答契约：骨架先行 + 八项输出结构（定位 / 术语 / 时序 / 数据形态 / 失效矩阵 / 取舍 / 证据 / 自检）+ 多轮纠错纪律；原 `AGENTS.md` §10 全文抽离为本体 | 主仓库 |
| 19 | `mermaid-master` | 绘图可视化 | Mermaid 技术文档图表：流程图、架构图、时序图、状态图、ER 图、甘特图 | 主仓库 |
| 20 | `multi-agent` | 开发与质量 | 多代理任务规划与可审计的子代理任务简报生成 | 主仓库 |
| 21 | `repo-wiki` | 文档与 Office | 生成完整多页项目 Wiki（含内置模板，输出语言跟随提问语言） | GitHub: devin2255/repo-wiki-skill |
| 22 | `superpowers` | 开发与质量 | 开发流程技能库：头脑风暴、系统化调试、TDD、计划编写、代码审查等 | GitHub: obra/superpowers |
| 23 | `web-access` | 浏览器与联网 | 统一联网操作：搜索、网页抓取、登录后操作、动态渲染页面 | GitHub: eze-is/web-access |
| 24 | `workbuddy-auto-credits` | 工具链 | WorkBuddy 自动领积分：每日签到 + 派猫猫旅行 | 主仓库 |

### 来源分类小结

| 来源 | 数量 | 说明 |
|------|------|------|
| GitHub 克隆 | 5 | 各自保留独立 `.git`，由主仓库 `.gitignore` 排除，整体不入库（`anatomy`、`fireworks-tech-graph`、`repo-wiki`、`superpowers`、`web-access`） |
| 主仓库跟踪 | 19 | 由 `.ai-shared` 主仓库直接版本管理。其中 5 个有已核实的上游仓库但**未保留 `.git`**（展平 / 合并安装）：`markitdown`、`frontend-design`、`doc-coauthoring`、`find-skills`，以及 `browser-automation` 的两个子技能（`playwright/`、`webapp-testing/`）；更新方式见「上游更新记录（2026-10-15）」 |

### 类别分布

| 类别 | 数量 |
|------|------|
| 开发与质量 | 8 |
| 绘图可视化 | 5 |
| 文档与 Office | 3 |
| 工具链 | 2 |
| 浏览器与联网 | 2 |
| 输出表达 | 3 |
| 环境治理 | 1 |

> 「学术科研」类（原 6 个）已于 2026-10-16 全部迁出到独立科研库 `C:\Users\20448\research-skills\`。

## 对账记录（2026-10-12 完成）

结果：花名册 **28** 行 = 磁盘 **28** 个顶层 skill 目录；三条复核命令均命中预期值。

本次修正：

- **删除 17 行**「登记了但磁盘不存在」的历史条目——**经用户确认是其手动删除**，不是丢失，因此不列为待恢复项：`canvas`、`code-to-interview-docs`、`feishu-job-import`、`migrate-to-skills`、`morph-ppt`、`morph-ppt-3d`、`officecli` 及其 8 个变体（`-academic-paper`、`-data-dashboard`、`-docx`、`-financial-model`、`-pitch-deck`、`-pptx`、`-word-form`、`-xlsx`）、`resume-tech-interview-decompose`、顶层 `skill-creator`。
- **补登记 2 项**此前漏登的：`find-skills`、`grilling`。
- **新增 1 项**：`archify`（替换 `project-chain-atlas`，边界见「已知功能重叠」）。
- **悬空引用检查**：全仓 grep 上述 17 个名字，除本文件自身的登记行外无命中；尤其 `agents/*.md` 的 Skills 路由表未引用它们。`project-chain-atlas` 仅在其自身目录内自引用，已随目录一并移入 `.trash`。
- **同批发现**：`fireworks-tech-graph` 克隆内被上游跟踪的嵌套副本（`skills/fireworks-tech-graph/`，140 文件）在本地工作区**已被删除且未提交**，本表旧文「重复 140 文件 / 9.0MB」已失效，按现状改写（见「已知重名」）。另：本表此前引用的 `.agent_docs/audits/2026-09-24-skills-audit.md` 在磁盘上不存在，属悬空引用，本次一并清除。

欠账成因：手动删除 skill 后未同批更新本表，而本表此前长期只增不删。**此后删除 skill 必须同批删行**；批量核对走 `ai-config-sharing` 的「清单盘点：花名册与实测目录对账」三步法。

## 对账记录（2026-10-16，科研类 skill 迁出）

结果：花名册 **22** 行 = 磁盘 **22** 个顶层 skill 目录；复核命令命中预期值。

- **迁出 6 个「学术科研」类 skill** 到独立科研库 `C:\Users\20448\research-skills\`（用户裁决：新建独立库、不破坏 Junction，工具不再自动发现）：`ai-fast-learning-loop`、`arxiv-paper-downloader`、`awesome-ai-research-writing`、`humanizer-zh`、`nature-skills`。
- **`claude-deep-research-skill` 属去重删除**（未随迁）：与科研库内 `academic-research-skills/deep-research`（13-agent / 8 模式 / 含系统综述与元分析）功能重复且方法更弱，已移入 `.trash/research-dedup-2026-10-16/`。
- **悬空引用同步**：`agents/analyst.md`、`agents/analyst.toml`、`agents/researcher.md`、`agents/researcher.toml` 中 `deep-research` 的路由已改指科研库路径（绝对路径）。`skills/ai-config-sharing` 内的历史注释按原样保留。
- 复核命令：`ls -1 skills | grep -vE '^(README\.md|_bm_skillid_migration\.json)$' | wc -l` 应为 **22**。

## 对账记录（2026-10-17，新增 anatomy）

结果：花名册 **23** 行 = 磁盘 **23** 个顶层 skill 目录；复核命令命中预期值。

- **新增 1 个 skill**：`anatomy`——GitHub 克隆 `wheresryan22/anatomy`（MIT，约 13.7k★，153 文件 / 11.7 MB，保留独立 `.git` 未展平）。归入「绘图可视化」类。
- **主仓库侧同步**：`.gitignore` 新增 `skills/anatomy/`，与其余克隆一致整体不入库。
- 计数影响：顶层 22 → **23**；全部 `SKILL.md` 41 → **42**（嵌套 19 不变）；GitHub 克隆 4 → **5**；主仓库跟踪 **18** 不变。
- 悬空引用：本次为**新增**，无需清理；`agents/*.md` 路由表未引用绘图类 skill，无需同步。

## 对账记录（2026-10-19，新增 mechanism-explainer）

结果：花名册 **24** 行 = 磁盘 **24** 个顶层 skill 目录；复核命令命中预期值。

- **新增 1 个 skill**：`mechanism-explainer`——由 `AGENTS.md` §10「机制解释规范」全文抽离而成（用户要求：正文不再堆在规则文件里）。归入「输出表达」类。
- **唯一维护源转移**：八项输出契约、失效矩阵样例、多轮纪律的正文移入 `skills/mechanism-explainer/SKILL.md`；`AGENTS.md` §10 只留「骨架先行 + 证据优先」两条硬底线与路由指针；两处 `.mdc` 用户级规则（`C:\Users\20448\.codebuddy\rules\agents.md.mdc`）同步为摘要 + 指针，避免与 skill 双份维护。
- 同源改动：`AGENTS.md` §2 新增「提问必须走工具的提问」（`AskUserQuestion` / `ask_followup_question`），同步写入用户级 `.mdc`。
- 悬空引用：`skills/ai-output-readability` 的 Level 1 已加反向指针；全仓 grep `机制解释规范` / `八项输出契约` 现仅命中 `skills/mechanism-explainer/SKILL.md`。
- 计数影响：顶层 23 → **24**；全部 `SKILL.md` 42 → **43**（嵌套 19 不变）；GitHub 克隆 **5** 不变；主仓库跟踪 18 → **19**；「输出表达」2 → **3**。

## 上游更新记录（2026-10-14）

对 7 个 GitHub 克隆逐个人工 `git fetch` 比对后，按三类处置：

| Skill | 结果 | 说明 |
|-------|------|------|
| `humanizer-zh` | 91f3d39 → f4518a8（+1） | 干净克隆，直接 `pull --ff-only` |
| `web-access` | 33eef84 → d173a75（+26） | 干净克隆，直接 `pull --ff-only`；上游打 tag v2.6.0 |
| `nature-skills` | bd4e415 → 19be8d4（+100） | 本地仅新增根 `SKILL.md`（未跟踪），与 incoming 无交集，ff 安全；上游新增子技能 `nature-paper-trans`、`nature-paper-xray`、`nature-social-science`，已补登根索引 |
| `superpowers` | b36e082 → bb92a77（+3） | 同上；上游发版 v7.0.0（rebuilt brainstorming、Antigravity manifest、Windows hook fixes），新增子技能 `diagnosing-superpowers`，已补登根索引 |
| `claude-deep-research-skill` | 已是最新（f2f2c0f） | 无操作 |
| `repo-wiki` | 已是最新（c9adbfc） | 展平改动（删 `repo-wiki/*`、根目录重建）原样保留，上游无新提交故无冲突 |
| `fireworks-tech-graph` | 已是最新（31fea36） | 本地功能扩展（`body` 多行字段 + showcase 版式）与嵌套副本删除原样保留，上游无新提交故无冲突 |

pull 前后均确认：四个更新克隆的本地未提交改动（根 `SKILL.md`）未被覆盖，`repo-wiki` / `fireworks-tech-graph` 未执行 pull。本机 TLS 仍需 `http.sslBackend=openssl` + `GIT_SSL_NO_VERIFY=1`。

## 上游更新记录（2026-10-15，无 `.git` 的 skills）

对 21 个非克隆 skill 逐个做上游取证（本地 URL/署名文件 → GitHub 仓库核实 → 星数与活跃度 → 内容 diff），只从**规范高星仓库**更新，避免认错来源：

| Skill | 上游（星数） | 结果 |
|-------|-------------|------|
| `markitdown` | microsoft/markitdown（190k★） | **已更新** 0.1.6b2 → v0.1.8：同步 98 个变更文件 + 20 个新文件；本地新增的根 `SKILL.md` 保留（上游无此文件）；`compileall` 通过 |
| `frontend-design` | anthropics/skills（181k★） | **已更新**正文到上游 2026-09-03 版（#1713「avoid generic design defaults」）；本地合并的 `ui-ux-data/` 数据库小节已重新追加到正文末尾 |
| `archify` | tt-a1i/archify（83k★） | **已更新** v3.0.1 → v3.1.0（用户要求不全量下载）：下载 v3.1.0 release zip（展平 skill 包），SHA256 比对后只复制 65 个变更 + 51 个新增文件；4 处本地扩展补丁已在 v3.1.0 上重新套用（`LOCAL_CHANGES.md` 同步改基线）；删除被新版取代的孤儿 `renderers/lifecycle/grid-routing.mjs`；`doctor` 全绿（含新增 erd/class/tree/timeline/waterfall 五种渲染器）；`test/` 与 `generate-*.mjs` 为本地保留的开发件，未动 |
| `doc-coauthoring` | anthropics/skills（181k★） | 已是最新（与上游逐字节一致） |
| `webapp-testing`（`browser-automation/` 内） | anthropics/skills（181k★） | 已是最新（一致） |
| `awesome-ai-research-writing` | zengrong233/awesome-ai-research-writing-skill（76★） | 已是最新（仅 `.openskills.json` 为本地元数据） |
| `find-skills` | guipi888/find-skills（0★） | **不更新**：上游 master 与本地同为 v1.7.0，但本地是 SkillsHub 安装 + 实测增强版（score 判读表、fallback 来源、客户端检测）；上游 master 反而更简且新增了引流广告段。从上游覆盖会丢本地内容 |
| `playwright`（`browser-automation/` 内） | microsoft/playwright-cli（14k★） | **不更新**：本地是刻意改写版——目标为 Playwright 内置 `npx playwright cli`（≥1.62）+ 包装脚本，上游 SKILL.md 面向独立的 `playwright-cli` 包，覆盖即成退化 |
| `mermaid-master` | — | **无有效上游**：GitHub 无同名高星仓库（唯一同名仓库 0 星且无关），按主仓库 skill 维护 |

其余非克隆 skill（`ai-code-review`、`ai-config-sharing`、`ai-fast-learning-loop`、`ai-output-readability`、`arxiv-paper-downloader`、`explainer-video`、`git-branch-diff-merge`、`git-commit`、`grilling`、`kaggle-modularize`、`kaggle-notebook-to-cloud-jupyter`、`mechanism-explainer`、`multi-agent`、`workbuddy-auto-credits`）经 GitHub 搜索未找到可确认的高星上游，按主仓库 skill 维护。

> 该记录截止 2026-10-15；此后新增的主仓库 skill（如 `mechanism-explainer`）为本地自建，同样按主仓库维护。

**方法备注**：`archify` 的「精准更新」模式（release zip + 哈希比对 + 补丁重放）可作为其他「已展平 + 有本地补丁」skill 的更新范式；`test/` 等开发件不同步是已知限制。

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
| ~~`claude-deep-research-skill` 命名不一致~~ | 该 skill 已于 2026-10-16 去重删除并迁出本目录 | 不再适用（备份于 `.trash/research-dedup-2026-10-16/`）；现由科研库 `academic-research-skills/deep-research` 承接 |
| `web-access` 触发声明过宽 | 其 description 声称「所有联网操作必须通过此 skill 处理」，与 `browser-automation` 重叠 | 边界已在**主仓库侧**的 `browser-automation` description 中写明（搜索 / 登录态抓取 / 社交媒体 → `web-access`）；`web-access` 是干净克隆，未改动以免 `git pull` 冲突 |

### 已知功能重叠（保留，未合并）

`ai-output-readability` 与 `mermaid-master` / `archify` / `fireworks-tech-graph` / `explainer-video` 是**路由与执行的分工**：前者只决定「该用哪一级表达」，具体画图 / 出视频交给后者，不重复定义绘图规则。

`mechanism-explainer` 与上述关系同上：**内容结构（答什么、按什么顺序答）归它，载体级别（图 / 网页 / 视频）归 `ai-output-readability`**。理解类提问先过 `mechanism-explainer` 定结构，再按 `ai-output-readability` 选载体；两者互为单向引用（`ai-output-readability` 的 Level 1 指向它），不互相复制正文。

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

### GitHub 克隆的 Skills（5 个）

克隆状态分三类，**不能统一用 `git pull --ff-only`**（2026-09-24 实测）：

| 类别 | 克隆 | 更新方式 |
|------|------|----------|
| 干净 | `web-access`、`anatomy` | 可直接 `cd ~/.ai-shared/skills/<name> && git pull --ff-only` |
| 仅新增根 `SKILL.md` | `superpowers` | 上游顶层无 `SKILL.md`，新增文件不与 pull 冲突；pull 后确认根 `SKILL.md` 仍在，不在则从子目录重建索引 |
| **有本地改动，禁止直接 pull** | `repo-wiki`、`fireworks-tech-graph` | 先备份本地改动再 pull；改动内容见下 |

> 原克隆 `claude-deep-research-skill`、`humanizer-zh`、`nature-skills` 已于 2026-10-16 迁出本目录：`claude-deep-research-skill` 按去重删除；`humanizer-zh`、`nature-skills` 移入科研库 `C:\Users\20448\research-skills\`，更新方法随迁。

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

### 主仓库跟踪的 Skills（18 个）

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
