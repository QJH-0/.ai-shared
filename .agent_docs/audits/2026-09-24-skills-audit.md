# Skills 审查报告

> 生成时间：2026-09-24T19:20+08:00
> 审查范围：`skills/` 全部 60 个顶层 skill 目录 + `.system/` 6 个，共 105 个 `SKILL.md`
> 审查方法：① frontmatter `name:` 全库重名扫描 ② 目录名 vs `name` 一致性 ③ 描述聚类找功能重叠 ④ **逐组读正文确认**（避免只看描述误判）⑤ 悬空引用扫描 ⑥ 体积分布
> 结论口径：`确认` = 有直接证据；`疑似` = 描述高度重叠但未逐行比对正文

---

## 一、结论速览

| 判定 | 数量 | 条目 |
|---|---|---|
| **确认重复 → 建议删除** | 1 | `fireworks-tech-graph/skills/fireworks-tech-graph/`（内嵌副本，140 文件 / 9.0MB） |
| **高度重叠 → 建议合并或删除** | 2 | `create-skill`（被 `skill-creator` 完全覆盖）、`officecli`（基座，与 `officecli-docx/xlsx/pptx` 抢触发） |
| **触发边界冲突 → 建议更新 description** | 4 组 | `web-access` ↔ `browser-automation`；`officecli` ↔ `officecli-*`；`ai-code-review` ↔ `review*`；`loop` ↔ `automate` |
| **命名/一致性缺陷 → 建议更新** | 1 | `claude-deep-research-skill`（目录名与 `name:` 不一致） |
| **看着像重复、实为设计 → 不要动** | 4 | `review`（路由器）、`frontend-design`（容器）、`morph-ppt-3d`（显式扩展）、`nature-skills`（合集） |
| **悬空 skill 引用** | 0 | — |

---

## 二、确认重复（有直接证据）

### 2.1 `fireworks-tech-graph` 内嵌完整副本 ★ 唯一确认的重复

| 项 | 值 |
|---|---|
| 父目录 | `skills/fireworks-tech-graph/` — 190 文件，26MB |
| 内嵌副本 | `skills/fireworks-tech-graph/skills/fireworks-tech-graph/` — 140 文件，9.0MB |
| 证据 | 两者 `SKILL.md` **md5 完全相同**（`4858521086`，均 99 行 / 5757B）；`diff -rq` 全量比对仅 12 条差异，且差异都是「父目录多出的仓库级文件」（`.github/`、`index.html`、`tools/`、`site.webmanifest` 等），另有 2 个文件版本不同（`CHANGELOG.md`、`scripts/generate-from-template.py`） |
| 性质 | 上游仓库的发布布局（`skills/<name>/` 是打包目录），克隆根恰好也有一份同级内容 |

**影响**：① 9.0MB 冗余；② 两个 `SKILL.md` 的 `name:` 都是 `fireworks-tech-graph`，构成重名冲突（见 §五）。

**处置方案（三选一）**：

| 方案 | 做法 | 代价 |
|---|---|---|
| **A（推荐）** | 保持克隆原样，在 `skills/README.md` 记为「预期豁免」：该 skill 克隆内含上游打包目录，与本体重名，不参与加载 | 无副作用；冗余仍占 9MB |
| B | 删除 `skills/fireworks-tech-graph/skills/` | 该目录在上游仓库里，`git pull` 会拉回，需每次重删 |
| C | 把克隆挪到 `skills/` 之外（如 `.ai-shared/vendor/`），只把内层内容作为 skill | 彻底消除重复，但改动大、要重建 Junction 验证 |

> 注：该 skill 由主仓库 `.gitignore` 整体排除，**删除不影响主仓库版本管理**，只影响本地克隆与 `git pull` 工作流。

---

## 三、高度重叠（建议合并或删除）

### 3.1 `create-skill` 与 `skill-creator`（`确认` 能力子集关系）

| Skill | 体量 | 覆盖能力 |
|---|---|---|
| `skills/create-skill/` | 504 行 / 14KB | 创建新 skill、`SKILL.md` 结构、元数据字段、description 写法 |
| `skills/skill-creator/` | 485 行 / 33KB | 创建 **+ 修改改进 + 评测（eval / 方差分析）+ description 触发率优化** |
| `skills/.system/skill-creator/` | 229 行 / 15KB | Codex 内置（vendor 管理，**不动**） |

