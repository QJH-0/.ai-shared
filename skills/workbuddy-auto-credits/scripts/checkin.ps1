# checkin.ps1 - WorkBuddy 每日积分签到（Windows PowerShell，兼容 PS 5.1）
#
# 用法:
#   powershell -ExecutionPolicy Bypass -File checkin.ps1 [-NodePath <node.exe>] [-SkillDir <路径>]
# 环境变量:
#   WB_CHECKIN_NODE   指定 node.exe 路径
#   WB_CHECKIN_JITTER 启动前随机等待 0~N 秒
#
# 安全: 令牌仅在内存/管道中流转，不落盘；logs/checkin.log 只记录结果。
param(
  [string]$NodePath = "",
  [string]$SkillDir = ""
)

$ErrorActionPreference = 'Stop'
if (-not $SkillDir) { $SkillDir = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent }
$LogDir = Join-Path $SkillDir 'logs'
if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }
$LogFile = Join-Path $LogDir 'checkin.log'

function Write-Log([string]$msg) {
  $line = (Get-Date -Format 'yyyy-MM-dd HH:mm:ss') + "  " + $msg
  Add-Content -Path $LogFile -Value $line -Encoding UTF8
}

# 随机错峰
$jitter = 0
if ($env:WB_CHECKIN_JITTER -match '^\d+$') { $jitter = [int]$env:WB_CHECKIN_JITTER }
if ($jitter -gt 0) { Start-Sleep -Seconds (Get-Random -Minimum 0 -Maximum $jitter) }

# ---------- 定位 Node ----------
if (-not $NodePath -and $env:WB_CHECKIN_NODE) { $NodePath = $env:WB_CHECKIN_NODE }
if (-not $NodePath) {
  $managed = Join-Path $env:USERPROFILE '.workbuddy\binaries\node\versions'
  if (Test-Path $managed) {
    $latest = Get-ChildItem $managed -Directory | Sort-Object Name -Descending | Select-Object -First 1
    if ($latest) {
      $candidate = Join-Path $latest.FullName 'node.exe'
      if (Test-Path $candidate) { $NodePath = $candidate }
    }
  }
}
if (-not $NodePath) { $NodePath = 'node' }

# ---------- 解密令牌 ----------
$decryptJs = Join-Path $SkillDir 'scripts\decrypt-token.js'
$stdout = & $NodePath $decryptJs 2>$null
$lines = @($stdout | ForEach-Object { [string]$_ })
$resLine = $lines | Where-Object { $_ -like 'DECRYPT_RESULT:*' } | Select-Object -First 1

if (-not $resLine -or $resLine -notlike 'DECRYPT_RESULT:OK*') {
  $reason = if ($resLine) { $resLine -replace '^DECRYPT_RESULT:', '' } else { 'decrypt-token.js 无有效输出' }
  Write-Output "签到失败：获取令牌失败（$reason）"
  Write-Log "FAIL 获取令牌失败: $reason"
  exit 1
}
$token = ($lines | Where-Object { $_ -like 'TOKEN:*' } | Select-Object -First 1) -replace '^TOKEN:', ''
$uid = ($lines | Where-Object { $_ -like 'ACCOUNT_UID:*' } | Select-Object -First 1) -replace '^ACCOUNT_UID:', ''
$domain = ($lines | Where-Object { $_ -like 'AUTH_DOMAIN:*' } | Select-Object -First 1) -replace '^AUTH_DOMAIN:', ''
$entId = ($lines | Where-Object { $_ -like 'ENTERPRISE_ID:*' } | Select-Object -First 1) -replace '^ENTERPRISE_ID:', ''

