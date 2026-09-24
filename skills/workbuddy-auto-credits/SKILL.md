---
name: workbuddy-auto-credits
description: WorkBuddy 自动领积分全家桶。①每日签到：解密本机登录令牌，调用官方签到 API 自动领取每日积分（100/天，连续第 7 天 1000）；②派猫猫旅行：按状态机自动派出/领取 Buddy 旅行奖励（5~10/次，每天限 1 次）。均支持配置定时自动化。触发词：WorkBuddy 签到、每日积分、check-in、credits、派猫猫旅行、派 Buddy 旅行、自动领积分、travel auto。
version: "1.1.0"
license: MIT
---

# WorkBuddy 自动领积分

自动完成 WorkBuddy 两大免费积分动作，全流程在本机完成：读取本地登录态 → 调用腾讯官方接口。无后端服务。

| 能力 | 收益 | 频次 | 脚本 |
|------|------|------|------|
| 每日签到 | 100 积分/天，连续第 7 天 1000 | 每天 1 次（幂等可多次跑） | `checkin.js`（推荐）/ `checkin.ps1` |
| 派猫猫旅行 | 5~10 积分/次（与 Buddy 稀有度正相关），每月约 200~270 | 每天派 1 次 + 4 时点巡检 | `travel_auto.py` |

## 原理

### 共用部分：读取本机登录态

1. WorkBuddy 桌面端登录后，会在本地保存登录态。**v5.3.8+ 的新版桌面端**改为明文 JSON 文件：
   - macOS：`~/Library/Application Support/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`
   - Windows：`%LOCALAPPDATA%\CodeBuddyExtension\Data\Public\auth\workbuddy-desktop.info`（回退 `%APPDATA%`）
   - Linux：`~/.config/CodeBuddyExtension/Data/Public/auth/workbuddy-desktop.info`
   - 结构 `{ account, auth: { accessToken, refreshToken, expiresAt, ... }, accounts }`，纯 Node 即可读取 `auth.accessToken`。
2. **旧版 WorkBuddy/CodeBuddy** 仍把 auth session 用 Electron `safeStorage` 加密存于 `state.vscdb`；新版明文文件缺失时回退到此路径，用 Electron 执行 `safeStorage.decryptString()` 解密（macOS 命中钥匙串；Windows/Linux 走 DPAPI/keyring）。
3. 运行时策略：**Node 优先**（读新版明文文件，无需 Electron），缺失时回退 Electron（解旧版 `state.vscdb`）。
4. 认证头（与桌面端一致）：`Authorization: Bearer <accessToken>` + `X-User-Id: <account.uid>`；有 `auth.domain` 时加 `X-Domain`，企业账号另加 `X-Enterprise-Id` / `X-Tenant-Id`。**实测网关当前不强制 `/v2/` 前缀与 `X-User-Id`**，对齐桌面端属前向兼容加固，不是修复 401 的必要条件。

### 能力一：每日签到 API

- 查状态：`POST https://copilot.tencent.com/v2/billing/meter/checkin-status`
- 执行签到：`POST https://copilot.tencent.com/v2/billing/meter/daily-checkin`
- 兼容说明：`checkin.ps1` 走 `/v2/` 全量签名；`checkin.sh` 走不带 `/v2/` 前缀、仅 `Authorization` 的旧写法，两种实测均返回 200（见 `references/CHANGELOG.md` 1.0.3 验证矩阵）。
- **幂等**：先查状态（命中即跳过）；`daily-checkin` 返回 `code=10001`（今天已签到）同样视为成功。
- ⚠️ v5.3.8 实测 `checkin-status` 的 `today_checked_in` 字段不可靠（签到成功后仍可能为 `false`），幂等主要靠 `code=10001` 兜底。

### 能力二：派猫猫旅行 API（⚠️ 不带 `/v2/` 前缀，与签到路径体系不同）

| 用途 | 方法 | 路径 |
|------|------|------|
| 旅行状态 | GET | `https://copilot.tencent.com/activity/growth/buddy/travel/status` |
| 地点配置 | GET | `/activity/growth/buddy/travel/config` |
| 派出旅行 | POST | `/activity/growth/buddy/travel/depart` |
| 领取奖励 | POST | `/activity/growth/buddy/travel/claim` |

