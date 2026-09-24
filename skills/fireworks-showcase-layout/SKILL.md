---
name: fireworks-showcase-layout
description: 用 fireworks-tech-graph 画「论文级」结构图时，如何设计版式一次过 showcase 硬门禁（折点预算 8、微段 16px、桥接交叉 0、文本零截断），以及如何保证重绘图与原图逐行文字/元素一致。适用于：手写契约 JSON 生成结构图、把 Mermaid/论文插图重绘成 SVG/PNG、撞上 EDGE_BEND_BUDGET / EDGE_MICRO_SEGMENT / BRIDGE_BUDGET / TEXT_FIT / EDGE_ROUTE_STRETCH 反复调坐标调不动。核心教训：这些门禁是「设计期约束」不是「调参问题」，超预算要重构版式而不是挪坐标。
agent_created: true
---

# fireworks-tech-graph 的 showcase 版式设计

## 适用场景

- 用 `fireworks-tech-graph` 的 `render` 生成结构图，`quality_profile: "showcase"`，反复撞构图门禁。
- 手填坐标（`nodes[].x/y/width/height` + `arrows[]`），而不是让上游自动布局。
- 需要把已有的 Mermaid / 论文插图**逐行保真**重绘，不允许压缩文字或删减元素。

不适用：用 `export-png` 的常规出图、统计图表、纯装饰插画。

## 一、先读源码，别猜渲染器能力

`fireworks-tech-graph` 的 SKILL.md 不写这些边界，必须读 `scripts/`：

| 事实 | 位置 |
| --- | --- |
| 节点只有 `label` / `sublabel` 两条文本通道，且都过 `fit_single_line_text`（折叠空白 + 超宽截断，strict 下报错） | `generate-from-template.py` `render_rect_node` / `fit_single_line_text` |
| 想放多行必须**扩展渲染器**加 `body: [行,...]`；不传 `body` 时输出与上游逐字节一致 | 见 `references/fwg_layout.py` 顶部说明 |
| 容器**只有标题头**是路由障碍（`container_header_bounds`），容器本体不是，边可自由穿越边框 | `section_obstacles` 只取 `container_header_bounds` |
| 容器不能当连线端点，必须接到容器内真实节点 | 报 `references unknown node` |
| 容器标签默认强制大写，需 `preserve_case: true` 才保住原文案 | `section_header_text` |
| 节点文本预算 = `width − 24`；宽度用 `fireworks_geometry.estimate_text_width` 反算 | `render_rect_node` 的 `title_budget` |
| 边按**契约声明顺序**依次定线，先声明的先占走廊 | `routing_order` = 声明序 |
| 打分 `score = length + bends×22 + crossings×640 + 端口轴不符×180`，走廊提示只值 −28 | `route_score` |
| 同一 `(节点, 端口)` 上 n 条边会被摊开 `min(18, (span−24)/(n−1))` px | `prepare_arrows` |
| 标题/副标题画在画布顶部**固定位置**（副标题基线 y=82），且**不在障碍表里** | 见 §四 |

## 二、showcase 门禁的硬数字（`composition_quality.py` 的 `PROFILES["showcase"]`）

```
max_bends_per_edge = 2      max_total_bends = 8        max_route_stretch = 1.35
max_bridged_crossings = 0   min_node_gap = 40          min_container_gutter = 20
min_label_clearance = 4     min_segment_length = 16
```

**`max_total_bends = 8` 是全图总和**，是最容易超的一条。开工前先算：

> 折点预算算法：数出「无法做成直线」的边，逐条给最小折点，加起来 ≤ 8 才动手画。
> 水平链上的边、同轴竖直边都是 0 折点；换带（行末→下一行行首）天然 2 折点。

## 三、六条能显著省折点/避交叉的版式手法

1. **让竖直边同轴** —— 上游节点的水平中心与下游节点对齐，竖直边 0 折点。
   把整条带横向平移对齐即可（平移量保持浮点，取整会引入 0.5px 微段）。
2. **合并节点内联，别做右侧竖列** —— 若有一条主干汇合点（如 Skip 求和）要接来自多行的边，
   把它和后续节点**内联到中间那条带右侧**，让各条汇入边分别落在它的 `top`/`left`/`bottom` 端口上，
   每条只需 1 折点。做成右侧竖列会逼出 2~3 折点，且竖直边的目标端口会被后续节点挡住。
3. **长旁路走主行上方浅弧，且主行用统一带高** —— `route_stretch = (D + 2d)/D`（D 为横跨宽度，d 为折回深度），
   上限 1.35 ⇒ `d ≤ 0.175·D`。旁路压在支路下方时 d 很快吃满预算，改走上方只留一条浅弧。
   关键细节：主行若逐节点按自身高度居中（`emit_centered`），`in.top` 会比带顶低十几像素，
   横跨全宽的旁路绕行距离凭空多一倍高度差 —— **用 `emit_band` 给整行统一带高**，
   再把带距压到 65px 左右，才落得进预算。
4. **短直边先声明** —— 交叉权重 640 远高于折点 22。把 `n2→sk` 这类短直边写在 `in→add` 长旁路**之前**，
   长旁路自己会绕开，而不是短边被迫穿过它。
