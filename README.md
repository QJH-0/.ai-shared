# .ai-shared

全部 AI 工具共享配置的唯一维护源，通过硬链接与目录联接透明分发到 7 个工具目录。

## 文件说明

| 文件 | 用途 | 分发 |
| --- | --- | --- |
| `AGENTS.md` | 通用 AI 助手行为规范（开发原则、编码规范、多 agent 协作、门禁等） | ✅ 硬链接分发到所有工具目录 |
| `AI_READ_FIRST.md` | 分发目录入口说明：链接副本如何工作、仓库结构、Agents 路由表、维护规则 | ✅ 分发 |
| `HARDLINK_INVENTORY.md` | 完整链接清单与分发状态 | ✅ 分发 |

## 目录结构

| 路径 | 内容 |
| --- | --- |
| `agents/` | 5 个角色定义文件（analyst / coder / researcher / reviewer / tester） |
| `skills/` | 技能库（37+ skills；`superpowers/skills/` 为命名空间子集） |

## 快速开始

1. 所有配置修改都在本仓库进行，由硬链接/联接自动分发
2. AI 助手读取各工具目录中的链接副本即可获得相同内容
3. 详见 `AI_READ_FIRST.md` 了解分发机制、仓库结构和维护规则
4. 详见 `AGENTS.md` 了解 AI 助手行为规范