`create-skill` 的能力是 `skill-creator` 的**真子集**，且无外部引用（`AGENTS.md`、`agents/` 均未引用）。

**建议**：删除 `skills/create-skill/`，把其独有的「目录布局 / 存储位置」小节并入 `skill-creator`。
**保留顾虑**：它是 `create-hook` / `create-rule` / `create-skill` / `create-subagent` 四件套之一，删掉会破坏家族对称性——若更看重对称性，可保留但**必须**在 description 里写明「仅讲 SKILL.md 结构，创建/改进/评测请用 skill-creator」以消除抢触发。

### 3.2 `officecli` 基座 与 `officecli-docx/xlsx/pptx`（`确认` 触发重叠）

| Skill | 体量 | description 的触发条件 |
|---|---|---|
| `officecli` | 417 行 / 26KB | 「Create, analyze, proofread, and modify Office documents (.docx, .xlsx, .pptx)」 |
| `officecli-docx` | 572 行 / 45KB | 「**any time a .docx file is involved** — as input, output, or both」 |
| `officecli-xlsx` | 496 行 / 36KB | 「**any time a .xlsx file is involved**」 |
| `officecli-pptx` | 568 行 / 45KB | 「**any time a .pptx file is involved**」 |

两边对同一个 `.docx` 任务**都会命中**。已确认 `officecli` 基座正文**不引用** `officecli-docx/xlsx/pptx`（不是路由器），而是独立覆盖同一领域的实现——属实质重叠。

**建议**：不删（四份都内容厚实、各有独立价值），但**必须划边界**：
- `officecli` → 收窄为「CLI 工具本身的使用 / 安装 / 排障 / 跨格式批处理」
- `officecli-docx/xlsx/pptx` → 保留「单格式文档的创作与编辑」

> 另有 5 个领域变体（`officecli-academic-paper` / `-data-dashboard` / `-financial-model` / `-pitch-deck` / `-word-form`），它们与上述四份的关系是「领域配方 vs 通用能力」，重叠可接受，**不动**。

---

## 四、触发边界冲突（建议更新 description）

| 组 | 冲突点 | 建议 |
|---|---|---|
| `web-access` ↔ `browser-automation` | 前者声称「**所有联网操作必须通过此 skill 处理**」，后者声称「统一的浏览器自动化套件」并含网页抓取——同一句用户话两边都命中 | 二者职责二选一或明确分工：`web-access`（第三方，v2.5.4）偏「搜索 / 登录态抓取 / 社交媒体」，`browser-automation` 偏「可复跑 E2E / 需托管被测服务器」；在 description 里互相排除 |
| `ai-code-review` ↔ `review` / `review-bugbot` / `review-security` | 前四者都触发于「审查代码改动」 | `ai-code-review`（202 行，方法论）→ 保留为 AI 生成代码专项审查；`review-*` 是子代理调用入口（52 行 ×2）；`review` 是斜杠命令菜单。建议在 `ai-code-review` description 里写明「不用于子代理审查入口」 |
| `loop` ↔ `automate` | 前者「按周期重复跑 prompt / skill」，后者「创建 Codex Automations」——都触发于「定时 / 定期执行」 | `loop` = 会话内临时循环；`automate` = 持久化自动化。建议各自 description 加排除语 |
| `code-to-interview-docs` ↔ `resume-tech-interview-decompose` | 都产出「面试准备文档」 | 前者输入是**项目代码**、后者输入是**简历技术点**，边界清楚，但 description 都没写明输入源。建议补一句输入源限定 |

**轻度重叠（可暂不处理）**：`plan-premise-verification` ↔ `framework-migration-verification`（都是「先核实前提是否成立」，但域不同）；`doc-coauthoring` ↔ `awesome-ai-research-writing` ↔ `humanizer-zh`（`awesome-ai-research-writing` 的 description 明确含 humanize，与 `humanizer-zh` 重叠）；`multi-agent` ↔ `superpowers:dispatching-parallel-agents`；`arxiv-paper-downloader` ↔ `nature-skills:nature-downloader`；`mermaid-master` ↔ `fireworks-tech-graph`（前者 Mermaid、后者手写 SVG，且 `fireworks-showcase-layout` 明确覆盖「把 Mermaid 重绘成 SVG」——三者构成一条流水线，重叠合理）。

