#!/usr/bin/env node
/**
 * checkin.js — WorkBuddy 每日积分签到（跨平台 Node 版，Node 18+ 自带 fetch）
 *
 * 与 checkin.ps1 / checkin.sh 等价的实现，作为 Windows PowerShell 5.1
 * 中文路径 / 会话 exit 兼容问题的首选入口。
 *
 * 用法: node checkin.js
 * 环境变量:
 *   WB_CHECKIN_NODE   仅由调用方使用（本脚本自身就是 Node）
 *   WB_CHECKIN_JITTER 启动前随机等待 0~N 秒
 *
 * 幂等: code=10001（今日已签到）视为成功；HTTP 状态码真实判定（防假 401）。
 * 安全: 令牌仅内存使用；logs/checkin.log 只记录结果。
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const SKILL_DIR = path.resolve(__dirname, '..');
const LOG_FILE = path.join(SKILL_DIR, 'logs', 'checkin.log');

function log(msg) {
  fs.mkdirSync(path.dirname(LOG_FILE), { recursive: true });
  fs.appendFileSync(LOG_FILE, new Date().toISOString().replace('T', ' ').slice(0, 19) + '  ' + msg + '\n');
}

// 随机错峰
const jitter = parseInt(process.env.WB_CHECKIN_JITTER || '0', 10);
if (jitter > 0) {
  Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, Math.floor(Math.random() * jitter * 1000));
}

// ---------- 1. 解密令牌 ----------
function getCredentials() {
  const decryptJs = path.join(SKILL_DIR, 'scripts', 'decrypt-token.js');
  if (!fs.existsSync(decryptJs)) throw new Error('未找到 decrypt-token.js');
  // 沙箱内 ELECTRON_RUN_AS_NODE 不影响纯 Node 分支，保留移除以防旧版回退
  const env = { ...process.env };
  delete env.ELECTRON_RUN_AS_NODE;
  const r = require('child_process').spawnSync(process.execPath, [decryptJs], { env, encoding: 'utf8' });
  const lines = (r.stdout || '').split('\n').map((s) => s.trim()).filter(Boolean);
  const result = lines.find((l) => l.startsWith('DECRYPT_RESULT:'));
  if (!result || !result.startsWith('DECRYPT_RESULT:OK')) {
    const reason = result ? result.replace('DECRYPT_RESULT:', '') : 'decrypt-token.js 无有效输出';
    throw new Error('获取令牌失败（' + reason + '）');
  }
  const pick = (p) => {
    const l = lines.find((x) => x.startsWith(p));
    return l ? l.slice(p.length) : '';
  };
  return {
    token: pick('TOKEN:'),
    uid: pick('ACCOUNT_UID:'),
    domain: pick('AUTH_DOMAIN:'),
    entId: pick('ENTERPRISE_ID:'),
    tenantId: pick('TENANT_ID:'),
  };
}

// ---------- 2. API 调用（真实 HTTP 状态码判定） ----------
function buildHeaders(cred) {
  const h = {
    Authorization: 'Bearer ' + cred.token,
    'Content-Type': 'application/json',
    'User-Agent': 'workbuddy-checkin/1.1.0',
  };
  if (cred.uid) h['X-User-Id'] = cred.uid;
  if (cred.domain && cred.domain !== '-') h['X-Domain'] = cred.domain;
  if (cred.entId && cred.entId !== '-') h['X-Enterprise-Id'] = cred.entId;
  if (cred.tenantId && cred.tenantId !== '-') h['X-Tenant-Id'] = cred.tenantId;
  return h;
}

async function callApi(url, headers) {
  try {
    const resp = await fetch(url, { method: 'POST', headers, signal: AbortSignal.timeout(30000) });
    const body = await resp.text();
    return { status: resp.status, body };
  } catch (e) {
    return { status: 0, body: '', error: e.message };
  }
}

// ---------- 3. main ----------
(async () => {
  let cred;
  try {
    cred = getCredentials();
  } catch (e) {
    console.log('签到失败：' + e.message);
    log('FAIL ' + e.message);
    process.exit(1);
  }
  const headers = buildHeaders(cred);
  const API = 'https://copilot.tencent.com/v2/billing/meter';

  // 查状态（today_checked_in 不可靠，仅作参考）
  const s = await callApi(API + '/checkin-status', headers);
  if (s.status === 0) {
    console.log('签到失败：网络异常（' + (s.error || '无 HTTP 响应') + '）');
    log('FAIL 网络异常');
    process.exit(2);
  }
  if (s.status === 401 || s.status === 403) {
    console.log('签到失败：令牌已失效（HTTP ' + s.status + '）。请打开 WorkBuddy 桌面端刷新登录态后重试。');
    log('FAIL 令牌失效 HTTP ' + s.status);
    process.exit(3);
  }

  // 执行签到
  const c = await callApi(API + '/daily-checkin', headers);
  if (c.status === 0) {
    console.log('签到失败：网络异常（' + (c.error || '无 HTTP 响应') + '）');
    log('FAIL 网络异常(daily-checkin)');
    process.exit(2);
  }
  if (c.status === 401 || c.status === 403) {
    console.log('签到失败：令牌已失效（HTTP ' + c.status + '）');
    log('FAIL 令牌失效 HTTP ' + c.status);
    process.exit(3);
  }
  if (c.status !== 200) {
    // 2026-09-07 实测：服务端把 code=10001（今日已签到）改为 HTTP 400 返回，仍视为幂等成功
    let r4 = null;
    try { r4 = JSON.parse(c.body); } catch (e) { /* fallthrough */ }
    if (r4 && r4.code === 10001) {
      console.log('今日已签到（幂等跳过，HTTP ' + c.status + ' code=10001）');
      log('OK 今日已签到（HTTP ' + c.status + ' code=10001）');
      process.exit(0);
    }
    console.log('签到失败：HTTP ' + c.status);
    log('FAIL HTTP ' + c.status);
    process.exit(4);
  }

  let r = null;
  try { r = JSON.parse(c.body); } catch (e) { /* fallthrough */ }
  const code = r ? r.code : undefined;

  if (code === 0) {
    const d = (r && r.data) || {};
    const credit = d.credit !== undefined ? d.credit : (d.reward_credit !== undefined ? d.reward_credit : '');
    const streak = d.streak !== undefined ? d.streak : (d.continuous_days !== undefined ? d.continuous_days : '');
    let msg = '签到成功！领取积分: ' + credit;
    if (streak !== '') msg += '，连续签到: ' + streak + ' 天';
    console.log(msg);
    log('OK 签到成功 credit=' + credit + ' streak=' + streak);
    process.exit(0);
  } else if (code === 10001) {
    console.log('今日已签到，无需重复领取。');
    log('OK 今日已签到（code=10001 兜底）');
    process.exit(0);
  } else {
    const m = r && r.msg ? r.msg : '未知业务错误';
    console.log('签到失败：业务码 ' + code + '，' + m);
    log('FAIL code=' + code + ' msg=' + m);
    process.exit(4);
  }
})();
