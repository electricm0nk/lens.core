# Workflow: Audience Promotion

**Module:** lens-work
**Type:** Core workflow
**Trigger:** `/promote` command via `lens-work.promote.prompt.md`

---

## Purpose

Promote an initiative from the current audience tier to the next audience in the chain (small → medium → large → base) with comprehensive pre-promotion gate checks.

All gate checks run before the promotion PR is created. Once gate checks pass, the PR is created and **immediately auto-merged** — no manual review step. After the merge, the source audience branch and all its phase children are deleted eagerly.

When promoting to `base` (the final audience), a further PR is automatically created from `{root}-base` → `main`, auto-merged, and all initiative branches are deleted.

## Prerequisites

- User is on an initiative branch
- Current audience is determined from branch name
- Next audience exists in the audience chain

## Workflow Steps

### Step 0: Run Preflight

Run preflight before executing this workflow:

1. Execute shared preflight from `_bmad/lens-work/workflows/includes/preflight.md`.
2. If preflight reports missing authority repos, stop and direct the user to run `/onboard` first.

### Step 1: Determine Current and Next Audience

1. Use `git-state` skill → `current-audience` to parse audience from branch name
2. Look up audience chain in `lifecycle.yaml`: small → medium → large → base
3. Determine next audience
4. If no next audience: report `✅ Initiative at final audience — no promotion available`

### Step 2: Pre-Promotion Gate Checks

Run ALL gate checks before creating the promotion PR:

#### 2a: Phase PR Verification

Use `git-state` skill to verify all required phase PRs for the current audience are merged:

| Current Audience | Required Merged Phase PRs |
|------------------|--------------------------|
| small | preplan, businessplan, techplan (per track) |
| medium | devproposal |
| large | sprintplan |

- Query provider adapter for PR status: `{root}-{audience}-{phase}` → `{root}-{audience}`
- If any required phase PR is NOT merged: **HARD GATE FAILURE**

#### 2b: Artifact Validation

Check required artifacts per the track's phase list:

1. Read committed artifacts on the current audience branch
2. Compare against lifecycle.yaml `phases[].artifacts` for each completed phase
3. If required artifacts are missing: **HARD GATE FAILURE**

#### 2c: Constitution Compliance Check

1. Invoke `constitution` skill → `resolve-constitution` for this initiative
2. Invoke `constitution` skill → `check-compliance` against resolved constitution
3. If hard gate failures exist: **HARD GATE FAILURE**
4. Informational failures: include as warnings in PR body

#### 2d: Cross-Initiative Sensing

1. Invoke `sensing` skill → `scan-initiatives` for this initiative's domain/service
2. Produce sensing report
3. Check if constitution upgrades sensing to hard gate for this domain
4. If hard gate + overlaps found: **HARD GATE FAILURE**
5. If informational (default): include results in PR body

### Step 3: Gate Check Result Processing

If ANY hard gate failed:

```
❌ Promotion blocked — gate check failures:

1. [HARD] Missing merged PR: {root}-{audience}-techplan → {root}-{audience}
2. [HARD] Required artifact missing: architecture.md for techplan phase

Resolve these issues and re-run /promote.
```

If all gates pass (with possible informational warnings): proceed to Step 4.

### Step 4: Create Next Audience Branch (Lazy)

1. Check if `{root}-{next-audience}` branch exists
2. If not: use `git-orchestration` skill → `create-branch` to create `{root}-{next-audience}` from `{root}` (the initiative root branch, NOT from the current audience branch)
3. If already exists: proceed (promotion was previously attempted or branch was pre-created)

### Step 5: Create Promotion PR

Use provider adapter to create PR:

- **From:** `{root}-{current-audience}`
- **To:** `{root}-{next-audience}`
- **Title:** `[PROMOTE] {initiative} {current}→{next}`
- **Body:** Assembled from sections below

### Step 6: Assemble PR Body

