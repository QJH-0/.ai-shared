# HTML 图谱规范：分页壳 · 导航 · 图表渲染 · 模拟器契约

交付物是**单个自包含 HTML**（离线可开、无外部依赖）。这份文档给的是各部分的接口契约，
照着改 `assets/atlas-scaffold.html` 即可，不要从零写。

---

## 一、分页壳

### 结构

```html
<header class="topbar">        <!-- 固定顶栏：品牌 / 面包屑 / 翻页 / 进度条 -->
<div class="layout">
  <nav class="toc">            <!-- 左侧目录：data-page="p-xxx" -->
  <main id="pages">
    <section class="page" id="p-xxx" data-title="显示名">…</section>
    …
  </main>
</div>
<script>…</script>
```

### 硬性约定

| 约定 | 原因 |
|---|---|
| 每个页面是 `<section class="page" id="p-*" data-title="…">` | `data-title` 供面包屑与翻页按钮显示目标页名，读者不用点进去就知道下一页是什么 |
| 只有 `.page.active` 可见（`display:none` 切换） | 一次性加载全部内容，切页零延迟，且离线单文件不需要路由 |
| 页内「上一页/下一页」按钮也放在页尾 | 长页读到底后不必回到顶部 |
| URL 用 `history.replaceState` 同步 `#p-xxx` | 锚点可分享；用 replace 避免污染浏览历史（翻 20 页后按返回不该退 20 次） |

### 导航必须覆盖的**全部**入口

这是最容易漏的地方。以下每一类都必须能跳转：

1. 左侧目录（`data-page`）
2. 页尾翻页按钮（`data-goto`）
3. 顶栏上一页 / 下一页
4. 总索引表里的行内链接（`data-goto`）
5. 总关系图里的节点（DSL 链接指向 `#p-xxx`，或手写 SVG 的 `data-goto`）
6. 键盘 `←` `→` `Home` `End`
7. URL 锚点直达与 `hashchange`

**用一个事件委托同时匹配两类标记**，不要分别绑：

```js
document.addEventListener('click', function (event) {
  var el = event.target.closest ? event.target.closest('[data-goto],[data-page]') : null;
  if (!el) return;
  event.preventDefault();
  go(el.dataset.goto || el.dataset.page);
});
```

只匹配其中一个，另一类入口就会**静默失效**——表现为「有的地方能点、有的不能」，
而且因为不报错，非常容易漏测。

键盘处理要排除输入控件，否则在搜索框里按方向键会翻页：

```js
var tag = (event.target && event.target.tagName) || '';
if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
```

---

## 二、图表：用成熟 DSL 编写 + 离线预渲染

### 为什么不手写 SVG

手写内联 SVG 把三件事全压在人工上：**坐标**（布局靠肉眼试）、**箭头 marker**
（每张图都要重配一组 id）、**多图共存**（同名 id 互相覆盖，表现是「第二张图箭头消失」）。
改一处要重排全图，且极易出错。换成成熟 DSL 后，布局交给引擎，作者只描述
「谁连谁、什么条件走哪条」。

### 硬约束不变

交付物仍是**单个自包含 HTML**。所以图表必须是**构建期渲染好的静态 SVG**：
不引 CDN、不在页面里跑图表运行时——`<script src="...mermaid...">` 一样破坏离线，
还会让页面多背数 MB。一句话：**DSL 写在构建期，SVG 落在交付物里。**

### DSL 选型

| DSL | 强项 | 适合 | 备注 |
|---|---|---|---|
| **Mermaid**（默认） | 生态最广，GitHub / Notion / Obsidian 原生渲染 | 流程图（链路）、时序图（调用次序）、状态图（状态机） | 语义直白，最不容易写错 |
| D2 | 架构图排版最好，单二进制 | 分层架构、模块关系 | 需装 `d2` |
| Graphviz (DOT) | 最成熟、布局确定、依赖极小 | 大图、自动布局的关系图 | 需装 `graphviz` |
| PlantUML | 时序图最完整 | 参与者多的复杂时序 | 需 Java + graphviz |

三类图直接对应本技能的三种表达：**链路用 flowchart、时序用 sequence、状态机用 state**。
一张图仍只表达一条链路，节点控制在 6~12 个，超了就拆页。

### 渲染与内联

用 `scripts/render_diagrams.py`：调用渲染器 → 净化 SVG → 回填 HTML 槽位。

```bash
# 查看本机有哪些渲染器（不联网、不安装）
python <skill_dir>/scripts/render_diagrams.py --check

# 渲染并回填到槽位
python <skill_dir>/scripts/render_diagrams.py diagrams/order-flow.mmd \
  --into docs/链路手册.html --slot order-flow

# 批量：diagrams/*.{mmd,mermaid,d2,dot,gv} 按文件名词干回填同名槽位
python <skill_dir>/scripts/render_diagrams.py --batch diagrams --into docs/链路手册.html

# 纯离线：只内联已经渲染好的 SVG（本机无任何渲染器也能交付）
python <skill_dir>/scripts/render_diagrams.py build/order-flow.svg \
  --into docs/链路手册.html --slot order-flow
```

