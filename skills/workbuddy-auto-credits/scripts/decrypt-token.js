#!/usr/bin/env node
/**
 * decrypt-token.js — WorkBuddy 本机登录令牌读取
 *
 * 输出契约（stdout，按行前缀过滤，消费方禁止整段捕获）：
 *   成功: DECRYPT_RESULT:OK / TOKEN:<accessToken> / ACCOUNT_UID:<uid> /
 *         AUTH_DOMAIN:<domain|-> / ENTERPRISE_ID:<id|->
 *   失败: DECRYPT_RESULT:ERR:<原因>
 *
 * 优先级：v5.3.8+ 明文 JSON（win32 优先 %LOCALAPPDATA%，回退 %APPDATA%）
 *        → 旧版 state.vscdb（Electron safeStorage，缺 Electron 时报错）
 *
 * 安全：令牌仅经 stdout 管道传递，不写任何文件。
 */
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

const APP_NAME = process.env.WB_CHECKIN_APP_NAME || 'WorkBuddy';

function emitAndExit(text, code) {
  // 延迟退出，确保 stdout flush 完成
  process.stdout.write(text + '\n', () => {
    setTimeout(() => process.exit(code), 200);
  });
}

function fail(reason) {
  emitAndExit('DECRYPT_RESULT:ERR:' + reason, 5);
}

// ---------- 新版明文 JSON 分支 ----------
function candidatesPlaintext() {
  const rel = path.join('CodeBuddyExtension', 'Data', 'Public', 'auth', 'workbuddy-desktop.info');
  const list = [];
  if (process.platform === 'win32') {
    if (process.env.LOCALAPPDATA) list.push(path.join(process.env.LOCALAPPDATA, rel));
    if (process.env.APPDATA) list.push(path.join(process.env.APPDATA, rel));
  } else if (process.platform === 'darwin') {
    list.push(path.join(os.homedir(), 'Library', 'Application Support', rel));
  } else {
    list.push(path.join(os.homedir(), '.config', rel));
  }
  return list;
}

function tryPlaintext() {
  for (const p of candidatesPlaintext()) {
    try {
      if (!fs.existsSync(p)) continue;
      const data = JSON.parse(fs.readFileSync(p, 'utf8'));
      const token = data && data.auth && data.auth.accessToken;
      if (!token) continue; // 明文文件存在但缺 token（升级中途等），继续回退
      const uid =
        (data.account && (data.account.uid || data.account.userId || data.account.id)) ||
        (data.auth && (data.auth.uid || data.auth.userId)) || '';
      const domain = (data.auth && data.auth.domain) || '';
      const enterpriseId =
        (data.account && data.account.enterpriseId) || (data.auth && data.auth.enterpriseId) || '';
      const tenantId = (data.account && data.account.tenantId) || (data.auth && data.auth.tenantId) || '';
      process.stderr.write('[decrypt-token] 使用新版明文登录态: ' + p + '\n');
      process.stderr.write('[decrypt-token] 安全提示: 令牌等同账号密码，仅限内存使用，勿写入日志/文件/终端回显。\n');
      let out =
        'DECRYPT_RESULT:OK\n' +
        'TOKEN:' + token + '\n' +
        'ACCOUNT_UID:' + uid + '\n' +
        'AUTH_DOMAIN:' + (domain || '-') + '\n' +
        'ENTERPRISE_ID:' + (enterpriseId || '-') + '\n';
      if (tenantId) out += 'TENANT_ID:' + tenantId + '\n';
      return out;
    } catch (e) {
      // 解析失败继续尝试下一个候选
    }
  }
  return null;
}

// ---------- 旧版 state.vscdb 分支（回退，需要 Electron safeStorage） ----------
function tryLegacyVscdb() {
  const candidates = [];
  if (process.platform === 'win32') {
    const base = process.env.APPDATA;
    if (base) {
      candidates.push(path.join(base, APP_NAME, 'User', 'globalStorage', 'state.vscdb'));
      candidates.push(path.join(base, 'CodeBuddy', 'User', 'globalStorage', 'state.vscdb'));
    }
  } else if (process.platform === 'darwin') {
    candidates.push(path.join(os.homedir(), 'Library', 'Application Support', APP_NAME, 'User', 'globalStorage', 'state.vscdb'));
  } else {
    candidates.push(path.join(os.homedir(), '.config', APP_NAME, 'User', 'globalStorage', 'state.vscdb'));
  }
  const dbPath = candidates.find((p) => fs.existsSync(p));
  if (!dbPath) return null;

  let electron;
  try {
    electron = require('electron');
  } catch (e) {
    fail('LEGACY_DB_FOUND_BUT_NO_ELECTRON:' + dbPath);
    return undefined; // 不会到达
  }
  if (electron && electron.app && !electron.app.isReady && !process.env.ELECTRON_RUN_AS_NODE) {
    // Electron 主进程内
    try {
      const { safeStorage } = electron;
      return decryptLegacy(dbPath, safeStorage, electron.app);
    } catch (e) {
      fail('LEGACY_DECRYPT_ERROR:' + e.message);
      return undefined;
    }
  }
  fail('LEGACY_DB_FOUND_BUT_ELECTRON_CONTEXT_UNAVAILABLE:' + dbPath);
  return undefined;
}

function decryptLegacy(dbPath, safeStorage, app) {
  const { DatabaseSync } = require('node:sqlite');
  const db = new DatabaseSync(dbPath, { readOnly: true });
  const keys = ['authState', 'workbuddy.auth', 'codebuddy.auth', 'auth'];
  let enc = null;
  for (const k of keys) {
    const row = db.prepare('SELECT value FROM ItemTable WHERE key = ?').get(k);
    if (row && row.value) { enc = row.value; break; }
  }
  db.close();
  if (!enc) { fail('LEGACY_DB_NO_AUTH_KEY:' + dbPath); return; }
  const buf = typeof enc === 'string' ? Buffer.from(enc, 'base64') : Buffer.from(enc);
  const tokenJson = safeStorage.decryptString(buf);
  const parsed = JSON.parse(tokenJson);
  const token = parsed.accessToken || parsed.auth && parsed.auth.accessToken;
  if (!token) { fail('LEGACY_DECRYPT_NO_TOKEN'); return; }
  const out =
    'DECRYPT_RESULT:OK\n' +
    'TOKEN:' + token + '\n' +
    'ACCOUNT_UID:' + (parsed.uid || parsed.account && parsed.account.uid || '') + '\n' +
    'AUTH_DOMAIN:' + (parsed.domain || '-') + '\n' +
    'ENTERPRISE_ID:' + (parsed.enterpriseId || '-') + '\n';
  emitAndExit(out, 0);
}

// ---------- main ----------
try {
  const plain = tryPlaintext();
  if (plain) { emitAndExit(plain, 0); }
  const r = tryLegacyVscdb();
  if (r === null) {
    fail('NO_LOCAL_LOGIN_STATE:未找到新版明文登录态或旧版 state.vscdb，请确认 WorkBuddy 桌面端已登录');
  }
} catch (e) {
  fail('UNEXPECTED:' + e.message);
}
