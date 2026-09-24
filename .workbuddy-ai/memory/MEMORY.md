# .ai-shared 项目长期约定

> 唯一维护源：`C:\Users\20448\.ai-shared`。一切修改在此进行，由硬链接 / 目录联接自动分发。

## agents 角色定义：`.md` 是源，`.toml` 是派生副本

- `agents/<name>.md` 是唯一维护源；`agents/<name>.toml`（`name` + `description` + `developer_instructions`）是给 Codex 用的派生副本，**改 md 必须同步 toml**，否则 Codex 侧仍执行旧规则。
- 无生成脚本，两种既有格式并存，同步时保持各自现状、不要统一：
  - `"""` 形式（analyst / coder / researcher / reviewer / tester）：正文每行末尾追加**字面量** `\r`（反斜杠 + r 两个字符，TOML 解析时还原为 CR），正文里的反斜杠转义为 `\\`；`"` 不转义。
  - `'''` 形式（sre）：正文为真实换行，无 `\r` 标记、无转义。
- 校验方式：把 toml 正文还原（去字面量 `\r`、`\\`→`\`）后，应与其 md 正文（去 frontmatter、去首尾空行）逐行相等。
- 坑：本机 `core.autocrlf=true`，`git show` 取出的历史版本是 LF，而工作区 `agents/*.md` 是 CRLF——按行比对时须先统一换行。

## 行尾格式（实测）

- LF：`AGENTS.md`、`agents/standards/*.md`
- CRLF：`agents/*.md`、`skills/git-branch-diff-merge/SKILL.md`

## 硬链接改动后必须复核

修改经硬链接分发的文件（`AGENTS.md`、`AI_READ_FIRST.md`）后，用 `stat -c %h <file>` 复核链接数未下降；`AGENTS.md` 应为 **9**。降为 1 说明副本已脱钩，须按 `HARDLINK_INVENTORY.md` §八 重建。
