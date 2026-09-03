---
name: agent-definition-writing
description: |
  编写或重写 agent 定义文件（.md + YAML frontmatter，如 .ai-shared/agents、.claude/agents、
  .agents/agents 下的 analyst/coder/researcher/reviewer/tester 等）。基于 2026-09 行业最佳实践
  调研（Anthropic Building Effective Agents、Claude Code subagents 官方文档、Google ADK 指令
  六段式、agentpatterns.ai 定义格式标准）提供统一骨架与检查清单。触发场景：新建 agent、重写
  agent、审查 agent 定义质量、跨工具分发 agent 定义。
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - WebSearch
  - WebFetch
metadata:
  trigger: 新建/重写/审查 agent 定义文件（.md + YAML frontmatter）
  source: 2026-09-03 行业调研（Anthropic 工程博客 ×2、Claude Code 官方文档、Google ADK、agentpatterns.ai、agentshelf、agents.md）
  agent_created: true
---

# Agent Definition Writing — 按行业最佳实践编写 agent 定义

## 六大关注点（任何工具的 agent 定义都回答同样的问题）

identity（身份角色）/ instructions（指令约束）/ tools（工具访问）/ model（模型选择）/ permissions（人机权限）/ skills（按需加载的知识）。

## 统一骨架

**frontmatter**（运行时读取）：
- `name`：小写连字符 slug，无 `:`；必填
- `description`：**路由提示而非能力罗列**——一句身份 + 触发时机（如 "use after coding, before commit"、"use proactively at the start of feature work"）；保持精简（多 agent description 合计超 15K tokens 会告警）；细节下沉到 body
- `allowed-tools`：白名单。**白名单已定义一切**——disallowed 只保留危险操作双保险（git push/commit/merge、rm -rf），删除与白名单重复的冗余项
- 字段名遵循目标工作区既有约定（如 allowed-tools vs tools），body 可跨工具移植

**body**（模型读取，统一六段式）：
1. **角色与边界**（Role & Scope）：一句话身份 + CAN / CANNOT 清单——防止幻觉能力
2. **Skills 路由**：触发条件 → 技能名表格；**不内嵌技能内容**（单体定义反模式：identity 与 expertise 必须分离）
3. **工作流程**（Workflow）：编号步骤 + 显式决策点（"遇到问题？→ …"）；描述思考过程而非纯动作列表
4. **行为规则**（Rules）：具体、可审查；**行为级约束而非工具名级**（按请求目标/方法/数据归属分级，不 blanket 禁 curl/wget/委派）；"check security" 这类模糊规则不合格
5. **输出格式**（Output Format）：结构化模板（表格、字段清单、file:line 锚点要求）
6. **停止条件 + 失败处理**：agent 必须有终止条件；工具/环境失败时怎么办（降级路径、标注 ❌ 不静默跳过、报告阻塞点不伪造结果）

## 高价值模式（来自 Anthropic 多 agent 系统经验）

- **委派简报四要素**：目标 / 输出格式 / 工具与来源指引 / 任务边界——生成子代理任务简报时缺一不可
- **智能过滤器**：研究/测试类 agent 返回浓缩结论而非原始输出
- **先宽后窄**：探索类工作流先用宽泛扫描把握全景再聚焦
- **文件系统输出**：跨 agent 协作产物（如门禁报告 .agent_test/gate/report.md）写文件系统传递轻量引用，避免"传话游戏"
- **回归 vs 已知失败**：测试类 agent 必须区分新增失败与存量失败

## 检查清单

- [ ] description 含触发时机，且是给编排者看的路由提示
- [ ] body 六段齐全（或按 agent 类型合理裁剪）
- [ ] CAN/CANNOT 边界明确，无占位符（TBD/TODO/待补充）
- [ ] 约束是行为级而非工具名级；危险操作双保险保留
- [ ] 有停止条件与失败处理段
- [ ] YAML frontmatter 可解析（name 必填、格式错误会被运行时静默跳过）
- [ ] 多 agent 间协作机制（门禁、报告合并规则）双方定义一致，状态判定取最严格
- [ ] 引用的 skills 真实存在于维护源目录（防幻觉引用）

## 落地参考

本工作区已按此骨架重写的实例：`C:\Users\20448\.ai-shared\agents\{analyst,coder,researcher,reviewer,tester}.md`（唯一维护源，经 Junction/hardlink 分发到各工具目录）。
