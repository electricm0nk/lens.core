# Custom Agent Manifest

This file is the source of truth for which agent variant files are currently active, and defines
every pointer location that must be updated when switching an agent. It is consumed by the agent
switch script located alongside this file.

---

## Script Contract

The switch script reads each agent's YAML block and performs the following:

1. Reads `active_file` (the filename currently in use)
2. Accepts a new variant filename as input
3. For each entry in `pointer_files`, runs a string replacement:
   `{prefix}{old_basename}` → `{prefix}{new_basename}` in `{path}`
4. Updates `active_file` in this manifest to reflect the new active file

Paths in `pointer_files` are relative to the **workspace root** (`/home/todd/Projects`).

The `prefix` field is the exact path prefix as it appears in each pointer file — note that
`agent-manifest.csv` uses `_bmad/` while `default-party.csv` omits the leading underscore.

---

## Active Agents — Quick Reference

| Agent ID              | Module     | Active File                                           |
|-----------------------|------------|-------------------------------------------------------|
| bmad-master           | core       | _bmad/core/agents/bmad-master.md                      |
| analyst               | bmm        | _bmad/bmm/agents/analyst.md                           |
| architect             | bmm        | _bmad/custom_agents/40k/architect_perturabo.md               |
| dev                   | bmm        | _bmad/bmm/agents/dev.md                               |
| pm                    | bmm        | _bmad/bmm/agents/pm.md                                |
| qa                    | bmm        | _bmad/bmm/agents/qa.md                                |
| quick-flow-solo-dev   | bmm        | _bmad/bmm/agents/quick-flow-solo-dev.md               |
| sm                    | bmm        | _bmad/bmm/agents/sm.md                                |
| tech-writer           | bmm        | _bmad/bmm/agents/tech-writer/tech-writer.md           |
| ux-designer           | bmm        | _bmad/bmm/agents/ux-designer.md                       |
| brainstorming-coach   | cis        | _bmad/cis/agents/brainstorming-coach.md               |
| creative-problem-solver | cis      | _bmad/cis/agents/creative-problem-solver.md           |
| design-thinking-coach | cis        | _bmad/cis/agents/design-thinking-coach.md             |
| innovation-strategist | cis        | _bmad/cis/agents/innovation-strategist.md             |
| presentation-master   | cis        | _bmad/cis/agents/presentation-master.md               |
| storyteller           | cis        | _bmad/cis/agents/storyteller/storyteller.md           |
| lens                  | lens-work  | _bmad/lens-work/agents/lens.agent.md                  |

---

## Agent Pointer Catalog

Each agent block below is a parseable YAML definition. The `pointer_files` list is exhaustive —
every location in the repository that contains a reference to this agent's file path.

---

### architect

```yaml
id: architect
module: bmm
default_file: _bmad/bmm/agents/architect.md
active_file: _bmad/custom_agents/40k/architect_perturabo.md
pointer_files:
  # IDE / AI activation entrypoints
  - path: lens.core/.github/agents/bmad-agent-bmm-architect.agent.md
    prefix: "{project-root}/_bmad/custom_agents/40k/"
  - path: .github/agents/bmad-agent-bmm-architect.agent.md
    prefix: "{project-root}/_bmad/custom_agents/40k/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-architect.md
    prefix: "{project-root}/_bmad/custom_agents/40k/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-architect.md
    prefix: "{project-root}/_bmad/custom_agents/40k/"
  # Shared agent registry CSVs (updated for ALL agent switches)
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/custom_agents/40k/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/custom_agents/40k/"
  # Workflow router references
  - path: lens.core/_bmad/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/custom_agents/40k/"
  - path: lens.core/_bmad/lens-work/workflows/router/techplan/workflow.md
    prefix: "_bmad/custom_agents/40k/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/custom_agents/40k/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/techplan/workflow.md
    prefix: "_bmad/custom_agents/40k/"
```

---

### pm

```yaml
id: pm
module: bmm
default_file: _bmad/bmm/agents/pm.md
active_file: _bmad/bmm/agents/pm.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-pm.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-pm.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-pm.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-pm.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/devproposal/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/devproposal/workflow.md
    prefix: "_bmad/bmm/agents/"
```

---

### ux-designer

