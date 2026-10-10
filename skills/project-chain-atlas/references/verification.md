# 验证：为什么必须用真实浏览器

## 一句话结论

**自建 DOM 桩只能验证纯逻辑，不能替代真实浏览器。** 桩在 `closest()`、`innerHTML=''`
是否清空子节点、事件冒泡这些行为上的差异，**恰好会掩盖最常见的那类缺陷**。

实测教训：两个真实缺陷——「切换场景无效」和「侧边目录点击不跳转」——用 DOM 桩测全绿，
在真实浏览器里才现形。前者是异步循环未作废，后者是事件委托选择器漏了一半入口。

---

## 分层验证策略

| 层 | 工具 | 能抓到什么 | 抓不到什么 |
|---|---|---|---|
| L1 语法 | `node --check`（抽出内联脚本） | 语法错误 | 一切运行时问题 |
| L2 结构 | 标签配对计数 | 未闭合标签 | 行为问题 |
| L3 纯逻辑 | DOM 桩 | 状态机、脚本生成、去重逻辑 | DOM 语义差异导致的缺陷 |
| L4 **真实浏览器** | 无头 Chrome + 注入探针 | **交互、事件、渲染、时序** | 视觉美观度（需人眼） |

**L4 是不可省的那一层。** L1~L3 全绿不代表能用。

---

## L4 的具体做法

用 `scripts/browser_regression.py`：

```bash
python <skill_dir>/scripts/browser_regression.py docs/链路手册.html probes/nav.js
python <skill_dir>/scripts/browser_regression.py docs/链路手册.html probes/sim.js --budget-ms 30000
```

**先用脚手架自检**（确认工具链本身可用）：

```bash
python <skill_dir>/scripts/browser_regression.py \
  <skill_dir>/assets/atlas-scaffold.html \
  <skill_dir>/scripts/scaffold_probe.js
# 期望输出 ok=15 bad=none / RESULT=PASS / [OK] 交互回归通过
```

工具做的事：把探针脚本注入 HTML 副本 → `chrome --headless=new --dump-dom
--virtual-time-budget=N` → 取回 `<div id="__result">` 的内容 → 按 `RESULT=PASS` 判定退出码。

`--virtual-time-budget` 会让 `setTimeout` 按虚拟时间加速跑完，所以几秒的动画序列
在一次命令里就能跑完，不用真的等。

### 探针脚本契约

探针必须：

1. 自己创建 `<div id="__result">` 并往里写行；
2. 注册 `window.onerror` 把 JS 报错也写进去（**这是最重要的一行**——
   静默的 JS 报错会让后面所有断言产生假阳性）；
3. 最后写一行 `RESULT=PASS` 或 `RESULT=FAIL`。

```js
(function () {
  function out(t) {
    var d = document.getElementById('__result');
    if (!d) { d = document.createElement('div'); d.id = '__result'; document.body.appendChild(d); }
    d.textContent += t + '\n';
  }
  window.addEventListener('error', function (e) { out('JSERROR=' + e.message); });

  var bad = [], ok = 0;
  function chk(name, cond) { cond ? ok++ : bad.push(name); }
  function active() { var a = document.querySelector('.page.active'); return a ? a.id : null; }

  setTimeout(function () {
    document.querySelector('#toc a[data-page="p-l4"]').click();
    chk('nav-sidebar', active() === 'p-l4');
    // … 其余断言
    out('ok=' + ok + ' bad=' + (bad.length ? bad.join(',') : 'none'));
    out(bad.length ? 'RESULT=FAIL' : 'RESULT=PASS');
  }, 400);
})();
```

### 用 `dispatchEvent` 而不是 `.click()`

对 `<select>` 要发 `change` 事件；对 SVG 元素要发带 `bubbles:true` 的 `MouseEvent`。
特别注意：**SVG 的 `<a>`（图表 DSL 链接渲染出来就是它）没有 `.click()` 方法**，
调它会抛 `TypeError: ... .click is not a function`，必须走 `dispatchEvent`：

```js
sel.value = 'direct';
sel.dispatchEvent(new Event('change'));

svgNode.dispatchEvent(new MouseEvent('click', { bubbles: true }));
```

