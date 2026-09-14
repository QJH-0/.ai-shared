---
name: browser-automation
description: >
  统一的浏览器自动化套件（内含三条互斥通道，先读正文「路由表」再选引擎）。
  网页操作（导航/填表/截图/数据提取/UI 流程调试）→ Playwright："打开网页"、"填表"、"截图"、"抓取数据"。
  可复跑 Web 测试（E2E/功能验证/需托管被测服务器）→ Webapp Testing："测试这个网页"、"E2E测试"、"验证前端功能"。
  桌面与探索式（Electron 应用、Slack、探索性测试/dogfood/QA/bug 猎手、云端浏览器）→ Agent Browser："操作VS Code"、"自动化Slack"、"控制桌面应用"、"挖 bug"。
  合并自: playwright, agent-browser, webapp-testing
metadata:
  version: "2.2.0"
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
  - Electron
  - 桌面应用
  - 探索性测试
  - dogfood
---

# Browser Automation — 统一浏览器自动化套件

## 路由表

| 用户意图 | 引擎 | 详细指南 |
|---------|------|---------|
| Electron 桌面应用 / Slack / 探索性测试 | **Agent Browser** | `agent-browser/SKILL.md` |
| Web 应用测试（可复跑 E2E / 功能验证） | **Webapp Testing** | `webapp-testing/SKILL.md` |
| 网页操作（导航/填表/截图/抓取） | **Playwright** | `playwright/SKILL.md` |

**判定顺序（自上而下，先命中先停，三条通道互斥）：**

1. **目标是 Electron / 桌面应用**（VS Code、Slack、Discord、Figma、Notion…），**或任务是探索性测试 / QA / bug 猎手** → Agent Browser
2. **任务是可复跑的 Web E2E / 功能验证**（有固定用例、需要断言、需要脚本留痕） → Webapp Testing（自带服务器生命周期管理）
3. **其余网页操作** → Playwright（默认兜底）

**边界说明（两个易混点）：**

- ⚠️ 「测试」≠ 一律走 Webapp Testing。**有固定用例、要能重跑**（断言 + 可进门禁）才是它；**边逛边找 bug、没有预设用例**属探索性测试，走 Agent Browser 的 `dogfood`。
- ⚠️ Playwright 是**兜底默认**，不是"优先级最高"。先用上面两条判定，都不命中才落到它。

**切换信号（跑到一半发现选错了，按此切）：**

| 出现的信号 | 根因 | 应切到 |
|---|---|---|
| 连不上 localhost / 服务没起 | 缺服务器生命周期管理 | Webapp Testing |
| 目标进程是 Electron 应用，浏览器挂不上 | Playwright 无法附着桌面应用 | Agent Browser |
| 需要断言、脚本要可重跑进门禁 | CLI 命令流不留可复跑产物 | Webapp Testing |
| 没有预设用例，只想找出问题 | 无固定断言对象 | Agent Browser（`dogfood`） |

---

## Playwright — 网页自动化（详见 `playwright/SKILL.md`）

CLI-first 浏览器自动化，支持导航、表单填写、截图、数据提取。

**走它**：通用网页操作（导航 / 填表 / 截图 / 抓数据）、UI 流程调试、多标签、trace 录制。
**不走它**：需要断言、脚本要可重跑 → Webapp Testing；目标含 Electron / 走探索式 → Agent Browser。

> **v1.62.0+ 变更**：Playwright 已将 `playwright-cli` 内置到主包中，通过 `npx playwright cli` 调用。旧的独立包 `@playwright/cli`（最后版本 0.1.18）已废弃。

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
**不走它**：一次性的网页操作 / 探索式点一点 → Playwright；目标是 Electron 或探索性测试 → Agent Browser。

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

## Agent Browser — 高级浏览器自动化（详见 `agent-browser/SKILL.md`）

CDP-based 浏览器自动化，支持可访问性树和紧凑元素引用。**Rust 原生 CLI，不依赖 Playwright / Puppeteer。**

**走它**：Electron / 桌面应用（VS Code、Slack、Discord、Figma、Notion）、Slack 工作区自动化、探索性测试 / dogfood / bug 猎手、Vercel Sandbox、AWS Bedrock AgentCore 云浏览器。
**不走它**：普通网页操作与可复跑 E2E → 上面两条通道更轻、依赖更少。

**安装与自检：**
```bash
npm i -g agent-browser && agent-browser install
agent-browser --version      # 本机实测 0.27.0
agent-browser skills list    # 列出本版本可用技能
```

**加载使用指南：**
```bash
agent-browser skills get core           # 核心工作流
agent-browser skills get core --full    # 完整命令参考
```

**扩展场景：**
```bash
agent-browser skills get electron       # Electron 应用（VS Code, Slack, Discord, Figma）
agent-browser skills get slack          # Slack 自动化
agent-browser skills get dogfood        # 探索性测试 / QA / Bug 猎手
agent-browser skills get vercel-sandbox # Vercel Sandbox 微型虚拟机
agent-browser skills get agentcore      # AWS Bedrock AgentCore 云浏览器
```

> **为什么不 vendor**：本 skill 目录下**只放一份 stub**（`agent-browser/skills/agent-browser/SKILL.md`），真正的用法内容由 CLI 在运行时输出（`skills get …`），因此**永远与已安装版本对齐、不会过期**。
> 也正因如此，`electron` / `slack` / `dogfood` / `vercel-sandbox` / `agentcore` **不需要 vendor 到 `.ai-shared`** —— 它们由二进制自带，升级即生效。

---

## 通用注意事项

1. **先检查环境** — Node.js/npm/npx 可用；Playwright 路线还需浏览器二进制，缺失则 `npx playwright install`
2. **默认 Playwright，但不吞掉上游分支** — 先按「判定顺序」分流（Electron/Slack/探索性测试 → Agent Browser；可复跑 Web E2E → Webapp Testing），两条都不命中才落到 Playwright
3. **测试场景用 with_server.py** — 自动管理服务器启停，会话结束不留孤儿进程
4. **等待语义按引擎来** — Playwright / Agent Browser：ref 失效就重新 snapshot；Webapp Testing：动态应用必须先 `wait_for_load_state('networkidle')` 再检视 DOM，禁止用 sleep 代替等待
5. **证据留存** — 失败用例截图 / trace 落盘，console 报错与网络失败同样计入证据
6. **截图优先** — 遇到问题时先截图确认页面状态
