#Requires -Version 5.1
<#
.SYNOPSIS
    Interactive agent variant switcher for lens.core.

.DESCRIPTION
    Reads agent_manifest.md, prompts the user to switch agents by theme (package)
    or individually, then updates all pointer files and the manifest in-place.

.PARAMETER WorkspaceRoot
    Path to the workspace root that contains lens.core as a submodule.
    Defaults to the parent directory of the script's location.

.EXAMPLE
    .\agent_selector.ps1
    .\agent_selector.ps1 -WorkspaceRoot "C:\Projects"
#>
[CmdletBinding()]
param(
    [string]$WorkspaceRoot = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
$ScriptDir        = Split-Path -Parent $MyInvocation.MyCommand.Path
$ManifestPath     = Join-Path $ScriptDir "_bmad\custom_agents\agent_manifest.md"
$CustomAgentsDir  = Join-Path $ScriptDir "_bmad\custom_agents"
$SubmoduleName    = Split-Path -Leaf $ScriptDir

if ([string]::IsNullOrEmpty($WorkspaceRoot)) {
    $WorkspaceRoot = Split-Path -Parent $ScriptDir
}

# ---------------------------------------------------------------------------
# Color helpers
# ---------------------------------------------------------------------------
function Write-Header([string]$Text) {
    Write-Host "`n$Text" -ForegroundColor Cyan
}
function Write-Ok([string]$Text) {
    Write-Host "  + $Text" -ForegroundColor Green
}
function Write-Warn([string]$Text) {
    Write-Host "  ! $Text" -ForegroundColor Yellow
}
function Write-Err([string]$Text) {
    Write-Host "  x $Text" -ForegroundColor Red
}

# ---------------------------------------------------------------------------
# Manifest parsing helpers
# ---------------------------------------------------------------------------

# Extract a key value from the YAML block for a given agent-id.
# Returns empty string if not found.
function Get-AgentField([string]$AgentId, [string]$Key) {
    $content       = Get-Content $ManifestPath -Raw
    $inBlock       = $false
    $foundAgent    = $false

    foreach ($line in ($content -split "`n")) {
        if ($line -match "^id: $([regex]::Escape($AgentId))`$") {
            $foundAgent = $true
            $inBlock    = $true
            continue
        }
        if ($inBlock) {
            # End of yaml block
            if ($line -match "^``````") { break }
            if ($line -match "^${Key}: (.+)$") {
                return $Matches[1].Trim()
            }
        }
    }
    return ""
}

# Return all agent IDs listed in the manifest (from YAML id: lines)
function Get-AgentIds() {
    $ids = @()
    foreach ($line in (Get-Content $ManifestPath)) {
        if ($line -match "^id: (.+)$") {
            $ids += $Matches[1].Trim()
        }
    }
    return $ids
}

# Return theme names: subdirectory names under custom_agents that contain .md files
function Get-Themes() {
    $themes = @()
    foreach ($d in (Get-ChildItem -Path $CustomAgentsDir -Directory)) {
        $mdFiles = Get-ChildItem -Path $d.FullName -Filter "*.md" -ErrorAction SilentlyContinue
        if ($mdFiles.Count -gt 0) {
            $themes += $d.Name
        }
    }
    return $themes
}

# Given a theme name and agent-id, return the variant filename (basename) or empty
function Find-VariantForAgent([string]$ThemeName, [string]$AgentId) {
    $themeDir = Join-Path $CustomAgentsDir $ThemeName
    $pattern  = "${AgentId}_*.md"
    $match    = Get-ChildItem -Path $themeDir -Filter $pattern -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($match) { return $match.Name }
    return ""
}

# Parse a theme's agents: returns array of [pscustomobject] with AgentId, Variant, Character
function Get-AgentsInTheme([string]$ThemeName) {
    $results  = @()
    $themeDir = Join-Path $CustomAgentsDir $ThemeName

    foreach ($id in (Get-AgentIds)) {
        $variant = Find-VariantForAgent $ThemeName $id
        if ([string]::IsNullOrEmpty($variant)) { continue }

        # Pull character label from Available Variants table in manifest
        # Use 'custom_agents/' anchor to avoid matching the Quick Reference table row
        $escapedAgent   = [regex]::Escape($id)
        $variantAnchor  = "| custom_agents/${ThemeName}/${variant}"
        $character = ""
        foreach ($line in (Get-Content $ManifestPath)) {
            if ($line.Contains($variantAnchor) -and $line -match "^\|\s*${escapedAgent}\s*\|") {
                $cols      = $line -split "\|"
                $character = $cols[3].Trim()
                break
            }
        }
        if ([string]::IsNullOrEmpty($character)) { $character = $variant -replace "\.md$","" }

        $results += [pscustomobject]@{
            AgentId   = $id
            Variant   = $variant
            Character = $character
        }
    }
    return $results
}

# ---------------------------------------------------------------------------
# Apply a switch: update all pointer files + manifest
#   $AgentId    — e.g. "architect"
#   $NewFile    — e.g. "_bmad/custom_agents/40k/architect_perturabo.md"
# ---------------------------------------------------------------------------
function Apply-Switch([string]$AgentId, [string]$NewFile) {
    $oldFile = Get-AgentField $AgentId "active_file"

    if ($oldFile -eq $NewFile) {
        Write-Warn "${AgentId}: already set to ${NewFile} — skipping"
        return
    }

    $oldBasename = Split-Path -Leaf $oldFile
    $newBasename = Split-Path -Leaf $NewFile

    Write-Host "  $AgentId`: $oldFile -> $NewFile" -ForegroundColor White

    # ---- Parse pointer_files for this agent and update each file ----
    $content    = Get-Content $ManifestPath -Raw
    $lines      = $content -split "`n"
    $inAgent    = $false
    $inPointer  = $false
    $ptrPath    = ""
    $ptrPrefix  = ""

    # Locate the ### {AgentId} header, then scan inside the yaml block
    $insideBlock = $false

    foreach ($line in $lines) {
        # Detect agent section header
        if ($line -match "^### $([regex]::Escape($AgentId))`$") {
            $inAgent     = $true
            $insideBlock = $false
            $inPointer   = $false
            continue
        }
        if (-not $inAgent) { continue }

        # Detect yaml fence start
        if ($line -match "^``````yaml") { $insideBlock = $true; continue }
        # Detect yaml fence end — stop processing this agent
        if ($line -match "^``````" -and $insideBlock) { break }

        if (-not $insideBlock) { continue }

        if ($line -match "^pointer_files:") {
            $inPointer = $true
            continue
        }

        if ($inPointer) {
            if ($line -match "^\s+-\s+path:\s+(.+)$") {
                $ptrPath   = $Matches[1].Trim()
                $ptrPrefix = ""
            }
            elseif ($line -match "^\s+prefix:\s+(.+)$") {
                $ptrPrefix = $Matches[1].Trim().Trim('"').Trim("'")

                if (-not [string]::IsNullOrEmpty($ptrPath) -and -not [string]::IsNullOrEmpty($ptrPrefix)) {
                    # Resolve absolute path (pointer paths are relative to workspace root)
                    $absPath = Join-Path $WorkspaceRoot ($ptrPath -replace "/", [IO.Path]::DirectorySeparatorChar)

                    if (-not (Test-Path $absPath)) {
                        Write-Warn "pointer file not found, skipping: $ptrPath"
                        $ptrPath = ""; $ptrPrefix = ""
                        continue
                    }

                    $oldStr = "${ptrPrefix}${oldBasename}"
                    $newStr = "${ptrPrefix}${newBasename}"

                    $fileContent = Get-Content $absPath -Raw
                    if ($fileContent -like "*${oldStr}*") {
                        $updated = $fileContent.Replace($oldStr, $newStr)
                        Set-Content -Path $absPath -Value $updated -NoNewline
                        Write-Ok "updated $ptrPath"
                    } else {
                        Write-Warn "pattern '$oldStr' not found in $ptrPath"
                    }

                    $ptrPath = ""; $ptrPrefix = ""
                }
            }
            elseif ($line -match "^\s+note:" -or $line -match "^\s+#") {
                # skip
            }
        }
    }

    # ---- Update manifest: active_file + Quick Reference table + variants table ----
    $manifest = Get-Content $ManifestPath -Raw

    # Update active_file in YAML block
    $manifest = [regex]::Replace(
        $manifest,
        "(?s)(id: $([regex]::Escape($AgentId)).*?active_file: )$([regex]::Escape($oldFile))",
        "`${1}${NewFile}",
        [System.Text.RegularExpressions.RegexOptions]::Singleline
    )

    # Update Quick Reference table row
    $manifest = [regex]::Replace(
        $manifest,
        "(\|\s*$([regex]::Escape($AgentId))\s*\|[^|\n]*\|)\s*$([regex]::Escape($oldFile))\s*(\|)",
        "`${1} ${NewFile} `${2}"
    )

    # Update Available Variants table: old variant → available
    $oldBaseEsc = [regex]::Escape($oldBasename)
    $manifest = [regex]::Replace(
        $manifest,
        "(\|\s*[^|]*\|\s*custom_agents/[^/]+/$oldBaseEsc\s*\|[^|\n]*\|)\s*\w+\s*(\|)",
        "`${1} available `${2}"
    )

    # New variant → active
    $newBaseEsc = [regex]::Escape($newBasename)
    $manifest = [regex]::Replace(
        $manifest,
        "(\|\s*[^|]*\|\s*custom_agents/[^/]+/$newBaseEsc\s*\|[^|\n]*\|)\s*\w+\s*(\|)",
        "`${1} active `${2}"
    )

    Set-Content -Path $ManifestPath -Value $manifest -NoNewline
    Write-Ok "manifest updated for ${AgentId}"
}

# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

# Display a numbered menu, return 0-based index of chosen item
function Show-Menu([string]$Prompt, [string[]]$Items) {
    for ($i = 0; $i -lt $Items.Count; $i++) {
        Write-Host ("  {0,2}) {1}" -f ($i + 1), $Items[$i])
    }
    Write-Host ""

    while ($true) {
        $raw = Read-Host "${Prompt}"
        $n   = 0
        if ([int]::TryParse($raw, [ref]$n) -and $n -ge 1 -and $n -le $Items.Count) {
            return ($n - 1)
        }
        Write-Err "Invalid choice — enter a number between 1 and $($Items.Count)"
    }
}

# Yes/no confirm — returns $true for yes
function Confirm-Action([string]$Prompt = "Continue?") {
    while ($true) {
        $ans = Read-Host "${Prompt} [y/n]"
        switch ($ans.ToLower()) {
            "y" { return $true  }
            "n" { return $false }
            default { Write-Host "  Enter y or n" }
        }
    }
}

# ---------------------------------------------------------------------------
# MODE 1: Apply entire theme as a package
# ---------------------------------------------------------------------------
function Invoke-ApplyTheme([string]$ThemeName) {
    Write-Header "Applying theme package: $ThemeName"
    Write-Host ""

    $agentsInTheme = Get-AgentsInTheme $ThemeName
    $changes       = @()

    foreach ($entry in $agentsInTheme) {
        $newFile       = "_bmad/custom_agents/${ThemeName}/$($entry.Variant)"
        $currentActive = Get-AgentField $entry.AgentId "active_file"
        if ($currentActive -ne $newFile) {
            $changes += $entry
        }
    }

    if ($changes.Count -eq 0) {
        Write-Host "  All agents are already using the '$ThemeName' theme."
        return
    }

    Write-Host "  The following agents will be switched to the '$ThemeName' theme:"
    foreach ($entry in $changes) {
        $cur    = Get-AgentField $entry.AgentId "active_file"
        Write-Host "    $($entry.AgentId): $(Split-Path -Leaf $cur) -> $($entry.Variant)"
    }
    Write-Host ""

    if (-not (Confirm-Action "Apply these changes?")) {
        Write-Host "  Aborted."
        return
    }

    Write-Host ""
    foreach ($entry in $changes) {
        $newFile = "_bmad/custom_agents/${ThemeName}/$($entry.Variant)"
        Apply-Switch $entry.AgentId $newFile
        Write-Host ""
    }

    Write-Header "Theme '$ThemeName' applied successfully."
}

# ---------------------------------------------------------------------------
# MODE 2: Switch a single agent
# ---------------------------------------------------------------------------
function Invoke-SwitchIndividual() {
    Write-Header "Select an agent to switch:"
    Write-Host ""

    $agentIds    = Get-AgentIds
    $displayItems = @()
    foreach ($id in $agentIds) {
        $active       = Get-AgentField $id "active_file"
        $displayItems += "${id}  (currently: $(Split-Path -Leaf $active))"
    }

    $idx          = Show-Menu "Choose agent" $displayItems
    $chosenAgent  = $agentIds[$idx]

    # Build variant list
    Write-Host ""
    Write-Header "Select a variant for '$chosenAgent':"
    Write-Host ""

    $variantFiles  = @()
    $variantLabels = @()

    # Default first
    $defaultFile = Get-AgentField $chosenAgent "default_file"
    $variantFiles  += $defaultFile
    $variantLabels += "Default  ($defaultFile)"

    # Theme variants
    foreach ($theme in (Get-Themes)) {
        $variant = Find-VariantForAgent $theme $chosenAgent
        if ([string]::IsNullOrEmpty($variant)) { continue }

        $character   = ""
        $variantAnchor = "| custom_agents/${theme}/${variant}"
        $escapedAgent  = [regex]::Escape($chosenAgent)
        foreach ($line in (Get-Content $ManifestPath)) {
            if ($line.Contains($variantAnchor) -and $line -match "^\|\s*${escapedAgent}\s*\|") {
                $cols      = $line -split "\|"
                $character = $cols[3].Trim()
                break
            }
        }
        if ([string]::IsNullOrEmpty($character)) { $character = $variant -replace "\.md$","" }

        $variantFiles  += "_bmad/custom_agents/${theme}/${variant}"
        $variantLabels += "[$theme] $character  ($variant)"
    }

    # Annotate current choice
    $currentActive  = Get-AgentField $chosenAgent "active_file"
    $labeledItems   = @()
    for ($i = 0; $i -lt $variantLabels.Count; $i++) {
        if ($variantFiles[$i] -eq $currentActive) {
            $labeledItems += "$($variantLabels[$i])  <- current"
        } else {
            $labeledItems += $variantLabels[$i]
        }
    }

    $idx2    = Show-Menu "Choose variant" $labeledItems
    $newFile = $variantFiles[$idx2]

    if ($newFile -eq $currentActive) {
        Write-Host "  Already active — nothing to do."
        return
    }

    Write-Host ""
    if (-not (Confirm-Action "Switch '$chosenAgent' to '$(Split-Path -Leaf $newFile)'?")) {
        Write-Host "  Aborted."
        return
    }

    Write-Host ""
    Apply-Switch $chosenAgent $newFile
    Write-Host ""
    Write-Header "Done."
}

# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
function Invoke-Main() {
    Write-Host ""
    Write-Header "Agent Selector -- lens.core"
    Write-Host ""
    Write-Host "  Workspace root : $WorkspaceRoot"
    Write-Host "  Manifest       : $ManifestPath"
    Write-Host "  Submodule name : $SubmoduleName"
    Write-Host ""

    if (-not (Test-Path $ManifestPath)) {
        Write-Err "Manifest not found: $ManifestPath"
        exit 1
    }

    Write-Header "How would you like to switch agents?"
    Write-Host ""
    Write-Host "  1) Apply a theme package  (switch all agents to a theme at once)"
    Write-Host "  2) Switch individual agents"
    Write-Host "  3) Show current agent status"
    Write-Host "  4) Exit"
    Write-Host ""

    while ($true) {
        $choice = Read-Host "Choose [1-4]"
        switch ($choice) {
            "1" {
                Write-Host ""
                Write-Header "Available themes:"
                Write-Host ""

                $themes = Get-Themes
                if ($themes.Count -eq 0) {
                    Write-Warn "No themes found in $CustomAgentsDir"
                    break
                }

                $themeItems = @()
                foreach ($t in $themes) {
                    $count      = (Get-AgentsInTheme $t).Count
                    $themeItems += "${t}  ($count agents)"
                }

                $idx = Show-Menu "Choose theme" $themeItems
                Invoke-ApplyTheme $themes[$idx]
                return
            }
            "2" {
                $more = "y"
                while ($more.ToLower() -eq "y") {
                    Invoke-SwitchIndividual
                    Write-Host ""
                    $more = Read-Host "Switch another agent? [y/n]"
                }
                return
            }
            "3" {
                Write-Host ""
                Write-Header "Current agent assignments:"
                Write-Host ""
                Write-Host ("  {0,-30} {1}" -f "AGENT", "ACTIVE FILE")
                Write-Host ("  {0,-30} {1}" -f "-----", "-----------")
                foreach ($id in (Get-AgentIds)) {
                    $active = Get-AgentField $id "active_file"
                    Write-Host ("  {0,-30} {1}" -f $id, $active)
                }
                Write-Host ""
                Invoke-Main
                return
            }
            "4" {
                Write-Host "Exiting."
                exit 0
            }
            default {
                Write-Err "Enter 1, 2, 3, or 4"
            }
        }
    }
}

Invoke-Main
