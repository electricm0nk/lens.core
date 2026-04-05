"""
agent_selector_update_manifest.py — called by agent_selector.sh to update agent_manifest.md

Usage: python3 agent_selector_update_manifest.py <manifest_path> <agent_id> <new_theme> <new_variant>

Updates `active_theme` and `active_variant` fields for the specified agent,
the corresponding row in the Active Agents quick-reference table,
the Available Agents table in .github/copilot-instructions.md (persona/title/capabilities),
the displayName column in agent-manifest.csv and team default-party.csv files,
and the description field in .github/agents/*.agent.md files.
"""
import csv
import sys
import re
from pathlib import Path

manifest_path = sys.argv[1]
agent_id      = sys.argv[2]
new_theme     = sys.argv[3]
new_variant   = sys.argv[4]

with open(manifest_path, 'r') as f:
    content = f.read()

# Update active_theme in the YAML block for this agent
content = re.sub(
    r'(id: ' + re.escape(agent_id) + r'.*?active_theme: )\S+',
    r'\g<1>' + new_theme,
    content, count=1, flags=re.DOTALL
)

# Update active_variant in the YAML block for this agent
content = re.sub(
    r'(id: ' + re.escape(agent_id) + r'.*?active_variant: )\S+',
    r'\g<1>' + new_variant,
    content, count=1, flags=re.DOTALL
)

# Update quick-reference table: match the row by agent_id in column 1,
# then replace columns 3 (Active Theme) and 4 (Active Variant) in place.
# Table row format: | agent_id  | module  | active_theme | active_variant |
def replace_table_row(m):
    col1, col2 = m.group(1), m.group(2)
    # Preserve column widths from original
    w3 = max(len(new_theme), len(m.group(3).strip()))
    w4 = max(len(new_variant), len(m.group(4).strip()))
    return f'| {col1}| {col2}| {new_theme.ljust(w3)} | {new_variant.ljust(w4)} |'

content = re.sub(
    r'\| (' + re.escape(agent_id) + r'\s+)\| ([^|]+)\| ([^|]+)\| ([^|]+)\|',
    replace_table_row,
    content
)

with open(manifest_path, 'w') as f:
    f.write(content)

# ---------------------------------------------------------------------------
# Update Available Agents table in .github/copilot-instructions.md
# Derive control repo root: manifest is in lens.core/_bmad/custom_agents/,
# so we go: manifest -> custom_agents -> _bmad -> lens.core -> control repo
# ---------------------------------------------------------------------------
manifest_file = Path(manifest_path).resolve()
repo_root     = manifest_file.parent.parent.parent.parent   # control repo (parent of lens.core)
active_file   = manifest_file.parent / "active" / f"{agent_id}.md"
ci_file       = repo_root / ".github" / "copilot-instructions.md"

