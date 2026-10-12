# 本地扩展记录（archify）

> 上游基线：`tt-a1i/archify` v3.0.1（MIT），已展平安装为 `skills\archify\`，**未保留 `.git`**。
> 下列改动是**本地扩展**，不属于上游；上游若更新（`finalize` 会提示 update 通知），需在刷新后按本文件重新套用。

## 2026-10-12：一次到位契约（one-pass completeness）

### 起因

本机第一次用 archify 给 `deepresearchagent` 出图时，只产出一张 14 节点 / 17 关系的浅层总览，随后经历了三轮追加对话（补细架构 → 补时序 → 补数据流与状态机）才达到可用深度。复盘出四个可固化的缺陷：

1. `references/authoring-defaults.md` 的「默认给系统总览、由主用户旅程领读」被理解为"只画主链路"，把后台任务、存储、横切层当成可选补充。
2. 真实容量上限（sequence 桌面 930px 预算、dataflow 只有 4 个 stage 可用、`row` 只能 0..4 等）没有前置，导致先写后拆、反复返工。
3. 引用行号没有在写入前核验；子代理给的 `db/models/chunk.py:206` 实际不在该文件（真实位置在 `db/repositories/chunk.py:209`），触发 `repository-evidence/line-out-of-range`。
4. 环境与证据卫生问题消耗了两轮：IDE 注入的 Node loader 让 `finalize` 报 `…hardlinked` 假失败；重发时 `browser-check` 拒绝覆盖上一版未归属的证据文件。

### 改动文件

| 文件 | 改动 |
|------|------|
| `references/one-pass-completeness.md` | **新增**。范围触发、默认视图集、覆盖清单（8 项）、实测容量上限表、引用核验规则、环境与证据卫生 |
| `SKILL.md` | 「Fast authoring path」第 1、3 步各加一句范围与核验要求；新增「One-pass completeness (local extension)」小节；「Setup and fallback」加 Node loader 预检 |
| `references/authoring-defaults.md` | 「Composition and meaning」两处补丁：系统级请求的 overview = **完整运行时表面**且交付**视图集**；禁止把真实组件/关系降级塞进卡片 |
| `references/repository-authoring.md` | 「Trace ownership」补：系统级请求下后台/异步 worker、存储、外部系统、改变行为的横切层都在范围内；「Record evidence while reading」补：写入前核验每段引用在冻结 revision 内存在 |

### 契约要点（会给后续每次出图带来什么）

- 仓库/系统级请求默认交付**视图集**：完整运行时的 architecture + 源码支持的 sequence / dataflow / lifecycle，各自独立目录、各自 `finalize`，一次交付。
- 写候选图**之前**先按容量上限决定拆几张：sequence ≤8 参与者 / ≤22 消息、dataflow ≤4 stage、lifecycle `col` 0..4、architecture 画布 ~1070px 内。
- 覆盖清单逐项确认（进程/入口、后台与异步、每个存储的读写方、外部系统、横切层、失败路径、状态门禁、配置来源），排除项必须在卡片与回复中说明。
- 引用先核验再写入；不采信摘要或子代理给的行号。
- 出图前 `$env:NODE_OPTIONS=''`；重发前把旧证据移入 `published-r1/` 或 `review-N/`。

### 与上游的差异定位

所有改动均在文内以 `[local extension 2026-10-12]` 标注（新增文件在标题注明），便于上游刷新后 `diff` 出本地补丁；上游同步后请重新套用并更新本文件日期。
