# Copilot Adapter: copilot-instructions.md Template

This is the template for the `.github/copilot-instructions.md` file that gets installed into control repos by the `setupRepo` prompt.

---

```markdown
<!-- LENS-WORK ADAPTER -->
# LENS Workbench — Copilot Instructions

## Module Reference

This control repo uses the LENS Workbench module from the release payload:

- **Module path:** `lens.core/_bmad/lens-work/`
- **Lifecycle contract:** `lens.core/_bmad/lens-work/lifecycle.yaml`
- **Module version:** See `lens.core/_bmad/lens-work/module.yaml`

## Agent

The `@lens` agent is defined at `.github/agents/lens.agent.md` and references
the module agent at `lens.core/_bmad/lens-work/agents/lens.agent.md`.

## Skills (by path reference)

| Skill | Path |
|-------|------|
| git-state | `lens.core/_bmad/lens-work/skills/git-state.md` |
| git-orchestration | `lens.core/_bmad/lens-work/skills/git-orchestration.md` |
| constitution | `lens.core/_bmad/lens-work/skills/constitution.md` |
| sensing | `lens.core/_bmad/lens-work/skills/sensing.md` |
| checklist | `lens.core/_bmad/lens-work/skills/checklist.md` |

## Important

- This adapter references module content by path — it NEVER duplicates it
- Do not copy skills, workflows, or lifecycle definitions into `.github/`
- Module updates propagate automatically through path references
<!-- /LENS-WORK ADAPTER -->
```

---

# Copilot Adapter: lens.agent.md Template

This is the template for the `.github/agents/lens.agent.md` file.

---

```markdown
---
description: "LENS Workbench — guided lifecycle routing with git-orchestrated discipline"
---

# @lens Agent

Thin adapter that activates the LENS Workbench agent from the release module.

## Module Agent Reference

The full agent definition lives at:
`lens.core/_bmad/lens-work/agents/lens.agent.yaml`

## Available Commands

See `lens.core/_bmad/lens-work/module-help.csv` for the complete command list.

## Skills (path references)

- [git-state](lens.core/_bmad/lens-work/skills/git-state.md)
- [git-orchestration](lens.core/_bmad/lens-work/skills/git-orchestration.md)
- [constitution](lens.core/_bmad/lens-work/skills/constitution.md)
- [sensing](lens.core/_bmad/lens-work/skills/sensing.md)
- [checklist](lens.core/_bmad/lens-work/skills/checklist.md)

## Lifecycle Contract

All lifecycle semantics are defined in:
`lens.core/_bmad/lens-work/lifecycle.yaml`

This agent does NOT hardcode any lifecycle rules — everything is derived from the contract.
```
