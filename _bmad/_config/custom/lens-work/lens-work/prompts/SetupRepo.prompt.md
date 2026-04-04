---
agent: agent
model: Claude Sonnet 4.6 (copilot)
description: "First-time repository setup — clones authority repos and triggers onboarding"
---

# SetupRepo — LENS Workbench Initial Setup

This prompt performs first-time setup of a control repo for lens-work.

## Steps

### 0. Verify Working Directory

Ensure the path is set to the root of the repository (the control repo you want to set up).

### 1. Clone lens.core

Clone the release module and checkout the appropriate branch:

```bash
git clone https://github.com/crisweber2600/lens.core lens.core
cd lens.core
git checkout release/4.0.0   # or alpha/beta for pre-release
cd ..
```

### 2. Sync .github from Release Repo

The `.github` folder is now part of `lens.core` (no longer a separate repo).

```powershell
# PowerShell
if (Test-Path ".github") { Remove-Item -Recurse -Force ".github" }
Copy-Item -Recurse "lens.core/.github" ".github"
```

```bash
# Bash
rm -rf .github
cp -r lens.core/.github .github
```

### 3. Clone Governance Repository (if configured)

If you have a governance repo configured:

- Read coordinates from `_bmad-output/lens-work/governance-setup.yaml` (if it exists)
- Clone `remote_url` into `local_path` and checkout `default_branch`
- If already cloned, run `git pull` to ensure it's up to date

### 4. Trigger Onboarding

Run the onboarding prompt to complete setup:

```
/lens-work.onboard
```

This will:
- Create workspace directories
- Detect your git provider
- Validate authentication
- Bootstrap TargetProjects from governance
- Run health check

## Notes

- The `.github` folder syncs from `lens.core/.github/` during preflight
- Future updates to agents/prompts will auto-sync when preflight detects changes
- See `_bmad/lens-work/workflows/includes/preflight.md` for sync logic
