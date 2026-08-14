---
name: multi-agent
description: >-
  将用户目标收敛为可审计、有边界的子代理任务简报（agent brief）。适用于并行探索、角色化拆分、安全审查、验证交接或明确子代理协作；也适用于编写 Task/子代理提示前整理范围。使用 skill 不等于必须启动子代理——是否委派遵循当前环境与上层规则。Use when the user needs multi-agent planning, sub-agent briefs, parallel exploration splits, review handoffs, or scoped delegation boundaries.
---

# Multi Agent

## Overview

Use this skill to turn a user goal into a **bounded agent brief** that a human or sub-agent can execute without scope creep.

- Output is a brief, not implementation—unless the user explicitly asked you to implement in the same turn.
- **Do not spawn child agents** just because this skill is active. First produce (or refine) the brief; delegate only when the environment supports it and the brief is complete.
- One role per brief unless the user explicitly requests multiple roles or parallel tracks.
- Prefer conservative boundaries: smallest verifiable scope, explicit stop conditions, evidence before summaries.

## When to Use

- Parallel exploration of independent areas (different dirs, services, or hypotheses)
- Role split: explore → implement → review → verify → handoff
- Security or compliance review before merge
- Verification-only pass after changes
- Handoff to another session, human, or agent with disjoint ownership

## When Not to Use

- Single-file, obvious, one-step fix
- User only wants direct implementation with no delegation planning
- Permissions, data access, or ownership are still unclear (clarify first)

## Workflow

1. **Identify the task class**: exploration, implementation, security review, verification, or handoff.
2. **Choose one role** only unless the user explicitly asks for multiple roles.
3. **Fill every required brief field** with concrete paths, commands, boundaries, and stop conditions.
4. **Make ownership disjoint** for implementation work (no two agents editing the same files).
5. **Set forbidden actions conservatively** (e.g. no git push, no secrets, no unrelated refactors).
6. **Require findings and evidence** before summaries (commands run, files read, repro steps).
7. **Stop** if permissions, ownership, or data access are unclear—report gaps instead of guessing.

## Role Selection

| Role | Use when |
|------|----------|
| **read-only explorer** | Map codebase, find references, compare options; no writes |
| **scoped implementation worker** | Apply a bounded change set in named paths only |
| **security reviewer** | Threat model, unsafe patterns, auth/data exposure; read-only |
| **verification worker** | Run tests/lint/build; report pass/fail with evidence |
| **handoff writer** | Summarize state for the next agent/human; no new feature work |

## Required Brief Template

Copy and complete every field. Use 中文 for brief text unless the user or repo requires English.

```markdown
Role:
Goal:
Context:
Allowed actions:
Ownership:
Forbidden actions:
Output format:
Stop condition:
```

### Field guidance

- **Role**: One of the roles above.
- **Goal**: One measurable outcome; link to user request.
- **Context**: Relevant paths, prior decisions, `agent_memory/` pointers; label unverified items as 假设.
- **Allowed actions**: Explicit tools/commands (e.g. read `src/`, run `npm test -- X`).
- **Ownership**: Files/dirs this agent may change; must not overlap another active implementation brief.
- **Forbidden actions**: git push, prod access, drive-by refactors, secrets in output, etc.
- **Output format**: Sections required in the return (findings, diffs, risks, next steps).
- **Stop condition**: When to stop and report (success criteria met, blocker, out-of-scope).

## Parallel Tracks

When the user needs multiple agents:

1. Split by **disjoint ownership** (directories or modules), not by vague “help with backend.”
2. Give each track its own brief from the template above.
3. Define integration order (who merges results, who verifies).

## Integration with agent_memory

- Read `agent_memory/context.md`, `progress.md`, `bugs.md` before drafting briefs for non-trivial work.
- After delegation or phase completion, update `progress.md` (and `bugs.md` if new risks found).

## Example (minimal)

```markdown
Role: read-only explorer
Goal: 列出 `src/auth/` 下所有登录入口及对应测试文件
Context: 用户报告 OAuth 回调偶发失败；勿改代码
Allowed actions: 读取仓库；可运行 `rg`/`grep`；不可写文件
Ownership: 无写权限
Forbidden actions: 修改代码、提交、访问生产
Output format: 表格（入口文件 | 函数 | 测试路径 | 备注）
Stop condition: 已覆盖所有入口或发现权限无法读取某路径时停止并说明
```
