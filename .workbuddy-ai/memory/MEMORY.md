# .ai-shared 项目长期约定

> 唯一维护源：`C:\Users\20448\.ai-shared`。一切修改在此进行，由硬链接 / 目录联接自动分发。

## agents 角色定义：`.md` 是源，`.toml` 是派生副本

- `agents/<name>.md` 是唯一维护源；`agents/<name>.toml`（`name` + `description` + `developer_instructions`）是给 Codex 用的派生副本，**改 md 必须同步 toml**，否则 Codex 侧仍执行旧规则。
- **不要手工同步**，跑脚本（2026-09-24 新增，已验证可字节级复现全部 6 个文件）：
  ```bash
  python skills/ai-config-sharing/scripts/sync-agent-toml.py --check   # 只校验，漂移则退出码 1
  python skills/ai-config-sharing/scripts/sync-agent-toml.py           # 写回
  ```
  脚本按原文件引号形式自动识别两种既有格式，**不做统一**：
  - `"""` 形式（analyst / coder / researcher / reviewer / tester）：正文每行末尾追加**字面量** `\r`（反斜杠 + r 两个字符，TOML 解析时还原为 CR），正文里的反斜杠转义为 `\\`；`"` 不转义。
  - `'''` 形式（sre）：正文为真实换行，无 `\r` 标记、无转义。
- 校验方式：把 toml 正文还原（去字面量 `\r`、`\\`→`\`）后，应与其 md 正文（去 frontmatter、去首尾空行）逐行相等。
- 坑：本机 `core.autocrlf=true`，`git show` 取出的历史版本是 LF，而工作区 `agents/*.md` 是 CRLF——按行比对时须先统一换行。

## MCP 配置（2026-09-26 建立）

- 唯一维护源 `C:\Users\20448\.ai-shared\mcp.json`，硬链接分发到 `.cursor` / `.qoder` / `.workbuddy` /
  `.workbuddy-ai` / `.catpawai` / `.agents`（源 nlink 应为 7）。**改 MCP 只改这一份。**
- Codex（`config.toml` 的 TOML）与 Claude（`~/.claude.json` 顶层 `mcpServers`）格式不兼容、无法硬链接，
  由 `skills\ai-config-sharing\scripts\sync-mcp-config.py` 从源派生（`--check` 校验 / 直接跑写回）。
- **Windows 上 command 必须写 `cmd /c npx`**：`spawn('npx')` 不带 shell 直接 ENOENT（实测）。
- 本机 PowerShell 工具返回空输出 + exit 1，建硬链接用 Python `os.link()` 代替 `mklink /h`。
- 换源方式：本地 stdio（现方案，command/args 各家通用）vs 远程 `https://mcp.context7.com/mcp`
  （官方推荐，但键名各家不统一，无法共用一份 json）。

## 行尾格式（实测）

- LF：`AGENTS.md`、`agents/standards/*.md`
- CRLF：`agents/*.md`、`skills/git-branch-diff-merge/SKILL.md`

## 硬链接改动后必须复核

修改经硬链接分发的文件（`AGENTS.md`、`AI_READ_FIRST.md`）后，用 `stat -c %h <file>` 复核链接数未下降；`AGENTS.md` 应为 **9**。降为 1 说明副本已脱钩，须按 `HARDLINK_INVENTORY.md` §八 重建。

## GitHub 克隆 skill 的本地改动状态（2026-09-24 实测）

`skills/README.md`「更新方法」里写「7 个克隆都 `git pull --ff-only`」是**错的**——7 个克隆里 4 个有本地改动，pull 会失败或覆盖成果：

| 克隆 | 状态 | 说明 |
|---|---|---|
| `web-access`、`claude-deep-research-skill`、`humanizer-zh` | ✅ 干净 | 可直接 pull |
| `superpowers`、`nature-skills` | 新增根 `SKILL.md`（上游无此文件） | 安全，不与 pull 冲突 |
| `repo-wiki` | **展平**：删掉上游跟踪的 `repo-wiki/SKILL.md`，内容提到根目录 | 上游更新该路径时会冲突 |
| `fireworks-tech-graph` | **本地功能扩展**：`body` 多行节点，CHANGELOG 自标 `Local extension — 2026-09-23 (not upstream)`，2 文件 +31 行 | **禁止 pull 覆盖**，否则丢失扩展 |

**推论（可复用）**：遇到「第三方克隆 skill 需要修改」时，优先把改动落到**主仓库侧的对端 skill** 上，而不是改克隆——改克隆会让 `git pull` 产生摩擦。`web-access` 的触发边界就是这样处理的（改 `browser-automation`）。

## 子代理派发：默认派发（2026-09-29 定案，唯一维护源 = `AGENTS.md`「派发规范」）

- 姿态反转：派子代理是**默认工作方式**（上下文隔离 + 并行扇出），边界只用于「派得对」，
  不再作为不派的理由。已删除的旧条款：边界不成立就不派发 / 一次能做完不派发 /
  不得同时派发多个实现型子代理 / 验证执行不可委派。
- 固定不变的硬约束：**执行可委派，判定不可委派**——跑测试、扫描、E2E、压测可派子代理；
  结论、门禁、`RELEASE_GATE` 判定必须本人基于原始证据（命令原文、退出码、产物路径、
  `file:line`）作出，不得采信子代理摘要。
- 并行实现方式：靠**写集不重叠**（不同模块 / 独立 worktree）隔离，不是靠串行回避；
  同一文件或共享状态的写入仍必须串行（与「验证铁律」禁止同文件并行编辑一致）。
- 改角色文件后照旧跑 `sync-agent-toml.py`（md 改完 toml 必须同步），改 `AGENTS.md` 后
  复核 `stat -c %h AGENTS.md` 仍为 9。
