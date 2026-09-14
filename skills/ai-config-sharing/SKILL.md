---
name: ai-config-sharing
description: >-
  统一管理多个 AI 编程助手（Claude、Codex、Cursor、Qoder、WorkBuddy、WorkBuddy AI、CatPaw 等）的
  skills/agents/AGENTS.md 配置。通过 Windows 目录联接（Junction）和硬链接（HardLink）
  实现单点维护、多工具共享。触发场景："共享 skills"、"统一 AI 配置"、"skills 同步"、
  "Junction 联接"、"AI 工具配置合并"、"hardlink AGENTS.md"、"共享 agents"、
  "有工具在自己目录自建了 skills"、"把自建 skill 同步回 .ai-shared"。
  适用于 Windows 环境，需 PowerShell 执行。
---

# AI 编程助手 Skills/Agents 共享配置

## 背景

用户同时使用多个 AI 编程助手（Claude Code、Codex、Cursor、Qoder、WorkBuddy、WorkBuddy AI、CatPaw 等），
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
  ... (cursor, qoder, workbuddy, workbuddy-ai, catpawai, agents 同理)
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
   foreach ($t in @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai','.agents')) {
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

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai')
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

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai')
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
$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai')
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

$tools = @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai')
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
   foreach ($t in @('.claude','.codex','.cursor','.qoder','.workbuddy','.workbuddy-ai','.catpawai','.agents')) {
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

## 阶段 8：工具自建 skills 回灌同步（只扫主路径）

### 为什么会有这一步

Junction 只接管了 `~\<工具>\skills` 这一层**主入口**。但工具在重装、更新或手动安装 skill 时，
可能把这个主入口**重建为真实目录**（Junction 被替换掉），于是在自己配置文件夹里长出一批
skills —— 这些 skill 不在 `.ai-shared` 中，**其他工具看不到**，共享事实上被打破。

典型症状：某个 skill 只在 Cursor 里能用，Claude / WorkBuddy 里搜不到。

### 扫描原则：只扫 `~\<工具>\skills` 主路径

**不要**递归扫整个 `~\<工具>\`。判断依据只有一个——主入口本身是什么：

| 主入口状态 | 含义 | 处理 |
|-----------|------|------|
| **Junction** → `.ai-shared\skills` | 已共享 | ✅ 无需处理 |
| **真实目录（REAL DIR）** | 工具自建/重装，内容脱离共享源 | ⚠️ 逐个比对，缺失的回灌到 `.ai-shared` |
| 不存在 | 该工具当前无 skills 目录 | — |

**明确不扫的路径**（重要，勿扩大范围）：

- `plugins\cache\`、`plugins\marketplaces\`、`connectors-marketplace\`、`connectors\skills\`
- `minimax-skills\`、`skills-update-temp\`、`.tmp\plugins\`
- `node_modules\`、`site-packages\`、`binaries\`、`envs\`

理由：这些是**工具私有的插件运行时缓存**——数量庞大（实测数百个）、随插件更新被覆盖、
且 skill 依赖对应插件/连接器的运行时与版本。复制进 `.ai-shared` 没有意义，只会污染共享源。
共享源只收「通用、可独立运行」的 skill。

### 操作

```powershell
$dir = "$env:USERPROFILE\.ai-shared\skills\ai-config-sharing\scripts"

# 1) 预览：列出每个工具主入口状态 + 未同步的 skill
powershell -ExecutionPolicy Bypass -File "$dir\collect-tool-skills.ps1"

# 2) 回灌：把缺失的 skill 复制进 .ai-shared\skills（不覆盖已存在的）
powershell -ExecutionPolicy Bypass -File "$dir\collect-tool-skills.ps1" -Apply

# 3) 只处理指定 skill
powershell -ExecutionPolicy Bypass -File "$dir\collect-tool-skills.ps1" -Apply -Name ui-ux-pro-max
```

脚本行为（已实测验证）：

- 输出「主入口状态表」：`SHARED` / `REAL-DIR` / `NO-SKILLS-DIR`
- 只列出 `.ai-shared` 中**尚不存在**的 skill；已存在的跳过，绝不覆盖
- 兼容 skill 包结构：`\<name>\SKILL.md` 与 `\<name>\skills\<sub>\SKILL.md` 都能识别
- 复制后校验目标是否含 `SKILL.md`，失败会 WARN
- 不传 `-Apply` 只预览，不写任何文件

### 回灌后

`.ai-shared\skills` 是所有工具 `skills\` 的 Junction 目标，新 skill 放进去后
**所有工具立即可见**，无需再做任何分发操作。

若某工具主入口已退化成真实目录，回灌完还应按「阶段 4」重建 Junction（先备份原目录内容），
否则下次它还会继续自建。

## 完整脚本

此 skill 目录下附带的脚本可直接执行：

| 脚本 | 用途 |
|------|------|
| `scripts/merge-share-skills.ps1` | 一键合并+共享（支持 `-DryRun` 预览、`-Restore` 恢复） |
| `scripts/verify-junctions.ps1` | 验证联接状态、内容一致性、写入穿透 |
| `scripts/collect-tool-skills.ps1` | **阶段 8**：扫描工具自建 skills（只扫主入口）并回灌到 `.ai-shared`（支持 `-Apply`、`-Name`） |
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
- **受限环境优先用原生 PowerShell**：在 WorkBuddy 沙箱等环境里，`cmd.exe` 从 **Bash 和 PowerShell 两个入口都被拦截**
  （报 `cmd.exe cannot be used from ...`）。此时**唯一可行路径是原生 cmdlet**，实测均可用：
  ```powershell
  New-Item -ItemType Junction -Path <链接> -Target <目标>   # 目录联接
  New-Item -ItemType HardLink -Path <链接> -Target <目标>   # 文件硬链接
  ```
  删除联接（不要 `Remove-Item -Recurse`，会连目标内容一起删）：
  `[System.IO.Directory]::Delete($link, $false)`；判断是否联接用 `(Get-Item $p -Force).LinkType -eq 'Junction'`。

### 兼容性
- **Junction 跨卷**：Junction 只能指向本地路径，不能跨网络驱动器
- **HardLink 跨卷**：HardLink 必须在同一卷（同一盘符），跨卷会降级为复制
- **`.lnk` ≠ Junction**：`.lnk` 快捷方式对程序不透明，必须替换为 Junction
- **工具更新**：如果工具通过插件市场更新 skill，更新会写入共享目录，所有工具同步受益

### 维护
- **修改入口**：以后只在 `~/.ai-shared/` 中修改 skills/agents/AGENTS.md 与 `AI_READ_FIRST.md`
- **定期检查自建**：工具重装/更新后可能把 `~\<工具>\skills` 从 Junction 变回真实目录，
  跑 `collect-tool-skills.ps1` 看状态表即可（正常应全部 `SHARED`）。发现 `REAL-DIR` 就回灌 + 重建 Junction
- **回灌范围**：只收「通用可独立运行」的 skill；插件/连接器市场缓存里的 skill 依赖运行时，不要回灌
- **AI 先读说明**：每个工具目录的 `AI_READ_FIRST.md` 是硬链接到 `.ai-shared\AI_READ_FIRST.md` 的副本；
  说明须覆盖 AGENTS.md（硬链接）+ skills/、agents/（目录联接）。需改说明只改源文件，副本自动同步。
- **新增工具**：新装 AI 工具时，删除其默认 `skills/`/`agents/` 目录，创建 Junction 指向共享目录，
  并为其创建 `AI_READ_FIRST.md` 硬链接（见阶段 7）
- **同工具多实例**（2026-09-14 新增）：WorkBuddy 存在 `.workbuddy` 与 `.workbuddy-ai` 两个**独立**配置目录
  （各自有 `binaries\`、`sessions\`、`workbuddy.db`、`settings.json`）。只联接**配置类**对象——
  `skills\`、`agents\`（Junction）+ `AGENTS.md`、`AI_READ_FIRST.md`（HardLink）；
  **运行时数据一律不联接**（否则两个实例会互相覆盖会话/数据库/工作区）。
  新增实例时按同一套 4 项操作处理，并把目录名加进 `collect-tool-skills.ps1` 的 `-Tools` 与
  `verify-junctions.ps1` 的工具表，否则定期体检会漏掉它。
- **定期备份**：重大修改前备份 `.ai-shared/` 目录

### 已知限制
- 仅适用于 Windows（macOS/Linux 用 `ln -s` 符号链接）
- 目录联接不能跨网络驱动器（SMB/NFS）
- 如果工具的 skill 加载器有特殊路径逻辑（如递归搜索 `SKILL.md`），Junction 不影响此行为

### 写 PowerShell 脚本时的两个坑（本 skill 脚本已踩过）

1. **中文脚本必须存成 UTF-8 with BOM**：Windows PowerShell 5.1 按 ANSI 读取无 BOM 的 `.ps1`，
   中文注释会导致解析失败（报一堆 `ParserError`，甚至完全没输出）。
2. **双引号里 `$var:` 会被当成驱动器限定变量**：`"$n: xxx"` 报
   `变量引用无效。':' 后面的变量名称字符无效`，必须写成 `"${n}: xxx"`。

### 用「PowerShell 工具」时的两个坑（2026-09-14 实测）

1. **stdout 可能完全不被捕获**：工具只回一句 `Command completed with exit code 0`，`Write-Output`/`Write-Host`
   都拿不到。**解决办法：把结果写进文件再读**——
   `$L -join "`r`n" | Out-File $LOG -Encoding UTF8`（或用 `-Append` **逐步追加**，
   便于在命令中途被安全策略中断时定位到具体哪一步）。
2. **`$env:TEMP` 不一定是 `%LOCALAPPDATA%\Temp`**：本机解析为 `D:\WindowsTemp`。
   找日志时别按默认路径猜，直接在脚本里打印或用固定绝对路径（如项目 `.workbuddy\` 下）。
3. **一次执行太多步骤容易中途被杀**：把「备份 → 删原目录 → 建链接 → 验证」拆成多轮，
   每轮先写日志，避免半途失败后既无日志又不知道状态（本次踩过：备份和删除已生效但断言脚本整体退出，日志没落盘）。

排查技巧：脚本跑起来「什么都没输出」时，用 `Start-Transcript` 捕获——
`Write-Host` **不进入管道**，`... | Out-File` 抓不到它，容易误判成脚本没执行。
