#!/usr/bin/env python3
"""
agent_selector.py — Interactive agent variant switcher for lens.core (cross-platform)

Reads agent_manifest.md, prompts the user to switch agents by theme (package)
or individually, then copies the chosen variant into _bmad/custom_agents/active/
and calls agent_selector_update_manifest.py to keep the manifest in sync.

Usage:
    python agent_selector.py [--workspace-root /path/to/workspace]

Requirements: Python 3.9+, git on PATH
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR        = Path(__file__).resolve().parent
MANIFEST          = SCRIPT_DIR / "_bmad" / "custom_agents" / "agent_manifest.md"
CUSTOM_AGENTS_DIR = SCRIPT_DIR / "_bmad" / "custom_agents"
ACTIVE_DIR        = SCRIPT_DIR / "_bmad" / "custom_agents" / "active"
UPDATE_MANIFEST   = SCRIPT_DIR / "agent_selector_update_manifest.py"
SUBMODULE_NAME    = SCRIPT_DIR.name

# ---------------------------------------------------------------------------
# Color helpers — ANSI with Windows VT support, silenced when not a TTY
# ---------------------------------------------------------------------------
if sys.platform == "win32":
    os.system("")  # Enable VT100 processing in Windows console

_IS_TTY = sys.stdout.isatty()


def _c(code: str, text: str) -> str:
    return f"\033[{code}m{text}\033[0m" if _IS_TTY else text


def print_header(text: str) -> None:
    print(_c("1;36", text))


def print_ok(text: str) -> None:
    print(_c("1;32", f"  \u2713 {text}"))


def print_warn(text: str) -> None:
    print(_c("1;33", f"  \u26a0 {text}"))


def print_err(text: str) -> None:
    print(_c("1;31", f"  \u2717 {text}"))


# ---------------------------------------------------------------------------
# Manifest parsing helpers
# ---------------------------------------------------------------------------

def get_agent_field(agent_id: str, key: str) -> str:
    """Extract a YAML key value from the agent's block in the manifest."""
    in_block = False
    with open(MANIFEST, encoding="utf-8") as f:
        for raw in f:
            line = raw.rstrip("\n")
            if not in_block and line == f"id: {agent_id}":
                in_block = True
                continue
            if in_block:
                if line.startswith("```"):
                    break
                if line.startswith(f"{key}:"):
                    val = line[len(key) + 1:].strip().strip('"').strip("'")
                    return val
    return ""


def list_agent_ids() -> list[str]:
    """Return all agent IDs from the manifest (excludes lens, which is not theme-able)."""
    ids: list[str] = []
    with open(MANIFEST, encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if line.startswith("id: "):
                agent_id = line[4:].strip()
                if agent_id != "lens":
                    ids.append(agent_id)
    return ids


def list_themes() -> list[str]:
    """Return theme names — subdirs of custom_agents/ that contain at least one .md file."""
    themes: list[str] = []
    for d in sorted(CUSTOM_AGENTS_DIR.iterdir()):
        if not d.is_dir() or d.name == "active":
            continue
        if any(d.glob("*.md")):
            themes.append(d.name)
    return themes


def find_variant_for_agent(theme_dir: Path, agent_id: str) -> str:
    """Return the variant filename (basename) for agent_id in theme_dir, or ''."""
    for f in theme_dir.glob(f"{agent_id}_*.md"):
        return f.name
    return ""


def get_active_theme(agent_id: str) -> str:
    return get_agent_field(agent_id, "active_theme")


def get_active_variant(agent_id: str) -> str:
    return get_agent_field(agent_id, "active_variant")


def agents_in_theme(theme: str) -> list[tuple[str, str]]:
    """Return (agent_id, variant_basename) pairs for every agent that has a variant in theme."""
    theme_dir = CUSTOM_AGENTS_DIR / theme
    result: list[tuple[str, str]] = []
    for agent_id in list_agent_ids():
        variant = find_variant_for_agent(theme_dir, agent_id)
        if variant:
            result.append((agent_id, variant))
    return result


# ---------------------------------------------------------------------------
# Apply a switch for a single agent
# ---------------------------------------------------------------------------

def _git_update_index(flag: str, rel_path: str) -> None:
    """Run git update-index with --skip-worktree or --no-skip-worktree; ignore errors."""
    subprocess.run(
        ["git", "-C", str(SCRIPT_DIR), "update-index", flag, rel_path],
        capture_output=True,
    )


def apply_switch(agent_id: str, new_theme: str, new_variant: str) -> None:
    cur_theme   = get_active_theme(agent_id)
    cur_variant = get_active_variant(agent_id)

    if cur_theme == new_theme and cur_variant == new_variant:
        print_warn(f"{agent_id}: already using {new_theme}/{new_variant} — skipping")
        return

    src = CUSTOM_AGENTS_DIR / new_theme / new_variant
    if not src.exists():
        print_err(f"source file not found: {src}")
        return

    # Copy into active/ and hide from git status
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)
    dest    = ACTIVE_DIR / f"{agent_id}.md"
    rel     = f"_bmad/custom_agents/active/{agent_id}.md"

    _git_update_index("--no-skip-worktree", rel)
    shutil.copy2(src, dest)
    _git_update_index("--skip-worktree", rel)

    bold  = "\033[1m" if _IS_TTY else ""
    reset = "\033[0m" if _IS_TTY else ""
    print(f"  {bold}{agent_id}{reset}: {cur_theme}/{cur_variant} \u2192 {new_theme}/{new_variant}")
    print_ok(f"{dest} updated")

    # Delegate manifest field updates to the Python helper
    subprocess.run(
        [sys.executable, str(UPDATE_MANIFEST), str(MANIFEST), agent_id, new_theme, new_variant],
        check=True,
    )
    print_ok(f"manifest updated for {agent_id}")


# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

def numbered_menu(prompt: str, items: list[str]) -> int:
    """Display a numbered list, prompt for a choice, return 0-based index."""
    for i, item in enumerate(items, 1):
        print(f"  {i:2}) {item}")
    print()
    while True:
        raw = input(f"{prompt}: ").strip()
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(items):
                return n - 1
        print_err(f"Invalid choice — enter a number between 1 and {len(items)}")


def confirm(prompt: str = "Continue?") -> bool:
    while True:
        ans = input(f"{prompt} [y/n]: ").strip().lower()
        if ans in ("y", "yes"):
            return True
        if ans in ("n", "no"):
            return False
        print("  Enter y or n")


# ---------------------------------------------------------------------------
# MODE 1: Apply entire theme as a package
# ---------------------------------------------------------------------------

def mode_apply_theme(theme: str) -> None:
    print_header(f"\nApplying theme package: {theme}")
    print()

    theme_agents = agents_in_theme(theme)
    changes = [
        (aid, var) for aid, var in theme_agents
        if get_active_theme(aid) != theme or get_active_variant(aid) != var
    ]

    if not changes:
        print(f"  All agents are already using the '{theme}' theme.")
        return

    print(f"  The following agents will be switched to the '{theme}' theme:")
    for agent_id, new_var in changes:
        cur_t = get_active_theme(agent_id)
        cur_v = get_active_variant(agent_id)
        print(f"    {agent_id}: {cur_t}/{cur_v} \u2192 {theme}/{new_var}")
    print()

    if not confirm("Apply these changes?"):
        print("  Aborted.")
        return

    print()
    for agent_id, new_var in changes:
        apply_switch(agent_id, theme, new_var)
        print()

    print_header(f"Theme '{theme}' applied successfully.")


# ---------------------------------------------------------------------------
# MODE 2: Switch a single agent
# ---------------------------------------------------------------------------

def mode_switch_individual() -> None:
    print_header("\nSelect an agent to switch:")
    print()

    agent_ids    = list_agent_ids()
    display_items = [
        f"{aid}  (currently: {get_active_theme(aid)}/{get_active_variant(aid)})"
        for aid in agent_ids
    ]

    idx           = numbered_menu("Choose agent", display_items)
    chosen_agent  = agent_ids[idx]

    # Build variant list
    print()
    print_header(f"Select a variant for '{chosen_agent}':")
    print()

    variant_themes:   list[str] = []
    variant_variants: list[str] = []
    variant_labels:   list[str] = []

    for theme in list_themes():
        theme_dir = CUSTOM_AGENTS_DIR / theme
        variant = find_variant_for_agent(theme_dir, chosen_agent)
        if not variant:
            continue
        variant_themes.append(theme)
        variant_variants.append(variant)
        variant_labels.append(f"[{theme}] {variant[:-3]}  ({variant})")

    if not variant_labels:
        print_warn(f"No variants found for '{chosen_agent}'")
        return

    cur_theme   = get_active_theme(chosen_agent)
    cur_variant = get_active_variant(chosen_agent)

    labeled_items = [
        f"{label}  \u2190 current"
        if variant_themes[i] == cur_theme and variant_variants[i] == cur_variant
        else label
        for i, label in enumerate(variant_labels)
    ]

    idx2        = numbered_menu("Choose variant", labeled_items)
    new_theme   = variant_themes[idx2]
    new_variant = variant_variants[idx2]

    if new_theme == cur_theme and new_variant == cur_variant:
        print("  Already active — nothing to do.")
        return

    print()
    if not confirm(f"Switch '{chosen_agent}' to '{new_theme}/{new_variant}'?"):
        print("  Aborted.")
        return

    print()
    apply_switch(chosen_agent, new_theme, new_variant)
    print()
    print_header("Done.")