**状态机**（脚本每次启动只做「一次状态判断 + 一个动作」就退出，不用长轮询——会话结束后台任务会停）：

| state | 含义 | 动作 |
|-------|------|------|
| `arrived` | 已回来 | `claim` 领取（body 带 `record_id`） |
| `idle` 且 `daily_limit_reached=false` | 空闲可派 | `depart` 派出（body `{"location_id": 1}`） |
| `traveling` | 旅行中 | 只记录，**绝不重复派出** |
| `idle` 且 `daily_limit_reached=true` | 今日已派过 | 跳过 |
| 异常 / token 失效 | — | 只记录，退出，不无限重试 |

**地点与奖励**（来自 `travel/config` 实测）：1 咖啡馆 / 2 商场店铺 / 3 健身房 / 4 古镇客栈，均为 1~4 小时、5~10 积分。R 级 Buddy 5~6 分、SR 约 7 分、UR（如「暴富喵」）8~9 分。

## 文件结构

```
workbuddy自动领积分/
├── SKILL.md                       # 本文档
├── scripts/
│   ├── decrypt-token.js           # 登录态解密（跨平台，新版明文优先 → 旧版 state.vscdb 回退）
│   ├── checkin.js                 # 每日签到（跨平台 Node 版，Node 18+，推荐入口）
│   ├── checkin.sh                 # 每日签到（macOS / Linux / Git Bash 版）
│   ├── checkin.ps1                # 每日签到（Windows PowerShell 版）
│   └── travel_auto.py             # 猫猫旅行巡检（Python 标准库）
├── references/
│   ├── CHANGELOG.md               # 签到 skill 版本变更日志（v1.0.0 → v1.0.3）
│   └── archive/                   # 合并前的原始文档存档
│       ├── 每日签到SKILL1.md
│       ├── 每日签到SKILL2.md
│       └── 派猫猫SKILL.md
└── logs/                          # 运行后自动创建，只记结果不含令牌
```

> **Windows 下推荐用 `checkin.js`**：PS 5.1 经工具会话嵌套调用 `checkin.ps1` 时会静默失败（无输出、无日志），Node 版无此问题（2026-09-07 实测）。

## 依赖

| 依赖 | 用途 | 说明 |
|------|------|------|
| WorkBuddy 桌面端（已登录） | 提供本机登录态 | 必须登录过至少一次 |
| Node.js（推荐 20+） | 读取 v5.3.8+ 明文登录态、解析 JSON | 主路径必需；可用 `WB_CHECKIN_NODE` 指定 |
| curl（Win10 1803+ 自带 / macOS/Linux 自带） | 调用签到 API | — |
| Electron 运行时（≥ 30） | **仅旧版** `state.vscdb` 分支解密令牌 | v5.3.8+ 新版账户无需安装 |
| Python 3 | 运行 `travel_auto.py` | 标准库即可，无需第三方包 |
| workbuddy-checkin 的 `decrypt-token.js` | 猫猫脚本读取登录态 | 缺失时用 `WB_DECRYPT_JS` 指定 |

可选回退：`node:sqlite` 不可用时旧版分支回退 `python3`（默认关闭，需 `WB_CHECKIN_ALLOW_PY_FALLBACK=1`）；npm 自动装 Electron 默认关闭（需 `WB_CHECKIN_AUTO_INSTALL_ELECTRON=1`）。

## 快速开始

```bash
# ① 签到：直接运行（幂等，重复运行无副作用）
node scripts/checkin.js                                    # 全平台推荐（Node 18+）
bash scripts/checkin.sh                                    # macOS / Linux
powershell -ExecutionPolicy Bypass -File scripts\checkin.ps1   # Windows

# ② 猫猫：首次务必先 --check 只读验证，再建自动化
python scripts/travel_auto.py --check
python scripts/travel_auto.py                              # 巡检一次
WB_TRAVEL_LOCATION=2 python scripts/travel_auto.py         # 指定地点
```

