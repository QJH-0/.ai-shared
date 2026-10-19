# research-skills — 独立科研技能库

> 位置：`C:\Users\20448\research-skills\`
> 建立：2026-10-16
> 内容：由图片「科研 Skills 榜（10 个 AI Skill）」整理下载 + 本地科研类 skill 归集而来。
> ⚠️ **本目录不在 `.ai-shared\skills` 的 Junction 分发范围内**——8 个 AI 工具（Claude/Codex/Cursor/Qoder/WorkBuddy/WorkBuddy-AI/.agents）**不会自动发现**此处的技能；需要时按绝对路径手动加载。
> 唯一维护源仍是 `C:\Users\20448\.ai-shared`；本目录是其外的独立科研集合。

---

## 一、图片所列 10 项 → 实际来源

| # | 图片名称 | 核实/替代结论 | 星数 | 本地目录 |
|---|---------|--------------|------|---------|
| 1 | ellis | 无同名仓库 → 按功能替代 `DreambigOu/ELI5`（复杂概念分级讲解） | 1.8k | `ellis-ELI5/`（技能在 `skills/eli5`） |
| 2 | Research-Starter-Kit | `LAMDA-NeSy/Research-Starter-Kit`（南大 LAMDA-NeSy） | 7.5k | `research-starter-kit/`（**仅指南 README，无 SKILL.md**，非可执行技能） |
| 3 | chinese-academic-paper-search | 无同名仓库 → 替代候选 `wp-a/nature-academic-search` | 325 | **已去重删除**（见第三节；功能由 `nature-skills` 内的 `nature-academic-search` 覆盖） |
| 4 | academic-html-ppt | 无实际同名仓库 → 替代 `lewislulu/html-ppt-skill` | 8.7k | `html-ppt-skill/` |
| 5 | ChatPaper | `kaixindelele/ChatPaper` | 19k | **仅登记，未下载**（完整 Python 应用，非 SKILL.md 技能） |
| 6 | gpt_academic | `binary-husky/gpt_academic` | 68k | **仅登记，未下载**（完整应用） |
| 7 | awesome-ai-research-writing | 本地已存在同一 skill（GitHub: `zengrong233/awesome-ai-research-writing-skill`） | 76★ | `awesome-ai-research-writing/`（由共享库迁入） |
| 8 | Academic Research Skills | `Imbad0202/academic-research-skills`（research→write→review→revise→finalize） | 52k | `academic-research-skills/` |
| 9 | scientific-agent-skills | `K-Dense-AI/scientific-agent-skills`（177 子技能） | 51k | `scientific-agent-skills/`（**稀疏检出，仅保留 8 个关键子技能**） |
| 10 | Light-skills | `Light0305/Light-skills`（28 子技能） | 653 | `light-skills/` |

### 大仓库的取舍

- `scientific-agent-skills`（全量 >470MB / 177 子技能）按「只保留最重要的几个」处理，用 `git sparse-checkout` 仅取 8 个通用子技能：`literature-review`、`scientific-writing`、`peer-review`、`statistical-analysis`、`scientific-visualization`、`hypothesis-generation`、`experimental-design`、`research-grants`。
- `academic-research-skills`、`light-skills`、`html-ppt-skill` 已剔除文档/评测/示例目录（`docs/`、`evals/`、`examples/`、`projects/` 等），仅留技能本体与其依赖（`scripts/`、`shared/`、`_shared/`）。

---

## 二、由共享库 `C:\Users\20448\.ai-shared\skills\` 迁入的本地科研技能

| 技能 | 说明 |
|------|------|
| `nature-skills/` | Nature 级全流程科研集合（23 个子技能：检索/引用/绘图/写作/审稿/统计/翻译/精读等） |
| `awesome-ai-research-writing/` | 中英双语学术写作工具包（图片第 7 项） |
| `ai-fast-learning-loop/` | 十步 AI 学习闭环 |
| `arxiv-paper-downloader/` | arXiv 批量下载 + 首页标题校验 |
| `humanizer-zh/` | 中文去 AI 味写作助手 |

---

## 三、去重记录（删除「功能重复中方法较弱」的一方）

| 被删项 | 位置变化 | 依据 |
|-------|---------|------|
| `claude-deep-research-skill` | `.ai-shared\skills\` → `.trash\research-dedup-2026-10-16\` | 与 `academic-research-skills/skills/deep-research`（13-agent / 8 模式 / 含系统综述与元分析）功能重复且方法更弱 |
| `nature-academic-search`（下载的 wp-a 版本） | `research-skills\` → `.ai-shared\.trash\research-dedup-2026-10-16\` | 与 `nature-skills/skills/nature-academic-search` 是**同一项目**（同名、同指纹文件），属重复 |

> 备份路径：`C:\Users\20448\.ai-shared\.trash\research-dedup-2026-10-16\`
> 同步更新：`skills\README.md`（花名册 28→22）、`HARDLINK_INVENTORY.md`、`agents\analyst|researcher`（deep-research 路由改指本库）。

---

## 四、更新方法

| 目录 | 类型 | 更新 |
|------|------|------|
| `ellis-ELI5`、`research-starter-kit`、`html-ppt-skill`、`academic-research-skills`、`light-skills` | git 克隆（`--depth 1`） | `cd <dir> && git -c http.sslBackend=openssl pull --ff-only`（本机需 `GIT_SSL_NO_VERIFY=1`） |
| `scientific-agent-skills` | 稀疏克隆 | 加减子技能：`git -C <dir> sparse-checkout set skills/<name> ...` |
| `nature-skills`、`humanizer-zh` | git 克隆（迁入） | 同上；`nature-skills` 上游为 `Yuan1z0825/nature-skills` |
| `ai-fast-learning-loop`、`arxiv-paper-downloader`、`awesome-ai-research-writing` | 主仓库跟踪（迁入） | 无独立上游；原位于 `.ai-shared\skills\`，改动请在本库进行 |

> 本机 TLS 备注：默认 schannel 后端会报 `schannel: failed to receive handshake`；用
> `GIT_SSL_NO_VERIFY=1 git -c http.sslBackend=openssl clone/pull` 可正常访问。

---

## 五、回退说明

- **恢复去重删除的技能**：把 `.ai-shared\.trash\research-dedup-2026-10-16\` 下目录移回原位（`claude-deep-research-skill` → `.ai-shared\skills\`；`nature-academic-search` → `research-skills\`）。
- **把科研技能收回共享库**：将 `nature-skills`、`awesome-ai-research-writing`、`ai-fast-learning-loop`、`arxiv-paper-downloader`、`humanizer-zh` 移回 `C:\Users\20448\.ai-shared\skills\`，并同步还原 `skills\README.md` 花名册与 `HARDLINK_INVENTORY.md` 计数。
- **让工具自动发现本库**：把本目录整体建 Junction 到各工具的 `skills\`（会与共享库并列，可能造成同名冲突，谨慎）。