HTML 里先放好成对槽位标记；脚本只替换标记之间的内容，且**槽位不存在时直接报错**
（不静默新建，避免图被塞进错误位置）：

```html
<div class="diagram">
  <!-- atlas:diagram order-flow -->
  <!-- /atlas:diagram order-flow -->
</div>
```

**为什么必须经脚本回填、不要手工把 SVG 贴进去**：脚本会自动做四件事，手做极易漏：

| 脚本自动完成 | 漏掉会怎样 |
|---|---|
| 去 XML 声明 / DOCTYPE / 注释 | 内联后是无效节点，或注释里的字符破坏解析 |
| **全量 id 命名空间化**（`id`、`#id`、`url(#id)` 一起改） | 多图同名 `id` / arrow marker 互相覆盖 → 后画的图箭头消失 |
| 去掉根元素 `width` / `height` / `style` | 渲染器写死的 `max-width` 让图不再随内容列自适应 |
| 加 `class="flow"` + `role="img"` | 图不响应 CSS 尺寸；缺可访问性语义 |

`svg.flow` 的尺寸由 CSS 统一控制（`width:100%; height:auto`），所以图必须带 `viewBox`
（渲染器通常会写；脚本会在缺失时告警）。

### 图内节点可点击（读者才能顺着链路走）

优先用 DSL 自带的链接能力，让点击走 **URL 锚点**，页面已有的 `hashchange` 处理器会接住：

```mermaid
flowchart LR
  A[发起请求] --> B[编排] --> C[执行]
  click A href "#p-l1"
  click B href "#p-l2"
```

- Mermaid：`click <节点ID> href "#p-xxx"`
- D2：在节点上写 `link: "#p-xxx"`
- Graphviz：节点属性加 `URL="#p-xxx"`

这一层与分页壳的事件委托仍然兼容：`closest()` 对 SVG 元素同样有效，
`[data-goto]` / `[data-page]` 的委托处理器不用改；遇到 `<a>` 则走锚点。

### 配色（层次编码，全篇一致）

| 层次 | 颜色 |
|---|---|
| 前端 / 客户端 | `#8250df` |
| API / 网关 | `#0969da` |
| 编排 / 任务 | `#9a6700` |
| 智能体 / 业务节点 | `#1a7f37` |
| 事件 / 流 | `#cf222e` |
| 存储 / 外部依赖 | `#57606a` |
| 人工介入 | `#bc4c00` |

**不要把颜色写死在每张图里**，二选一：在 DSL 里定义 `classDef` 后复用，或在 HTML 的 CSS 里
覆盖。脚本去掉了根元素的内联 `style`，所以外部 CSS 能生效，深色主题也能一次覆盖全篇。

### 逃生通道：确实要手写 SVG 时

只在渲染器不可用、又必须精细控制时使用。此时遵守：

- 每张图自己的 `<defs>` + **唯一 marker id**（命名带图号，如 `ar1` / `ar5d`），否则箭头消失。
- 文本用 `text-anchor:middle` + `dominant-baseline:middle`，坐标给矩形中心，不要手工调基线。
- 失败 / 降级分支用 `stroke-dasharray:4 3` + 红色，与正常路径区分。
- 根元素保留 `viewBox`，尺寸交给 CSS。

---

## 三、模拟器契约

模拟器是这份交付物区别于普通文档的核心。它的价值全在**语义驱动**——如果只是定时播放
几段预设动画，那就是装饰品，读者一眼能看穿。

### 3.0 为什么这一层不换成现成图库

图表（上一节）换成成熟 DSL 是对的；模拟器则相反。现成的流程动画库（React Flow、
Cytoscape.js、vis-network 等）能画节点与连线，但不知道「这一刻该发哪个事件、该挂起
还是该在下一个节点边界收口」——那层语义只能按真实代码自己写。所以保留自研引擎，
但把**节点渲染**留成薄层：`renderNodes()` 之外的状态与事件逻辑不依赖 DOM 结构，
真需要缩放 / 拖拽 / 自动布局时，把这一层换成成熟图库即可，语义层不动。

### 3.1 必须来自真实代码的四类信息

| 模拟器元素 | 必须取自 |
|---|---|
| 节点名与顺序 | 真实代码里的节点常量与图的边定义 |
| 事件名与载荷字段 | 真实的事件枚举与各处的 emit 调用 |
| 序号 / 游标语义 | 真实的序号分配逻辑（行锁自增 / 单调游标） |
| 状态迁移 | 真实的状态机枚举与迁移条件 |

在页面显著位置说明这个对应关系（读者据此判断可信度）。

### 3.2 场景脚本的数据结构

用**声明式步骤数组**，不要写成命令式的一长串 `setTimeout`：

