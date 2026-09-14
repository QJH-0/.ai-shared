#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
travel_auto.py — WorkBuddy「派猫猫旅行」自动巡检

每次启动只做「一次状态判断 + 一个动作」就退出（短任务接力，不做长轮询）。
状态机: arrived→claim / idle且未达上限→depart / traveling→只记录 /
        idle且达上限→跳过 / 异常→只记录退出。

用法:
  python travel_auto.py            # 巡检一次
  python travel_auto.py --check    # 只读检查（绝不派不领）
环境变量:
  WB_CHECKIN_NODE / WB_NODE          node.exe 路径
  WB_DECRYPT_JS / WB_CHECKIN_DECRYPT_JS  decrypt-token.js 路径
  WB_TRAVEL_LOCATION                 派遣地点 id（默认 1 咖啡馆）

安全: 令牌仅内存使用，日志（logs/travel_auto.log, UTF-8）只记录结果。
"""
import json
import os
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = SKILL_DIR / "logs" / "travel_auto.log"
BASE = "https://copilot.tencent.com"
CHECK_ONLY = "--check" in sys.argv


def log(msg: str) -> None:
    LOG_FILE.parent.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with LOG_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{stamp}  {msg}\n")


def out(msg: str) -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    print(msg)


def find_node() -> str:
    for var in ("WB_CHECKIN_NODE", "WB_NODE"):
        p = os.environ.get(var)
        if p and Path(p).exists():
            return p
    managed = Path.home() / ".workbuddy" / "binaries" / "node" / "versions"
    if managed.exists():
        for d in sorted(managed.iterdir(), reverse=True):
            cand = d / "node.exe"
            if cand.exists():
                return str(cand)
    return "node"


def find_decrypt_js() -> str:
    for var in ("WB_DECRYPT_JS", "WB_CHECKIN_DECRYPT_JS"):
        p = os.environ.get(var)
        if p and Path(p).exists():
            return p
    cand = SKILL_DIR / "scripts" / "decrypt-token.js"
    if cand.exists():
        return str(cand)
    return ""


def get_credentials():
    """运行 decrypt-token.js，返回 (token, uid, domain, ent_id)；失败返回 None。"""
    decrypt_js = find_decrypt_js()
    if not decrypt_js:
        log("FAIL 未找到 decrypt-token.js")
        out("未找到 decrypt-token.js，请设 WB_DECRYPT_JS")
        return None
    node = find_node()
    try:
        proc = subprocess.run([node, decrypt_js], capture_output=True, text=True, timeout=60)
    except Exception as e:
        log(f"FAIL decrypt-token 运行异常: {e}")
        out(f"decrypt-token 运行异常: {e}")
        return None
    lines = (proc.stdout or "").splitlines()
    result = next((l for l in lines if l.startswith("DECRYPT_RESULT:")), "")
    if not result.startswith("DECRYPT_RESULT:OK"):
        reason = result.replace("DECRYPT_RESULT:", "", 1) or "无输出"
        log(f"FAIL 获取令牌失败: {reason}")
        out(f"获取令牌失败: {reason}")
        return None

    def pick(prefix):
        return next((l[len(prefix):] for l in lines if l.startswith(prefix)), "")

    token = pick("TOKEN:")
    if not token:
        log("FAIL 令牌为空")
        out("令牌为空")
        return None
    return token, pick("ACCOUNT_UID:"), pick("AUTH_DOMAIN:"), pick("ENTERPRISE_ID:")


def build_headers(cred) -> dict:
    token, uid, domain, ent_id = cred
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "User-Agent": "workbuddy-travel-auto/1.1.0",
    }
    if uid:
        headers["X-User-Id"] = uid
    if domain and domain != "-":
        headers["X-Domain"] = domain
    if ent_id and ent_id != "-":
        headers["X-Enterprise-Id"] = ent_id
    return headers


def http_request(method: str, url: str, headers: dict, body: dict = None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        return e.code, {}
    except Exception as e:
        return 0, {"_error": str(e)}


def main() -> int:
    cred = get_credentials()
    if not cred:
        return 3
    headers = build_headers(cred)

    # 1. 查旅行状态（⚠️ 不带 /v2/ 前缀）
    status_url = f"{BASE}/activity/growth/buddy/travel/status"
    status, body = http_request("GET", status_url, headers)
    if status == 0:
        log(f"FAIL 网络异常: {body.get('_error', '')}")
        out("网络异常，等下一轮")
        return 2
    if status in (401, 403):
        log(f"FAIL 令牌失效 HTTP {status}")
        out(f"令牌失效（HTTP {status}），请打开 WorkBuddy 刷新登录态")
        return 3
    if status != 200:
        log(f"FAIL HTTP {status}")
        out(f"状态接口异常 HTTP {status}")
        return 2

    data = body.get("data", body)
    state = data.get("state") or data.get("status") or ""
    limit = bool(data.get("daily_limit_reached"))
    record_id = data.get("record_id") or (data.get("current_record") or {}).get("id")
    log(f"state={state} daily_limit_reached={limit} record_id={record_id}")

    if CHECK_ONLY:
        cfg_status, cfg = http_request("GET", f"{BASE}/activity/growth/buddy/travel/config", headers)
        out(f"[--check] state={state} daily_limit_reached={limit} record_id={record_id}")
        out(f"[--check] config HTTP {cfg_status}: {json.dumps(cfg, ensure_ascii=False)[:500]}")
        out("只读检查完成，未派出未领取。")
        return 0

    # 2. 状态机决策
    if state == "arrived":
        code, resp = http_request("POST", f"{BASE}/activity/growth/buddy/travel/claim", headers,
                                  {"record_id": record_id})
        if code == 200 and resp.get("code") == 0:
            reward = (resp.get("data") or {}).get("reward_credit", "?")
            log(f"OK claim 成功 reward_credit={reward}")
            out(f"猫猫旅行归来，领取奖励 +{reward} 积分！")
            return 0
        log(f"FAIL claim HTTP={code} resp={json.dumps(resp, ensure_ascii=False)[:200]}")
        out(f"领取失败 HTTP {code}，等下一轮")
        return 2

    if state == "idle" and not limit:
        loc = os.environ.get("WB_TRAVEL_LOCATION", "1")
        code, resp = http_request("POST", f"{BASE}/activity/growth/buddy/travel/depart", headers,
                                  {"location_id": int(loc)})
        if code == 200 and resp.get("code") == 0:
            log(f"OK depart 成功 location_id={loc}")
            out(f"猫猫已派出旅行（地点 {loc}），预计 1~4 小时后回来。")
            return 0
        log(f"FAIL depart HTTP={code} resp={json.dumps(resp, ensure_ascii=False)[:200]}")
        out(f"派出失败 HTTP {code}，等下一轮")
        return 2

    if state == "traveling":
        out("猫猫旅行中，等下一轮巡检。")
        return 0

    if state == "idle" and limit:
        out("今日已达派出上限，明天自动恢复。")
        return 0

    out(f"未知状态 state={state}，只记录不动作。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