```yaml
id: ux-designer
module: bmm
default_file: _bmad/bmm/agents/ux-designer.md
active_file: _bmad/bmm/agents/ux-designer.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-ux-designer.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-ux-designer.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-ux-designer.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-ux-designer.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/businessplan/workflow.md
    prefix: "_bmad/bmm/agents/"
```

---

### sm

```yaml
id: sm
module: bmm
default_file: _bmad/bmm/agents/sm.md
active_file: _bmad/bmm/agents/sm.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-sm.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-sm.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-sm.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-sm.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/sprintplan/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/dev/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/sprintplan/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/dev/workflow.md
    prefix: "_bmad/bmm/agents/"
```

---

### qa

```yaml
id: qa
module: bmm
default_file: _bmad/bmm/agents/qa.md
active_file: _bmad/bmm/agents/qa.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-qa.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-qa.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-qa.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-qa.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
  - path: lens.core/_bmad/lens-work/workflows/router/dev/workflow.md
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/custom/lens-work/lens-work/workflows/router/dev/workflow.md
    prefix: "_bmad/bmm/agents/"
```

---

### analyst

```yaml
id: analyst
module: bmm
default_file: _bmad/bmm/agents/analyst.md
active_file: _bmad/bmm/agents/analyst.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-analyst.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-analyst.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-analyst.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-analyst.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
```

---

### dev

```yaml
id: dev
module: bmm
default_file: _bmad/bmm/agents/dev.md
active_file: _bmad/bmm/agents/dev.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-dev.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-dev.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-dev.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-dev.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
```

---

### quick-flow-solo-dev

```yaml
id: quick-flow-solo-dev
module: bmm
default_file: _bmad/bmm/agents/quick-flow-solo-dev.md
active_file: _bmad/bmm/agents/quick-flow-solo-dev.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-quick-flow-solo-dev.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: .github/agents/bmad-agent-bmm-quick-flow-solo-dev.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-quick-flow-solo-dev.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-quick-flow-solo-dev.md
    prefix: "{project-root}/_bmad/bmm/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/"
```

---

### tech-writer

```yaml
id: tech-writer
module: bmm
default_file: _bmad/bmm/agents/tech-writer/tech-writer.md
active_file: _bmad/bmm/agents/tech-writer/tech-writer.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmm-tech-writer.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/tech-writer/"
  - path: .github/agents/bmad-agent-bmm-tech-writer.agent.md
    prefix: "{project-root}/_bmad/bmm/agents/tech-writer/"
  - path: lens.core/.cursor/commands/bmad-agent-bmm-tech-writer.md
    prefix: "{project-root}/_bmad/bmm/agents/tech-writer/"
  - path: lens.core/.claude/commands/bmad-agent-bmm-tech-writer.md
    prefix: "{project-root}/_bmad/bmm/agents/tech-writer/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/bmm/agents/tech-writer/"
  - path: lens.core/_bmad/bmm/teams/default-party.csv
    prefix: "bmad/bmm/agents/tech-writer/"
```

---

### bmad-master

```yaml
id: bmad-master
module: core
default_file: _bmad/core/agents/bmad-master.md
active_file: _bmad/core/agents/bmad-master.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-bmad-master.agent.md
    prefix: "{project-root}/_bmad/core/agents/"
  - path: .github/agents/bmad-agent-bmad-master.agent.md
    prefix: "{project-root}/_bmad/core/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-bmad-master.md
    prefix: "{project-root}/_bmad/core/agents/"
  - path: lens.core/.claude/commands/bmad-agent-bmad-master.md
    prefix: "{project-root}/_bmad/core/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/core/agents/"
```

---

### brainstorming-coach

```yaml
id: brainstorming-coach
module: cis
default_file: _bmad/cis/agents/brainstorming-coach.md
active_file: _bmad/cis/agents/brainstorming-coach.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-brainstorming-coach.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: .github/agents/bmad-agent-cis-brainstorming-coach.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-brainstorming-coach.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.claude/commands/bmad-agent-cis-brainstorming-coach.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
```

---

### creative-problem-solver

```yaml
id: creative-problem-solver
module: cis
default_file: _bmad/cis/agents/creative-problem-solver.md
active_file: _bmad/cis/agents/creative-problem-solver.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-creative-problem-solver.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: .github/agents/bmad-agent-cis-creative-problem-solver.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-creative-problem-solver.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.claude/commands/bmad-agent-cis-creative-problem-solver.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
```

