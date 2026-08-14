# Verify that junctions are working correctly
$tools = @(
    @{ Name = "claude";   Path = "C:\Users\20448\.claude" }
    @{ Name = "codex";    Path = "C:\Users\20448\.codex" }
    @{ Name = "cursor";   Path = "C:\Users\20448\.cursor" }
    @{ Name = "qoder";    Path = "C:\Users\20448\.qoder" }
    @{ Name = "workbuddy"; Path = "C:\Users\20448\.workbuddy" }
)

Write-Host "=== Junction Verification ===" -ForegroundColor Cyan

# Check that all tools point to the same physical location
Write-Host "`n1. Physical path resolution (should all be the same):" -ForegroundColor Yellow
foreach ($t in $tools) {
    $sp = Join-Path $t.Path "skills"
    $ap = Join-Path $t.Path "agents"
    
    # Get real path (resolve junction)
    $realSkills = if (Test-Path $sp) { (Get-Item $sp).Target } else { "NOT FOUND" }
    $realAgents = if (Test-Path $ap) { (Get-Item $ap).Target } else { "NOT FOUND" }
    
    Write-Host "  $($t.Name):"
    Write-Host "    skills -> $realSkills"
    Write-Host "    agents -> $realAgents"
}

# Read the same file through each tool's path to verify they see the same content
Write-Host "`n2. Content consistency (reading git-commit/SKILL.md through each tool):" -ForegroundColor Yellow
$testFile = "skills\git-commit\SKILL.md"
$hashes = @{}
foreach ($t in $tools) {
    $fullPath = Join-Path $t.Path $testFile
    if (Test-Path $fullPath) {
        $hash = (Get-FileHash $fullPath -Algorithm MD5).Hash
        $hashes[$t.Name] = $hash
        Write-Host "  $($t.Name): $hash"
    } else {
        Write-Host "  $($t.Name): FILE NOT FOUND" -ForegroundColor Red
    }
}

$allSame = ($hashes.Values | Sort-Object -Unique).Count -eq 1
if ($allSame) {
    Write-Host "  RESULT: ALL IDENTICAL" -ForegroundColor Green
} else {
    Write-Host "  RESULT: DIFFERENT!" -ForegroundColor Red
}

# List shared skills
Write-Host "`n3. Shared skills listing:" -ForegroundColor Yellow
$shared = "C:\Users\20448\.ai-shared\skills"
$skills = Get-ChildItem $shared -Directory | Select-Object -ExpandProperty Name | Sort-Object
Write-Host "  Total: $($skills.Count) skills"
foreach ($s in $skills) { Write-Host "    $s" }

# List shared agents
Write-Host "`n4. Shared agents listing:" -ForegroundColor Yellow
$sharedAgents = "C:\Users\20448\.ai-shared\agents"
$agents = Get-ChildItem $sharedAgents -File | Select-Object -ExpandProperty Name | Sort-Object
Write-Host "  Total: $($agents.Count) agents"
foreach ($a in $agents) { Write-Host "    $a" }

# Verify a write test - create a file in shared, read through each tool
Write-Host "`n5. Write-through test (create in shared, read from each tool):" -ForegroundColor Yellow
$testContent = "junction-test-$(Get-Date -Format 'yyyyMMddHHmmss')"
$testFile2 = "C:\Users\20448\.ai-shared\skills\.junction-test"
Set-Content -Path $testFile2 -Value $testContent -Force
foreach ($t in $tools) {
    $tp = Join-Path $t.Path "skills\.junction-test"
    if (Test-Path $tp) {
        $read = Get-Content $tp -Raw
        if ($read.Trim() -eq $testContent) {
            Write-Host "  $($t.Name): OK (content matches)" -ForegroundColor Green
        } else {
            Write-Host "  $($t.Name): CONTENT MISMATCH" -ForegroundColor Red
        }
    } else {
        Write-Host "  $($t.Name): FILE NOT FOUND" -ForegroundColor Red
    }
}
Remove-Item $testFile2 -Force -ErrorAction SilentlyContinue
Write-Host "  (test file cleaned up)"

Write-Host "`n=== Verification Complete ===" -ForegroundColor Cyan