5. **短竖边上的边标签要短** —— 标签 bounds 会被当作后续边的路由障碍。一条 65px 的竖边配上
   235px 宽的长标签，放到竖线一侧后（加 24px padding）正好盖住旁边旁路的必经走廊，
   于是旁路只能贴着主行绕行 → 桥接交叉 + 折点 4 + stretch 1.404 一起爆。
   把标签缩到「concat 注入」这种量级（bounds ≈ 87px），旁路立刻走回上方浅弧。长解释放节点正文里。
6. **同排高度不等就按中心对齐** —— 一律顶对齐会让水平连线的端口差出半个高度差，几像素的落差就是一条微段
   （`emit_centered` 负责这件事）。注意与第 3 条配合：需要长旁路的行用统一带高，其余行才用中心对齐。

## 四、构图门禁查不到的三类缺陷（必须自己防）

1. **容器标题头压副标题** —— 副标题基线固定 y=82 且不是障碍。容器标题头基线 = 容器顶 + 24，
   故容器顶须 ≥ 90（`CONTAINER_TOP_MIN`，推导：副标题底 ≈86 + 标题头文字高 ≈10 + 6px 间隙 ⇒ ≥78，再留 12 余量）。
2. **图例色块与边色不一致** —— 边色由 `style.arrow_colors` 决定；`FLOW_ALIASES` 里没有的 flow 名会
   **静默回落到 control**，而箭头 marker 是按色值反查的，色值不在表里就退化成 control 的箭头。
   ⇒ **图例颜色必须从 `STYLE_PROFILES[style]["arrow_colors"]` 取**（`importlib` 载入该模块约 0.5s、无副作用），
   并给每条边**显式写 `color`**，让线色 / 图例色块 / 箭头 marker 三者同源。语义 flow 名要先经一张映射表落到调色板真实键上。
3. **图例里有没被任何边使用的条目** —— 换版式时旧条目忘了删，图例就开始误导读者。

## 五、重绘的保真纪律

原图（Mermaid / 论文插图）是唯一事实源，重绘只改版式、不改内容：

- 节点文字**逐行**搬：首行进 `title`，其余行全进 `body`，不合并不省略不改写。
- 连线按「**成员归属**」比对，不按字面 id：原图 `convIn --> Stage1`（子图）在契约里落到子图首/末个真实节点上。
- 原图 `-.->`（虚线）与 `-->`（实线）的区分**是图片要素**，要逐条还原；
  注意同一条语义流里可能只有部分边是虚线（例：`n2 --> sk` 实线、`in -.-> add` 虚线）。
- 写一个核对器脚本，逐项断言：节点文字逐行相等、无多余节点、子图标签存在于容器、连线集合双向匹配、
  图例与边同色同集合、容器标题头不压副标题。**每次改版式都跑它**——保真缺陷和版式缺陷是两类问题，门禁只查后者。
- 一个仓库里有多份事实源（多个模型）时，把核对器的 `--source <md>` 与 `--dir <dir>` 做成参数，
  默认值保持原行为，一套脚本服务全部事实源；每份事实源配一个自己的契约目录。
- 事实源是**手写**的时候，先逐行核对代码再落笔：文档里的结构描述常与实现漂移
  （本轮就抓到「某条通路其实不过共享投影层」「某模块其实没有 Skip 分支」两处），
  图一旦画错，比没有图更糟。**代码是权威**，文档错误要当场记下来并订正。

## 六、参考实现

`references/fwg_layout.py` 是本次落地的版式模块，可直接复制到新项目（只需改顶部 `SKILL_ROOT`）：

- `natural_width` / `natural_height`：按文本反算节点尺寸，与渲染器的 `NODE_LINE_HEIGHT` 同源。
- `band` / `emit_band` / `row_height`：一条带内节点与容器统一 y 与高度，水平连线天然端口对齐。
- `emit_centered`：同排高度不等时按**中心**对齐（顶对齐会让水平连线两端差半个高度差 = 一条微段）。
- `panel_pad_for`：把容器左内边距顶到标题头障碍右侧（顶部进线的容器才需要）。
- `flow_color`：从渲染器样式表取 flow 色，图例与边色同源。
- `CONTAINER_TOP_MIN`：容器顶下界。
- `Figure.edge`：显式写 `color`，并支持 `dashed` / `corridor_x` / `corridor_y`。
- `render_and_check`：渲染 + 5 项 check + 读排版报告，一行拿到 `text=完整/截断` 与各项 ok。

## 七、PNG 导出（本机无 cairo，用浏览器通道）

`fireworks.py export-png` 依赖 cairo；改用 `scripts/svg2png.js`（Puppeteer + 系统 Chrome，2× deviceScaleFactor）：

```bash
NODE_PATH="<node-workspace>/node_modules" \
FIREWORKS_PYTHON="<可用解释器>" \
node scripts/svg2png.js "<目标目录的 Windows 路径>"
```

两个坑：目录参数必须是 **Windows 风格路径**（Git Bash 的 `/d/...` 会被解析成 `D:\d\...` → ENOENT）；
必须设 `FIREWORKS_PYTHON`（默认 `python3` 可能不存在）。脚本会处理目录下**所有** `.svg`。
