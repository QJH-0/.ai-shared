# 硬链接 / 目录联接清单

> 本文件记录 C:\Users\20448\.ai-shared 作为唯一维护源，向各 AI 工具配置目录分发的所有链接。
> 更新时间：2026-08-29（恢复后重建）

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
| `C:\Users\20448\.catpawai\agents` | Junction → `.ai-shared\agents` |
| `C:\Users\20448\.agents\agents` | Junction → `.ai-shared\agents` |

---

## 四、Skills 目录清单

`.ai-shared\skills\` 下的所有 skill 目录（共 37 个）：

| # | Skill 名称 | 来源 | 恢复状态 |
| --- | --- | --- | --- |
| 1 | `ai-code-review` | git 跟踪 | ✅ 完整 |
| 2 | `ai-config-sharing` | git 跟踪 | ✅ 完整 |
| 3 | `algorithmic-art` | git 跟踪 | ✅ 完整 |
| 4 | `arxiv-paper-downloader` | git 跟踪 | ✅ 完整 |
| 5 | `awesome-ai-research-writing` | git 跟踪 | ✅ 完整 |
| 6 | `browser-automation` | git 跟踪 | ✅ 完整 |
| 7 | `claude-deep-research-skill` | GitHub 克隆（199-biotechnologies/claude-deep-research-skill） | ✅ 已恢复 |
| 8 | `doc-coauthoring` | git 跟踪 | ✅ 完整 |
| 9 | `frontend-design` | git 跟踪 | ✅ 完整 |
| 10 | `git-commit` | git 跟踪 | ✅ 完整 |
| 11 | `git-nested-repo-backup` | 原始来源未知 | ⚠️ 占位文件，需手动恢复 |
| 12 | `humanizer-zh` | GitHub 克隆（op7418/Humanizer-zh） | ✅ 已恢复 |
| 13 | `kaggle-modularize` | git 跟踪 | ✅ 完整 |
| 14 | `kaggle-notebookify` | git 跟踪 | ✅ 完整 |
| 15 | `markitdown` | git 跟踪 | ✅ 完整 |
| 16 | `mermaid-master` | git 跟踪 | ✅ 完整 |
| 17 | `model-architecture-diagram` | 原始来源未知 | ⚠️ 占位文件，需手动恢复 |
| 18 | `morph-ppt` | git 跟踪 | ✅ 完整 |
| 19 | `morph-ppt-3d` | git 跟踪 | ✅ 完整 |
| 20 | `multi-agent` | git 跟踪 | ✅ 完整 |
| 21 | `nature-skills` | GitHub 克隆（Yuan1z0825/nature-skills） | ✅ 已恢复 |
| 22 | `officecli` | git 跟踪 | ✅ 完整 |
| 23 | `officecli-academic-paper` | git 跟踪 | ✅ 完整 |
| 24 | `officecli-data-dashboard` | git 跟踪 | ✅ 完整 |
| 25 | `officecli-docx` | git 跟踪 | ✅ 完整 |
| 26 | `officecli-financial-model` | git 跟踪 | ✅ 完整 |
| 27 | `officecli-pitch-deck` | git 跟踪 | ✅ 完整 |
| 28 | `officecli-pptx` | git 跟踪 | ✅ 完整 |
| 29 | `officecli-word-form` | git 跟踪 | ✅ 完整 |
| 30 | `officecli-xlsx` | git 跟踪 | ✅ 完整 |
| 31 | `repo-wiki` | GitHub 克隆（devin2255/repo-wiki-skill） | ✅ 已恢复 |
| 32 | `resume-tech-interview-decompose` | 本地文件（未入 git） | ✅ 完整 |
| 33 | `skill-creator` | git 跟踪 | ✅ 完整 |
| 34 | `superpowers` | GitHub 克隆（obra/superpowers） | ✅ 已恢复 |
| 35 | `web-access` | GitHub 克隆（eze-is/web-access） | ✅ 已恢复 |
| 36 | `.system` | Codex 内部目录 | ⚠️ 空占位，内容未恢复 |
| 37 | `.disable_to_model_invocation_migration.json` | Codex 配置 | ⚠️ 重建为默认值 |

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

---

## 六、恢复历史

| 日期 | 操作 | 说明 |
| --- | --- | --- |
| 2026-08-29 | 恢复 8 个丢失的 skill | 从 GitHub 重新克隆 6 个 skill（claude-deep-research-skill, superpowers, humanizer-zh, repo-wiki, web-access, nature-skills），创建 2 个占位 SKILL.md（git-nested-repo-backup, model-architecture-diagram） |
| 2026-08-29 | 恢复 AGENTS.md 硬链接 | 7 个工具目录的 AGENTS.md 重新硬链接到 `.ai-shared\AGENTS.md` |
| 2026-08-29 | 恢复 AI_READ_FIRST.md 硬链接 | 7 个工具目录的 AI_READ_FIRST.md 重新硬链接到 `.ai-shared\AI_READ_FIRST.md` |
| 2026-08-29 | 恢复 .disable_to_model_invocation_migration.json | 重建为默认值 |
| 2026-08-29 | 创建 .system 目录占位 | 空目录，原始内容未恢复 |

---

## 七、待手动恢复的内容

以下内容无法自动恢复，需要用户手动处理：

1. **`git-nested-repo-backup` skill** — 原始 SKILL.md 内容丢失，当前为占位文件。需要用户提供原始来源或备份。
2. **`model-architecture-diagram` skill** — 同上，原始内容丢失，当前为占位文件。
3. **`.system` 目录** — Codex 内部系统 skill 目录，原始内容丢失，当前为空占位目录。
4. **`.disable_to_model_invocation_migration.json`** — 已重建为默认值，可能与原始内容不同。

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
dir /al C:\Users\20448\.catpawai
dir /al C:\Users\20448\.agents
```