前提：本机已安装并**登录** WorkBuddy 桌面端；系统有 Node.js（v5.3.8+ 主路径，无需 Electron）。

## 定时任务

### 每日签到（幂等，推荐 5 时点补签）

电脑非全天开机时，`09:00 / 12:00 / 15:00 / 18:00 / 21:00` 各尝试一次，任一时间点开机即可签上。

**WorkBuddy 自动化**（recurring；⚠️ 实测 rrule **不支持多值 `BYHOUR`**，多时点需建多条任务，每条一个时点）：

```jsonc
// 每个时点一条任务，示例为 09:00（15:00 / 21:00 同理，改 BYHOUR 即可）
{
  "name": "WorkBuddy 每日积分签到·09点",
  "scheduleType": "recurring",
  "rrule": "FREQ=DAILY;BYHOUR=9;BYMINUTE=0;BYSECOND=0",
  "cwds": ["<用户工作目录>"],
  "status": "ACTIVE",
  "prompt": "运行 Node 脚本 <skill路径>/scripts/checkin.js（node 路径可从环境变量或 nodejs.org 获取）。该脚本幂等：今日已签到会直接跳过。读取输出并汇报：签到成功领取多少积分 / 今日已签到 / 令牌失效需打开 WorkBuddy 刷新。"
}
```

**crontab**：`0 9,12,15,18,21 * * * /path/to/scripts/checkin.sh >> logs/checkin.log 2>&1`

**Windows 任务计划程序**：`schtasks /Create /TN WorkBuddyDailyCheckin /TR "powershell -ExecutionPolicy Bypass -File C:\path\checkin.ps1" /SC DAILY /ST 09:00 /F`（单任务仅一个 /ST，多时点建多个任务；macOS 长期后台用 launchd `StartCalendarInterval` 数组）。

> 注意：`automation_update` 的 update 模式修改已有任务时必须显式传 `rrule`，否则可能被重置；`cwds` 不能用 Claw 工作区。

### 派猫猫旅行（4 条独立巡检，❌ 不要合并成一条 `BYMINUTE` 规则）

猫旅行时长**随机 1~4 小时**，所以：不能每天定点领一次（猫可能没回来）、不能后台等（会话结束任务停）。正确做法是 4 条独立自动化各跑一次短巡检，互相接力：

```
08:15  巡检1  大概率 idle       -> 派出
12:30  巡检2  大概率 arrived    -> 领取（比 4 小时留 15 分钟缓冲）
16:45  巡检3  已上限/仍在路上   -> 跳过
21:00  巡检4  兜底补领          -> 领取或跳过
```

| 名称 | RRULE |
|------|-------|
| 派猫猫旅行巡检·08:15 | `FREQ=DAILY;BYHOUR=8;BYMINUTE=15;BYSECOND=0` |
| 派猫猫旅行巡检·12:30 | `FREQ=DAILY;BYHOUR=12;BYMINUTE=30;BYSECOND=0` |
| 派猫猫旅行巡检·16:45 | `FREQ=DAILY;BYHOUR=16;BYMINUTE=45;BYSECOND=0` |
| 派猫猫旅行巡检·21:00 | `FREQ=DAILY;BYHOUR=21;BYMINUTE=0;BYSECOND=0` |

**⚠️ Windows 调用方式（必须遵守，否则失败）**：`travel_auto.py` 内部调用 `sys.exit()`，在当前会话中直接调用会终止整个会话。必须独立进程启动：

```powershell
$py = "C:\Users\<用户名>\.workbuddy\binaries\python\envs\default\Scripts\python.exe"
$out = "$env:TEMP\wbtravel_out.txt"; $err = "$env:TEMP\wbtravel_err.txt"
$p = Start-Process -FilePath $py -ArgumentList @('<skill路径>\scripts\travel_auto.py') -NoNewWindow -Wait -PassThru -RedirectStandardOutput $out -RedirectStandardError $err
```

