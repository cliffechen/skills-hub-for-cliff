param([switch]$Force)

$ErrorActionPreference = "Stop"
$SkillName = "amazon-sorftime-mcp-with-serpapi-tavily"
$Source = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$CodexHome = if ($env:CODEX_HOME) { $env:CODEX_HOME } else { Join-Path $HOME ".codex" }
$SkillsHome = Join-Path $CodexHome "skills"
$Destination = Join-Path $SkillsHome $SkillName

New-Item -ItemType Directory -Path $SkillsHome -Force | Out-Null
$sourceFull = [System.IO.Path]::GetFullPath($Source)
$destinationFull = [System.IO.Path]::GetFullPath($Destination)

if ($sourceFull -ne $destinationFull) {
    if ((Test-Path $Destination) -and -not $Force) {
        throw "The target skill already exists: $Destination. Add -Force to update it."
    }
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Get-ChildItem -LiteralPath $Source -Force | Copy-Item -Destination $Destination -Recurse -Force
    Write-Host "Installed main skill: $Destination"
} else {
    Write-Host "Main skill is already in the Codex skills directory: $Destination"
}

Write-Host "Next: configure Sorftime and Tavily using README.md, then restart Codex."
