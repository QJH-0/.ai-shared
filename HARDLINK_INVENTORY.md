# 硬链接 / 目录联接清单

> 本文件记录 C:\Users\20448\.ai-shared 作为唯一维护源，向各 AI 工具配置目录分发的所有链接。
> 更新时间：2026-10-04（移除 `.catpawai` 分发目标；校正 skills 计数口径为顶层目录）

---

## 一、共享目标目录

以下 8 个 AI 工具配置目录共享 `.ai-shared` 的内容：

| 目录路径 | 对应工具 |
| --- | --- |
| `C:\Users\20448\.ai-shared` | **唯一维护源（本目录）** |
| `C:\Users\20448\.claude` | Claude (Anthropic CLI) |
| `C:\Users\20448\.codex` | Codex (OpenAI CLI) |
| `C:\Users\20448\.cursor` | Cursor IDE |
| `C:\Users\20448\.qoder` | Qoder |
| `C:\Users\20448\.workbuddy` | WorkBuddy |
| `C:\Users\20448\.workbuddy-ai` | WorkBuddy AI（第二个实例） |
| `C:\Users\20448\.agents` | 通用 Agent 目录 |

> `.catpawai`（CatPaw AI）已由用户删除，并明确**不再保留**；其硬链接与联接一并移除。若日后重新纳入 CatPaw，按 §八「新增 AI 工具目录」重建。

---

## 二、硬链接（HardLink）文件清单

硬链接文件：修改任意一份，所有副本立即同步。

### 1. AGENTS.md

源文件：`C:\Users\20448\.ai-shared\AGENTS.md`

| 硬链接路径 | 链接类型 |
| --- | --- |
| `C:\Users\20448\.ai-shared\AGENTS.md` | 源文件 |
| `C:\Users\20448\.claude\AGENTS.md` | HardLink |
| `C:\Users\20448\.codex\AGENTS.md` | HardLink |
| `C:\Users\20448\.cursor\AGENTS.md` | HardLink |
| `C:\Users\20448\.qoder\AGENTS.md` | HardLink |
| `C:\Users\20448\.workbuddy\AGENTS.md` | HardLink |
| `C:\Users\20448\.workbuddy-ai\AGENTS.md` | HardLink |
| `C:\Users\20448\.agents\AGENTS.md` | HardLink |

### 2. AI_READ_FIRST.md

源文件：`C:\Users\20448\.ai-shared\AI_READ_FIRST.md`

| 硬链接路径 | 链接类型 |
| --- | --- |
| `C:\Users\20448\.ai-shared\AI_READ_FIRST.md` | 源文件 |
| `C:\Users\20448\.claude\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.codex\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.cursor\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.qoder\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.workbuddy\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.workbuddy-ai\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.agents\AI_READ_FIRST.md` | HardLink |

### 3. mcp.json

源文件：`C:\Users\20448\.ai-shared\mcp.json`（2026-09-26 新增；**当前内容为空 `{}`**——context7 已于 2026-10-05 按用户裁决移除）

| 硬链接路径 | 链接类型 |
| --- | --- |
| `C:\Users\20448\.ai-shared\mcp.json` | 源文件 |
| `C:\Users\20448\.cursor\mcp.json` | HardLink |
| `C:\Users\20448\.qoder\mcp.json` | HardLink |
| `C:\Users\20448\.workbuddy\mcp.json` | HardLink |
| `C:\Users\20448\.workbuddy-ai\mcp.json` | HardLink |
| `C:\Users\20448\.agents\mcp.json` | HardLink |

**为什么 command 写 `cmd /c npx` 而不是 `npx`**：Windows 下 Node 的 `spawn('npx')` 不带 shell
会直接 ENOENT（实测 `npx.cmd` 不是可执行体，报错 `spawn npx ENOENT`），MCP 客户端起不来服务。
走 `cmd /c` 包一层后实测可执行（`cmd /c npx --version` → 10.9.7）。同理 `@latest` 交给 npx 解析版本。