然后读 `$out` 取结果、`$p.ExitCode` 取退出码。若 stdout 中文乱码，直接读脚本自己写的 `logs/travel_auto.log`（UTF-8）判定。

> **⚠️ 本机实测该 `Start-Process` 写法确定性失败**，报「已添加项。字典中的关键字 Path/PATH」（宿主同时存在 `Path` 与 `PATH` 两键，PS 5.1 的 `Start-Process` 必抛异常，`-UseNewEnvironment` 也无效；2026-09-14 复现）。**Windows 自动化里请默认直接用下面的 Git Bash 写法**，效果等价且 stdout 中文正常（无需回退读日志）：
> ```bash
> PY="C:/Users/<用户名>/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
> "$PY" "C:/Users/<用户名>/.workbuddy/skills/workbuddy-auto-credits/scripts/travel_auto.py" > /tmp/wbtravel_out.txt 2> /tmp/wbtravel_err.txt
> echo "EXITCODE=$?"
> ```

**⚠️ 模型选择**：WorkBuddy 自动化默认 `model_id = hy4-preview`。若任务被改成消耗积分的第三方模型，到自动化编辑页底部切回 HY 系列——否则「猫在领积分，自动化在花积分」。

**验收标准**：自动化是否成功只认真实日志，不认聊天记忆。完整闭环：自动 depart → 后续时点检测到 arrived → 自动 claim → 日志出现 `reward_credit`。

## 环境变量

| 变量 | 作用 |
|------|------|
| `WB_CHECKIN_NODE=<path>` / `WB_NODE` | 指定 Node 二进制路径（主路径用，sh/ps1/py 通用） |
| `WB_CHECKIN_ELECTRON=<path>` / `-ElectronPath` | 指定 Electron 二进制路径（仅旧版 state.vscdb 回退用） |
| `WB_DECRYPT_JS` / `WB_CHECKIN_DECRYPT_JS` | 指定 decrypt-token.js 路径（猫猫脚本用） |
| `WB_CHECKIN_APP_NAME=CodeBuddy` | 兼容旧版应用名（仅旧版 state.vscdb 分支的 macOS 钥匙串密钥） |
| `WB_CHECKIN_JITTER=<秒>` | 启动前随机等待 0~N 秒，避免整点风暴 |
| `WB_TRAVEL_LOCATION=<1~4>` | 猫猫派遣地点（默认 1 咖啡馆） |
| `WB_CHECKIN_ALLOW_PY_FALLBACK=1` | 允许 python3 读取旧版 sqlite（默认关闭） |
| `WB_CHECKIN_AUTO_INSTALL_ELECTRON=1` | 允许 setup 从 npm 自动下载 Electron（默认关闭） |

## 排错

