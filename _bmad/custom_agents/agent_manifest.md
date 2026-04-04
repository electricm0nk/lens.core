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

---

## Available Theme Packages

Theme files live in `_bmad/custom_agents/{theme}/`. Use `agent_selector.sh` to switch.

### 40k (Warhammer 40,000)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_malcador.md                 | Malcador the Sigillite  |
| analyst               | analyst_greyfax.md                      | Inquisitor Greyfax      |
| architect             | architect_perturabo.md                  | Perturabo               |
| dev                   | dev_magos.md                            | Magos Dominus           |
| pm                    | pm_creed.md                             | Ursarkar Creed          |
| qa                    | qa_artemis.md                           | Artemis                 |
| quick-flow-solo-dev   | quick-flow-solo-dev_eversor.md          | Eversor Assassin        |
| sm                    | sm_grimaldus.md                         | Reclusiarch Grimaldus   |
| tech-writer           | tech-writer_sindermann.md               | Sindermann              |
| ux-designer           | ux-designer_navigator.md               | Navigator               |
| brainstorming-coach   | brainstorming-coach_tigurius.md         | Tigurius                |
| creative-problem-solver | creative-problem-solver_cawl.md       | Belisarius Cawl         |
| design-thinking-coach | design-thinking-coach_eldrad.md         | Eldrad Ulthran          |
| innovation-strategist | innovation-strategist_rogue-trader.md   | Rogue Trader            |
| presentation-master   | presentation-master_solitaire.md        | Solitaire               |
| storyteller           | storyteller_shadowseer.md               | Shadowseer              |

---

### bmad (BMAD Defaults)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_bmad.md                     | BMad Master (default)   |
| analyst               | analyst_bmad.md                         | Business Analyst        |
| architect             | architect_bmad.md                       | Architect               |
| dev                   | dev_bmad.md                             | Developer Agent         |
| pm                    | pm_bmad.md                              | Product Manager         |
| qa                    | qa_bmad.md                              | QA Engineer             |
| quick-flow-solo-dev   | quick-flow-solo-dev_bmad.md             | Quick Flow Solo Dev     |
| sm                    | sm_bmad.md                              | Scrum Master            |
| tech-writer           | tech-writer_bmad.md                     | Technical Writer        |
| ux-designer           | ux-designer_bmad.md                     | UX Designer             |
| brainstorming-coach   | brainstorming-coach_bmad.md             | Brainstorming Coach     |
| creative-problem-solver | creative-problem-solver_bmad.md       | Creative Problem Solver |
| design-thinking-coach | design-thinking-coach_bmad.md           | Design Thinking Coach   |
| innovation-strategist | innovation-strategist_bmad.md           | Innovation Strategist   |
| presentation-master   | presentation-master_bmad.md             | Presentation Master     |
| storyteller           | storyteller_bmad.md                     | Storyteller             |

---

### dune (Dune Universe)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_leto-ii.md                  | Leto II, God Emperor    |
| analyst               | analyst_mohiam.md                       | Gaius Helen Mohiam      |
| architect             | architect_rhombur.md                    | Rhombur Vernius         |
| dev                   | dev_duncan-idaho.md                     | Duncan Idaho            |
| pm                    | pm_jessica.md                           | Lady Jessica            |
| qa                    | qa_alia.md                              | Alia Atreides           |
| quick-flow-solo-dev   | quick-flow-solo-dev_chani.md            | Chani                   |
| sm                    | sm_stilgar.md                           | Stilgar                 |
| tech-writer           | tech-writer_irulan.md                   | Princess Irulan         |
| ux-designer           | ux-designer_margot-fenring.md           | Margot Fenring          |
| brainstorming-coach   | brainstorming-coach_hawat.md            | Thufir Hawat            |
| creative-problem-solver | creative-problem-solver_paul.md       | Paul Atreides           |
| design-thinking-coach | design-thinking-coach_odrade.md         | Darwi Odrade            |
| innovation-strategist | innovation-strategist_fenring.md        | Hasimir Fenring         |
| presentation-master   | presentation-master_sheeana.md          | Sheeana Brugh           |
| storyteller           | storyteller_irulan.md                   | Princess Irulan         |

