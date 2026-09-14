#Requires -Version 5.1
<#
.SYNOPSIS
    扫描各 AI 工具「主入口」~/<工具>/skills 下自建的 skills，回灌同步到 .ai-shared\skills。

.DESCRIPTION
    设计原则：只扫主路径，不做全盘递归。

    Junction 方案只接管 ~\.claude\skills 这一层「主入口」。因此判断工具是否自建了
    skills，只看这个主入口：
      - 是 Junction      → 已共享，无需处理
      - 是真实目录(REAL) → 工具在自己配置文件夹里自建/重装了 skills，
                           里面的 skill 不在 .ai-shared 中，其他工具看不到，需要回灌
      - 不存在           → 该工具当前没有 skills 目录

    为什么不扫 plugins\ / connectors\ / marketplaces\：
    那些路径是工具私有的插件运行时缓存，数量庞大、随插件更新被覆盖、且依赖插件本身，
    复制到 .ai-shared 没有意义（甚至污染共享源）。共享源只收「通用可独立运行」的 skill。

.PARAMETER SharedRoot  唯一维护源根目录，默认 $env:USERPROFILE\.ai-shared
.PARAMETER Apply       实际执行复制；不加则只预览
.PARAMETER Tools       要检查的工具配置目录名（相对 $env:USERPROFILE）
.PARAMETER Name        只处理指定 skill 名（可多次传或逗号分隔）

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File collect-tool-skills.ps1                # 预览
    powershell -ExecutionPolicy Bypass -File collect-tool-skills.ps1 -Apply         # 回灌
    powershell -ExecutionPolicy Bypass -File collect-tool-skills.ps1 -Apply -Name ui-ux-pro-max
#>
[CmdletBinding()]
param(
    [string]$SharedRoot = (Join-Path $env:USERPROFILE '.ai-shared'),
    [switch]$Apply,
    [string[]]$Tools = @('.claude', '.codex', '.cursor', '.qoder', '.workbuddy', '.workbuddy-ai', '.catpawai', '.agents'),
    [string[]]$Name = @()
)

$ErrorActionPreference = 'SilentlyContinue'
$SharedSkills = Join-Path $SharedRoot 'skills'

function Test-Junction($p) {
    $i = Get-Item $p -Force
    return ($i -and (($i.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0))
}

if (-not (Test-Path $SharedSkills)) {
    Write-Host "共享目录不存在: $SharedSkills" -ForegroundColor Red
    return 1
}

# .ai-shared\skills 中已有的 skill 名
$existing = @{}
Get-ChildItem $SharedSkills -Directory | ForEach-Object { $existing[$_.Name] = $true }

$cand = @{}    # skillName -> 源路径
$from = @{}    # skillName -> 工具名
$status = @()  # 每个工具的主入口状态

function Add-Cand($path, $tool) {
    $n = Split-Path $path -Leaf
    if ([string]::IsNullOrWhiteSpace($n)) { return }
    if (-not (Test-Path (Join-Path $path 'SKILL.md'))) { return }
    if (-not $cand.ContainsKey($n)) { $cand[$n] = $path; $from[$n] = $tool }
}

foreach ($t in $Tools) {
    $sp = Join-Path (Join-Path $env:USERPROFILE $t) 'skills'

    if (-not (Test-Path $sp)) {
        $status += [pscustomobject]@{ Tool = $t; State = 'NO-SKILLS-DIR'; Detail = '无 skills 目录' }
        continue
    }
    if (Test-Junction $sp) {
        $tgt = (Get-Item $sp -Force).Target -join ';'
        $status += [pscustomobject]@{ Tool = $t; State = 'SHARED'; Detail = "Junction -> $tgt" }
        continue
    }

    # 真实目录 → 工具自建，收集其下的 skill
    $n1 = 0
    Get-ChildItem $sp -Directory -Force | ForEach-Object {
        if (Test-Path (Join-Path $_.FullName 'SKILL.md')) {
            Add-Cand $_.FullName $t; $n1++
        } else {
            # 兼容 skill 包结构：<name>\skills\<sub>\SKILL.md
            $inner = Join-Path $_.FullName 'skills'
            if (Test-Path $inner) {
                Get-ChildItem $inner -Directory -Force | ForEach-Object {
                    Add-Cand $_.FullName $t; $n1++
                }
            }
        }
    }
    $status += [pscustomobject]@{ Tool = $t; State = 'REAL-DIR'; Detail = "自建目录，发现 $n1 个 skill" }
}

Write-Host "`n=== 主入口状态 (~\<工具>\skills) ===" -ForegroundColor Cyan
$status | Format-Table -AutoSize Tool, State, Detail

$missing = @($cand.Keys | Where-Object { -not $existing.ContainsKey($_) } | Sort-Object)
if ($Name.Count -gt 0) { $missing = @($missing | Where-Object { $Name -contains $_ }) }

if ($missing.Count -eq 0) {
    Write-Host "没有「自建但未同步」的 skill —— 所有工具的 skills 主入口都已指向共享源。" -ForegroundColor Green
    return 0
}

Write-Host "=== 自建但未同步到 .ai-shared 的 skills ($($missing.Count)) ===" -ForegroundColor Cyan
$rows = foreach ($n in $missing) {
    [pscustomobject]@{
        Skill = $n
        From  = $from[$n]
        KB    = [math]::Round(((Get-ChildItem $cand[$n] -Recurse -File | Measure-Object -Property Length -Sum).Sum / 1KB), 1)
        Path  = $cand[$n]
    }
}
$rows | Format-Table -AutoSize Skill, From, KB

if (-not $Apply) {
    Write-Host "（预览）加 -Apply 执行回灌复制。" -ForegroundColor Yellow
    return 0
}

$ok = 0; $fail = 0
foreach ($n in $missing) {
    $dst = Join-Path $SharedSkills $n
    if (Test-Path $dst) { Write-Host "  SKIP (已存在): $n" -ForegroundColor DarkGray; continue }
    try {
        Copy-Item -Path $cand[$n] -Destination $dst -Recurse -Force
        if (Test-Path (Join-Path $dst 'SKILL.md')) {
            Write-Host "  OK   $n  <- $($from[$n])" -ForegroundColor Green; $ok++
        } else {
            Write-Host "  WARN ${n}: 复制后缺少 SKILL.md" -ForegroundColor Yellow; $fail++
        }
    } catch {
        Write-Host "  FAIL ${n}: $($_.Exception.Message)" -ForegroundColor Red; $fail++
    }
}
Write-Host "`n完成：成功 $ok，失败 $fail。回灌后所有工具的 skills\ (Junction) 立即可见。" -ForegroundColor Cyan
return 0
