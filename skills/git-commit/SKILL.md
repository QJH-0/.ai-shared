---
name: git-commit
description: Creates git commits following Conventional Commits format with type/scope/subject. Subject line defaults to Chinese unless project docs require English. Use when user wants to commit changes, create commit, save work, or stage and commit. Enforces project-specific conventions from CLAUDE.md and .cursor/rules.
---

# Git commit

Creates git commits following Conventional Commits format.

## Recent project commits

!`git log --oneline -5 2>/dev/null`

## Quick start

```bash
# 1. Stage changes
git add <files>

# 2. Create commit（标题里 type/scope 保持英文惯例，冒号后为中文说明）
git commit -m "feat(api): 新增视频元数据接口"
```

## Subject 语言（默认中文）

- **默认**：`type(scope):` 之后使用**中文**撰写简短说明——祈使语气、动词或动宾短语开头，不用句号结尾。
- **例外**：若 `CLAUDE.md`、`.cursor/rules`（如 `dev-workflow.mdc`）、`CONTRIBUTING.md` 或用户当场要求使用**英文**标题，则以项目/用户为准。
- **正文（body）**：可用中文或英文，与团队文档一致即可；开源对外仓库若需英文 release note，可在 body 中补充英文段落。

## Project conventions

- Scope is **required** (kebab-case): `validation`, `auth`, `cookie-service`, `api`
- Additional type beyond standard CC: `security` (vulnerability fixes or hardening)
- HEREDOC for multi-line commits:

```bash
git commit -m "$(cat <<'EOF'
feat(validation): 增加带域名白名单的 URL 校验器

实现 URLValidator：
- 域名白名单
- 危险 scheme 拦截

Addresses Requirement 31
Part of Task 5.1
EOF
)"
```

## Important rules

- **ALWAYS** check `CLAUDE.md` and `.cursor/rules` first — use project format if it differs
- **ALWAYS** include scope in parentheses
- **ALWAYS** use imperative mood for the subject（中文：「添加/修复/重构…」式短句；英文项目同理）
- **DEFAULT** Chinese subject after the colon unless project rules say otherwise
- **NEVER** end the subject line with a period
- **NEVER** use a vague subject（避免「修改代码」「fix bug」「更新」）
- Keep the first line reasonably short（建议整行约 72 字符内以便 `git log --oneline` 可读；纯中文标题约 20–35 字内更稳妥）
- Group related changes into a single focused commit

## References

- `references/commit_examples.md` - Extended examples by type, good/bad comparisons, and Chinese title patterns
