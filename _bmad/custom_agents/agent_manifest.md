# Custom Agent Manifest

This file tracks which agent variant is currently active for each agent.
It is consumed by `agent_selector.sh` and `agent_selector_update_manifest.py`.

The `active/` directory (gitignored) is the runtime indirection layer —
all committed IDE entrypoints load from `_bmad/custom_agents/active/{id}.md`.

---

## Script Contract

The agent selector script:
1. Reads `active_theme` and `active_variant` for each agent
2. On switch: copies the chosen file into `_bmad/custom_agents/active/{id}.md`
3. Updates `active_theme` and `active_variant` in this manifest
4. Never touches any other committed file

`active_theme: default` means the agent loads from its canonical module path (no custom theme).
The `init` command populates `active/` for all agents from current manifest state.

Paths are relative to `lens.core/`, i.e. the directory containing this file's `_bmad/` parent.

---

## Active Agents — Quick Reference

| Agent ID              | Module     | Active Theme | Active Variant                    |
|-----------------------|------------|--------------|-----------------------------------|
| bmad-master           | core       | 40k | bmad-master_malcador.md |
| analyst               | bmm        | 40k | analyst_greyfax.md |
| architect             | bmm        | 40k | architect_perturabo.md |
| dev                   | bmm        | 40k | dev_magos.md |
| pm                    | bmm        | 40k | pm_creed.md |
| qa                    | bmm        | 40k | qa_artemis.md |
| quick-flow-solo-dev   | bmm        | 40k | quick-flow-solo-dev_eversor.md |
| sm                    | bmm        | 40k | sm_grimaldus.md |
| tech-writer           | bmm        | 40k | tech-writer_sindermann.md |
| ux-designer           | bmm        | 40k | ux-designer_navigator.md |
| brainstorming-coach   | cis        | 40k | brainstorming-coach_tigurius.md |
| creative-problem-solver | cis      | 40k | creative-problem-solver_cawl.md |
| design-thinking-coach | cis        | 40k | design-thinking-coach_eldrad.md |
| innovation-strategist | cis        | 40k | innovation-strategist_rogue-trader.md |
| presentation-master   | cis        | 40k | presentation-master_solitaire.md |
| storyteller           | cis        | 40k | storyteller_shadowseer.md |
| lens                  | lens-work  | n/a          | lens.agent.md                     |

---

## Agent Catalog

Each agent block defines its identity and source locations.
`default_file` is the module-canonical path used when `active_theme: default`.
Theme variants live in `_bmad/custom_agents/{theme}/{agent-id}_{character}.md`.

---

### bmad-master

```yaml
id: bmad-master
module: core
default_file: _bmad/core/agents/bmad-master.md
active_theme: 40k
active_variant: bmad-master_malcador.md
```

---

### analyst

```yaml
id: analyst
module: bmm
default_file: _bmad/bmm/agents/analyst.md
active_theme: 40k
active_variant: analyst_greyfax.md
```

---

### architect

```yaml
id: architect
module: bmm
default_file: _bmad/bmm/agents/architect.md
active_theme: 40k
active_variant: architect_perturabo.md
```

---

### dev

```yaml
id: dev
module: bmm
default_file: _bmad/bmm/agents/dev.md
active_theme: 40k
active_variant: dev_magos.md
```

---

### pm

```yaml
id: pm
module: bmm
default_file: _bmad/bmm/agents/pm.md
active_theme: 40k
active_variant: pm_creed.md
```

---

### qa

```yaml
id: qa
module: bmm
default_file: _bmad/bmm/agents/qa.md
active_theme: 40k
active_variant: qa_artemis.md
```

---

### quick-flow-solo-dev

```yaml
id: quick-flow-solo-dev
module: bmm
default_file: _bmad/bmm/agents/quick-flow-solo-dev.md
active_theme: 40k
active_variant: quick-flow-solo-dev_eversor.md
```

---

### sm

```yaml
id: sm
module: bmm
default_file: _bmad/bmm/agents/sm.md
active_theme: 40k
active_variant: sm_grimaldus.md
```

---

### tech-writer

```yaml
id: tech-writer
module: bmm
default_file: _bmad/bmm/agents/tech-writer/tech-writer.md
active_theme: 40k
active_variant: tech-writer_sindermann.md
```

---

### ux-designer

```yaml
id: ux-designer
module: bmm
default_file: _bmad/bmm/agents/ux-designer.md
active_theme: 40k
active_variant: ux-designer_navigator.md
```

---

### brainstorming-coach

```yaml
id: brainstorming-coach
module: cis
default_file: _bmad/cis/agents/brainstorming-coach.md
active_theme: 40k
active_variant: brainstorming-coach_tigurius.md
```

---

### creative-problem-solver

```yaml
id: creative-problem-solver
module: cis
default_file: _bmad/cis/agents/creative-problem-solver.md
active_theme: 40k
active_variant: creative-problem-solver_cawl.md
```

---

### design-thinking-coach

```yaml
id: design-thinking-coach
module: cis
default_file: _bmad/cis/agents/design-thinking-coach.md
active_theme: 40k
active_variant: design-thinking-coach_eldrad.md
```

---

### innovation-strategist

```yaml
id: innovation-strategist
module: cis
default_file: _bmad/cis/agents/innovation-strategist.md
active_theme: 40k
active_variant: innovation-strategist_rogue-trader.md
```

---

### presentation-master

```yaml
id: presentation-master
module: cis
default_file: _bmad/cis/agents/presentation-master.md
active_theme: 40k
active_variant: presentation-master_solitaire.md
```

---

### storyteller

```yaml
id: storyteller
module: cis
default_file: _bmad/cis/agents/storyteller/storyteller.md
active_theme: 40k
active_variant: storyteller_shadowseer.md
```

---

### lens

```yaml
id: lens
module: lens-work
# The lens agent is not theme-able — it loads directly from the module.
# active/ indirection does not apply to this agent.
default_file: _bmad/lens-work/agents/lens.agent.md
active_theme: "n/a"
active_variant: lens.agent.md
```