---

### design-thinking-coach

```yaml
id: design-thinking-coach
module: cis
default_file: _bmad/cis/agents/design-thinking-coach.md
active_file: _bmad/cis/agents/design-thinking-coach.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-design-thinking-coach.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: .github/agents/bmad-agent-cis-design-thinking-coach.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-design-thinking-coach.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.claude/commands/bmad-agent-cis-design-thinking-coach.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
```

---

### innovation-strategist

```yaml
id: innovation-strategist
module: cis
default_file: _bmad/cis/agents/innovation-strategist.md
active_file: _bmad/cis/agents/innovation-strategist.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-innovation-strategist.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: .github/agents/bmad-agent-cis-innovation-strategist.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-innovation-strategist.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.claude/commands/bmad-agent-cis-innovation-strategist.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
```

---

### presentation-master

```yaml
id: presentation-master
module: cis
default_file: _bmad/cis/agents/presentation-master.md
active_file: _bmad/cis/agents/presentation-master.md
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-presentation-master.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: .github/agents/bmad-agent-cis-presentation-master.agent.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-presentation-master.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/.claude/commands/bmad-agent-cis-presentation-master.md
    prefix: "{project-root}/_bmad/cis/agents/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
```

---

### storyteller

```yaml
id: storyteller
module: cis
default_file: _bmad/cis/agents/storyteller/storyteller.md
active_file: _bmad/cis/agents/storyteller/storyteller.md
# NOTE: cis/teams/default-party.csv has an inconsistency — it references
# "bmad/cis/agents/storyteller.md" (no subdirectory) while all activation files
# use "_bmad/cis/agents/storyteller/storyteller.md". The CSV uses a flat path;
# the script must handle this entry with a different prefix than the others.
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-cis-storyteller.agent.md
    prefix: "{project-root}/_bmad/cis/agents/storyteller/"
  - path: .github/agents/bmad-agent-cis-storyteller.agent.md
    prefix: "{project-root}/_bmad/cis/agents/storyteller/"
  - path: lens.core/.cursor/commands/bmad-agent-cis-storyteller.md
    prefix: "{project-root}/_bmad/cis/agents/storyteller/"
  - path: lens.core/.claude/commands/bmad-agent-cis-storyteller.md
    prefix: "{project-root}/_bmad/cis/agents/storyteller/"
  - path: lens.core/_bmad/_config/agent-manifest.csv
    prefix: "_bmad/cis/agents/storyteller/"
  - path: lens.core/_bmad/cis/teams/default-party.csv
    prefix: "bmad/cis/agents/"
    note: "CSV uses flat path 'storyteller.md' not 'storyteller/storyteller.md' — verify before switching"
```

---

### lens

```yaml
id: lens
module: lens-work
# The lens agent loads multiple files on activation — not a single agent file.
# Switching variants requires updating all four load targets below.
default_file: _bmad/lens-work/agents/lens.agent.md
active_file: _bmad/lens-work/agents/lens.agent.md
activation_files:
  - lens.core/_bmad/lens-work/module.yaml
  - lens.core/_bmad/lens-work/agents/lens.agent.md
  - lens.core/_bmad/lens-work/lifecycle.yaml
  - lens.core/_bmad/lens-work/module-help.csv
pointer_files:
  - path: lens.core/.github/agents/bmad-agent-lens-work-lens.agent.md
    prefix: "lens.core/_bmad/lens-work/agents/"
  - path: .github/agents/bmad-agent-lens-work-lens.agent.md
    prefix: "lens.core/_bmad/lens-work/agents/"
  - path: lens.core/.cursor/commands/bmad-agent-lens-work-lens.md
    prefix: "lens.core/_bmad/lens-work/agents/"
  - path: lens.core/.claude/commands/bmad-agent-lens-work-lens.md
    prefix: "lens.core/_bmad/lens-work/agents/"
```

---

## Available Variants

### Theme: 40k (Warhammer 40,000)

| Agent ID  | Variant File                                  | Status  |
|-----------|-----------------------------------------------|---------|
| architect | custom_agents/40k/architect_perturabo.md      | active  |

> Additional 40k variants can be added alongside this file and registered in the table above.
> Set `status` to `available` for inactive variants, `active` for the one currently in use.