| 现象 | 原因 / 处理 |
|------|------------|
| 「获取令牌失败（未知原因）」/ 未找到登录态 | 确认桌面端已登录并打开过至少一次；v5.3.8+ 检查 Node（`node -v`）或设 `WB_CHECKIN_NODE` |
| v5.3.8 已登录但报令牌失败 | 本机 skill 版本 < 1.0.2，不识别新版明文存储；升级 |
| 偶发「令牌已过期 401」但次日正常（< 1.0.3） | 401 判定原为扫响应体子串，随机 `requestId` 恰好含 `401` 时误判（约 0.57%/次），导致当日签到被跳过、连续签到中断。1.0.3 起改用真实 HTTP 状态码判定 |
| Windows 已登录却持续 401（< 1.0.3） | 旧版只探 `%APPDATA%`，桌面端实际写在 `%LOCALAPPDATA%`，回退后取到过期令牌。**排查 401 先确认令牌来源，而非怀疑请求路径/请求头** |
| 401 令牌过期（正常情况） | 打开 WorkBuddy 刷新登录态，脚本每次重新读最新 token，次日自动恢复 |
| 当日重跑报「签到未成功 / code=10001」 | 版本 < 1.0.2 未把 `code=10001` 识别为已签到；升级 |
| macOS 解密报错但已登录（旧版账户） | 设 `export WB_CHECKIN_APP_NAME=CodeBuddy` 后重试 |
| Electron 下载慢/失败（旧版账户） | 配 npm 镜像重跑 setup，或手动放置后用环境变量指定；v5.3.8+ 无需 Electron |
| Windows 提示不是内部或外部命令 | 用 `powershell -ExecutionPolicy Bypass -File …` 运行；确认 `curl.exe` 存在 |
| 自动化里 PowerShell 报「字典中的关键字 Path/PATH」 | 宿主环境同时有 `Path` 与 `PATH` 两键，PS 5.1 `Start-Process` 抛异常（加 `-UseNewEnvironment` 也无效）。① `checkin.ps1` → 用调用运算符起子进程：`& powershell.exe -NoProfile -ExecutionPolicy Bypass -File "<checkin.ps1>" 1> $out 2> $err`；② `travel_auto.py` → 直接用 Git Bash 起独立子进程：`"$PY" scripts/travel_auto.py > /tmp/out.txt 2> /tmp/err.txt; echo "EXITCODE=$?"`。两者脚本内部 `exit`/`sys.exit` 都只终止子进程，不影响宿主会话 |
| 沙箱里 `require('electron')` 报错 | 沙箱默认 `ELECTRON_RUN_AS_NODE=1`，脚本已处理；v5.3.8+ 主路径纯 Node 不受影响 |
| 猫猫 status 返回 401 | Header 缺 `X-User-Id`，或路径误加了 `/v2/` |
| 猫猫 status 返回 404 | 路径写错，确认是 `/activity/growth/buddy/travel/status` |
| 猫猫一直「旅行中」不领 | 猫确实没回来，等下一轮（4 时点兜底） |
| 猫猫一直「跳过」 | 今日已达派出上限，明天自动恢复 |
| 中文乱码 | Windows 控制台 GBK 问题；脚本用 UTF-8 写日志，日志本身正常 |
| 读到的 `wbtravel_out.txt` 内容与日志不符（像是好几天前的结果） | **读错目录**：本机 Git Bash 的 `/tmp` 映射到 `D:\WindowsTemp`（`TEMP=/tmp`），而 `C:\Users\<用户>\AppData\Local\Temp` 下可能残留旧同名文件。统一读 `/tmp/wbtravel_out.txt`（即 `D:\WindowsTemp\`），并用 `ls -l --time-style=full-iso` 核对 mtime 是否为本次运行 |
| 缺 python3 时 sh 版解析为空 | 提示「请求已提交，缺 python3 无法解析」而非签到失败（服务端可能已成功） |

## 安全说明与所需权限

> ⚠️ **凭据即账号密码**：本 skill 解密的 `accessToken` 等同你的 WorkBuddy 账号密码，高敏感。

- 令牌仅在内存中通过管道立即消费，**不写日志、不落盘、不回显、不提交仓库**；`logs/` 只记录签到/巡检结果，绝不含令牌原文。切勿将日志或输出粘贴分享。
- 网络访问仅发往腾讯官方接口 `copilot.tencent.com`（`/billing/meter/*`、`/v2/billing/meter/*`、`/activity/growth/buddy/travel/*`），不上传任何第三方。
- 禁止修改/删除本机登录态文件；禁止自动安装依赖（除显式环境变量确认的 Electron）。
- 本 skill 等价于「每天手动点一次领取」与「手动派猫领奖」，仅操作本机当前登录用户自己的账户。请勿用于他人账户、批量注册刷分或任何违反 WorkBuddy 用户协议的用途；使用者自行承担风险。

**所需权限**（均为最小范围）：本地代码执行（仅本 skill 脚本，用户/定时触发，非后台常驻）；本地文件读取（仅 WorkBuddy 登录态文件）；网络访问（仅 `copilot.tencent.com`）；环境变量读取（仅 `WB_*`）；定时任务由用户显式配置，skill 不自动写入系统定时。

**已知限制**：签到按自然日结算，整天未开机则当日无法补签，连续天数会重置；企业账号、多区域、网关策略调整下的行为未全部覆盖（详见 `references/CHANGELOG.md` 的验证边界）。
