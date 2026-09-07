# AI 先读 / READ FIRST — 本目录是共享配置的硬链接入口

本目录（某个 AI 工具的配置根目录）通过链接指向唯一维护源：

    C:\Users\20448\.ai-shared

具体映射关系：
- AGENTS.md   → 硬链接（HardLink）    → C:\Users\20448\.ai-shared\AGENTS.md
- skills\     → 目录联接（Junction）   → C:\Users\20448\.ai-shared\skills\
- agents\     → 目录联接（Junction）   → C:\Users\20448\.ai-shared\agents\

## 重要：模型读的是这里的链接副本，不是 .ai-shared
你（AI 助手）直接读取的就是本目录下的 AGENTS.md / skills\ / agents\。
这些与 .ai-shared 下的是**同一份内容**：
- AGENTS.md 是硬链接（HardLink）：任意一个被修改，其余全部立即同步。
- skills\、agents\ 是目录联接（Junction）：读取与写入都透明穿透到 .ai-shared，无需复制。

## 仓库结构

| 路径 | 内容 |
| --- | --- |
| `agents\` | 5 个角色定义文件（analyst / coder / researcher / reviewer / tester，见「Agents 路由表」） |
| `skills\` | 技能库（37+ skills；`superpowers\skills\` 为命名空间子集） |
| `AGENTS.md` | 通用 AI 助手行为规范（经硬链接分发） |
| `AI_READ_FIRST.md` | 本文件 — 分发目录入口说明（经硬链接分发） |
| `HARDLINK_INVENTORY.md` | 完整链接清单与分发状态 |

## Agents 路由表

5 个角色定义文件的唯一维护源为 `C:\Users\20448\.ai-shared\agents\`。每个定义文件自带完整的职责边界（CAN/CANNOT）、Skills 路由、工作流程、行为规则、输出格式与停止条件——**本表仅保留路由提示，细节以定义文件为准**：

| Agent | 定义文件（绝对路径） | 何时委派（路由提示） | 写权限 |
| --- | --- | --- | --- |
| **analyst** | `C:\Users\20448\.ai-shared\agents\analyst.md` | 任何新需求、新功能或重构启动时主动委派——需求澄清、方案对比、任务拆解、风险评估 | ⚠️ 仅计划文档 |
| **coder** | `C:\Users\20448\.ai-shared\agents\coder.md` | 实现功能、修复 bug、重构代码——TDD 驱动、完成前强制验证 | ✅ 代码文件 + 执行记录 |
| **researcher** | `C:\Users\20448\.ai-shared\agents\researcher.md` | 理解陌生代码、梳理架构、定位实现、生成项目文档、深度技术调研 | ⚠️ 仅调研报告 |
| **reviewer** | `C:\Users\20448\.ai-shared\agents\reviewer.md` | 代码变更完成后、提交/合并前——多维度审查 + AI 幻觉专项 + 门禁审查报告 | ⚠️ 门禁 + 审查报告 |
| **tester** | `C:\Users\20448\.ai-shared\agents\tester.md` | 功能实现后验证质量、编写/运行测试、E2E 测试、门禁测试报告 | ✅ 测试文件 + 测试报告 + 门禁报告 |

## Agents 与 Skills 维护规则

### 路径引用规则

- 引用 agent 定义文件时，**必须**写绝对路径 `C:\Users\20448\.ai-shared\agents\<name>.md`
- agent 文件中引用 skill 时，**必须**写维护源路径 `C:\Users\20448\.ai-shared\skills\<skill-name>`
- 带命名空间的 `superpowers:xxx` 技能对应子目录 `C:\Users\20448\.ai-shared\skills\superpowers\skills\xxx`
- 不得写入 `.claude\skills`、`.claude\agents` 等工具目录路径——这些是分发副本（联接/硬链接），不是维护源

### 修改与分发

- 一切修改在 `C:\Users\20448\.ai-shared\` 进行，由硬链接 / 目录联接自动分发到所有工具目录
- 禁止在分发副本目录删除链接后重建（会脱钩成独立副本，改动不再同步）
- 新增 / 修改 agent 定义时遵循统一六段式骨架：**角色边界（CAN/CANNOT）→ Skills 路由 → 工作流程 → 行为规则 → 输出格式 → 停止条件+失败处理**；`description` 写成「一句身份 + 触发时机」的路由提示；约束用行为级而非工具名级
- 完整链接清单和分发状态见 `HARDLINK_INVENTORY.md`

## 更新规则（务必遵守）
1. ✅ 要改配置，直接编辑唯一源 C:\Users\20448\.ai-shared\ 下的对应文件/目录。
2. ✅ 保存后，本目录的 AGENTS.md / skills\ / agents\ 会自动同步更新。
3. ❌ 不要在本目录直接改写 AGENTS.md，也不要删除它后用新文件覆盖
   （删除 + 新建会破坏硬链接，使本目录与共享源脱钩，变成独立副本，改动不再同步）。
4. ❌ skills\ / agents\ 是目录联接，不要在本目录删除它们再重建
   （联接只应建一次；要改内容请直接操作 .ai-shared 下的源目录）。
5. 任何新增 / 调整都应在 C:\Users\20448\.ai-shared\ 中进行，由硬链接 / 联接自动分发到所有工具。
