---
name: ai-config-sharing
description: >-
  统一管理多个 AI 编程助手（Claude、Codex、Cursor、Qoder、WorkBuddy、CatPaw 等）的
  skills/agents/AGENTS.md 配置。通过 Windows 目录联接（Junction）和硬链接（HardLink）
  实现单点维护、多工具共享。触发场景："共享 skills"、"统一 AI 配置"、"skills 同步"、
  "Junction 联接"、"AI 工具配置合并"、"hardlink AGENTS.md"、"共享 agents"。
  适用于 Windows 环境，需 PowerShell 执行。
---

# AI 编程助手 Skills/Agents 共享配置

## 背景

用户同时使用多个 AI 编程助手（Claude Code、Codex、Cursor、Qoder、WorkBuddy、CatPaw 等），
每个工具在 `~/.<工具名>/` 下维护独立的 `skills/`、`agents/` 和 `AGENTS.md`。
这些文件内容高度重复，导致：

- **维护成本高**：改一个 skill 要同步到 5~6 个目录
- **磁盘浪费**：相同内容复制多份
- **不一致风险**：某些工具的 skill 版本落后

## 核心原理

### Windows 链接类型对比

| 类型 | 命令 | 适用对象 | 需管理员 | 程序透明 | 用途 |
|------|------|---------|----------|---------|------|
| **目录联接 (Junction)** | `mklink /J` | 目录 | 否 | **是** | skills/、agents/ 目录 |
| **硬链接 (HardLink)** | `mklink /H` | 文件 | 否 | **是** | AGENTS.md 文件 |
| 符号链接 (Symlink) | `mklink /D` | 目录 | 是 | 是 | — |
| 快捷方式 (.lnk) | 资源管理器 | 文件/目录 | 否 | **否** | ❌ 不适用 |

**关键**：Junction 和 HardLink 对程序完全透明——程序以为自己在读本地目录/文件，
实际读取的是共享目录。**`.lnk` 快捷方式对程序不透明，不能用。**

### 共享架构

```
C:\Users\<用户>\.ai-shared\           ← 唯一维护点
  ├── skills/          (22 个 skill 目录)
  ├── agents/          (5 个 agent 文件)
  └── AGENTS.md        (全局规则)

~/.claude/skills/     ──Junction──→ .ai-shared/skills/
~/.claude/agents/     ──Junction──→ .ai-shared/agents/
~/.claude/AGENTS.md   ──HardLink──→ .ai-shared/AGENTS.md
~/.codex/skills/      ──Junction──→ .ai-shared/skills/
~/.codex/agents/      ──Junction──→ .ai-shared/agents/
~/.codex/AGENTS.md    ──HardLink──→ .ai-shared/AGENTS.md
  ... (cursor, qoder, workbuddy, catpawai 同理)
```

## 触发场景

- 用户说"共享 skills"、"统一 AI 配置"、"skills 同步"
- 用户说"几个 AI 工具的 skills 重复了"
- 用户说"Junction 联接"、"hardlink AGENTS.md"
- 用户说"合并 skills 目录"
- 用户发现多个 AI 工具的 skills/agents 内容不一致

## 前置检查

动手前必须确认：

1. **操作系统**：此方案仅适用于 **Windows**（macOS/Linux 用 symlink）
2. **工具路径**：确认各工具配置目录存在
   ```powershell
   foreach ($t in @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai')) {
       $p = "$env:USERPROFILE\$t"
       Write-Host "$t exists: $(Test-Path $p)"
   }
   ```
3. **是否已有联接**：避免重复操作
   ```powershell
   $p = "$env:USERPROFILE\.claude\skills"
   $item = Get-Item $p -Force -ErrorAction SilentlyContinue
   $isJunction = ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
   Write-Host "Is Junction: $isJunction, LinkType: $($item.LinkType)"
   ```
4. **备份**：操作前必须备份原始目录

## 操作流程

### 阶段 1：差异对比

对比各工具 skills/agents 的内容，确定合并策略。

