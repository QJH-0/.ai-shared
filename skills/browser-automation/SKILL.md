---
name: browser-automation
description: >
  统一的浏览器自动化套件，支持 Web 页面操作、端到端测试、Electron 应用自动化。
  导航/表单/截图/数据提取: "打开网页"、"填表"、"截图"、"抓取数据"。
  测试: "测试这个网页"、"E2E测试"、"验证前端功能"。
  Electron: "操作VS Code"、"自动化Slack"、"控制桌面应用"。
  合并自: playwright, agent-browser, webapp-testing
metadata:
  version: "2.1.0"
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
---

# Browser Automation — 统一浏览器自动化套件

## 路由表

| 用户意图 | 引擎 | 详细指南 |
|---------|------|---------|
| 网页操作（导航/填表/截图/抓取） | **Playwright** | `playwright/SKILL.md` |
| Web 应用测试（E2E/功能验证） | **Webapp Testing** | `webapp-testing/SKILL.md` |
| Electron 桌面应用 / Slack / 高级自动化 | **Agent Browser** | `agent-browser/SKILL.md` |

**路由规则：**
1. 测试场景 → Webapp Testing（含服务器生命周期管理）
2. Electron/Slack/桌面应用 → Agent Browser
3. 其他网页操作 → Playwright（默认）

---

## Playwright — 网页自动化（详见 `playwright/SKILL.md`）

CLI-first 浏览器自动化，支持导航、表单填写、截图、数据提取。

> **v1.62.0+ 变更**：Playwright 已将 `playwright-cli` 内置到主包中，通过 `npx playwright cli` 调用。旧的独立包 `@playwright/cli`（最后版本 0.1.18）已废弃。

**前置检查：**
```bash
command -v npx >/dev/null 2>&1  # 确保 npx 可用
```

**核心命令（通过 wrapper 脚本）：**
```bash
export PWCLI="$HOME/.ai-shared/skills/browser-automation/playwright/scripts/playwright_cli.sh"
$PWCLI navigate <url>          # 导航到页面
$PWCLI screenshot <url> <out>  # 截图
$PWCLI fill <selector> <value> # 填写表单
$PWCLI click <selector>        # 点击元素
```

**或直接用 npx（无需 wrapper）：**
```bash
npx playwright cli open <url>
npx playwright cli screenshot
npx playwright cli click e3
```

---

## Webapp Testing — Web 应用测试（详见 `webapp-testing/SKILL.md`）

使用 Playwright 进行端到端测试，支持服务器生命周期管理。

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

---

## Agent Browser — 高级浏览器自动化（详见 `agent-browser/SKILL.md`）

CDP-based 浏览器自动化，支持可访问性树和紧凑元素引用。

**安装：**
```bash
npm i -g agent-browser && agent-browser install
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

---

## 通用注意事项

1. **先检查环境** — 确保 Node.js/npm/npx 可用
2. **优先用 Playwright** — 除非明确需要 Electron/Slack 支持
3. **测试场景用 with_server.py** — 自动管理服务器启停
4. **截图优先** — 遇到问题时先截图确认页面状态
