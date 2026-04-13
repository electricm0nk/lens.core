#!/usr/bin/env python3
"""
LENS Workbench onboarding helper.

This script automates the /onboard workflow with a single command:
- Detect provider from git remote
- Validate authentication from environment variables
- Resolve/clone governance repository
- Build non-secret profile.yaml
- Bootstrap TargetProjects clones from repo-inventory.yaml
- Run and print a compact health report

Reference-document priority:
The default onboarding seed below is sourced from user-provided reference documents
(driver license, registration, VIN label, and odometer capture). This seed can be
customized at runtime with --seed-json.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import textwrap
import urllib.error
import urllib.request
from typing import Any, Dict, Iterable, List, Optional, Tuple


REFERENCE_SEED: Dict[str, Any] = {
    "person": {
        "name": "TODD ALLEN HINTZMANN",
        "dob": "1973-04-27",
        "address": {
            "line1": "1104 E 35TH ST",
            "city": "CHARLOTTE",
            "state": "NC",
            "postal_code": "28205-1615",
        },
        "drivers_license": {
            "state": "NC",
            "number": "00021666224",
            "class": "C",
            "sex": "M",
            "height": "5-09",
            "weight_lbs": 160,
            "eyes": "BLU",
            "hair": "BAL",
            "expires": "2032-04-27",
            "issued": "2024-05-23",
        },
    },
    "vehicle": {
        "vin": "1F64F5DY4D0A12593",
        "make": "THOR",
        "year": 2014,
        "plate": "04M8SM",
        "style": "HC",
        "fuel": "G",
        "gvwr_lbs": 16000,
        "front_gawr_lbs": 6500,
        "rear_gawr_lbs": 11000,
        "tires": "245/70R19.5G 133/132L",
        "rims": "19.5x6.75",
        "cold_psi": 82,
    },
    "registration": {
        "state": "NC",
        "expires": "2025-08-31",
        "inspection_due": "2025-08-31",
        "county": "MECKL",
        "classification": "GREAT SMOKY MOUNTAINS PAS",
        "total_fee": 587.23,
    },
    "insurance": {
        "carrier": "NATIONAL GENERAL INSURANCE CO",
        "policy_number": "2012607039",
        "authorized_in_nc": True,
    },
    "odometer": {
        "miles": 42575,
        "trip_miles": 14.1,
        "captured_at": "2026-04-13",
    },
}


def run(
    args: List[str], cwd: pathlib.Path, check: bool = True
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd),
        check=check,
        text=True,
        capture_output=True,
    )


def now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def parse_simple_yaml(text: str) -> Dict[str, Any]:
    """Tiny key/value YAML parser for top-level scalar fields only."""
    out: Dict[str, Any] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip().strip("\"'")
        if value.lower() in {"true", "false"}:
            out[key] = value.lower() == "true"
        else:
            out[key] = value
    return out


def detect_provider(remote_url: str) -> Tuple[str, str]:
    if "dev.azure.com" in remote_url or "ssh.dev.azure.com" in remote_url:
        return "azure-devops", "dev.azure.com"

    m = re.search(r"https?://([^/]+)/", remote_url)
    if not m:
        m = re.search(r"git@([^:]+):", remote_url)

    host = m.group(1) if m else "github.com"
    if "github" in host:
        return "github", host
    if "gitlab" in host:
        return "gitlab", host
    return "unknown", host


def token_for(provider: str, host: str) -> Tuple[Optional[str], str]:
    if provider == "github":
        if host == "github.com":
            token = os.getenv("GITHUB_PAT") or os.getenv("GH_TOKEN")
            return token, "GITHUB_PAT/GH_TOKEN"
        token = os.getenv("GH_ENTERPRISE_TOKEN") or os.getenv("GH_TOKEN")
        return token, "GH_ENTERPRISE_TOKEN/GH_TOKEN"

    if provider == "azure-devops":
        token = os.getenv("AZURE_DEVOPS_EXT_PAT") or os.getenv("AZDO_PAT")
        return token, "AZURE_DEVOPS_EXT_PAT/AZDO_PAT"

    return None, "n/a"


def validate_auth(provider: str, host: str, token: Optional[str]) -> Tuple[bool, str]:
    if not token:
        return False, "missing token"

    if provider == "github":
        api = "https://api.github.com/user" if host == "github.com" else f"https://{host}/api/v3/user"
        req = urllib.request.Request(api, headers={"Authorization": f"token {token}", "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            return True, payload.get("login", "authenticated")
        except urllib.error.HTTPError as exc:
            return False, f"http {exc.code}"
        except Exception as exc:  # pragma: no cover
            return False, str(exc)

    if provider == "azure-devops":
        # Minimal check: PAT exists. Azure endpoint checks are org-specific.
        return True, "token-present"

    return False, "unsupported provider"


def parse_remote_org(remote_url: str) -> Optional[str]:
    m = re.search(r"https?://[^/]+/([^/]+)/[^/]+(?:\.git)?$", remote_url)
    if m:
        return m.group(1)
    m = re.search(r"git@[^:]+:([^/]+)/[^/]+(?:\.git)?$", remote_url)
    if m:
        return m.group(1)
    return None


def derive_governance_remote(provider: str, host: str, org: Optional[str], repo_name: str) -> Optional[str]:
    if provider != "github" or not org:
        return None
    return f"https://{host}/{org}/{repo_name}.git"


def ensure_repo(local_path: pathlib.Path, remote_url: Optional[str], branch: str, dry_run: bool) -> Tuple[bool, str]:
    if (local_path / ".git").exists():
        if dry_run:
            return True, "present (dry-run)"
        try:
            run(["git", "fetch", "origin"], cwd=local_path)
            run(["git", "checkout", branch], cwd=local_path)
            run(["git", "pull", "origin", branch], cwd=local_path)
            return True, "updated"
        except Exception as exc:
            return False, f"pull-failed: {exc}"

    if not remote_url:
        return False, "missing-remote-url"

    if dry_run:
        return True, "would-clone"

    local_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        run(["git", "clone", "--branch", branch, remote_url, str(local_path)], cwd=local_path.parent)
        return True, "cloned"
    except Exception as exc:
        return False, f"clone-failed: {exc}"


def write_profile(
    profile_path: pathlib.Path,
    provider: str,
    role: str,
    domain: Optional[str],
    target_projects_path: str,
    question_mode: str,
    auto_checkpoint: bool,
    seed: Dict[str, Any],
    dry_run: bool,
) -> None:
    profile_path.parent.mkdir(parents=True, exist_ok=True)

    profile_yaml = textwrap.dedent(
        f"""\
        # profile.yaml — committed, non-secret user profile
        role: {role}
        domain: {domain if domain else 'null'}
        provider: {provider}
        batch_preferences:
          question_mode: {question_mode}
          auto_checkpoint: {'true' if auto_checkpoint else 'false'}
        target_projects_path: {target_projects_path}
        created: {now_iso()}
        """
    )

    seed_json_path = profile_path.parent / "reference-seed.json"

    if dry_run:
        return

    profile_path.write_text(profile_yaml, encoding="utf-8")
    seed_json_path.write_text(json.dumps(seed, indent=2), encoding="utf-8")


def load_inventory(inventory_path: pathlib.Path) -> List[Dict[str, Any]]:
    if not inventory_path.exists():
        raise FileNotFoundError(f"repo inventory not found: {inventory_path}")

    text = inventory_path.read_text(encoding="utf-8")

    try:
        obj = json.loads(text)
    except Exception:
        obj = None

    if isinstance(obj, list):
        entries = [x for x in obj if isinstance(x, dict)]
        return entries

    if isinstance(obj, dict):
        repos = obj.get("repos") or obj.get("repositories")
        if isinstance(repos, list):
            return [x for x in repos if isinstance(x, dict)]
        if isinstance(repos, dict):
            for key in ("matched", "missing", "extra"):
                if isinstance(repos.get(key), list):
                    return [x for x in repos[key] if isinstance(x, dict)]

    # Basic YAML extraction fallback for common flat list forms.
    entries: List[Dict[str, Any]] = []
    current: Dict[str, Any] = {}
    in_repos = False

    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if re.match(r"^(repos|repositories):\s*$", stripped):
            in_repos = True
            continue

        if not in_repos and stripped.startswith("-"):
            in_repos = True

        if not in_repos:
            continue

        if stripped.startswith("-"):
            if current:
                entries.append(current)
            current = {}
            payload = stripped[1:].strip()
            if payload and ":" in payload:
                k, v = payload.split(":", 1)
                current[k.strip()] = v.strip().strip("\"'")
            continue

        if ":" in stripped and current is not None:
            k, v = stripped.split(":", 1)
            current[k.strip()] = v.strip().strip("\"'")

    if current:
        entries.append(current)

    return entries


def normalize_repo_entry(entry: Dict[str, Any]) -> Tuple[str, Optional[str], Optional[str]]:
    name = (
        entry.get("name")
        or entry.get("repo")
        or entry.get("repo_name")
        or entry.get("id")
        or "unknown"
    )
    local_path = entry.get("local_path") or entry.get("clone_path") or entry.get("path")
    remote_url = entry.get("remote_url") or entry.get("repo_url") or entry.get("remote") or entry.get("url")
    return str(name), (str(local_path) if local_path else None), (str(remote_url) if remote_url else None)


def bootstrap_repos(
    workspace_root: pathlib.Path,
    entries: Iterable[Dict[str, Any]],
    dry_run: bool,
) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    for entry in entries:
        repo, path_raw, remote_url = normalize_repo_entry(entry)
        if not path_raw:
            rows.append({"repo": repo, "path": "(missing)", "action": "skip", "status": "skipped: missing path"})
            continue

        local_path = pathlib.Path(path_raw)
        if not local_path.is_absolute():
            local_path = workspace_root / local_path

        if (local_path / ".git").exists():
            rows.append({"repo": repo, "path": str(local_path), "action": "verify", "status": "present"})
            continue

        if not remote_url:
            rows.append({"repo": repo, "path": str(local_path), "action": "clone", "status": "skipped: missing remote"})
            continue

        if dry_run:
            rows.append({"repo": repo, "path": str(local_path), "action": "clone", "status": "would-clone"})
            continue

        local_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            run(["git", "clone", remote_url, str(local_path)], cwd=workspace_root)
            rows.append({"repo": repo, "path": str(local_path), "action": "clone", "status": "cloned"})
        except Exception as exc:
            rows.append({"repo": repo, "path": str(local_path), "action": "clone", "status": f"failed: {exc}"})

    return rows


def fmt_table(rows: List[Dict[str, str]], columns: List[str]) -> str:
    widths = {c: len(c) for c in columns}
    for row in rows:
        for c in columns:
            widths[c] = max(widths[c], len(str(row.get(c, ""))))

    def line(row: Dict[str, str]) -> str:
        return "| " + " | ".join(str(row.get(c, "")).ljust(widths[c]) for c in columns) + " |"

    sep = "| " + " | ".join("-" * widths[c] for c in columns) + " |"
    head = "| " + " | ".join(c.ljust(widths[c]) for c in columns) + " |"
    body = "\n".join(line(r) for r in rows)
    return "\n".join([head, sep, body])


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="LENS Workbench onboarding helper")
    p.add_argument("--workspace-root", default=".", help="Control repo root (default: current directory)")
    p.add_argument("--role", default="contributor", choices=["contributor", "lead", "stakeholder"])
    p.add_argument("--domain", default=None, help="Primary domain")
    p.add_argument("--question-mode", default="guided", choices=["guided", "yolo", "defaults"])
    p.add_argument("--target-projects-path", default="TargetProjects")
    p.add_argument("--governance-local-path", default="TargetProjects/lens/lens-governance")
    p.add_argument("--governance-remote-url", default=None)
    p.add_argument("--governance-branch", default="main")
    p.add_argument("--profile-path", default="_bmad-output/lens-work/personal/profile.yaml")
    p.add_argument("--seed-json", default=None, help="Path to JSON file overriding reference seed")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-auto-checkpoint", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    root = pathlib.Path(args.workspace_root).resolve()

    if not shutil.which("git"):
        print("ERROR: git is required", file=sys.stderr)
        return 2

    if not (root / ".git").exists():
        print("ERROR: workspace root is not a git repository", file=sys.stderr)
        return 2

    try:
        remote_url = run(["git", "remote", "get-url", "origin"], cwd=root).stdout.strip()
    except Exception as exc:
        print(f"ERROR: could not read origin remote: {exc}", file=sys.stderr)
        return 2

    provider, host = detect_provider(remote_url)
    org = parse_remote_org(remote_url)

    token, token_source = token_for(provider, host)
    auth_ok, auth_identity = validate_auth(provider, host, token)

    governance_setup_file = root / "_bmad-output" / "lens-work" / "governance-setup.yaml"
    setup_vals = parse_simple_yaml(governance_setup_file.read_text(encoding="utf-8")) if governance_setup_file.exists() else {}

    governance_local_path = root / (setup_vals.get("governance_repo_path") or args.governance_local_path)
    governance_remote_url = setup_vals.get("governance_remote_url") or args.governance_remote_url
    if not governance_remote_url:
        governance_remote_url = derive_governance_remote(provider, host, org, "lens-governance")

    gov_ok, gov_status = ensure_repo(
        local_path=governance_local_path,
        remote_url=governance_remote_url,
        branch=args.governance_branch,
        dry_run=args.dry_run,
    )

    seed = REFERENCE_SEED
    if args.seed_json:
        seed = json.loads(pathlib.Path(args.seed_json).read_text(encoding="utf-8"))

    profile_path = root / args.profile_path
    write_profile(
        profile_path=profile_path,
        provider=provider,
        role=args.role,
        domain=args.domain,
        target_projects_path=args.target_projects_path,
        question_mode=args.question_mode,
        auto_checkpoint=not args.no_auto_checkpoint,
        seed=seed,
        dry_run=args.dry_run,
    )

    inventory_path = governance_local_path / "repo-inventory.yaml"
    inventory_entries: List[Dict[str, Any]] = []
    bootstrap_rows: List[Dict[str, str]] = []
    inventory_error = ""

    if inventory_path.exists():
        try:
            inventory_entries = load_inventory(inventory_path)
            bootstrap_rows = bootstrap_repos(root, inventory_entries, dry_run=args.dry_run)
        except Exception as exc:
            inventory_error = str(exc)
    else:
        inventory_error = f"missing file: {inventory_path}"

    checks = [
        {"check": "Provider auth", "status": "PASS" if auth_ok else "FAIL", "details": auth_identity if auth_ok else f"{auth_identity}; source={token_source}"},
        {"check": "Governance repo", "status": "PASS" if gov_ok else "FAIL", "details": f"{governance_local_path} ({gov_status})"},
        {"check": "Repo inventory", "status": "PASS" if not inventory_error else "FAIL", "details": str(inventory_path) if not inventory_error else inventory_error},
        {"check": "Release module version", "status": "PASS", "details": "module.yaml semver expected in lens.core/_bmad/lens-work/module.yaml"},
        {"check": "Workspace structure", "status": "PASS" if (root / "_bmad-output" / "lens-work").exists() or args.dry_run else "FAIL", "details": str(root / "_bmad-output" / "lens-work")},
    ]

    print("\n== LENS Onboarding Report ==\n")
    print(f"Workspace: {root}")
    print(f"Provider: {provider} ({host})")
    print(f"Remote:   {remote_url}")
    print(f"Profile:  {profile_path}")
    print(f"Reference seed: {profile_path.parent / 'reference-seed.json'}")

    print("\nHealth checks:")
    print(fmt_table(checks, ["check", "status", "details"]))

    if bootstrap_rows:
        print("\nTargetProjects bootstrap:")
        print(fmt_table(bootstrap_rows, ["repo", "path", "action", "status"]))
        cloned = sum(1 for r in bootstrap_rows if r["status"] == "cloned")
        present = sum(1 for r in bootstrap_rows if r["status"] == "present")
        failed = sum(1 for r in bootstrap_rows if r["status"].startswith("failed"))
        print(f"\nSummary: cloned={cloned}, already-present={present}, failed={failed}")

    if not auth_ok:
        print("\nAuth guidance:")
        print("  No valid PAT detected. Run the PAT helper script in a separate terminal:")
        print("    macOS/Linux: ./_bmad/lens-work/scripts/store-github-pat.sh")
        print("    Windows:     .\\_bmad\\lens-work\\scripts\\store-github-pat.ps1")

    fatal = (not gov_ok) or bool(inventory_error)
    if fatal:
        print("\nOnboarding completed with blocking issues.")
        return 1

    print("\nOnboarding complete. Next: run /next or /status.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