```powershell
# 列出各工具的 skill 名称
$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy')
foreach ($t in $tools) {
    $p = "$env:USERPROFILE\$t\skills"
    if (Test-Path $p) {
        $dirs = Get-ChildItem $p -Directory | Select-Object -ExpandProperty Name
        Write-Host "$t ($($dirs.Count) skills): $($dirs -join ', ')"
    }
}

# 文件级差异对比（以 .claude vs .cursor 为例）
function Get-FileTree($path) {
    Get-ChildItem $path -Recurse -File | ForEach-Object {
        $_.FullName.Substring($path.Length).TrimStart('\','/')
    }
}
$claudeFiles = Get-FileTree "$env:USERPROFILE\.claude\skills\repo-wiki" | Sort-Object
$cursorFiles = Get-FileTree "$env:USERPROFILE\.cursor\skills\repo-wiki" | Sort-Object
# 找出各自独有的文件
$onlyClaude = $claudeFiles | Where-Object { $cursorFiles -notcontains $_ }
$onlyCursor = $cursorFiles | Where-Object { $claudeFiles -notcontains $_ }
```

### 阶段 2：合并到共享目录

**策略**：选最完整的工具作为基准，逐个 skill 合并其他工具的独有文件。

```powershell
$SharedRoot = "$env:USERPROFILE\.ai-shared"
$SharedSkills = "$SharedRoot\skills"

# 1. 创建共享目录
New-Item -ItemType Directory -Path $SharedRoot -Force | Out-Null

# 2. 以最完整的工具为基准（通常 .claude 或 .codex）
$baseSkills = "$env:USERPROFILE\.claude\skills"
Copy-Item -Path "$baseSkills\*" -Destination $SharedSkills -Recurse -Force

# 3. 合并其他工具独有的 skill（不覆盖已有文件）
function Merge-UniqueFiles($srcDir, $dstDir) {
    Get-ChildItem $srcDir -Recurse -File | ForEach-Object {
        $rel = $_.FullName.Substring($srcDir.Length).TrimStart('\','/')
        $dst = Join-Path $dstDir $rel
        if (-not (Test-Path $dst)) {
            $dir = Split-Path $dst -Parent
            if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
            Copy-Item $_.FullName $dst -Force
            Write-Host "  Merged: $rel"
        }
    }
}

# 遍历其他工具，合并独有文件
foreach ($t in @('.cursor','.codex','.qoder','.workbuddy')) {
    $src = "$env:USERPROFILE\$t\skills"
    if (Test-Path $src) {
        Write-Host "Merging from $t..."
        Merge-UniqueFiles $src $SharedSkills
    }
}

# 4. 复制 agents 和 AGENTS.md
Copy-Item "$env:USERPROFILE\.claude\agents\*" "$SharedRoot\agents\" -Recurse -Force
Copy-Item "$env:USERPROFILE\.claude\AGENTS.md" "$SharedRoot\AGENTS.md" -Force
```

**合并注意事项**：
- 某些 skill 可能存在**结构性差异**（如 `.claude` 的 `skill-creator` 是嵌套目录 `skills/skill-creator/SKILL.md`，而 `.cursor` 是扁平结构 `SKILL.md`）。遇到这种情况，选择**扁平结构**（`SKILL.md` 在根目录）更兼容
- `.lnk` 快捷方式文件**不是**目录联接，必须替换为 Junction
- 某些工具有独有目录（如 `.codex` 的 `.system/`），需要单独合并

### 阶段 3：备份

**必须先备份再删除原始目录。**

```powershell
$ts = Get-Date -Format 'yyyyMMdd-HHmmss'
$backup = "$env:USERPROFILE\.ai-shared-backup-$ts"
New-Item -ItemType Directory -Path $backup -Force | Out-Null

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai')
foreach ($t in $tools) {
    $tp = "$env:USERPROFILE\$t"
    $tb = "$backup\$($t.TrimStart('.'))"
    New-Item -ItemType Directory -Path $tb -Force | Out-Null
    
    # 备份 skills（如果不是 junction）
    $sp = "$tp\skills"
    if (-not (IsJunction $sp) -and (Test-Path $sp)) {
        Copy-Item "$sp\*" "$tb\skills\" -Recurse -Force
    }
    # 备份 agents
    $ap = "$tp\agents"
    if (-not (IsJunction $ap) -and (Test-Path $ap)) {
        Copy-Item "$ap\*" "$tb\agents\" -Recurse -Force
    }
    # 备份 AGENTS.md
    $mp = "$tp\AGENTS.md"
    if (Test-Path $mp) { Copy-Item $mp "$tb\AGENTS.md" -Force }
}
Write-Host "Backup: $backup"
```

