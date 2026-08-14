# Fix .catpawai: replace .lnk shortcuts with Junctions, add AGENTS.md hardlink

$catPawDir = "C:\Users\20448\.catpawai"
$sharedSkills = "C:\Users\20448\.ai-shared\skills"
$sharedAgents = "C:\Users\20448\.ai-shared\agents"
$sharedAgentsMd = "C:\Users\20448\.ai-shared\AGENTS.md"

Write-Host "=== Fix .catpawai ===" -ForegroundColor Cyan

# Step 1: Replace skills.lnk with Junction
$skillsLnk = Join-Path $catPawDir "skills.lnk"
$skillsDir = Join-Path $catPawDir "skills"

Write-Host "1. Replace skills.lnk -> Junction" -ForegroundColor Yellow
if (Test-Path $skillsLnk) {
    Remove-Item $skillsLnk -Force
    Write-Host "  Deleted skills.lnk" -ForegroundColor Gray
}
if (-not (Test-Path $skillsDir)) {
    cmd /c "mklink /J `"$skillsDir`" `"$sharedSkills`"" 2>$null | Out-Null
    if ((Get-Item $skillsDir -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        Write-Host "  OK: skills Junction -> $sharedSkills" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: skills Junction" -ForegroundColor Red
    }
} else {
    Write-Host "  skills dir already exists" -ForegroundColor Yellow
}

# Step 2: Replace agents.lnk with Junction
$agentsLnk = Join-Path $catPawDir "agents.lnk"
$agentsDir = Join-Path $catPawDir "agents"

Write-Host "2. Replace agents.lnk -> Junction" -ForegroundColor Yellow
if (Test-Path $agentsLnk) {
    Remove-Item $agentsLnk -Force
    Write-Host "  Deleted agents.lnk" -ForegroundColor Gray
}
if (-not (Test-Path $agentsDir)) {
    cmd /c "mklink /J `"$agentsDir`" `"$sharedAgents`"" 2>$null | Out-Null
    if ((Get-Item $agentsDir -Force).Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        Write-Host "  OK: agents Junction -> $sharedAgents" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: agents Junction" -ForegroundColor Red
    }
} else {
    Write-Host "  agents dir already exists" -ForegroundColor Yellow
}

# Step 3: Create AGENTS.md hardlink
$agentsMd = Join-Path $catPawDir "AGENTS.md"
Write-Host "3. Create AGENTS.md hardlink" -ForegroundColor Yellow
if (Test-Path $agentsMd) {
    Remove-Item $agentsMd -Force
}
cmd /c "mklink /H `"$agentsMd`" `"$sharedAgentsMd`"" 2>$null | Out-Null
if (Test-Path $agentsMd) {
    Write-Host "  OK: AGENTS.md hardlink -> $sharedAgentsMd" -ForegroundColor Green
} else {
    Write-Host "  FAIL: AGENTS.md hardlink" -ForegroundColor Red
}

# Step 4: Verify
Write-Host "`n4. Verification" -ForegroundColor Yellow
$items = @(
    @{ Name = "skills"; Path = $skillsDir; Expected = "Junction" }
    @{ Name = "agents"; Path = $agentsDir; Expected = "Junction" }
    @{ Name = "AGENTS.md"; Path = $agentsMd; Expected = "HardLink" }
)
foreach ($item in $items) {
    if (Test-Path $item.Path) {
        $f = Get-Item $item.Path -Force
        $isJunction = ($f.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0
        $lt = $f.LinkType
        Write-Host "  $($item.Name): LinkType=$lt OK" -ForegroundColor Green
    } else {
        Write-Host "  $($item.Name): NOT FOUND" -ForegroundColor Red
    }
}

# Final check - read AGENTS.md through .catpawai
Write-Host "`n5. Content check" -ForegroundColor Yellow
$hash1 = (Get-FileHash $agentsMd -Algorithm MD5).Hash
$hash2 = (Get-FileHash $sharedAgentsMd -Algorithm MD5).Hash
Write-Host "  .catpawai AGENTS.md MD5: $hash1"
Write-Host "  .ai-shared AGENTS.md MD5: $hash2"
Write-Host "  Match: $($hash1 -eq $hash2)" -ForegroundColor $(if ($hash1 -eq $hash2) { "Green" } else { "Red" })

# Write-through test
$testContent = "catpawai-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
$testFile = Join-Path $skillsDir ".catpawai-junction-test"
Set-Content -Path $testFile -Value $testContent -Force
$readBack = Get-Content $testFile -Raw
if ($readBack.Trim() -eq $testContent) {
    Write-Host "  Write-through test: OK" -ForegroundColor Green
} else {
    Write-Host "  Write-through test: FAIL" -ForegroundColor Red
}
Remove-Item $testFile -Force -ErrorAction SilentlyContinue

Write-Host "`n=== Done ===" -ForegroundColor Cyan
Write-Host ".catpawai now uses Junctions + HardLink (same as other 5 tools)" -ForegroundColor Gray