**格式不兼容、无法硬链接的两个客户端**由脚本派生，不建链接：

| 客户端 | 配置文件 | 形式 |
| --- | --- | --- |
| Codex | `C:\Users\20448\.codex\config.toml` | `[mcp_servers.context7]` 段（TOML） |
| Claude | `C:\Users\20448\.claude.json` | 顶层 `mcpServers.context7`（与其他用户级配置共存） |

同步脚本（唯一维护源仍是 `mcp.json`）：

```bash
python skills/ai-config-sharing/scripts/sync-mcp-config.py --check   # 只校验，有漂移则退出码 1
python skills/ai-config-sharing/scripts/sync-mcp-config.py           # 写回
```

同步是**双向**的：源里新增/修改的 server 写入派生端，源里消失的也删除。删除范围只覆盖
脚本自己写过的 server，名单记在 `.ai-shared/.mcp-synced.json`（**该文件需入库**，是
「哪些段归脚本管」的唯一依据）。Codex 自管的 `[mcp_servers.node_repl]` 不在名单内，不会被误删。

脚本同时校验 5 个硬链接的内容一致性与源文件链接数（应为 6）。

---

## 三、目录联接（Junction）清单

目录联接：读取和写入透明穿透到 `.ai-shared` 源目录，无需复制。

### 1. skills\