### 阶段 4：创建联接

**先删后建**——删除原始目录/文件，创建 Junction/HardLink 指向共享目录。

```powershell
function IsJunction($path) {
    if (-not (Test-Path $path)) { return $false }
    $item = Get-Item $path -Force -ErrorAction SilentlyContinue
    return ($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
}

$SharedSkills = "$env:USERPROFILE\.ai-shared\skills"
$SharedAgents = "$env:USERPROFILE\.ai-shared\agents"
$SharedAgentsMd = "$env:USERPROFILE\.ai-shared\AGENTS.md"

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai')
foreach ($t in $tools) {
    $tp = "$env:USERPROFILE\$t"
    
    # --- skills: 目录联接 ---
    $sp = "$tp\skills"
    if (IsJunction $sp) { cmd /c "rmdir `"$sp`"" 2>$null }  # 删联接不影响目标
    elseif (Test-Path $sp) { Remove-Item $sp -Recurse -Force }
    cmd /c "mklink /J `"$sp`" `"$SharedSkills`""
    
    # --- agents: 目录联接 ---
    $ap = "$tp\agents"
    if (IsJunction $ap) { cmd /c "rmdir `"$ap`"" 2>$null }
    elseif (Test-Path $ap) { Remove-Item $ap -Recurse -Force }
    cmd /c "mklink /J `"$ap`" `"$SharedAgents`""
    
    # --- AGENTS.md: 硬链接 ---
    $mp = "$tp\AGENTS.md"
    if (Test-Path $mp) { Remove-Item $mp -Force }
    cmd /c "mklink /H `"$mp`" `"$SharedAgentsMd`""
    
    Write-Host "$t: skills=$(IsJunction $sp), agents=$(IsJunction $ap), AGENTS.md=$(Test-Path $mp)"
}
```

**关键命令**：
- `mklink /J "链接" "目标"` — 创建目录联接
- `mklink /H "链接" "目标"` — 创建文件硬链接
- `rmdir "联接路径"` — 删除联接（不影响目标目录内容）
- **不要**用 `Remove-Item` 删联接——可能递归删除目标内容

### 阶段 5：验证

```powershell
# 1. 联接验证
$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai')
foreach ($t in $tools) {
    $tp = "$env:USERPROFILE\$t"
    $sp = "$tp\skills"; $ap = "$tp\agents"; $mp = "$tp\AGENTS.md"
    $sOk = IsJunction $sp
    $aOk = IsJunction $ap
    $mOk = (Test-Path $mp) -and ((Get-Item $mp).LinkType -eq 'HardLink')
    Write-Host "$t : skills=$($sOk?'OK':'FAIL') agents=$($aOk?'OK':'FAIL') AGENTS.md=$($mOk?'OK':'FAIL')"
}

# 2. 内容一致性验证（通过不同工具路径读取同一文件，MD5 应相同）
$testFile = "skills\git-commit\SKILL.md"
$hashes = @{}
foreach ($t in $tools) {
    $fullPath = "$env:USERPROFILE\$t\$testFile"
    if (Test-Path $fullPath) {
        $hashes[$t] = (Get-FileHash $fullPath -Algorithm MD5).Hash
    }
}
$allSame = ($hashes.Values | Sort-Object -Unique).Count -eq 1
Write-Host "Content consistent: $allSame"

