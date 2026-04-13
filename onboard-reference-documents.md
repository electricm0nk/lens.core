# lens-local-setup.py - Reconstruction Reference

This document is reconstructed only from the latest screenshot set and supersedes the earlier image-derived reconstruction.

## Purpose

Bootstrap script that sets up a local LENS Workbench environment from scratch.
Run from the root of a new control repo folder.

Example run:

```bash
python lens-local-setup.py
```

## Vocabulary

| Term | Description |
| --- | --- |
| root | The folder where the script is executed. Local workspace container; not committed to source control. |
| lens.core | Read-only LENS release module cloned from central repo. Contains agents, prompts, workflows, scripts. |
| lens-governance | Governance repo containing constitutional rules, policies, shared docs; cloned under TargetProjects. |
| TargetProjects | Local folder that holds operating repo clones, organized by domain/service/repo. |

## Final Directory Structure After Setup

```text
<root>/
|- lens.core/              # LENS release module (read-only)
|- .github/                # GitHub Copilot adapter copied from lens.core
|- docs/                   # Planning and initiative artifacts
|- TargetProjects/
|  |- <project-control-lib-repo>/
|  |- <governance-repo>/
```

## CLI Arguments

| Argument | Default | Description |
| --- | --- | --- |
| --folder-name | lens.core | Target folder name to clone lens.core into |
| --repo-url | (prompted/default URL) | Remote URL for lens.core |
| --branch | (prompted) | Branch to clone; when omitted script fetches branch list and prompts |
| --project-url | (prompted/default URL) | URL of project/control library repo |
| --governance-url | (prompted/default URL) | URL of governance repo |

## Script Logic - Step by Step

1. Parse arguments using argparse with the five arguments listed above.
2. Fetch available branches from --repo-url via git ls-remote --heads.
3. Parse branch names from refs/heads/<branch> and build a list.
4. Prompt for branch if --branch is not provided:
- Default to beta when present, otherwise first branch.
- Show numbered list and highlight default.
- Accept Enter for default, number, or exact branch name.
- Exit on invalid selection.
5. Clone lens.core into <root>/<folder-name>:
- If target exists, delete first (force_rmtree for read-only safety).
- Use git clone -b <branch> <repo-url> <target>.
6. Copy <folder-name>/.github to <root>/.github:
- Delete destination first if it exists.
- Use shutil.copytree.
- Warn and continue if source .github does not exist.
7. Create standard directories:
- docs/
- TargetProjects/
8. Clone project/control library repo:
- Use --project-url or prompt/default.
- Derive destination from URL last path segment (strip .git).
- Clone into TargetProjects/<derived-name>/.
9. Clone governance repo:
- Same behavior as step 8 using --governance-url.
- Destination: TargetProjects/<derived-name>/.
10. Print completion status.

## Helper Functions

- force_rmtree(path):
- Wraps shutil.rmtree with onerror handler.
- Uses os.chmod(path, stat.S_IWRITE) before retry for read-only files.

- run(cmd, **kwargs):
- Thin wrapper around subprocess.run.
- Returns CompletedProcess.

- fetch_branches(repo_url):
- Executes git ls-remote --heads <repo_url>.
- Parses branch names with regex refs/heads/(.+)$.
- Returns list[str].

- prompt_branch(branches, preselected):
- Returns preselected immediately when provided.
- Otherwise prints numbered list, highlights default, reads input.
- Returns selected branch name.

- main():
- Entry point orchestrating all setup steps.

## Imports Required

```python
import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
```

## Console Color Constants

```python
CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"
```

Used via f-strings such as f"{CYAN}message{RESET}".

## Guidance Notes

- control repo: Each work pod should have its own root workspace; share only when cross-pod collaboration requires joint planning artifacts.
- governance repo: Default can be broadly universal; customize only when teams need lifecycle, constitutional, or policy variation.

## Entry Point Guard

```python
if __name__ == "__main__":
    main()
```