# ---------------------------------------------------------------------------
# MODE 3: Show current agent status
# ---------------------------------------------------------------------------

def mode_show_status() -> None:
    print()
    print_header("Current agent assignments:")
    print()
    print(f"  {'AGENT':<30} {'THEME':<12} VARIANT")
    print(f"  {'-----':<30} {'-----':<12} -------")
    for aid in list_agent_ids():
        theme   = get_active_theme(aid)
        variant = get_active_variant(aid)
        print(f"  {aid:<30} {theme:<12} {variant}")
    print()


# ---------------------------------------------------------------------------
# MODE 4: Initialize active/ from manifest state
# Run once after cloning, or to reset to the committed manifest state.
# ---------------------------------------------------------------------------

def mode_init() -> None:
    print_header("\nInitializing active/ from manifest...")
    print()
    ACTIVE_DIR.mkdir(parents=True, exist_ok=True)

    for agent_id in list_agent_ids():
        theme   = get_active_theme(agent_id)
        variant = get_active_variant(agent_id)
        src     = CUSTOM_AGENTS_DIR / theme / variant

        if not src.exists():
            print_warn(f"{agent_id}: source not found ({src}) — skipping")
            continue

        rel = f"_bmad/custom_agents/active/{agent_id}.md"
        _git_update_index("--no-skip-worktree", rel)
        shutil.copy2(src, ACTIVE_DIR / f"{agent_id}.md")
        _git_update_index("--skip-worktree", rel)
        print_ok(f"{agent_id} \u2192 {theme}/{variant}")

    print()
    print_header("active/ initialized. You're ready to go.")


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Interactive agent variant switcher for lens.core")
    parser.add_argument(
        "--workspace-root",
        default=str(SCRIPT_DIR.parent),
        help="Path to workspace root (default: parent of script dir)",
    )
    args = parser.parse_args()

    print()
    print_header("Agent Selector \u2014 lens.core")
    print()
    print(f"  Workspace root : {args.workspace_root}")
    print(f"  Manifest       : {MANIFEST}")
    print(f"  Submodule name : {SUBMODULE_NAME}")
    print()

    if not MANIFEST.exists():
        print_err(f"Manifest not found: {MANIFEST}")
        sys.exit(1)

    if not UPDATE_MANIFEST.exists():
        print_err(f"Python helper not found: {UPDATE_MANIFEST}")
        sys.exit(1)

    while True:
        print_header("How would you like to switch agents?")
        print()
        print("  1) Apply a theme package  (switch all agents to a theme at once)")
        print("  2) Switch individual agents")
        print("  3) Show current agent status")
        print("  4) Initialize active/  (run once after clone or to reset)")
        print("  5) Exit")
        print()

        choice = input("Choose [1-5]: ").strip()

        if choice == "1":
            print()
            print_header("Available themes:")
            print()
            themes = list_themes()
            if not themes:
                print_warn(f"No themes found in {CUSTOM_AGENTS_DIR}")
                continue
            theme_items = [f"{t}  ({len(agents_in_theme(t))} agents)" for t in themes]
            idx = numbered_menu("Choose theme", theme_items)
            mode_apply_theme(themes[idx])
            break

        elif choice == "2":
            while True:
                mode_switch_individual()
                print()
                more = input("Switch another agent? [y/n]: ").strip().lower()
                if more not in ("y", "yes"):
                    break
            break

        elif choice == "3":
            mode_show_status()
            # Re-display the main menu
            continue

        elif choice == "4":
            mode_init()
            break

        elif choice == "5":
            print("Exiting.")
            sys.exit(0)

        else:
            print_err("Enter 1, 2, 3, 4, or 5")


if __name__ == "__main__":
    main()