```js
{ k: 'note',   text: '…' }                    // 注释行（灰色斜体），解释「这里发生了什么」
{ k: 'emit',   type: 'EVENT_NAME', payload: {} }  // 事件：seq 自增 + 落日志
{ k: 'node',   id: 'node.id', s: 'start' }    // 'start' | 'end' | 'hitl' | 'err'
{ k: 'status', status: 'running', phase: 'x' } // 注意：允许只给 phase 不给 status
{ k: 'text',   text: '增量正文…' }             // 流式输出
{ k: 'source', value: {…} }                   // 追加一条来源（自动去重）
{ k: 'budget', tools: 1, rounds: 2 }          // 累加计数
{ k: 'awaitHitl' }                            // 阻塞等待人工应答
{ k: 'wait',   ms: 300 }
```

声明式的好处：场景可读、可 diff、可被测试直接断言。

### 3.3 三个必须实现的机制

#### (a) 代际令牌——防止旧循环污染新场景

**症状**：切换场景后，界面里仍然混着上一个场景的内容。

**根因**：`reset()` 只替换了状态对象，**在飞的旧循环仍以共享变量为迭代目标**，
于是继续把旧场景的步骤灌进新状态。

**实现**：

```js
var runToken = 0;

function reset() {
  runToken += 1;                          // 作废所有在飞的循环
  if (S && S.hitlAbort) S.hitlAbort();    // 解除可能挂起的等待，否则旧循环永久泄漏
  S = { /* 全新状态 */ };
}

async function run() {
  if (!S || S.running) return;
  var myToken = runToken;
  while (S.idx < S.script.length) {
    if (myToken !== runToken) return;     // 已被接管 → 静默退出，不碰任何 UI
    …
    var wait = apply(step);
    if (wait instanceof Promise) { await wait; } else { await sleep(wait); }
  }
  if (myToken !== runToken) return;       // 收尾也只属于当前代际
  …
}
```

配套两点：

- `sleep()` 用**局部定时器**（`return new Promise(r => setTimeout(r, ms))`），
  不要用模块级共享的 `timer` 变量——否则 `reset()` 里的 `clearTimeout` 会误杀新循环的定时器。
- `awaitHitl` 返回的 Promise 必须同时暴露一个 `abort` 出口，让 `reset()` 能解除它。

#### (b) 状态更新要容忍「只切 phase」

脚本里大量存在「进入某阶段」这类步骤，它只改 phase、不改 status。
如果无条件 `setStatus(step.status)`，状态胶囊会显示字面量 `undefined`。

```js
case 'status':
  if (step.status) { S.status = step.status; setStatus(step.status); }
  if (step.phase)  { S.phase  = step.phase;  /* 更新 phase 标签 */ }
  return 160;
```

#### (c) 内容渲染一次成型，不要二次查询

```js
// ✗ 脆：先写结构再 querySelector 回填
el.innerHTML = rows.map(…).join('');
var nodes = el.querySelectorAll('.x');
items.forEach((it, i) => { nodes[i].textContent = it.title; });

// ✓ 稳：一次性转义拼接
el.innerHTML = items.map(it =>
  '<div class="src"><span>' + esc(it.id) + '</span><span>' + esc(it.title) + '</span></div>'
).join('');
```

`esc()` 做 `& < > " '` 五个字符的转义，安全性等价于 `textContent`，但代码更短、无二次依赖。

### 3.4 控制项与联动面板

| 控件 | 行为 |
|---|---|
| 场景下拉 | **切换即自动重播新场景**（否则用户切完以为「没用」） |
| 播放 | 从当前场景**重新开始**（不区分「首次」与「重播」，行为可预测） |
| 暂停 / 继续 | 暂停循环（代际令牌不受影响） |
| 重置 | `reset()`，清空全部面板 |
| 取消运行 | 置取消标记，**在下一个节点边界**收口（演示协作式取消的语义） |
| 批准 / 拒绝 | 仅在挂起时可用；拒绝要走真实的拒绝分支 |

联动面板建议四块：**图节点执行** / **状态与预算** / **事件流日志** / **输出正文**。
日志用等宽字体、逐行追加、自动滚底，并按事件类型着色。

---

## 四、可访问性与可读性

- 状态用**文字 + 颜色**双重编码（色盲用户靠文字也能读懂）。
- 正文行宽限制在 78~90 字符。
- 打印友好：`.page` 的 `display:none` 在 `@media print` 下应改为全部展开（可选但推荐）。
- 移动端：窄屏隐藏左侧目录，靠顶栏翻页。
- **暗色主题跟随系统**：用 `@media (prefers-color-scheme: dark)` 覆盖 CSS 变量，
  **不要**写主题切换按钮 + `localStorage`——跟随系统是平台原生能力。
  前提是颜色必须走变量：硬编码颜色会让暗色下「一半亮一半暗」。脚手架已按此实现。
- 想要「切页 / 切状态」的平滑过渡时用 **View Transitions API**，但要知道它**异步**执行回调，
  「点击后立刻查 `.page.active`」这类同步断言会失效——探针需改成等待一帧再断言。
- 高亮 / 检索 / 图缩放等库能力见 `ui-tech-choices.md`，用 `scripts/embed_asset.py` 内联。
