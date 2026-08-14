# ==============================================================================
# AI 编程助手 Skills/Agents 统一合并与共享脚本
#
# 策略：
#   1. 以 .claude 为基准（与 .qoder、.codex 完全一致）
#   2. 合并 .cursor 独有文件（skill-creator 用 cursor 扁平结构、repo-wiki 合并脚本等）
#   3. 合并 .workbuddy 独有 skill（arxiv-paper-downloader）和 _user_meta.json
#   4. 合并 .codex 的 .system 目录
#   5. 备份所有工具原始目录 -> 创建 Directory Junction
#
# 用法：
#   预览:  powershell -ExecutionPolicy Bypass -File merge-share-skills.ps1 -DryRun
#   执行:  powershell -ExecutionPolicy Bypass -File merge-share-skills.ps1
#   恢复:  powershell -ExecutionPolicy Bypass -File merge-share-skills.ps1 -Restore
# ==============================================================================

param(
    [switch]$DryRun,
    [switch]$Restore
)

$ErrorActionPreference = "Stop"

# --- 路径配置 ---
$Home2 = "C:\Users\20448"
$SharedRoot     = Join-Path $Home2 ".ai-shared"
$SharedSkills   = Join-Path $SharedRoot "skills"
$SharedAgents   = Join-Path $SharedRoot "agents"
$SharedAgentsMd = Join-Path $SharedRoot "AGENTS.md"

$ClaudeSkills   = Join-Path $Home2 ".claude\skills"
$ClaudeAgents   = Join-Path $Home2 ".claude\agents"
$ClaudeAgentsMd = Join-Path $Home2 ".claude\AGENTS.md"
$CursorSkills   = Join-Path $Home2 ".cursor\skills"
$CodexSkills    = Join-Path $Home2 ".codex\skills"
$WBSkills       = Join-Path $Home2 ".workbuddy\skills"

$Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$BackupRoot = Join-Path $Home2 ".ai-shared-backup-$Timestamp"

# 要配置的工具
$Tools = @(
    @{ Name = "claude";   Path = Join-Path $Home2 ".claude" }
    @{ Name = "codex";    Path = Join-Path $Home2 ".codex" }
    @{ Name = "cursor";   Path = Join-Path $Home2 ".cursor" }
    @{ Name = "qoder";    Path = Join-Path $Home2 ".qoder" }
    @{ Name = "workbuddy"; Path = Join-Path $Home2 ".workbuddy" }
)

# --- 辅助函数 ---

function Log {
    param([string]$Msg, [string]$Level = "INFO")
    $colors = @{ INFO="Cyan"; OK="Green"; WARN="Yellow"; ERR="Red"; DRY="Magenta" }
    $c = $colors[$Level]; if (-not $c) { $c = "White" }
    $prefix = if ($DryRun) { "[DRY] " } else { "" }
    Write-Host "${prefix}[$Level] $Msg" -ForegroundColor $c
}

function IsJunction {
    param([string]$P)
    if (-not (Test-Path $P)) { return $false }
    $item = Get-Item $P -Force -ErrorAction SilentlyContinue
    return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
}

