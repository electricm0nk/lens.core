#!/usr/bin/env python3
"""
lens-local-setup.py style bootstrap utility (reconstructed from latest reference images).

Purpose:
Bootstrap a local LENS Workbench environment from scratch.
Run from the root of a new control repository folder.

Primary workflow:
1. Parse CLI args.
2. Fetch branches from lens.core repo URL.
3. Prompt branch (default beta if present).
4. Clone lens.core into target folder.
5. Copy lens.core/.github to root .github.
6. Create standard directories: docs/ and TargetProjects/.
7. Clone project/control library repo into TargetProjects/<repo-name>/.
8. Clone governance repo into TargetProjects/<repo-name>/.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import List


CYAN = "\033[96m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RED = "\033[91m"
RESET = "\033[0m"


def run(cmd: List[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Thin wrapper around subprocess.run that always captures text output."""
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, text=True, capture_output=True)


def force_rmtree(path: Path) -> None:
    """Delete directory tree including read-only files (Windows-safe)."""

    def onerror(func, p, exc_info):
        _ = exc_info
        os.chmod(p, stat.S_IWRITE)
        func(p)

    if path.exists():
        shutil.rmtree(path, onerror=onerror)


def fetch_branches(repo_url: str) -> List[str]:
    """Return branch names from `git ls-remote --heads <repo_url>`."""
    result = run(["git", "ls-remote", "--heads", repo_url])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "failed to fetch branches")

    branches: List[str] = []
    for line in result.stdout.splitlines():
        match = re.search(r"refs/heads/(.+)$", line.strip())
        if match:
            branches.append(match.group(1))

    if not branches:
        raise RuntimeError("no branches found")

    return branches


def prompt_branch(branches: List[str], preselected: str | None) -> str:
    """Prompt user for branch selection; default beta if present else first."""
    if preselected:
        return preselected

    default = "beta" if "beta" in branches else branches[0]

    print(f"{CYAN}Available branches:{RESET}")
    for idx, branch in enumerate(branches, start=1):
        marker = " (default)" if branch == default else ""
        color = YELLOW if branch == default else RESET
        print(f"  {idx}. {color}{branch}{RESET}{marker}")

    raw = input(f"Select branch [Enter for {default}]: ").strip()
    if not raw:
        return default

    if raw.isdigit():
        n = int(raw)
        if 1 <= n <= len(branches):
            return branches[n - 1]

    if raw in branches:
        return raw

    raise ValueError("invalid branch selection")


def repo_name_from_url(url: str) -> str:
    name = url.rstrip("/").split("/")[-1]
    return name[:-4] if name.endswith(".git") else name


def clone_repo(url: str, branch: str | None, target: Path) -> None:
    if target.exists():
        force_rmtree(target)

    target.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["git", "clone"]
    if branch:
        cmd.extend(["-b", branch])
    cmd.extend([url, str(target)])

    result = run(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"clone failed for {url}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a local LENS workbench environment")
    parser.add_argument("--folder-name", default="lens.core", help="Target folder name for lens.core clone")
    parser.add_argument(
        "--repo-url",
        default="https://github.wellsfargo.com/NonApp-CLAUT/lens-local.github",
        help="lens.core clone URL",
    )
    parser.add_argument("--branch", default=None, help="Branch to clone (prompts if omitted)")
    parser.add_argument(
        "--project-url",
        default="https://github.wellsfargo.com/NonApp-CLAUT/NonApp-claut-specDevEnvDevelopment.git",
        help="Project/control library repository URL",
    )
    parser.add_argument(
        "--governance-url",
        default="https://github.wellsfargo.com/NonApp-CLAUT/NonApp-claut-SDD-Config.git",
        help="Governance repository URL",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Non-interactive mode; picks default branch when --branch is not provided",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd()

    try:
        branches = fetch_branches(args.repo_url)
        if args.branch:
            branch = prompt_branch(branches, args.branch)
        elif args.yes:
            branch = "beta" if "beta" in branches else branches[0]
        else:
            branch = prompt_branch(branches, None)

        # Step 4: Clone lens.core
        lens_target = root / args.folder_name
        clone_repo(args.repo_url, branch, lens_target)
        print(f"{GREEN}Cloned lens repo -> {lens_target}{RESET}")

        # Step 5: Copy lens.core/.github -> <root>/.github
        source_github = lens_target / ".github"
        dest_github = root / ".github"
        if source_github.exists():
            if dest_github.exists():
                force_rmtree(dest_github)
            shutil.copytree(source_github, dest_github)
            print(f"{GREEN}Copied .github -> {dest_github}{RESET}")
        else:
            print(f"{YELLOW}Skipped .github copy (source missing: {source_github}){RESET}")

        # Step 6: Create standard directories.
        (root / "docs").mkdir(parents=True, exist_ok=True)
        target_projects = root / "TargetProjects"
        target_projects.mkdir(parents=True, exist_ok=True)
        print(f"{GREEN}Ensured docs/ and TargetProjects/{RESET}")

        # Step 7: Clone project/control library.
        project_name = repo_name_from_url(args.project_url)
        project_target = target_projects / project_name
        clone_repo(args.project_url, None, project_target)
        print(f"{GREEN}Cloned project repo -> {project_target}{RESET}")

        # Step 8: Clone governance repo.
        governance_name = repo_name_from_url(args.governance_url)
        governance_target = target_projects / governance_name
        clone_repo(args.governance_url, None, governance_target)
        print(f"{GREEN}Cloned governance repo -> {governance_target}{RESET}")

        print(f"{GREEN}Setup complete.{RESET}")
        return 0

    except KeyboardInterrupt:
        print(f"\n{RED}Cancelled by user.{RESET}")
        return 130
    except Exception as exc:
        print(f"{RED}Error: {exc}{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
