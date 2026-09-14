#!/usr/bin/env bash
# checkin.sh - WorkBuddy 每日积分签到（macOS / Linux / Git Bash）
#
# 用法: bash checkin.sh
# 环境变量:
#   WB_CHECKIN_NODE   指定 node 路径（默认 PATH 中的 node）
#   WB_CHECKIN_JITTER 启动前随机等待 0~N 秒
#
# 幂等: code=10001（今日已签到）视为成功；真实 HTTP 状态码判定（防假 401）。
# 安全: 令牌仅在内存/管道流转，logs/checkin.log 只记录结果。
set -u
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$SKILL_DIR/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/checkin.log"
log() { echo "$(date '+%Y-%m-%d %H:%M:%S')  $1" >> "$LOG_FILE"; }

# 随机错峰
if [ "${WB_CHECKIN_JITTER:-0}" -gt 0 ] 2>/dev/null; then
  sleep $((RANDOM % WB_CHECKIN_JITTER))
fi

NODE="${WB_CHECKIN_NODE:-node}"
command -v "$NODE" >/dev/null 2>&1 || { echo "签到失败：未找到 Node，请设 WB_CHECKIN_NODE"; log "FAIL 未找到 Node"; exit 1; }

# ---------- 解密令牌 ----------
DECRYPT_OUT=$("$NODE" "$SKILL_DIR/scripts/decrypt-token.js" 2>/dev/null) || DECRYPT_OUT=""
RESULT=$(printf '%s\n' "$DECRYPT_OUT" | grep '^DECRYPT_RESULT:' | head -1)
case "$RESULT" in
  "DECRYPT_RESULT:OK") ;;
  *)
    REASON=${RESULT#DECRYPT_RESULT:}
    echo "签到失败：获取令牌失败（${REASON:-decrypt-token.js 无有效输出}）"
    log "FAIL 获取令牌失败: ${REASON:-无输出}"
    exit 1 ;;
esac
TOKEN=$(printf '%s\n' "$DECRYPT_OUT" | grep '^TOKEN:' | head -1 | cut -c7-)
UID_=$(printf '%s\n' "$DECRYPT_OUT" | grep '^ACCOUNT_UID:' | head -1 | cut -c13-)
DOMAIN=$(printf '%s\n' "$DECRYPT_OUT" | grep '^AUTH_DOMAIN:' | head -1 | cut -c13-)
ENTID=$(printf '%s\n' "$DECRYPT_OUT" | grep '^ENTERPRISE_ID:' | head -1 | cut -c15-)

# ---------- 请求函数（真实 HTTP 状态码） ----------
call_api() { # $1=url
  local body_file; body_file=$(mktemp)
  local http_code
  http_code=$(curl -s -X POST "$1" \
    -H "Authorization: Bearer $TOKEN" \
    ${UID_:+-H "X-User-Id: $UID_"} \
    ${DOMAIN:+$([ "$DOMAIN" != "-" ] && echo "-H 'X-Domain: $DOMAIN'")} \
    ${ENTID:+$([ "$ENTID" != "-" ] && echo "-H 'X-Enterprise-Id: $ENTID'")} \
    --max-time 30 -o "$body_file" -w '%{http_code}' 2>/dev/null)
  echo "$http_code|$(cat "$body_file")"
  rm -f "$body_file"
}

# ---------- 查状态（today_checked_in 不可靠，仅参考） ----------
IFS='|' read -r CODE STATUS_BODY <<< "$(call_api 'https://copilot.tencent.com/v2/billing/meter/checkin-status')"
if [ "$CODE" = "000" ]; then echo "签到失败：网络异常"; log "FAIL 网络异常"; exit 2; fi
if [ "$CODE" = "401" ] || [ "$CODE" = "403" ]; then
  echo "签到失败：令牌已失效（HTTP $CODE）。请打开 WorkBuddy 桌面端刷新登录态后重试。"
  log "FAIL 令牌失效 HTTP $CODE"; exit 3
fi

# ---------- 执行签到 ----------
IFS='|' read -r CODE RESP_BODY <<< "$(call_api 'https://copilot.tencent.com/v2/billing/meter/daily-checkin')"
if [ "$CODE" = "000" ]; then echo "签到失败：网络异常"; log "FAIL 网络异常(daily-checkin)"; exit 2; fi
if [ "$CODE" = "401" ] || [ "$CODE" = "403" ]; then
  echo "签到失败：令牌已失效（HTTP $CODE）"; log "FAIL 令牌失效 HTTP $CODE"; exit 3
fi
if [ "$CODE" != "200" ]; then
  # 2026-09-07 实测：服务端把 code=10001（今日已签到）改为 HTTP 400 返回，仍视为幂等成功
  if printf '%s' "$RESP_BODY" | grep -q '"code": *10001'; then
    echo "今日已签到（幂等跳过，HTTP $CODE code=10001）"
    log "OK 今日已签到（HTTP $CODE code=10001）"
    exit 0
  fi
  echo "签到失败：HTTP $CODE"; log "FAIL HTTP $CODE"; exit 4
fi

# 解析业务码（优先 python3，缺失时降级 grep）
PARSED=$(printf '%s' "$RESP_BODY" | python3 -c 'import sys,json;d=json.load(sys.stdin);print(d.get("code",""),d.get("msg",""))' 2>/dev/null) \
  || PARSED=$(printf '%s' "$RESP_BODY" | grep -o '"code":[0-9]*' | head -1)
BCODE=$(echo "$PARSED" | awk '{print $1}' | grep -o '[0-9]*' | head -1)
BMSG=$(echo "$PARSED" | awk '{print $2}')

if [ "$BCODE" = "0" ]; then
  CREDIT=$(printf '%s' "$RESP_BODY" | python3 -c 'import sys,json;d=json.load(sys.stdin).get("data",{}) or {};print(d.get("credit", d.get("reward_credit","?")))' 2>/dev/null || echo "?")
  echo "签到成功！领取积分: $CREDIT"
  log "OK 签到成功 credit=$CREDIT"
  exit 0
elif [ "$BCODE" = "10001" ]; then
  echo "今日已签到，无需重复领取。"
  log "OK 今日已签到（code=10001 兜底）"
  exit 0
else
  echo "签到失败：业务码 $BCODE，$BMSG"
  log "FAIL code=$BCODE msg=$BMSG"
  exit 4
fi