# ---------- 请求函数（真实 HTTP 状态码判定，防假 401） ----------
function Invoke-Api([string]$url, [hashtable]$headers) {
  $curlExe = "$env:WINDIR\System32\curl.exe"
  if (-not (Test-Path $curlExe)) { $curlExe = 'curl.exe' }
  $tmpBody = [System.IO.Path]::GetTempFileName()
  try {
    $args = @('-s', '-X', 'POST', $url, '-H', ("Authorization: Bearer " + $token), '--max-time', '30', '-o', $tmpBody, '-w', "`n%{http_code}")
    if ($uid)     { $args += @('-H', ("X-User-Id: " + $uid)) }
    if ($domain -and $domain -ne '-') { $args += @('-H', ("X-Domain: " + $domain)) }
    if ($entId -and $entId -ne '-')   { $args += @('-H', ("X-Enterprise-Id: " + $entId)) }
    $raw = & $curlExe @args 2>$null
    $status = 0
    if ($raw) { $status = [int](($raw | Select-Object -Last 1)) }
    $body = ''
    if (Test-Path $tmpBody) { $body = [System.IO.File]::ReadAllText($tmpBody) }
    return @{ Status = $status; Body = $body }
  } finally {
    if (Test-Path $tmpBody) { Remove-Item $tmpBody -Force -ErrorAction SilentlyContinue }
  }
}

$h = @{}
$api1 = Invoke-Api 'https://copilot.tencent.com/v2/billing/meter/checkin-status' $h

if ($api1.Status -eq 0) {
  Write-Output "签到失败：网络异常（无 HTTP 响应）"
  Write-Log "FAIL 网络异常"
  exit 2
}
if ($api1.Status -eq 401 -or $api1.Status -eq 403) {
  Write-Output "签到失败：令牌已失效（HTTP $($api1.Status)）。请打开 WorkBuddy 桌面端刷新登录态后重试。"
  Write-Log "FAIL 令牌失效 HTTP $($api1.Status)"
  exit 3
}

# 状态检查（today_checked_in 不可靠，仅作参考）
$already = $false
try { $st = $api1.Body | ConvertFrom-Json; if ($st.data -and $st.data.today_checked_in) { $already = $true } } catch {}

if ($already) {
  Write-Output "今日已签到，无需重复领取。"
  Write-Log "OK 今日已签到（status 提前命中）"
  exit 0
}

# ---------- 执行签到 ----------
$api2 = Invoke-Api 'https://copilot.tencent.com/v2/billing/meter/daily-checkin' $h
if ($api2.Status -eq 0) {
  Write-Output "签到失败：网络异常（无 HTTP 响应）"
  Write-Log "FAIL 网络异常(daily-checkin)"
  exit 2
}
if ($api2.Status -eq 401 -or $api2.Status -eq 403) {
  Write-Output "签到失败：令牌已失效（HTTP $($api2.Status)）"
  Write-Log "FAIL 令牌失效 HTTP $($api2.Status)"
  exit 3
}
if ($api2.Status -ne 200) {
  Write-Output "签到失败：HTTP $($api2.Status)"
  Write-Log "FAIL HTTP $($api2.Status)"
  exit 4
}

try { $r = $api2.Body | ConvertFrom-Json } catch { $r = $null }
$code = if ($r) { $r.code } else { $null }

if ($code -eq 0) {
  $credit = ''
  $streak = ''
  try {
    if ($r.data) {
      if ($r.data.credit -ne $null) { $credit = $r.data.credit }
      elseif ($r.data.reward_credit -ne $null) { $credit = $r.data.reward_credit }
      if ($r.data.streak -ne $null) { $streak = $r.data.streak }
      elseif ($r.data.continuous_days -ne $null) { $streak = $r.data.continuous_days }
    }
  } catch {}
  $msg = "签到成功！领取积分: $credit"
  if ($streak -ne '') { $msg += "，连续签到: $streak 天" }
  Write-Output $msg
  Write-Log "OK 签到成功 credit=$credit streak=$streak"
  exit 0
}
elseif ($code -eq 10001) {
  Write-Output "今日已签到，无需重复领取。"
  Write-Log "OK 今日已签到（code=10001 兜底）"
  exit 0
}
else {
  $m = if ($r -and $r.msg) { $r.msg } else { '未知业务错误' }
  Write-Output "签到失败：业务码 $code，$m"
  Write-Log "FAIL code=$code msg=$m"
  exit 4
}