---

## 必须覆盖的断言清单

### 导航（最少 11 条）

- [ ] 侧边目录：抽 5~6 个不同位置的条目，逐个点击后断言 `.page.active` 的 id
- [ ] 索引表行内链接（`data-goto`）
- [ ] 顶栏「下一页」/「上一页」
- [ ] 总关系图里的图表节点（DSL 链接指向 `#p-xxx`，或 `data-goto`）——点击后切到对应链路页
- [ ] 页尾翻页按钮
- [ ] 计数器与面包屑同步更新
- [ ] 键盘方向键（可选）

### 模拟器（最少 6 条）

- [ ] **运行中切换场景**（这是最容易漏、也最容易出 bug 的路径）
- [ ] 切换后**无旧场景残留**（断言日志里不含旧场景的特征文本）
- [ ] 逐场景隔离：每个场景单独跑完，断言日志含本场景特征、不含他场景特征
- [ ] 人工介入：挂起态正确 + 按钮可用 + 应答后发出恢复事件
- [ ] 取消：在下一个节点边界收口
- [ ] 状态胶囊取值集合内**不含 `undefined`**（遍历取值，断言 `undefined` 出现 0 次）

### 结构

- [ ] 标签配对：`svg` / `table` / `pre` / `div` / `section` / `script` / `style`
- [ ] 页面数 == 目录条目数 == 预期页数
- [ ] 无 `JSERROR=`
- [ ] 图表已内联：每个槽位都含 `<svg class="flow"`，且无 `<?xml` 声明残留
- [ ] 多图不冲突：抽查两张图的 marker id 前缀不同（`diag-<slot>-`），两张图的箭头都显示
- [ ] 图内节点可点：点击图表节点能切到对应链路页（DSL 链接经 `hashchange` 生效）
- [ ] 暗色主题：以暗色偏好打开并截图核对——不能「一半亮一半暗」，说明没有硬编码颜色残留
- [ ] 内联过第三方库时：`embed_asset.py --list` 能列出它，且**已重跑**上面的交互回归与暗色截图

---

## 断言设计的两条纪律

1. **断言要能失败。** 写完断言后，故意把对应功能改坏一次，确认断言变红。
   恒真的断言（例如只断言「日志行数 > 3」）比没有断言更糟——它会给人虚假的信心。
   实测教训：早期只断言「行数 > 3」，六个场景全绿，但内容其实是错的。

2. **期望值要来自产出物本身，不要凭记忆写。** 例如断言「研究场景应包含 `kb_search`」之前，
   先去脚本里确认它确实会调这个工具。写错期望会浪费一轮排查。

---

## 交付前的最终自检

```bash
# 0. 图表回填（只在图源改动后才需要；产物会直接写进 HTML）
python <skill_dir>/scripts/render_diagrams.py --check
python <skill_dir>/scripts/render_diagrams.py --batch diagrams --into docs/链路手册.html

# 1. 语法（用系统临时目录，别写死 /tmp —— Windows 下不存在）
python -c "import re,tempfile,os;p=os.path.join(tempfile.gettempdir(),'_c.js');open(p,'w',encoding='utf-8').write(re.findall(r'<script>(.*?)</script>', open('docs/链路手册.html',encoding='utf-8').read(), re.S)[-1]);print(p)"
# 把上面打印出的路径喂给 node：
node --check "<上一步打印的路径>"

# 2. 结构
for t in svg table pre div section script style; do
  echo "$t: $(grep -o "<$t[ >]" docs/链路手册.html | wc -l) / $(grep -o "</$t>" docs/链路手册.html | wc -l)"
done

# 3. 真实浏览器交互回归
python <skill_dir>/scripts/browser_regression.py docs/链路手册.html probes/all.js

# 4. 主题与内联库
#    - 以系统暗色偏好打开一次并截图核对（浅色、暗色各一张）
#    - 内联过库的话，确认记录在案，并已重跑第 3 步
python <skill_dir>/scripts/embed_asset.py docs/链路手册.html --list
```

四项全过才算交付。任何一项没跑，**在交付说明里如实写「未验证」**，不要写成通过。
