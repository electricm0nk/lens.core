"""
agent_selector_update_manifest.py — called by agent_selector.sh to update agent_manifest.md

Usage: python3 agent_selector_update_manifest.py <manifest_path> <agent_id> <new_theme> <new_variant>

Updates `active_theme` and `active_variant` fields for the specified agent,
and the corresponding row in the Active Agents quick-reference table.
"""
import sys
import re

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
