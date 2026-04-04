"""
agent_selector_update_manifest.py — called by agent_selector.sh to update agent_manifest.md

Usage: python3 agent_selector_update_manifest.py <manifest_path> <agent_id> <new_theme> <new_variant>

Updates `active_theme` and `active_variant` fields for the specified agent,
the corresponding row in the Active Agents quick-reference table,
and the Available Agents table in .github/copilot-instructions.md (persona/title/capabilities).
"""
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

if active_file.exists() and ci_file.exists():
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

        if new_persona and new_title:
            ci_content = ci_file.read_text(encoding="utf-8")
            lines = ci_content.splitlines(keepends=True)
            
            # Find and replace the row for this agent
            new_lines = []
            for line in lines:
                # Match: | agent_id | ... | ... | ... |
                if line.strip().startswith(f"| {agent_id} |") or line.strip().startswith(f"|{agent_id}|"):
                    # Replace just the persona and title columns
                    # Parse the row: split by |, keep agent_id, replace columns 2 and 3
                    parts = [p.strip() for p in line.split("|")]
                    # parts[0] is empty (before first |)
                    # parts[1] is agent_id
                    # parts[2] is old persona
                    # parts[3] is old title
                    # parts[4] is capabilities
                    # parts[5] is empty (after last |)
                    if len(parts) >= 5:
                        new_line = f"| {parts[1]} | {new_persona} | {new_title} | {new_caps} |\n"
                        new_lines.append(new_line)
                    else:
                        new_lines.append(line)
                else:
                    new_lines.append(line)
            
            new_ci = "".join(new_lines)
            if new_ci != ci_content:
                ci_file.write_text(new_ci, encoding="utf-8")