# 3. 写入穿透测试（在共享目录创建文件，通过各工具路径读取）
$testContent = "junction-test-$(Get-Random)"
$testFile = "$env:USERPROFILE\.ai-shared\skills\.junction-test"
Set-Content $testFile -Value $testContent
foreach ($t in $tools) {
    $tp = "$env:USERPROFILE\$t\skills\.junction-test"
    if ((Test-Path $tp) -and ((Get-Content $tp -Raw).Trim() -eq $testContent)) {
        Write-Host "  $t: OK"
    } else {
        Write-Host "  $t: FAIL" -ForegroundColor Red
    }
}
Remove-Item $testFile -Force
```

### 阶段 6：恢复（如需要）

```powershell
# 恢复模式：从备份恢复原始目录
$backup = "$env:USERPROFILE\.ai-shared-backup-<timestamp>"

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai')
foreach ($t in $tools) {
    $tp = "$env:USERPROFILE\$t"
    $tn = $t.TrimStart('.')
    $bp = "$backup\$tn"
    
    # 删除联接
    $sp = "$tp\skills"; $ap = "$tp\agents"; $mp = "$tp\AGENTS.md"
    if (IsJunction $sp) { cmd /c "rmdir `"$sp`"" 2>$null }
    if (IsJunction $ap) { cmd /c "rmdir `"$ap`"" 2>$null }
    if (Test-Path $mp) { Remove-Item $mp -Force }
    
    # 从备份恢复
    if (Test-Path "$bp\skills") { Copy-Item "$bp\skills\*" "$tp\skills\" -Recurse -Force }
    if (Test-Path "$bp\agents") { Copy-Item "$bp\agents\*" "$tp\agents\" -Recurse -Force }
    if (Test-Path "$bp\AGENTS.md") { Copy-Item "$bp\AGENTS.md" "$tp\AGENTS.md" -Force }
}
```

### 阶段 7：写入「AI 先读」说明文件（推荐）

模型（AI 助手）读取的是**硬链接 / 联接后的副本**（如 `~/.claude/AGENTS.md`、`~/.claude/skills/`），
**不是**直接读 `~/.ai-shared`。为避免模型在副本目录里就地改写、破坏链接，应在每个工具目录放一份
「AI 先读」说明，讲清：AGENTS.md 是硬链接、skills/ 与 agents/ 是目录联接，统一在 `.ai-shared` 修改。

说明须覆盖三类对象：
- `AGENTS.md` → 硬链接（HardLink）→ `.ai-shared\AGENTS.md`
- `skills\`   → 目录联接（Junction）→ `.ai-shared\skills`
- `agents\`   → 目录联接（Junction）→ `.ai-shared\agents`

**步骤**：

1. 在共享源写唯一说明文件（之后硬链接分发，单点维护）：

   ```powershell
   $SharedRoot = "$env:USERPROFILE\.ai-shared"
   $note = @'
   # AI 先读 / READ FIRST — 本目录是共享配置的硬链接入口

   本目录（某个 AI 工具的配置根目录）通过链接指向唯一维护源：
       C:\Users\20448\.ai-shared
   具体映射关系：
   - AGENTS.md → 硬链接（HardLink） → C:\Users\20448\.ai-shared\AGENTS.md
   - skills\   → 目录联接（Junction） → C:\Users\20448\.ai-shared\skills\
   - agents\   → 目录联接（Junction） → C:\Users\20448\.ai-shared\agents\
   ## 重要：模型读的是这里的链接副本，不是 .ai-shared
   你（AI 助手）直接读取的就是本目录下的 AGENTS.md / skills\ / agents\。
   这些与 .ai-shared 下的是同一份内容：
   - AGENTS.md 是硬链接（HardLink）：任意一个被修改，其余全部立即同步。
   - skills\、agents\ 是目录联接（Junction）：读取与写入都透明穿透到 .ai-shared，无需复制。
   ## 更新规则（务必遵守）
   1. 要改配置，直接编辑唯一源 C:\Users\20448\.ai-shared\ 下的对应文件/目录。
   2. 保存后，本目录的 AGENTS.md / skills\ / agents\ 会自动同步更新。
   3. 不要在本目录直接改写 AGENTS.md，也不要删除它后用新文件覆盖（会破坏硬链接）。
   4. skills\ / agents\ 是目录联接，不要在本目录删除它们再重建（联接只应建一次）。
   5. 任何新增/调整都应在 C:\Users\20448\.ai-shared\ 中进行，由硬链接/联接自动分发到所有工具。
   '@
   Set-Content -Path "$SharedRoot\AI_READ_FIRST.md" -Value $note -Encoding UTF8
   ```

2. 硬链接到每个工具目录（与 AGENTS.md 同理，单点维护、自动同步）：

   ```powershell
   $SharedNote = "$env:USERPROFILE\.ai-shared\AI_READ_FIRST.md"
   foreach ($t in @('.claude','.codex','.cursor','.qoder','.workbuddy','.catpawai','.agents')) {
       $tp = "$env:USERPROFILE\$t"
       $target = "$tp\AI_READ_FIRST.md"
       if (-not (Test-Path $target)) {
           New-Item -ItemType HardLink -Path $target -Target $SharedNote -ErrorAction SilentlyContinue
       }
   }
   ```

> 说明：`.agents` 也是 AGENTS.md 的硬链接副本之一，按同样方式处理。
> 若希望模型在 `skills\` / `agents\` 目录内也能看到提示，可在 `.ai-shared\skills` 与
> `.ai-shared\agents` 中再放同名说明（联接透明，一处写入对所有工具生效）。

## 完整脚本

此 skill 目录下附带的脚本可直接执行：

| 脚本 | 用途 |
|------|------|
| `scripts/merge-share-skills.ps1` | 一键合并+共享（支持 `-DryRun` 预览、`-Restore` 恢复） |
| `scripts/verify-junctions.ps1` | 验证联接状态、内容一致性、写入穿透 |
| `scripts/fix-catpawai.ps1` | 修复 `.catpawai` 的 `.lnk` → Junction |

### 使用方法

```powershell
# 预览（不做任何更改）
powershell -ExecutionPolicy Bypass -File scripts\merge-share-skills.ps1 -DryRun

# 执行合并+共享
powershell -ExecutionPolicy Bypass -File scripts\merge-share-skills.ps1

# 恢复原始状态
powershell -ExecutionPolicy Bypass -File scripts\merge-share-skills.ps1 -Restore

# 验证
powershell -ExecutionPolicy Bypass -File scripts\verify-junctions.ps1
```

## 注意事项

### 安全性
- **必须先备份再操作**：脚本会创建带时间戳的备份目录
- **删除联接用 `rmdir`**：不用 `Remove-Item`，避免递归删除目标内容
- **`mklink` 需要 cmd 上下文**：PowerShell 原生 `New-Item -ItemType Junction` 也可以，但 `cmd /c "mklink /J"` 更可靠

### 兼容性
- **Junction 跨卷**：Junction 只能指向本地路径，不能跨网络驱动器
- **HardLink 跨卷**：HardLink 必须在同一卷（同一盘符），跨卷会降级为复制
- **`.lnk` ≠ Junction**：`.lnk` 快捷方式对程序不透明，必须替换为 Junction
- **工具更新**：如果工具通过插件市场更新 skill，更新会写入共享目录，所有工具同步受益

### 维护
- **修改入口**：以后只在 `~/.ai-shared/` 中修改 skills/agents/AGENTS.md 与 `AI_READ_FIRST.md`
- **AI 先读说明**：每个工具目录的 `AI_READ_FIRST.md` 是硬链接到 `.ai-shared\AI_READ_FIRST.md` 的副本；
  说明须覆盖 AGENTS.md（硬链接）+ skills/、agents/（目录联接）。需改说明只改源文件，副本自动同步。
- **新增工具**：新装 AI 工具时，删除其默认 `skills/`/`agents/` 目录，创建 Junction 指向共享目录，
  并为其创建 `AI_READ_FIRST.md` 硬链接（见阶段 7）
- **定期备份**：重大修改前备份 `.ai-shared/` 目录

### 已知限制
- 仅适用于 Windows（macOS/Linux 用 `ln -s` 符号链接）
- 目录联接不能跨网络驱动器（SMB/NFS）
- 如果工具的 skill 加载器有特殊路径逻辑（如递归搜索 `SKILL.md`），Junction 不影响此行为
