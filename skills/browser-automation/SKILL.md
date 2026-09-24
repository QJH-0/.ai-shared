---
name: browser-automation
description: >
  统一的浏览器自动化套件（内含两条互斥通道，先读正文「路由表」再选引擎）。
  网页操作（导航/填表/截图/数据提取/UI 流程调试）→ Playwright："打开网页"、"填表"、"截图"、"抓取数据"。
  可复跑 Web 测试（E2E/功能验证/需托管被测服务器）→ Webapp Testing："测试这个网页"、"E2E测试"、"验证前端功能"。
  合并自: playwright, webapp-testing
  边界：搜索、登录态抓取、社交媒体内容抓取（小红书/微博/推特等）归 web-access；本 skill 只做页面操作与可复跑测试，不承接通用联网检索。
metadata:
  version: "2.4.0"
  category: browser-automation
  playwright_min_version: "1.62.0"
triggers:
  - 浏览器
  - browser
  - playwright
  - 网页
  - 截图
  - 表单
  - E2E
  - 测试
  - 自动化
  - 爬虫
  - scrape
---

# Browser Automation — 统一浏览器自动化套件

## 路由表

| 用户意图 | 引擎 | 详细指南 |
|---------|------|---------|
| Web 应用测试（可复跑 E2E / 功能验证） | **Webapp Testing** | `webapp-testing/SKILL.md` |
| 网页操作（导航/填表/截图/抓取） | **Playwright** | `playwright/SKILL.md` |

**判定顺序（自上而下，先命中先停，两条通道互斥）：**

1. **任务是可复跑的 Web E2E / 功能验证**（有固定用例、需要断言、需要脚本留痕） → Webapp Testing（自带服务器生命周期管理）
2. **其余网页操作**（导航 / 填表 / 截图 / 抓数据 / UI 流程调试 / 探索性点一点） → Playwright（兜底默认）

**边界说明（易混点）：**

- ⚠️ 「测试」≠ 一律走 Webapp Testing。**有固定用例、要能重跑**（断言 + 可进门禁）才是它；**一次性看看、没有预设用例**的也属于网页操作，走 Playwright。
- ⚠️ Playwright 是**兜底默认**，不是"优先级最高"。先用上面第一条判定，不命中才落到它。

**不覆盖范围（命中即环境阻塞，不要硬上）：**

- **Electron / 桌面应用**（VS Code、Slack、Discord、Figma、Notion 等）——本机环境无对应引擎（原 Agent Browser 通道不支持 Windows，已移除）。命中时**记录为环境阻塞并报告给用户**，不要拿 Playwright 硬套桌面应用进程，避免假阳性。
- **真机 / 移动端系统级交互**——同上，不在本套件能力内。

**切换信号（跑到一半发现选错了，按此切）：**

| 出现的信号 | 根因 | 应切到 |
|---|---|---|
| 连不上 localhost / 服务没起 | 缺服务器生命周期管理 | Webapp Testing |
| 需要断言、脚本要可复跑进门禁 | CLI 命令流不留可复跑产物 | Webapp Testing |
| 只想看一眼页面状态、没有固定用例 | 无需断言与脚本留痕 | Playwright |

---

## Playwright — 网页自动化（详见 `playwright/SKILL.md`）

CLI-first 浏览器自动化，支持导航、表单填写、截图、数据提取。

**走它**：通用网页操作（导航 / 填表 / 截图 / 抓数据）、UI 流程调试、多标签、trace 录制。
**不走它**：需要断言、脚本要可重跑 → Webapp Testing。

> **v1.62.0+ 变更**：Playwright 已将 `playwright-cli` 内置到主包中，通过 `npx playwright cli` 调用。旧的独立包 `@playwright/cli` 已废弃——**不要安装、不要引用**，其版本号无需跟踪。

**前置检查：**
```bash
command -v npx >/dev/null 2>&1  # 确保 npx 可用
```

**核心命令（先 `snapshot` 拿 ref，再按 ref 操作）：**
```bash
export PWCLI="$HOME/.ai-shared/skills/browser-automation/playwright/scripts/playwright_cli.sh"

"$PWCLI" open https://example.com      # 打开页面（注意：子命令是 open，没有 navigate）
"$PWCLI" snapshot                      # 拿稳定元素 ref（e3 / e15 …）
"$PWCLI" click e3                      # 点击 ref
"$PWCLI" fill e5 "user@example.com"    # 按 ref 填值
"$PWCLI" type "search terms"           # 向当前焦点输入
"$PWCLI" press Enter
"$PWCLI" screenshot                    # 截图（可带 ref：screenshot e5）
"$PWCLI" pdf                           # 导出 pdf
```

> ⚠️ `click` / `fill` 的参数是 **ref（`e3`）不是 CSS 选择器**；导航、点击引起界面大变、开关弹窗、切标签后 ref 会失效，**必须重新 `snapshot`**。
> ⚠️ 本通道是 CLI 操作流，**不要**擅自转成 `@playwright/test` 测试文件（除非用户明确要测试文件）。
> 完整命令表见 `playwright/references/cli.md`（导航 / 键盘 / 鼠标 / 标签 / DevTools / 命名会话）。

---

## Webapp Testing — Web 应用测试（详见 `webapp-testing/SKILL.md`）

使用 Playwright（**Python 脚本形态**）进行端到端测试，支持服务器生命周期管理。

**走它**：可复跑的 E2E / 功能验证，需要**断言**、需要脚本留痕进门禁，被测服务需要**被托管启停**（尤其前后端多服务器）。
**不走它**：一次性的网页操作 / 探索式点一点 → Playwright。

**决策树：**
```
任务 → 静态 HTML？
├─ 是 → 直接读取 HTML → 用选择器写 Playwright 脚本
└─ 否 → 服务器已运行？
    ├─ 否 → python scripts/with_server.py --help
    └─ 是 → 侦察→操作：导航→截图→识别选择器→执行
```

**关键脚本：**
- `scripts/with_server.py` — 管理服务器生命周期（支持多服务器）

**用法：**
```bash
# 先 --help；再托管服务器执行自己的脚本
python scripts/with_server.py --server "npm run dev" --port 5173 -- python your_automation.py

# 多服务器（后端 + 前端）
python scripts/with_server.py \
  --server "cd backend && python server.py" --port 3000 \
  --server "cd frontend && npm run dev" --port 5173 \
  -- python your_automation.py
```

> ⚠️ 动态应用**不能**在 `networkidle` 之前检视 DOM：脚本里先 `page.wait_for_load_state('networkidle')` 再截图 / 读 DOM。这是本通道最常见的假失败来源。
> ⚠️ `with_server.py` 当**黑箱用**：先 `--help`，不要读它的源码（脚本很大，会污染上下文窗口）。
> 参考示例见 `webapp-testing/examples/`（元素发现、静态 HTML、console 日志）。

---

## 通用注意事项

1. **先检查环境** — Node.js/npm/npx 可用；还需 Playwright 浏览器二进制，缺失则 `npx playwright install`
2. **先按判定顺序分流** — 可复跑 Web E2E → Webapp Testing；其余 → Playwright
3. **测试场景用 with_server.py** — 自动管理服务器启停，会话结束不留孤儿进程
4. **等待语义按引擎来** — Playwright：ref 失效就重新 snapshot；Webapp Testing：动态应用必须先 `wait_for_load_state('networkidle')` 再检视 DOM，禁止用 sleep 代替等待
5. **证据留存** — 失败用例截图 / trace 落盘，console 报错与网络失败同样计入证据
6. **截图优先** — 遇到问题时先截图确认页面状态