function SafeRemove {
    param([string]$P)
    if ($DryRun) { Log "DEL: $P" "DRY"; return }
    if (IsJunction $P) {
        cmd /c "rmdir `"$P`"" 2>$null
    } elseif (Test-Path $P) {
        Remove-Item $P -Recurse -Force -ErrorAction SilentlyContinue
    }
}

function MakeJunction {
    param([string]$Target, [string]$Link)
    if ($DryRun) { Log "JUNCTION: $Link -> $Target" "DRY"; return }
    cmd /c "mklink /J `"$Link`" `"$Target`"" 2>$null | Out-Null
    if (IsJunction $Link) {
        Log "OK: $Link -> $Target" "OK"
    } else {
        Log "FAIL: $Link -> $Target" "ERR"
    }
}

function MakeHardLink {
    param([string]$Target, [string]$Link)
    if ($DryRun) { Log "HARDLINK: $Link -> $Target" "DRY"; return }
    cmd /c "mklink /H `"$Link`" `"$Target`"" 2>$null | Out-Null
    if (-not (Test-Path $Link)) {
        Copy-Item $Target $Link -Force -ErrorAction SilentlyContinue
        Log "COPY (hardlink failed): $Link" "WARN"
    } else {
        Log "OK: $Link -> $Target (hardlink)" "OK"
    }
}

function CopyTree {
    param([string]$Src, [string]$Dst)
    if ($DryRun) { Log "COPY: $Src -> $Dst" "DRY"; return }
    if (-not (Test-Path $Dst)) { New-Item -ItemType Directory -Path $Dst -Force | Out-Null }
    Copy-Item -Path "$Src\*" -Destination $Dst -Recurse -Force -ErrorAction SilentlyContinue
}

function OverlayUniqueFiles {
    param([string]$SrcDir, [string]$DstDir)
    # 将 SrcDir 中 DstDir 不存在的文件复制过去（不覆盖已有文件）
    if (-not (Test-Path $SrcDir)) { return }
    Get-ChildItem $SrcDir -Recurse -File -ErrorAction SilentlyContinue | ForEach-Object {
        $rel = $_.FullName.Substring($SrcDir.Length).TrimStart('\','/')
        $dstFile = Join-Path $DstDir $rel
        $dstDir2 = Split-Path $dstFile -Parent
        if (-not (Test-Path $dstFile)) {
            if ($DryRun) {
                Log "OVERLAY: $rel" "DRY"
            } else {
                if (-not (Test-Path $dstDir2)) { New-Item -ItemType Directory -Path $dstDir2 -Force | Out-Null }
                Copy-Item $_.FullName $dstFile -Force -ErrorAction SilentlyContinue
            }
        }
    }
}

# --- 恢复模式 ---
if ($Restore) {
    Log "=== RESTORE MODE ===" "WARN"
    if (-not (Test-Path $BackupRoot)) {
        Log "Backup not found: $BackupRoot" "ERR"
        $dirs = Get-ChildItem $Home2 -Directory -Filter ".ai-shared-backup-*" -ErrorAction SilentlyContinue
        if ($dirs) {
            Log "Available backups:" "WARN"
            $dirs | ForEach-Object { Write-Host "  $($_.FullName)" }
        }
        exit 1
    }
    foreach ($tool in $Tools) {
        $tn = $tool.Name; $tp = $tool.Path
        Log "Restoring $tn ..." "INFO"
        $bp = Join-Path $BackupRoot $tn

        $skillsPath = Join-Path $tp "skills"
        $agentsPath = Join-Path $tp "agents"
        $agentsMdPath = Join-Path $tp "AGENTS.md"

        if (IsJunction $skillsPath) { SafeRemove $skillsPath }
        if (IsJunction $agentsPath) { SafeRemove $agentsPath }
        if (IsJunction $agentsMdPath) { SafeRemove $agentsMdPath }  # junction for file won't exist, but check

        $bkSkills = Join-Path $bp "skills"
        $bkAgents = Join-Path $bp "agents"
        $bkAgentsMd = Join-Path $bp "AGENTS.md"

        if (Test-Path $bkSkills) { CopyTree $bkSkills $skillsPath }
        if (Test-Path $bkAgents) { CopyTree $bkAgents $agentsPath }
        if (Test-Path $bkAgentsMd) { if (-not $DryRun) { Copy-Item $bkAgentsMd $agentsMdPath -Force } }

        Log "$tn restored" "OK"
    }
    Log "Restore complete!" "OK"
    exit 0
}

# --- 主流程 ---

Log "=== MERGE & SHARE SKILLS/AGENTS ===" "INFO"
Log "Shared root: $SharedRoot" "INFO"
Log "Backup root: $BackupRoot" "INFO"
Log ""

# ================================================================
# 步骤 1: 创建共享目录 + 合并所有工具的内容
# ================================================================
Log "Step 1: Build shared directory (merge all sources)" "INFO"

# 1a. 以 .claude skills 为基准
Log "  1a. Base: copy .claude\skills -> shared" "INFO"
if (-not $DryRun) { New-Item -ItemType Directory -Path $SharedRoot -Force | Out-Null }
CopyTree $ClaudeSkills $SharedSkills

# 1b. 合并 .codex 的 .system 目录
Log "  1b. Merge: .codex\skills\.system -> shared" "INFO"
$codexSystem = Join-Path $CodexSkills ".system"
if (Test-Path $codexSystem) {
    $sharedSystem = Join-Path $SharedSkills ".system"
    CopyTree $codexSystem $sharedSystem
}

# 1c. 合并 .cursor 独有文件
Log "  1c. Merge: .cursor unique files -> shared" "INFO"

# skill-creator: 用 cursor 的扁平结构替换（SKILL.md 在根目录更兼容）
Log "    skill-creator: replace with .cursor flat structure" "INFO"
$scDst = Join-Path $SharedSkills "skill-creator"
SafeRemove $scDst
CopyTree (Join-Path $CursorSkills "skill-creator") $scDst

# repo-wiki: overlay cursor 独有文件
Log "    repo-wiki: overlay .cursor unique files" "INFO"
OverlayUniqueFiles (Join-Path $CursorSkills "repo-wiki") (Join-Path $SharedSkills "repo-wiki")

# superpowers: overlay cursor 独有文件
Log "    superpowers: overlay .cursor unique files" "INFO"
OverlayUniqueFiles (Join-Path $CursorSkills "superpowers") (Join-Path $SharedSkills "superpowers")

# awesome-ai-research-writing: overlay .openskills.json
Log "    awesome-ai-research-writing: overlay .openskills.json" "INFO"
OverlayUniqueFiles (Join-Path $CursorSkills "awesome-ai-research-writing") (Join-Path $SharedSkills "awesome-ai-research-writing")

# web-access: overlay config.env
Log "    web-access: overlay config.env" "INFO"
OverlayUniqueFiles (Join-Path $CursorSkills "web-access") (Join-Path $SharedSkills "web-access")

# humanizer-zh: .claude 已有完整内容，cursor 缺少文件，无需 overlay

# 1d. 合并 .workbuddy 独有内容
Log "  1d. Merge: .workbuddy unique content -> shared" "INFO"

# arxiv-paper-downloader (独有 skill)
Log "    arxiv-paper-downloader: copy from .workbuddy" "INFO"
CopyTree (Join-Path $WBSkills "arxiv-paper-downloader") (Join-Path $SharedSkills "arxiv-paper-downloader")

# kaggle-notebookify: overlay _user_meta.json
Log "    kaggle-notebookify: overlay _user_meta.json" "INFO"
$wbMetaSrc = Join-Path $WBSkills "kaggle-notebookify\_user_meta.json"
$wbMetaDst = Join-Path $SharedSkills "kaggle-notebookify\_user_meta.json"
if (Test-Path $wbMetaSrc) {
    if (-not (Test-Path $wbMetaDst)) {
        if (-not $DryRun) {
            $metaDir = Split-Path $wbMetaDst -Parent
            if (-not (Test-Path $metaDir)) { New-Item -ItemType Directory -Path $metaDir -Force | Out-Null }
            Copy-Item $wbMetaSrc $wbMetaDst -Force
        }
        Log "    _user_meta.json merged" "OK"
    }
}

# 1e. 复制 agents 目录
Log "  1e. Copy agents (.claude -> shared)" "INFO"
CopyTree $ClaudeAgents $SharedAgents

# 1f. 复制 AGENTS.md
Log "  1f. Copy AGENTS.md (.claude -> shared)" "INFO"
if (-not $DryRun) {
    Copy-Item $ClaudeAgentsMd $SharedAgentsMd -Force -ErrorAction SilentlyContinue
}

# 统计
if (-not $DryRun) {
    $skillCount = (Get-ChildItem $SharedSkills -Directory -ErrorAction SilentlyContinue).Count
    $agentCount = (Get-ChildItem $SharedAgents -File -ErrorAction SilentlyContinue).Count
    Log "Shared skills: $skillCount, agents: $agentCount" "OK"
}
Log ""

# ================================================================
# 步骤 2: 备份所有工具原始目录
# ================================================================
Log "Step 2: Backup original directories" "INFO"
if (-not $DryRun) { New-Item -ItemType Directory -Path $BackupRoot -Force | Out-Null }

foreach ($tool in $Tools) {
    $tn = $tool.Name; $tp = $tool.Path
    $tbk = Join-Path $BackupRoot $tn
    if (-not $DryRun) { New-Item -ItemType Directory -Path $tbk -Force | Out-Null }

    $skillsPath = Join-Path $tp "skills"
    $agentsPath = Join-Path $tp "agents"
    $agentsMdPath = Join-Path $tp "AGENTS.md"

    if (IsJunction $skillsPath) {
        Log "  $tn\skills already junction, skip backup" "WARN"
    } elseif (Test-Path $skillsPath) {
        Log "  Backup $tn\skills" "INFO"
        CopyTree $skillsPath (Join-Path $tbk "skills")
    }

    if (IsJunction $agentsPath) {
        Log "  $tn\agents already junction, skip backup" "WARN"
    } elseif (Test-Path $agentsPath) {
        Log "  Backup $tn\agents" "INFO"
        CopyTree $agentsPath (Join-Path $tbk "agents")
    }

    if (Test-Path $agentsMdPath) {
        Log "  Backup $tn\AGENTS.md" "INFO"
        if (-not $DryRun) { Copy-Item $agentsMdPath (Join-Path $tbk "AGENTS.md") -Force -ErrorAction SilentlyContinue }
    }
}
Log ""

# ================================================================
# 步骤 3: 删除原始目录，创建 Junction
# ================================================================
Log "Step 3: Replace with Directory Junctions" "INFO"

foreach ($tool in $Tools) {
    $tn = $tool.Name; $tp = $tool.Path
    Log "  --- $tn ---" "INFO"

    # skills
    $skillsPath = Join-Path $tp "skills"
    if (IsJunction $skillsPath) {
        if (-not $DryRun) { cmd /c "rmdir `"$skillsPath`"" 2>$null }
    } elseif (Test-Path $skillsPath) {
        SafeRemove $skillsPath
    }
    if (-not (Test-Path $skillsPath) -or $DryRun) {
        Log "  skills -> shared" "INFO"
        MakeJunction $SharedSkills $skillsPath
    }

    # agents
    $agentsPath = Join-Path $tp "agents"
    if (IsJunction $agentsPath) {
        if (-not $DryRun) { cmd /c "rmdir `"$agentsPath`"" 2>$null }
    } elseif (Test-Path $agentsPath) {
        SafeRemove $agentsPath
    }
    # workbuddy 原来没有 agents 目录，创建 junction 让它也共享
    Log "  agents -> shared" "INFO"
    MakeJunction $SharedAgents $agentsPath

    # AGENTS.md (hardlink)
    $agentsMdPath = Join-Path $tp "AGENTS.md"
    if (Test-Path $agentsMdPath) { SafeRemove $agentsMdPath }
    if (Test-Path $SharedAgentsMd) {
        Log "  AGENTS.md -> shared (hardlink)" "INFO"
        MakeHardLink $SharedAgentsMd $agentsMdPath
    }

    Log "  $tn done" "OK"
}
Log ""

# ================================================================
# 步骤 4: 验证
# ================================================================
Log "Step 4: Verify junctions" "INFO"

$allOk = $true
foreach ($tool in $Tools) {
    $tn = $tool.Name; $tp = $tool.Path
    $sp = Join-Path $tp "skills"
    $ap = Join-Path $tp "agents"
    $mp = Join-Path $tp "AGENTS.md"

    if (IsJunction $sp) { $sOk = "OK" } else { $sOk = "FAIL"; $allOk = $false }
    if (IsJunction $ap) { $aOk = "OK" } else { $aOk = "FAIL"; $allOk = $false }
    if (Test-Path $mp) { $mOk = "OK" } else { $mOk = "MISS" }

    $color = if ($sOk -eq "OK" -and $aOk -eq "OK") { "Green" } else { "Red" }
    Write-Host "  ${tn}: skills=$sOk agents=$aOk AGENTS.md=$mOk" -ForegroundColor $color
}

Log ""
if ($allOk) {
    Log "=== ALL DONE ===" "OK"
} else {
    Log "=== COMPLETED WITH WARNINGS ===" "WARN"
}

Log "Shared dir:  $SharedRoot" "INFO"
Log "Backup dir:  $BackupRoot" "INFO"
Log ""
Log "Notes:" "WARN"
Log "  - Edit skills/agents only in: $SharedRoot" "WARN"
Log "  - All 5 tools now share the same skills & agents" "WARN"
Log "  - Restore: powershell -File `"$PSCommandPath`" -Restore" "WARN"
