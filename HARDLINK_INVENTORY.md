# 硬链接 / 目录联接清单

> 本文件记录 C:\Users\20448\.ai-shared 作为唯一维护源，向各 AI 工具配置目录分发的所有链接。
> 更新时间：2026-09-17（重新盘点 skills 清单，花名册移交 `skills\README.md` 维护）

---

## 一、共享目标目录

以下 9 个 AI 工具配置目录共享 `.ai-shared` 的内容：

| 目录路径 | 对应工具 |
| --- | --- |
| `C:\Users\20448\.ai-shared` | **唯一维护源（本目录）** |
| `C:\Users\20448\.claude` | Claude (Anthropic CLI) |
| `C:\Users\20448\.codex` | Codex (OpenAI CLI) |
| `C:\Users\20448\.cursor` | Cursor IDE |
| `C:\Users\20448\.qoder` | Qoder |
| `C:\Users\20448\.workbuddy` | WorkBuddy |
| `C:\Users\20448\.workbuddy-ai` | WorkBuddy AI（第二个实例） |
| `C:\Users\20448\.catpawai` | CatPaw AI |
| `C:\Users\20448\.agents` | 通用 Agent 目录 |

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
| `C:\Users\20448\.catpawai\AGENTS.md` | HardLink |
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
| `C:\Users\20448\.catpawai\AI_READ_FIRST.md` | HardLink |
| `C:\Users\20448\.agents\AI_READ_FIRST.md` | HardLink |

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
| `C:\Users\20448\.catpawai\skills` | Junction → `.ai-shared\skills` |
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
| `C:\Users\20448\.catpawai\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.agents\agents` | Junction → `.ai-shared\agents` |

---

## 四、Skills 目录

skill 花名册的**唯一维护源为 `skills\README.md`**（含名称、说明、来源、待恢复项），本节不再重复列举，只记录与链接治理相关的结论。

- 实测（2026-09-17）：`skills\` 下有 **36 个 skill 目录** + `.system`（空目录），另有 6 个非目录条目（`.gitignore`、`README.md` 与 4 个迁移标记 JSON）
- 来源分布：GitHub 克隆 6 个（各带独立 `.git`，由 `.gitignore` 排除）；主仓库跟踪 30 个
- 待恢复：`model-architecture-diagram`（占位文件，`status: NEEDS_RECOVERY`）
- 复核命令：`find skills -maxdepth 1 -type d | sort`，与 `skills\README.md` 清单逐行核对

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

---

## 七、待手动恢复的内容

以下内容无法自动恢复，需要用户手动处理：

1. **`model-architecture-diagram` skill** — 原始 SKILL.md 内容丢失，当前为占位文件。需要用户提供原始来源或备份。
2. **`.system` 目录** — Codex 内部系统 skill 目录，原始内容丢失，当前为空目录。
3. **`.disable_to_model_invocation_migration.json`** — 已重建为默认值，可能与原始内容不同。

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
dir /al C:\Users\20448\.catpawai
dir /al C:\Users\20448\.agents
```

> 注：部分受限环境（沙箱 / 无 cmd 权限）下 `cmd.exe` 不可用，可用原生 PowerShell 等价替代：
> `New-Item -ItemType Junction -Path <链接> -Target <目标>`、
> `New-Item -ItemType HardLink -Path <链接> -Target <目标>`。
