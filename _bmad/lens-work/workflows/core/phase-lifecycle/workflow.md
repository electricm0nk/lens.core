# Phase Lifecycle Workflow

**Phase:** Core
**Purpose:** Manage phase completion, automatic PR creation, and branch cleanup.
**Trigger:** Automatically invoked at the end of each phase routing workflow.

## Preflight Gate

Run preflight before executing this workflow:

1. Execute shared preflight from `_bmad/lens-work/workflows/includes/preflight.md`.
2. If preflight reports missing authority repos, stop and direct the user to run `/onboard` first.

## Overview

This core workflow handles the lifecycle of a phase branch:
1. **Phase Start** — Branch creation (handled by phase router)
2. **Phase Work** — Artifact production (handled by delegated agent)
3. **Phase End** — Automatic PR creation (this workflow)
4. **Branch Cleanup** — Phase branch deletion after PR merge

## Phase Completion Detection

A phase is complete when all required artifacts exist for that phase.

**Algorithm:**
1. Read `lifecycle.yaml` to get required artifacts for the current phase
2. Check file existence at `_bmad-output/lens-work/initiatives/{path}/phases/{phase}/`
3. All required artifacts must be present

| Phase | Required Artifacts |
|-------|--------------------|
| preplan | product-brief.md, research.md |
| businessplan | prd.md, ux-design.md (or ux-design-specification.md) |
| techplan | architecture.md |
| devproposal | epics.md |
| sprintplan | sprint-status.yaml |

## Auto-PR Creation

When phase work is complete, automatically create a PR:

### PR Source and Target

```
Source branch: {initiative-root}-{audience}-{phase}
Target branch: {initiative-root}-{audience}
```

### PR Title Format

```
[PHASE] {initiative-root} — {display_name} complete
```

Examples:
- `[PHASE] foo-bar-auth — PrePlan complete`
- `[PHASE] foo-bar-auth — TechPlan complete`

### PR Body Generation

The PR body is generated dynamically from committed artifact content (not hardcoded templates):

```markdown
## Phase Completion: {display_name}

**Initiative:** {initiative-root}
**Track:** {track}
**Audience:** {audience}
**Phase Agent:** {agent} ({agent_role})

### Artifacts Produced

- [x] `{artifact-1}.md` — {first line or heading from artifact}
- [x] `{artifact-2}.md` — {first line or heading from artifact}

### Artifact Summaries

#### {artifact-1}
{First paragraph or executive summary extracted from artifact content}

#### {artifact-2}
{First paragraph or executive summary extracted from artifact content}

### Phase Gate Requirements

| Requirement | Status |
|-------------|--------|
| All required artifacts present | ✅ |
| Artifact content non-empty | ✅ |
| Constitution compliance | {PASS/PENDING — integrated at Story 6.2} |

### Review Instructions

Review the artifacts for completeness, quality, and alignment with initiative goals.
Merge this PR to mark the {display_name} phase as complete.
```

### PR Creation

Use provider-adapter `create-pr`:

```yaml
title: "[PHASE] {initiative-root} — {display_name} complete"
body: "{generated body}"
source_branch: "{initiative-root}-{audience}-{phase}"
target_branch: "{initiative-root}-{audience}"
```

### Auto-Merge

Immediately after the PR is created, merge it via GitHub REST API (do not wait for manual review):

1. Use `git-orchestration` skill → `auto-merge-pr` with the PR number returned from `create-pr`
2. Wait for merge confirmation
3. On merge success: proceed to Branch Cleanup
4. On merge failure: report error and stop

### Response

```
✅ Phase complete: {display_name}

- PR: [PHASE] {initiative-root} — {display_name} complete
- Merged automatically
- Artifacts: {count} files
- Phase branch cleaned up

Next: run `/{next_phase}` to continue.
```

### Step: Check Promotion Readiness After Phase Completion

After the phase PR is created, automatically check if promotion to the next audience should be available:

1. Read the current phase's `auto_advance_promote` setting from `lifecycle.yaml`
2. If `auto_advance_promote: false`: Continue to next step (no promotion check)
3. If `auto_advance_promote: true`: 
   - Run the promotion-check include: `_bmad/lens-work/workflows/includes/promotion-check.md`
   - If all phases for current audience are complete, display promotion readiness message:
   ```
   ⏭️  PROMOTION READY
   
   After merging this phase PR and completing any remaining phases:
   - All phases for [{current_audience}] will be complete
   - Run @lens /promote to promote to [{next_audience}]
   - The promote workflow will verify all gate requirements
   ```

## Phase Branch Cleanup

Phase branch cleanup is **eager** — it happens immediately after the phase PR is confirmed merged, not lazily.

### Algorithm

1. Confirm the merge return value from `auto-merge-pr` (do not re-query)
2. Immediately delete the phase branch using `git-orchestration` skill → `delete-branch`:
   ```bash
   git branch -d {root}-{audience}-{phase}              # Delete local
   git push origin --delete {root}-{audience}-{phase}   # Delete remote
   ```
3. Report cleanup:
   ```
   🧹 Phase branch `{root}-{audience}-{phase}` deleted
   ```

### Safety

- **ONLY** delete on confirmed merge return from `auto-merge-pr` — never on unconfirmed state
- git-state derives phase completion from PR metadata — branch deletion does not lose state

## Error Handling

| Error | Response |
|-------|----------|
| Missing required artifacts | `❌ Phase incomplete. Missing: {artifact-list}. Complete these before PR creation.` |
| PR creation fails | `❌ PR creation failed: {error}. Check provider authentication with /onboard.` |
| Branch cleanup on unmerged PR | Abort — never delete an unmerged phase branch |
