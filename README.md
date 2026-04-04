# lens.core

`lens.core` is the control repository for BMAD + LENS Workbench.  
It provides the lifecycle router, workflow definitions, agent instructions, and IDE adapters used to run disciplined planning and delivery workflows across repositories.

## What this repository contains

- **LENS Workbench module** in `_bmad/lens-work/` (v2 lifecycle routing + git orchestration)
- **BMAD modules** (`core`, `bmm`, `cis`, `tea`, `gds`, `bmb`)
- **IDE command/agent adapters** for:
  - GitHub Copilot (`.github/`)
  - Cursor (`.cursor/`)
  - Claude Code (`.claude/`)
  - Codex (`.codex/`)
- **Agent theme switching system** via:
  - `agent_selector.py`
  - `agent_selector.sh`
  - `_bmad/custom_agents/agent_manifest.md`

## Core concept

LENS Workbench uses a git-derived lifecycle model:

- Git branches + PR metadata + committed artifacts define state
- PRs are the lifecycle gates
- Planning phases are routed to specific agents
- Promotion happens audience-to-audience (`small → medium → large → base`)

Main lifecycle contract:  
`_bmad/lens-work/lifecycle.yaml`

## Repository layout

```text
lens.core/
├── _bmad/
│   ├── lens-work/          # LENS module (agent, lifecycle, skills, workflows, scripts)
│   ├── core/               # BMAD core module
│   ├── bmm/                # Business module agents/workflows
│   ├── cis/                # Creative Innovation Suite
│   ├── tea/                # Test Engineering Academy
│   ├── gds/                # Game Design Suite
│   └── custom_agents/      # Theme variants + active indirection layer
├── .github/                # Copilot adapter files
├── .cursor/                # Cursor command stubs
├── .claude/                # Claude command stubs
├── .codex/                 # Codex command stubs
├── agent_selector.py       # Cross-platform interactive theme switcher
├── agent_selector.sh       # Bash theme switcher
└── AGENTS.md / CLAUDE.md   # Runtime loading instructions for IDE agents
```

## Quick start

### 1) Install adapters (default: GitHub Copilot)

From repository root:

```bash
./_bmad/lens-work/scripts/install.sh
```

Windows PowerShell:

```powershell
./_bmad/lens-work/scripts/install.ps1
```

Useful options:

```bash
./_bmad/lens-work/scripts/install.sh --all-ides
./_bmad/lens-work/scripts/install.sh --update
```

### 2) Use LENS commands in your IDE

Primary lifecycle/utility commands:

- `/onboard`
- `/new-domain`, `/new-service`, `/new-feature`
- `/preplan`, `/businessplan`, `/techplan`, `/devproposal`, `/sprintplan`, `/dev`
- `/status`, `/next`, `/switch`, `/promote`, `/sense`, `/help`

Command manifest:
`_bmad/lens-work/module-help.csv`

## LENS phase flow

```text
preplan → businessplan → techplan → devproposal → sprintplan
```

Audience gates:

```text
small --/promote--> medium --/promote--> large --/promote--> base
```

## Agent themes and variants

This repo supports themed agent personas, including `40k`, `dune`, `expanse`, `star_wars`, and `tech_industry`.

- Active assignment source of truth:  
  `_bmad/custom_agents/agent_manifest.md`
- Runtime copies are placed in:  
  `_bmad/custom_agents/active/`

Switch themes interactively:

```bash
python ./agent_selector.py
# or
bash ./agent_selector.sh
```

## Scripts

LENS scripts (in `_bmad/lens-work/scripts/`) include:

- `install.sh` / `install.ps1` — adapter install/update
- `promote-branch.sh` / `promote-branch.ps1` — branch promotion + PR URL/API flow
- `store-github-pat.sh` / `store-github-pat.ps1` — secure PAT setup workflow

## Notes

- The top-level `.gitignore` intentionally treats `_bmad/custom_agents/active/` as tracked content with `skip-worktree` behavior controlled by the selector scripts.
- `lens.core` is primarily a workflow/control repo rather than an application code runtime.
