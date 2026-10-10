# 交互与动效选型：优先用成熟实现，不自己造轮子

本技能**只在单文件、离线可开这一条上保留自研**，其余能力一律先找成熟实现。

判断标准只有一条：**手写的那段逻辑，是不是本技能的独有价值？**
是（语义驱动的模拟器引擎）→ 自己写；不是（图表、动效、壳、检索、高亮、主题）→ 用成熟实现。

---

## 三层升级路径

| 层 | 手段 | 体积 | 何时用 |
|---|---|---|---|
| **L1** | 平台原生 API / CSS | 0 字节 | 默认。绝大多数交互与动效都能覆盖 |
| **L2** | 把成熟库**内联**进单文件 | 数十 ~ 数百 KB | 需要库能力，又必须保持单文件离线 |
| **L3** | 换成成熟**文档框架** | 多文件站点 | 页面数多（>15）、要站内搜索 / 多语言 / 版本化 |

- L1 → L2 的判据：**平台原生做不到，且该能力不是本技能的独有价值。**
- L2 → L3 的判据：**单文件已经不是需求**（读者接受用本地静态服务打开站点）。

---

## L1：平台原生（零依赖，优先用）

| 需求 | 别手写 | 用 |
|---|---|---|
| 页面 / 节点状态切换动效 | 自己用 `requestAnimationFrame` 写补间 | CSS `transition` / `@keyframes`；需 JS 精确控制时用 **Web Animations API** |
| 切页转场 | 自己叠两层 DOM 做淡入淡出 | **View Transitions API**（`document.startViewTransition`） |
| 暗色主题 | 自己写主题切换 + `localStorage` + 手动应用 | `@media (prefers-color-scheme: dark)` 覆盖 **CSS 变量** |
| 阅读进度条 | 监听 `scroll` 手算比例 | `animation-timeline: scroll()`（滚动驱动动画），或直接复用已有的页码状态 |
| 目录 / 详情联动高亮 | 手算滚动位置与阈值 | **IntersectionObserver** |
| 模态 / 确认框 | 手写遮罩、焦点陷阱、Esc 关闭 | **`<dialog>`** 与 **Popover API**（自带顶层与可访问性） |
| 平滑滚动 | 自己写缓动函数 | `scroll-behavior:smooth`、`scrollIntoView({ behavior })` |
| 响应式栅格 | 手写一堆断点 | CSS Grid `auto-fit` / `minmax` |
| 内容折叠 | 手写展开动画 + `max-height` 估算 | **`<details>`**，或 `grid-template-rows: 0fr → 1fr` |

**L1 的典型错误**：把「跟随系统暗色」做成一个主题切换按钮。那是平台能力，不该由应用实现。

---

## L2：内联成熟库

把库先取到本地（`npm i` 或下载 release），再用脚本内联——**脚本本身不联网**，
`node_modules` 里的文件可直接指路径。

```bash
python <skill_dir>/scripts/embed_asset.py docs/链路手册.html \
  --css node_modules/prismjs/themes/prism.css \
  --js  node_modules/prismjs/components/prism-core.min.js \
  --js  node_modules/prismjs/components/prism-python.min.js \
  --license MIT

# 查看已内联的资产与其 hash（判断是否需要更新）
python <skill_dir>/scripts/embed_asset.py docs/链路手册.html --list
```

| 需求 | 成熟库 | 大致体积 | 许可 |
|---|---|---|---|
| 代码高亮 | **Prism.js**（core + 按需语言） | 核心 ~2 KB + 每语言 ~1 KB | MIT |
| 离线全文检索 | **MiniSearch**（或 lunr） | ~10 ~ 30 KB | MIT |
| 列表增删动效 | **@formkit/auto-animate** | ~3 KB | MIT |
| 关系图缩放 / 拖拽 | **svg-pan-zoom** / **panzoom** | ~10 KB | MIT / MIT |
| 时序动效编排 | **GSAP** | 核心 ~25 KB | 自定义（非商用免费，商用需授权） |
| 交互式大图（力导向） | **Cytoscape.js** / **d3** | 数百 KB | MIT / ISC |
| 图表（本技能主用） | **Mermaid** / D2 / Graphviz | 见 `html-atlas-spec.md` 第二节 | MIT 等 |

内联的三条硬性要求：

1. **打上来源 + 版本 + 许可注释**——`embed_asset.py` 自动加，缺许可时会告警。
2. **体积写进交付说明**。单文件超过约 2 MB 就该考虑 L3，或只保留真正用得上的模块
   （例如 Prism 只装用到的语言，不要拉全家桶）。
3. **内联后必须重跑真实浏览器回归**（`browser_regression.py`）并截图核对暗色主题。
   第三方库常自带全局样式，会与既有 CSS 打架。

---

## L3：换成熟文档框架（放弃单文件时）

页面数 > 15，或需要站内搜索、多语言、版本化、多人协作时，自研壳已经不划算。

| 框架 | 强项 | 备注 |
|---|---|---|
| **MkDocs Material** | 文档站最省心：导航 / 搜索 / 暗色 / 锚点 / 代码复制开箱即用，有 Mermaid 插件 | Python，输出多文件 |
| **VitePress** | Vue 生态，内置搜索与暗色，构建快 | Node，输出多文件 |
| **Starlight**（Astro） | 默认自带 a11y / 搜索 / i18n，扩展干净 | Node |
| **Docusaurus** | 生态最大、插件最多，适合多版本产品文档 | Node |

代价讲清楚：**放弃「双击 HTML 就能开」**，改成静态服务（`mkdocs serve` / `pnpm docs:dev`）或托管。
如果读者是外部交付方、明确要求单文件，就留在 L1 / L2。

迁移姿势：本技能产出的**链路清单与四要素骨架可直接复用**——`chain-template.md` 本身就是纯
Markdown，换框架只换壳，不重写内容。

---

## 落地顺序（写每个交互前过一遍）

1. 这个能力平台原生有没有？有就用，不用库。（L1）
2. 没有，且不是本技能的独有价值 → 找一个成熟库，用 `embed_asset.py` 内联。（L2）
3. 单文件已经不是需求 → 换框架，参考 L3 表格。（L3）
4. 只有走到「语义驱动的模拟器」时，才自己写引擎，并说明为什么（`html-atlas-spec.md` 3.0）。