if active_file.exists():
    agent_content = active_file.read_text(encoding="utf-8")

    # Parse name, title, capabilities from the <agent> XML opening tag
    agent_tag_m = re.search(r'<agent\s([^>]*)>', agent_content, re.DOTALL)
    if agent_tag_m:
        tag_attrs = agent_tag_m.group(1)
        name_m  = re.search(r'name="([^"]*)"',         tag_attrs)
        title_m = re.search(r'title="([^"]*)"',        tag_attrs)
        caps_m  = re.search(r'capabilities="([^"]*)"', tag_attrs)

        new_persona = name_m.group(1)  if name_m  else None
        new_title   = title_m.group(1) if title_m else None
        new_caps    = caps_m.group(1)  if caps_m  else None

        if new_persona and new_title and new_caps:
            def update_available_agents_table(ci_path: Path) -> None:
                if not ci_path.exists():
                    return

                ci_content = ci_path.read_text(encoding="utf-8")
                lines = ci_content.splitlines(keepends=True)

                # Find and replace the row for this agent
                new_lines = []
                for line in lines:
                    # Match: | agent_id | ... | ... | ... |
                    if line.strip().startswith(f"| {agent_id} |") or line.strip().startswith(f"|{agent_id}|"):
                        parts = [p.strip() for p in line.split("|")]
                        # parts[1] is agent_id, parts[2] persona, parts[3] title, parts[4] capabilities
                        if len(parts) >= 5:
                            new_line = f"| {parts[1]} | {new_persona} | {new_title} | {new_caps} |\n"
                            new_lines.append(new_line)
                        else:
                            new_lines.append(line)
                    else:
                        new_lines.append(line)

                new_ci = "".join(new_lines)
                if new_ci != ci_content:
                    ci_path.write_text(new_ci, encoding="utf-8")

            # Keep both potential instruction files in sync:
            # - control repo root
            # - lens.core repo root
            ci_candidates = [
                repo_root / ".github" / "copilot-instructions.md",
                manifest_file.parent.parent.parent / ".github" / "copilot-instructions.md",
            ]
            seen = set()
            for ci_path in ci_candidates:
                resolved = str(ci_path.resolve())
                if resolved in seen:
                    continue
                seen.add(resolved)
                update_available_agents_table(ci_path)

            # ---------------------------------------------------------------
            # Update .github/agents/*.agent.md description (VS Code reads
            # agent personas from these files, not copilot-instructions.md)
            # ---------------------------------------------------------------
            new_desc = f"{new_persona} — {new_title}: {new_caps}"

            # lens.core submodule root (parent of _bmad)
            lens_core_root = manifest_file.parent.parent.parent

            # Both locations that may contain .agent.md files
            agent_dirs = [
                repo_root / ".github" / "agents",
                lens_core_root / ".github" / "agents",
            ]

            # Agent file naming: *-{agent_id}.agent.md
            suffix = f"-{agent_id}.agent.md"

            for agents_dir in agent_dirs:
                if not agents_dir.is_dir():
                    continue
                for agent_file in agents_dir.iterdir():
                    if agent_file.name.endswith(suffix):
                        af_content = agent_file.read_text(encoding="utf-8")
                        # Replace the description in YAML frontmatter
                        af_content = re.sub(
                            r"(?m)^(description:\s*)['\"]?.*?['\"]?\s*$",
                            r"\g<1>'" + new_desc.replace("'", "''") + "'",
                            af_content, count=1
                        )
                        agent_file.write_text(af_content, encoding="utf-8")

            # ---------------------------------------------------------------
            # Update CSV manifests from active agent file (skip-worktree)
            # Parse full persona from XML elements in the active file so
            # the CSVs stay in sync with whatever theme is active locally.
            # ---------------------------------------------------------------
            def parse_xml_element(text: str, tag: str) -> str | None:
                """Extract text content from <tag>...</tag> (may be multiline)."""
                m = re.search(
                    rf"<{re.escape(tag)}>(.*?)</{re.escape(tag)}>",
                    text, re.DOTALL,
                )
                return " ".join(m.group(1).split()) if m else None

            persona_fields = {
                "displayName": new_persona,
                "title":       new_title,
                "icon":        re.search(r'icon="([^"]*)"', tag_attrs).group(1)
                               if re.search(r'icon="([^"]*)"', tag_attrs) else None,
                "capabilities": new_caps,
                "role":        parse_xml_element(agent_content, "role"),
                "identity":    parse_xml_element(agent_content, "identity"),
                "communicationStyle":
                               parse_xml_element(agent_content, "communication_style"),
                "principles":  parse_xml_element(agent_content, "principles"),
            }

            bmad_root = manifest_file.parent.parent  # lens.core/_bmad/

            csv_files = [
                bmad_root / "_config" / "agent-manifest.csv",
                bmad_root / "bmm" / "teams" / "default-party.csv",
                bmad_root / "cis" / "teams" / "default-party.csv",
            ]

            for csv_path in csv_files:
                if not csv_path.exists():
                    continue
                with open(csv_path, "r", newline="", encoding="utf-8") as cf:
                    reader = csv.DictReader(cf)
                    fieldnames = reader.fieldnames
                    rows = list(reader)

                changed = False
                for row in rows:
                    if row["name"] != agent_id:
                        continue
                    for key, val in persona_fields.items():
                        if val is not None and key in row and row[key] != val:
                            row[key] = val
                            changed = True

                if changed:
                    with open(csv_path, "w", newline="", encoding="utf-8") as cf:
                        writer = csv.DictWriter(cf, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
                        writer.writeheader()
                        writer.writerows(rows)