Include the following sections in the promotion PR body:

```markdown
## Promotion Summary

**Initiative:** {initiative_root}
**Promotion:** {current_audience} → {next_audience}
**Track:** {track_type}

## Gate Check Results

{gate_check_summary — all passed}

## Compliance Status

{compliance_result from constitution check}

## Cross-Initiative Sensing

{sensing_report from sensing skill — see includes/sensing-report.md}

## Artifacts Summary

{list of committed artifacts by phase}
```

### Step 7: Auto-Merge Promotion PR

Immediately after the PR is created, merge it via GitHub REST API (do not wait for manual review):

1. Use `git-orchestration` skill → `auto-merge-pr` with the PR number returned from `create-pr`
2. Wait for merge confirmation
3. On merge success: proceed to Step 8 (Audience Branch Cleanup)
4. On merge failure: report error and stop — do not delete branches

### Step 8: Audience Branch Cleanup

After the promotion PR is confirmed merged, immediately clean up the source audience branch and all its phase children. **Do not use GitHub Actions for this cleanup — use the git-orchestration skill directly.**

```bash
# Delete all phase branches that were children of {root}-{current-audience}
# Pattern: {root}-{current-audience}-*
for each phase_branch matching {root}-{current-audience}-*:
    git branch -d {phase_branch}
    git push origin --delete {phase_branch}

# Delete the source audience branch
git branch -d {root}-{current-audience}
git push origin --delete {root}-{current-audience}
```

Use `git-orchestration` skill → `delete-branch` for each deletion. Report each deletion:
```
🧹 Cleaned up `{branch}`
```

### Step 9: Handle base Promotion — Final Merge to main

If `{next-audience}` is `base` (i.e., this was the `large → base` promotion):

1. Read `final_merge_target` from `lifecycle.yaml` `pr_behavior` (default: `main`)
2. Create a final PR:
   - **From:** `{root}-base`
   - **To:** `{final_merge_target}` (e.g., `main`)
   - **Title:** `[INITIATIVE COMPLETE] {initiative} — planning artifacts`
   - **Body:** Summary of the full initiative lifecycle and artifact index
3. Auto-merge this final PR via `git-orchestration` skill → `auto-merge-pr`
4. After merge confirmed, delete all remaining initiative branches:
   ```bash
   git branch -d {root}-base && git push origin --delete {root}-base
   git branch -d {root} && git push origin --delete {root}
   ```
5. Report initiative complete:
   ```
   🎉 Initiative complete: {initiative}

   Planning artifacts are now on `{final_merge_target}`.
   All initiative branches have been cleaned up.

   Next: run /dev to begin implementation in target projects.
   ```

### Step 10: Report Promotion Chain Status

```
✅ Promoted: {initiative} {current}→{next}

Branches cleaned up: {list of deleted branches}

**Promotion Chain:**
- ✅ small → medium: complete
- ✅ medium → large: complete    (example — show actual state)
- ⏳ large → base: Requires sprintplan

Continue with: /{next_phase} on the {next-audience} audience branch.
```

---

## Error Handling

| Error | Response |
|-------|----------|
| Not on initiative branch | `❌ Not on an initiative branch. Use /switch first.` |
| No next audience | `✅ Initiative is at final audience — no promotion needed.` |
| Hard gate failure | List all failures with actionable resolution steps |
| PR creation fails | `❌ Failed to create promotion PR. Check provider adapter config.` |
| Branch creation fails | `❌ Failed to create {next-audience} branch. Check git permissions.` |

## Key Constraints

- Gate checks must ALL pass before the promotion PR is created
- Promotion PRs are merge PRs (not rebase or squash)
- Gate checks are cumulative — higher audiences have stricter gates
- Sensing report is always included, even when no overlaps found
- Constitution can upgrade any check from informational to hard gate
- Branch cleanup is always performed immediately after merge — never via GitHub Actions