---

### expanse (The Expanse)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_fred-johnson.md             | Fred Johnson            |
| analyst               | analyst_prax.md                         | Praxidike Meng          |
| architect             | architect_naomi.md                      | Naomi Nagata            |
| dev                   | dev_amos.md                             | Amos Burton             |
| pm                    | pm_holden.md                            | James Holden            |
| qa                    | qa_bobbie.md                            | Bobbie Draper           |
| quick-flow-solo-dev   | quick-flow-solo-dev_drummer.md          | Camina Drummer          |
| sm                    | sm_alex.md                              | Alex Kamal              |
| tech-writer           | tech-writer_monica.md                   | Monica Stuart           |
| ux-designer           | ux-designer_anna.md                     | Anna Volovodov          |
| brainstorming-coach   | brainstorming-coach_miller.md           | Miller                  |
| creative-problem-solver | creative-problem-solver_clarissa.md   | Clarissa Mao            |
| design-thinking-coach | design-thinking-coach_elvi.md           | Elvi Okoye              |
| innovation-strategist | innovation-strategist_marco.md          | Marco Inaros            |
| presentation-master   | presentation-master_avasarala.md        | Chrisjen Avasarala      |
| storyteller           | storyteller_ashford.md                  | Klaes Ashford           |

---

### star_wars (Star Wars)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_yoda.md                     | Master Yoda             |
| analyst               | analyst_cassian.md                      | Cassian Andor           |
| architect             | architect_tarkin.md                     | Grand Moff Tarkin       |
| dev                   | dev_k2so.md                             | K-2SO                   |
| pm                    | pm_leia.md                              | Princess Leia           |
| qa                    | qa_dedra-meero.md                       | Dedra Meero             |
| quick-flow-solo-dev   | quick-flow-solo-dev_han-solo.md         | Han Solo                |
| sm                    | sm_dodonna.md                           | General Dodonna         |
| tech-writer           | tech-writer_c3po.md                     | C-3PO                   |
| ux-designer           | ux-designer_lando.md                    | Lando Calrissian        |
| brainstorming-coach   | brainstorming-coach_maz.md              | Maz Kanata              |
| creative-problem-solver | creative-problem-solver_bodhi.md      | Bodhi Rook              |
| design-thinking-coach | design-thinking-coach_chirrut.md        | Chirrut Îmwe            |
| innovation-strategist | innovation-strategist_aphra.md          | Doctor Aphra            |
| presentation-master   | presentation-master_palpatine.md        | Emperor Palpatine       |
| storyteller           | storyteller_lor-san-tekka.md            | Lor San Tekka           |

---

### tech_industry (Tech Industry Pioneers)

| Agent ID              | File                                    | Character               |
|-----------------------|-----------------------------------------|-------------------------|
| bmad-master           | bmad-master_ada-lovelace.md             | Ada Lovelace            |
| analyst               | analyst_mary-meeker.md                  | Mary Meeker             |
| architect             | architect_tim-berners-lee.md            | Tim Berners-Lee         |
| dev                   | dev_linus.md                            | Linus Torvalds          |
| pm                    | pm_tony-fadell.md                       | Tony Fadell             |
| qa                    | qa_james-bach.md                        | James Bach              |
| quick-flow-solo-dev   | quick-flow-solo-dev_wozniak.md          | Steve Wozniak (Woz)     |
| sm                    | sm_sutherland.md                        | Jeff Sutherland         |
| tech-writer           | tech-writer_knuth.md                    | Donald Knuth            |
| ux-designer           | ux-designer_don-norman.md               | Don Norman              |
| brainstorming-coach   | brainstorming-coach_osborn.md           | Alex Osborn             |
| creative-problem-solver | creative-problem-solver_bret-victor.md | Bret Victor            |
| design-thinking-coach | design-thinking-coach_tim-brown.md      | Tim Brown               |
| innovation-strategist | innovation-strategist_christensen.md    | Clayton Christensen     |
| presentation-master   | presentation-master_jobs.md             | Steve Jobs              |
| storyteller           | storyteller_alan-kay.md                 | Alan Kay                |