---

## 五、需要更新（命名与结构一致性）

| # | 条目 | 问题 | 证据 | 建议 |
|---|---|---|---|---|
| 1 | `claude-deep-research-skill` | 目录名与 `name:` **不一致** | 目录 `claude-deep-research-skill`，frontmatter `name: deep-research` | 二者统一。注意 `agents/analyst.md`、`agents/researcher.md` 按 `claude-deep-research-skill` 引用，改 `name:` 更省事；历史上 `agents/*.toml` 曾错写为 `Codex-deep-research-skill`（已于本次修复） |
| 2 | `fireworks-tech-graph` | 重名：`name:` 同时出现在本体与内嵌副本 | §2.1 | 按 §2.1 处置 |
| 3 | `frontend-design` | 重名：`name:` 同时出现在顶层与嵌套 | 顶层 55 行（容器索引）、`skills/frontend-design/SKILL.md` 76 行（正文） | **不改**（容器设计），但嵌套路径非标准发现路径，建议在 `README.md` 说明加载以顶层为准 |
| 4 | `skill-creator` | 重名：`.system/skill-creator` 与顶层同名 | 两处 `name: skill-creator` | `.system` 为 vendor 管理且被 gitignore，**不改**；在 `README.md` 记录「同名，加载以顶层为准」 |
| 5 | `markitdown` | `packages/` 占 24MB（内嵌依赖包） | `du -sh skills/markitdown/packages` = 24M | 体积问题非缺陷；如在意可改为安装时获取，需评估离线可用性 |
| 6 | `nature-skills` | `skills/` 子目录占 39MB（20 个子技能 + 数据），整体 78MB | `du -sh` | 正常（合集自带数据），不动 |

---

## 六、看着像重复但**不应动**（避免误删）

| 条目 | 为何像重复 | 实际是什么 |
|---|---|---|
| `review`（16 行 / 587B） | description 与 `review-bugbot`、`review-security` 几乎同义 | 是 `disable-model-invocation: true` 的**斜杠命令菜单**，用 AskQuestion 让用户二选一后转调另两个——路由器，不是重复 |
| `frontend-design`（顶层 55 行） | 与嵌套同名 | 顶层是**容器索引**（正文写「This is a skill collection」并列出子技能），嵌套是真身，第三个 `ui-ux-data/` 即 `ui-ux-pro-max` |
| `morph-ppt-3d` | 与 `morph-ppt` 大量重叠 | description 明写「**extends morph-ppt with** GLB model insertion…」——显式扩展，有意分层 |
| `nature-skills` | 20 个子技能，与 `arxiv-paper-downloader`、`humanizer-zh` 等有交集 | 上游**合集**包，按命名空间组织，内部一致性由上游维护 |

---

## 七、体积异常

| Skill | 体积 | 说明 |
|---|---|---|
| `nature-skills` | 78M | 20 子技能 + assets，正常 |
| `fireworks-tech-graph` | 26M | 其中 **9.0M 是内嵌副本**（见 §2.1） |
| `markitdown` | 24M | 内嵌 `packages/` 依赖 |
| `skills/` 合计 | 134M | 上三者占 128M（96%） |

---

## 八、建议的处置顺序

1. **先做零风险项**：§五 的 1、3、4（补文档说明与命名对齐），§四 的 4 组 description 收敛。
2. **再定 `create-skill`**：确认「保留家族对称性」还是「去重」，二选一。
3. **最后处理 `fireworks-tech-graph` 内嵌副本**：需要先定 A/B/C 方案（涉及 `git pull` 工作流）。
4. **`officecli` 边界**：属于 description 重写，不影响功能，可最后做。

> 本报告只做识别，**未删除或修改任何文件**。删除动作需用户明确下令后执行，且按 `AGENTS.md`「文件删除处理」先移入 `.trash/`。