源目录：`C:\Users\20448\.ai-shared\skills\`

| 联接路径 | 链接类型 |
| --- | --- |
| `C:\Users\20448\.claude\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.codex\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.cursor\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.qoder\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.workbuddy\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.workbuddy-ai\skills` | Junction → `.ai-shared\skills` |
| `C:\Users\20448\.agents\skills` | Junction → `.ai-shared\skills` |

### 2. agents\

源目录：`C:\Users\20448\.ai-shared\agents\`

| 联接路径 | 链接类型 |
| --- | --- |
| `C:\Users\20448\.claude\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.codex\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.cursor\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.qoder\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.workbuddy\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.workbuddy-ai\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.agents\agents` | Junction → `.ai-shared\agents` |

---

## 四、Skills 目录

skill 花名册的**唯一维护源为 `skills\README.md`**（含名称、说明、来源、待恢复项），本节不再重复列举，只记录与链接治理相关的结论。

- 实测（2026-10-12）：`skills\` 下有 **28 个 skill 目录** + `.system`（**非空**，含 6 个 Codex 系统 skill），另有 6 个非目录条目（`.gitignore`、`README.md`、3 个迁移标记 JSON，以及由 `skills\.gitignore` 排除的 `_bm_skillid_migration.json`）
- **口径校正（2026-10-12，已对账）**：此前登记的 42（2026-10-04）为历史值；实测顶层 **28**，`skills\README.md` 花名册已重建为 28 行，两处一致。多出的 17 行系**用户手动删除**的 skill（非丢失），明细见 `skills\README.md`「对账记录」
- 来源分布（2026-10-12 实测）：保留独立 `.git` 的克隆 **7 个**（`claude-deep-research-skill`、`fireworks-tech-graph`、`humanizer-zh`、`nature-skills`、`repo-wiki`、`superpowers`、`web-access`）；其余 21 个（含本次新增 `archify`，未保留 `.git`）归主仓库跟踪
- **口径校正（2026-10-04）**：此前登记的「60」与本目录 `ls` 实测（40）长期不一致；现统一为**顶层目录**口径。嵌套子技能（`superpowers/skills/*`、`nature-skills/skills/*` 等）不计入。
- **对账已收口（2026-10-12）**：花名册 28 行与实测 28 个目录逐行一致（新增 `archify`，补登 `find-skills`、`grilling`）。删除 skill 后必须同批删花名册行，否则会再次出现「表比磁盘多」的静默腐烂
- **2026-10-16 科研类迁出**：6 个「学术科研」类 skill 已移出 `skills\`——`ai-fast-learning-loop`、`arxiv-paper-downloader`、`awesome-ai-research-writing`、`humanizer-zh`、`nature-skills` 迁入独立科研库 `C:\Users\20448\research-skills\`（不在 Junction 分发范围，工具不再自动发现），`claude-deep-research-skill` 因去重删除（`.trash/research-dedup-2026-10-16/`）。顶层目录 **28 → 22**；保留独立 `.git` 的克隆 **7 → 4**（`fireworks-tech-graph`、`repo-wiki`、`superpowers`、`web-access`），主仓库跟踪 **21 → 18**。花名册已同步为 **22** 行，详见 `skills\README.md`「对账记录（2026-10-16）」
- **2026-10-17 新增 `anatomy`**：从 GitHub 克隆 `wheresryan22/anatomy`（MIT，约 13.7k★，保留独立 `.git` 未展平，已在 `.gitignore` 加 `skills/anatomy/` 排除项）。顶层目录 **22 → 23**；保留独立 `.git` 的克隆 **4 → 5**（新增 `anatomy`），主仓库跟踪 **18** 不变。花名册已同步为 **23** 行，详见 `skills\README.md`「对账记录（2026-10-17）」
- 无待恢复项（`model-architecture-diagram` 已确认磁盘上不存在，2026-09-23 从花名册移除）
- 复核命令：
  ```bash
  ls -1 skills | grep -vE '^(README\.md|_bm_skillid_migration\.json)$' | wc -l   # 顶层 skill 目录，2026-10-12 实测 28
  find skills -maxdepth 1 -mindepth 1 -type d | wc -l                            # 2026-10-12 实测 29（多出 .system）
  ```
  花名册按名称字典序排列，可逐行对应第一条命令的输出（2026-10-12 已对账）

---

## 五、未链接的独立文件

以下文件位于 `.ai-shared` 中但**未硬链接**到各工具目录（各目录下若有同名文件则为独立副本）：

| 文件 | 说明 |
| --- | --- |
| `C:\Users\20448\.ai-shared\README.md` | `.ai-shared` 目录自身的说明文件 |
| `C:\Users\20448\.ai-shared\.gitignore` | `.ai-shared` 的 git 忽略规则 |
| `C:\Users\20448\.ai-shared\HARDLINK_INVENTORY.md` | 本清单文件 |
| `C:\Users\20448\.ai-shared\skills\.gitignore` | skills 目录的 git 忽略规则 |
| `C:\Users\20448\.ai-shared\skills\README.md` | skills 目录说明文件 |
| `C:\Users\20448\.ai-shared\agents\*.md` | agents 目录下的角色定义文件（通过 Junction 共享，无需单独硬链接） |
| `C:\Users\20448\.ai-shared\agents\standards\*.md` | 生产级标准库（非功能基线 / 系统设计 / 高可用与运维 / 反模式 / 生命周期门禁）；位于 `agents\` 之下，随 Junction 自动分发，无需单独建链接 |

---

## 六、恢复历史

| 日期 | 操作 | 说明 |
| --- | --- | --- |
| 2026-08-29 | 恢复 8 个丢失的 skill | 从 GitHub 重新克隆 6 个 skill（claude-deep-research-skill, superpowers, humanizer-zh, repo-wiki, web-access, nature-skills），创建 2 个占位 SKILL.md（git-nested-repo-backup, model-architecture-diagram） |
| 2026-08-29 | 恢复 AGENTS.md 硬链接 | 7 个工具目录的 AGENTS.md 重新硬链接到 `.ai-shared\AGENTS.md` |
| 2026-08-29 | 恢复 AI_READ_FIRST.md 硬链接 | 7 个工具目录的 AI_READ_FIRST.md 重新硬链接到 `.ai-shared\AI_READ_FIRST.md` |
| 2026-08-29 | 恢复 .disable_to_model_invocation_migration.json | 重建为默认值 |
| 2026-08-29 | 创建 .system 目录占位 | 空目录，原始内容未恢复 |
| 2026-09-14 | 新增 `.workbuddy-ai` 分发目标 | `skills\`、`agents\` 建 Junction；`AGENTS.md`、`AI_READ_FIRST.md` 建 HardLink。原有真实 `skills\`（14 个文件）备份至 `~\.ai-shared-backup-20260914-164652\workbuddy-ai\`。验证：写入穿透 OK、8 个工具 MD5 一致 |
| 2026-09-17 | 重新盘点 skills 清单 | 实测 36 个 skill 目录；移除 `agent-definition-writing`、`broken-chain-audit`（工作区已删除，用户确认按现状处理）；花名册唯一维护源改为 `skills\README.md`，本节仅保留链接治理结论；同步清理 `agents\sre.md` 与 `skills\kaggle-modularize\SKILL.md` 的悬空 skill 引用 |
| 2026-09-23 | 新增 `fireworks-tech-graph` | 从 GitHub 克隆（含独立 `.git`），加入 `.gitignore` 嵌套仓库排除项；花名册 GitHub 克隆数 6 → 7 |
| 2026-09-23 | 花名册全量核对 | 实测 57 个 skill 目录（此前花名册只登记 36 个，另有 21 个用户自建/工具链 skill 未登记）；移除幽灵条目 `model-architecture-diagram`（磁盘上已不存在）；修正 `.system` 说明（原记为「空目录」，实含 6 个系统 skill）；来源分布更新为 GitHub 克隆 7 + 主仓库跟踪 50 |
| 2026-09-24 | 花名册增量核对 | 实测 60 个 skill 目录；补登记 3 个漏登项 `ai-fast-learning-loop`、`fireworks-showcase-layout`、`project-handover-docs`；总数 57 → 60，来源分布更新为 GitHub 克隆 7 + 主仓库跟踪 53 |
| 2026-09-26 | 新增 mcp.json 硬链接 | 唯一维护源 `.ai-shared\mcp.json`（context7），硬链接分发到 `.cursor` / `.qoder` / `.workbuddy` / `.workbuddy-ai` / `.catpawai` / `.agents`；Codex（TOML）与 Claude（`~/.claude.json`）由 `sync-mcp-config.py` 派生。原 `.qoder\mcp.json` 含 drawio，按用户裁决丢弃，备份在 `.trash\qoder-mcp.json.20260926.bak` |
| 2026-10-04 | 移除 `.catpawai` 分发目标 | 用户删除 `.catpawai` 目录并决定**不再保留 CatPaw**，其 `AGENTS.md` / `AI_READ_FIRST.md` / `mcp.json` 硬链接与 `skills` / `agents` 联接一并移除；同时清除 `skills/ai-config-sharing` 内的全部 CatPaw 引用（含删除 `scripts/fix-catpawai.ps1`）。源文件链接数由 9 校正为 **8**（`mcp.json` 由 7 校正为 **6**），清单与项目记忆同步更新 |
| 2026-10-04 | 新增 2 个 skill 并校正花名册口径 | 新增 `ai-output-readability`（四级表达路由）、`explainer-video`（3b1b 风格讲解视频）；花名册 40 → **42**。同时校正长期不一致的计数口径：此前登记的 60（含嵌套子技能）与 `ls` 实测的 40 并存，现统一为**顶层目录**口径 |
| 2026-10-05 | 移除 context7 + 修复 MCP 同步脚本 | 源 `mcp.json` 已为空 `{}`，但 Claude（`.claude.json`）与 Codex（`config.toml`）派生端仍残留 context7。按用户裁决移除：脚本改为**双向**同步（源里消失的 server 也从派生端删）+ 容忍空源；新增 `.ai-shared/.mcp-synced.json` 记录脚本写过的 server 名，据此避免误删 Codex 自管的 `[mcp_servers.node_repl]`。改前已备份两个配置到 `.trash/mcp-config-backup-20261005-095048/`；改后 `--check` 通过、重复执行幂等 |
| 2026-10-12 | 新增 `archify` 并替换 `project-chain-atlas` | 按用户要求从 GitHub 克隆 `tt-a1i/archify`（v3.0.1，MIT；官方 Skills CLI `npx -y skills add tt-a1i/archify --list --full-depth` 确认源内仅一个名为 `archify` 的技能）替换 `project-chain-atlas`。整仓克隆 86.3MB，其中技能包 `archify/archify/` 10.1MB **展平**提升为 `skills\archify\`（`SKILL.md` 落到发现路径顶层），克隆整仓与 `project-chain-atlas` 分别归档至 `.trash\archify-repo-clone-20261012-153826\`、`.trash\project-chain-atlas-20261012-153832\`（未删除，待用户处置）。因未保留 `.git`，来源归类为主仓库跟踪。悬空引用：全仓 grep `project-chain-atlas` 仅命中其自身文件，无外部引用需清理。验证：`node bin/archify.mjs --help` 正常（Node v24.16，browser-check 依赖的本机 Chrome 存在）；7 个工具目录下 `skills\archify\SKILL.md` 可见、`project-chain-atlas` 已消失。同批发现花名册与实测目录长期不一致（42 行 vs 28 目录）；用户随后确认那 17 行系其**手动删除**，当日完成对账收口（见下一行） |
| 2026-10-12 | 花名册对账收口 | 用户确认「登记了但磁盘不存在」的 17 个 skill 系其**手动删除**（非丢失）。据此重建 `skills\README.md`：删除 17 行历史登记（`canvas`、`code-to-interview-docs`、`feishu-job-import`、`migrate-to-skills`、`morph-ppt`、`morph-ppt-3d`、`officecli` 及 8 个变体、`resume-tech-interview-decompose`、顶层 `skill-creator`）、补登 `find-skills` 与 `grilling`、并重排编号 1–28；同步修正 §四计数与复核命令注释。验证：三步对账 `Compare-Object` 无输出（磁盘 28 = 花名册 28），编号 1..28 连续；全仓 grep 17 个已删名字仅命中本 README 自身的登记行（`agents/*.md` 路由表未引用）。同时修正「已知重名」中 `skill-creator` 的处置（现存仅 `.system/skill-creator`）与「已知功能重叠」（移除 `officecli` 段落，新增 `archify` / `fireworks-tech-graph` / `mermaid-master` 的绘图边界） |
| 2026-10-12 | archify 本地扩展：一次到位契约 | 针对首次出图只产出浅层总览、需三轮追加对话才达预期深度的问题，在 skill 包内新增 `references/one-pass-completeness.md`（范围触发、默认视图集、8 项覆盖清单、实测容量上限、引用先核验、环境与证据卫生），并给 `SKILL.md`（第 1/3 步 + 新小节 + Setup 预检）、`references/authoring-defaults.md`（overview = 完整运行时表面且交付视图集；禁止把真实组件降级塞进卡片）、`references/repository-authoring.md`（系统级请求的范围含后台/存储/横切；写入前核验引用）打上 `[local extension 2026-10-12]` 补丁。全部改动与重新套用方式记录在 `skills\archify\LOCAL_CHANGES.md`。该包无独立 `.git`（已展平、主仓库跟踪），故不与 `git pull` 冲突；但上游刷新会覆盖，需按 LOCAL_CHANGES 重新套用 |
| 2026-10-12 | 提交 skills 重组并清理过期报告 | 上述改动（新增 `archify` 与 `grilling`、删除 17 个用户手动移除的 skill 及被替换的 `project-chain-atlas`、`skills\README.md` 花名册对账至 28 行、本文件计数与时间线同步）一次提交入库。同批清理 `.agent_docs\` 两个过期报告（`audits\2026-09-24-skills-audit.md`、`impl\2026-10-11-agent-rules-simplification.md`）：按第 4 节流程先从 `HEAD` 归档至 `.trash\agent_docs-20261012\`，再随本次提交删除 |
| 2026-10-17 | 新增 `anatomy` | 按用户要求从 GitHub 克隆 `wheresryan22/anatomy`（Agent Skill：把技术概念画成可交互等距机械装置图；MIT，约 13.7k★），置于 `skills\anatomy\`，保留独立 `.git` 并在 `.gitignore` 加排除项；花名册 22 → 23、独立克隆 4 → 5。经 Junction 对全部 7 个工具目录立即可见，无需分发动作；`agents\*.md` 路由表无绘图类引用，无需同步 |

---

## 七、待手动恢复的内容

当前**无待手动恢复项**。

历史遗留项已于 2026-09-23 全部结清：

1. ~~**`model-architecture-diagram` skill**~~ — 全盘搜索确认磁盘上已不存在（既无目录也无占位文件），从花名册移除。其用途（从代码生成模型架构图）由 `fireworks-tech-graph` 覆盖，不再单独恢复。
2. ~~**`.system` 目录**~~ — 原记为「空目录，内容未恢复」，2026-09-23 核对时实际含 6 个 Codex 系统 skill（`imagegen`、`openai-docs`、`plugin-creator`、`review-agent`、`skill-creator`、`skill-installer`）+ `.codex-system-skills.marker`，且已随 Junction 分发到各工具目录。该项不存在待恢复内容。
3. **`.disable_to_model_invocation_migration.json`** — 仍为 2026-08-29 重建的默认值，与原始内容可能有差异。该文件是 Codex 的迁移标记，缺失时 Codex 会自行重建，不影响功能，保留现状。

---

## 八、维护操作指南

### 新增硬链接文件

1. 在 `.ai-shared` 中创建源文件
2. 对每个目标目录执行：`mklink /h <目标路径> <源路径>`（需 cmd 管理员权限或开发者模式）
3. 更新本清单文档

### 新增目录联接

1. 在 `.ai-shared` 中创建源目录
2. 对每个目标目录执行：`mklink /j <目标路径> <源路径>`（无需管理员权限）
3. 更新本清单文档

### 新增 AI 工具目录

1. 创建工具配置目录（如 `C:\Users\20448\.newtool`）
2. 为每个已有的硬链接文件执行 `mklink /h`
3. 为每个已有的目录联接执行 `mklink /j`
4. 更新本清单文档的第一节表格

### 修复断开的硬链接

如果某个目录下的文件变成了独立副本（不再是硬链接）：

1. 删除该独立副本：`del <目标路径>`
2. 重新创建硬链接：`mklink /h <目标路径> <源路径>`
3. 验证：`fsutil hardlink list <源路径>`，确认目标路径出现在列表中

### 验证所有链接

```cmd
:: 验证硬链接
fsutil hardlink list C:\Users\20448\.ai-shared\AGENTS.md
fsutil hardlink list C:\Users\20448\.ai-shared\AI_READ_FIRST.md

:: 验证目录联接
dir /al C:\Users\20448\.claude
dir /al C:\Users\20448\.codex
dir /al C:\Users\20448\.cursor
dir /al C:\Users\20448\.qoder
dir /al C:\Users\20448\.workbuddy
dir /al C:\Users\20448\.workbuddy-ai
dir /al C:\Users\20448\.agents
```

> 注：部分受限环境（沙箱 / 无 cmd 权限）下 `cmd.exe` 不可用，可用原生 PowerShell 等价替代：
> `New-Item -ItemType Junction -Path <链接> -Target <目标>`、
> `New-Item -ItemType HardLink -Path <链接> -Target <目标>`。
