# WorkBuddy 自动领积分（workbuddy-auto-credits）

一键自动化 WorkBuddy 两大免费积分动作，全流程本机运行、无后端服务、令牌不落盘。

| 能力 | 收益 | 频次 |
|------|------|------|
| 每日签到 | 100 积分/天，连续第 7 天 1000 | 每天 1 次 |
| 派猫猫旅行 | 5~10 积分/次，每月约 200~270 | 每天派 1 次 |

## 环境要求

- WorkBuddy 桌面端（**已登录过至少一次**，v5.3.8+ 最佳）
- Node.js 18+（签到必需，[nodejs.org](https://nodejs.org) 下载）
- Python 3（仅派猫猫需要，标准库即可）

> 旧版 WorkBuddy（`state.vscdb` 加密存储）需额外 Electron 运行时；v5.3.8+ 明文登录态无需。

## 30 秒上手

```bash
# 每日签到（幂等，重复运行无副作用）
node scripts/checkin.js

# 派猫猫旅行：首次先只读检查，确认账号支持后正式巡检
python scripts/travel_auto.py --check
python scripts/travel_auto.py
```

成功输出示例：

```
签到成功！领取积分: 100
猫猫已派出旅行（地点 1），预计 1~4 小时后回来。
猫猫旅行归来，领取奖励 +8 积分！
```

## 定时自动化

在 WorkBuddy 中新建 recurring 自动化任务即可（完整 RRULE 与注意事项见 `SKILL.md`）：

- **签到**：每天 09:00 / 15:00 / 21:00 各建一条（rrule 不支持多值 BYHOUR，须一条一个时点）
- **猫猫**：每天 08:15 / 12:30 / 16:45 / 21:00 四条巡检接力（猫旅行时长随机 1~4 小时，定点领取会漏）

## 目录结构

```
workbuddy-auto-credits/
├── SKILL.md                 # 完整文档：原理/定时/排错/安全
├── README.md                # 本文件
├── scripts/
│   ├── decrypt-token.js     # 登录态解密（共享）
│   ├── checkin.js           # 签到 · 全平台推荐入口
│   ├── checkin.sh           # 签到 · macOS/Linux
│   ├── checkin.ps1          # 签到 · Windows PowerShell
│   └── travel_auto.py       # 猫猫巡检
└── references/
    └── CHANGELOG.md         # 版本历史
```

## 常见问题

| 现象 | 处理 |
|------|------|
| 获取令牌失败 | 确认 WorkBuddy 桌面端已登录并打开过至少一次；检查 `node -v` 可用 |
| 401 令牌失效 | 打开 WorkBuddy 桌面端刷新登录态，脚本每次自动读最新 token，次日恢复 |
| 猫猫一直"旅行中" | 猫确实没回来（1~4 小时随机），等下一轮巡检 |
| 猫猫一直"跳过" | 今日已派过，明天自动恢复 |

更多排错条目见 `SKILL.md` 排错章节。

## 安全说明

- 脚本解密的 `accessToken` **等同账号密码**：仅内存使用，不写日志、不落盘、不回显
- 网络访问仅限腾讯官方接口 `copilot.tencent.com`，不上传任何第三方
- `logs/` 只记录结果（积分/状态/动作），绝不含令牌
- 仅限操作本人账户，请勿用于他人账户或批量刷分；使用风险自负

## 许可

MIT
