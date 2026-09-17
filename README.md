# .ai-shared

全部 AI 工具共享配置的唯一维护源，通过硬链接与目录联接透明分发到 8 个工具目录（清单见 `HARDLINK_INVENTORY.md` 第一节）。

## 文件说明

| 文件 | 用途 | 分发 |
| --- | --- | --- |
| `AGENTS.md` | 通用 AI 助手行为规范 + 生产级质量底线（开发原则、编码规范、多 agent 协作、两道门禁、反模式禁令等） | ✅ 硬链接分发到所有工具目录 |
| `AI_READ_FIRST.md` | 分发目录入口说明：链接副本如何工作、仓库结构、Agents 路由表、标准库路由、维护规则 | ✅ 分发 |
| `HARDLINK_INVENTORY.md` | 完整链接清单与分发状态 | ✅ 分发 |

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `agents/` | 6 个角色定义文件（analyst / coder / researcher / reviewer / tester / sre） |
| `agents/standards/` | 生产级标准库（非功能基线 / 系统设计 / 高可用与运维 / 反模式 / 生命周期门禁）；经 `agents/` 联接自动分发 |
| `skills/` | 技能库（`superpowers/skills/` 为命名空间子集） |

## 生产级质量基线

非功能需求（可用性、并发、扩展、可观测、安全、成本）在调研与需求阶段就必须定量，不得后置。入口为 `agents/standards/README.md`：

| 需要什么 | 读哪份 |
| --- | --- |
| 服务分级、SLI/SLO/SLA、RTO/RPO、延迟分位、容量与压测倍数、可观测性字段、安全基线、数据生命周期 | `agents/standards/nfr-baseline.md` |
| 分层边界、契约与版本、扩展点、缓存 / MQ / 分库分表 / 多租户、探针与弹性 | `agents/standards/system-design.md` |
| 冗余与故障域、容错参数、容灾备份、发布回滚、告警应急、演练复盘 | `agents/standards/resilience-and-ops.md` |
| 十条反模式与检测方法 | `agents/standards/anti-patterns.md` |
| 五阶段 DoR / DoD、生产就绪清单、放行判据 | `agents/standards/lifecycle-gates.md` |

## 快速开始

1. 所有配置修改都在本仓库进行，由硬链接/联接自动分发
2. AI 助手读取各工具目录中的链接副本即可获得相同内容
3. 详见 `AI_READ_FIRST.md` 了解分发机制、仓库结构、路由表和维护规则
4. 详见 `AGENTS.md` 了解 AI 助手行为规范与生产级质量底线
