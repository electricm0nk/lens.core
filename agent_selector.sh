#!/usr/bin/env bash
# agent_selector.sh — Interactive agent variant switcher for lens.core
#
# Reads agent_manifest.md, prompts user to switch by theme (package) or
# individual agent, then updates all pointer files and the manifest.
#
# Usage: ./agent_selector.sh [--workspace-root /path/to/workspace]

set -euo pipefail

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="${SCRIPT_DIR}/_bmad/custom_agents/agent_manifest.md"
CUSTOM_AGENTS_DIR="${SCRIPT_DIR}/_bmad/custom_agents"

# Workspace root: the parent of the lens.core directory by default,
# but can be overridden to handle the case where lens.core is used standalone.
WORKSPACE_ROOT="$(dirname "${SCRIPT_DIR}")"

# Parse optional --workspace-root argument
while [[ $# -gt 0 ]]; do
  case "$1" in
    --workspace-root)
      WORKSPACE_ROOT="$2"
      shift 2
      ;;
    *)
      echo "Unknown argument: $1" >&2
      exit 1
      ;;
  esac
done

# Submodule name (basename of lens.core dir, used to strip path prefix from
# pointer_file paths that start with "lens.core/...")
SUBMODULE_NAME="$(basename "${SCRIPT_DIR}")"

# ---------------------------------------------------------------------------
# Color helpers (no-op if stdout is not a TTY)
# ---------------------------------------------------------------------------
if [[ -t 1 ]]; then
  BOLD="\033[1m"
  CYAN="\033[1;36m"
  GREEN="\033[1;32m"
  YELLOW="\033[1;33m"
  RED="\033[1;31m"
  RESET="\033[0m"
else
  BOLD="" CYAN="" GREEN="" YELLOW="" RED="" RESET=""
fi

print_header() { echo -e "${CYAN}${BOLD}$*${RESET}"; }
print_ok()     { echo -e "${GREEN}  ✓ $*${RESET}"; }
print_warn()   { echo -e "${YELLOW}  ⚠ $*${RESET}"; }
print_err()    { echo -e "${RED}  ✗ $*${RESET}"; }

# ---------------------------------------------------------------------------
# Manifest parsing helpers
# ---------------------------------------------------------------------------

# Extract the value of a YAML key from a block for this agent
#   $1 = agent-id, $2 = key
get_agent_field() {
  local agent_id="$1" key="$2"
  local in_block=0
  while IFS= read -r line; do
    if [[ $in_block -eq 0 && "${line}" == "id: ${agent_id}" ]]; then
      in_block=1
      continue
    fi
    if [[ $in_block -eq 1 ]]; then
      [[ "${line}" == '```' ]] && break
      if [[ "${line}" =~ ^${key}:[[:space:]]*(.*) ]]; then
        # Strip surrounding quotes if present
        local val="${BASH_REMATCH[1]}"
        val="${val#\"}" ; val="${val%\"}"
        val="${val#\'}" ; val="${val%\'}"
        echo "${val}"
        return
      fi
    fi
  done < "${MANIFEST}"
}

# List all agent IDs from the manifest (excludes lens which is not theme-able)
list_agent_ids() {
  grep -E "^id: " "${MANIFEST}" | sed 's/^id: //' | grep -v '^lens$'
}

# List all theme names (subdirectory names under custom_agents that have .md files)
list_themes() {
  local themes=()
  for d in "${CUSTOM_AGENTS_DIR}"/*/; do
    [[ -d "$d" ]] || continue
    local name
    name="$(basename "$d")"
    [[ "${name}" == "active" ]] && continue  # skip the gitignored dir
    if ls "${d}"*.md &>/dev/null 2>&1; then
      themes+=("$name")
    fi
  done
  printf '%s\n' "${themes[@]}"
}

# Given a theme dir and an agent-id, find the matching variant file basename
# Convention: files are named {agent-id}_{character}.md
find_variant_for_agent() {
  local theme_dir="$1" agent_id="$2"
  local f
  for f in "${theme_dir}"/${agent_id}_*.md; do
    [[ -f "$f" ]] && basename "$f" && return 0
  done
  echo ""
}

# Return the default_file for an agent (canonical module path)
get_default_file() {
  local agent_id="$1"
  get_agent_field "${agent_id}" "default_file"
}

# Return current active_theme for an agent
get_active_theme() {
  local agent_id="$1"
  get_agent_field "${agent_id}" "active_theme"
}

# Return current active_variant for an agent
get_active_variant() {
  local agent_id="$1"
  get_agent_field "${agent_id}" "active_variant"
}

# Return the source path for an agent given theme+variant
# All themes (including "default") live in _bmad/custom_agents/{theme}/{variant}
resolve_source_path() {
  local theme="$2" variant="$3"
  echo "_bmad/custom_agents/${theme}/${variant}"
}

# ---------------------------------------------------------------------------
# Python helper for manifest field updates
# Called as: python3 "$UPDATE_MANIFEST_PY" manifest agent_id new_theme new_variant
# ---------------------------------------------------------------------------
UPDATE_MANIFEST_PY="${SCRIPT_DIR}/agent_selector_update_manifest.py"

# Active directory — gitignored, populated by apply_switch and mode_init
ACTIVE_DIR="${SCRIPT_DIR}/_bmad/custom_agents/active"

# ---------------------------------------------------------------------------
# Apply a switch for a single agent
#   $1 = agent-id
#   $2 = new_theme  ("default" or theme name)
#   $3 = new_variant  (basename of the file, e.g. "architect_perturabo.md")
# ---------------------------------------------------------------------------
apply_switch() {
  local agent_id="$1" new_theme="$2" new_variant="$3"

  local cur_theme cur_variant
  cur_theme="$(get_active_theme "${agent_id}")"
  cur_variant="$(get_active_variant "${agent_id}")"

  if [[ "${cur_theme}" == "${new_theme}" && "${cur_variant}" == "${new_variant}" ]]; then
    print_warn "${agent_id}: already using ${new_theme}/${new_variant} — skipping"
    return 0
  fi

  # Resolve the source file to copy
  local src_rel src_abs
  src_rel="$(resolve_source_path "${agent_id}" "${new_theme}" "${new_variant}")"
  src_abs="${SCRIPT_DIR}/${src_rel}"

  if [[ ! -f "${src_abs}" ]]; then
    print_err "source file not found: ${src_rel}"
    return 1
  fi

  # Copy into active/ and mark skip-worktree so git doesn't show it as modified
  mkdir -p "${ACTIVE_DIR}"
  git -C "${SCRIPT_DIR}" update-index --no-skip-worktree "_bmad/custom_agents/active/${agent_id}.md" 2>/dev/null || true
  cp "${src_abs}" "${ACTIVE_DIR}/${agent_id}.md"
  git -C "${SCRIPT_DIR}" update-index --skip-worktree "_bmad/custom_agents/active/${agent_id}.md" 2>/dev/null || true

  echo -e "  ${BOLD}${agent_id}${RESET}: ${cur_theme}/${cur_variant} → ${new_theme}/${new_variant}"
  print_ok "${ACTIVE_DIR}/${agent_id}.md updated"

  # Update manifest fields
  python3 "${UPDATE_MANIFEST_PY}" "${MANIFEST}" "${agent_id}" "${new_theme}" "${new_variant}"
  print_ok "manifest updated for ${agent_id}"
}

# ---------------------------------------------------------------------------
# Interactive prompt helpers
# ---------------------------------------------------------------------------

# Numbered menu: prints list, returns chosen index (0-based) in $REPLY_IDX
# $1 = prompt text, rest = items
numbered_menu() {
  local prompt="$1"; shift
  local items=("$@")
  local i=1
  for item in "${items[@]}"; do
    printf "  %2d) %s\n" "$i" "$item"
    i=$(( i + 1 ))
  done
  echo ""
  while true; do
    read -r -p "${prompt}: " choice
    if [[ "$choice" =~ ^[0-9]+$ ]] && (( choice >= 1 && choice <= ${#items[@]} )); then
      REPLY_IDX=$(( choice - 1 ))
      return 0
    fi
    print_err "Invalid choice — enter a number between 1 and ${#items[@]}"
  done
}

# Yes/no prompt — returns 0 for yes, 1 for no
confirm() {
  local prompt="${1:-Continue?}"
  while true; do
    read -r -p "${prompt} [y/n]: " yn
    case "${yn,,}" in
      y|yes) return 0 ;;
      n|no)  return 1 ;;
      *) echo "  Enter y or n" ;;
    esac
  done
}

# ---------------------------------------------------------------------------
# Collect all agents that have a variant in a given theme
# Outputs lines: "agent-id|variant-basename"
agents_in_theme() {
  local theme="$1"
  local theme_dir="${CUSTOM_AGENTS_DIR}/${theme}"
  local agent_id
  while IFS= read -r agent_id; do
    local variant
    variant="$(find_variant_for_agent "${theme_dir}" "${agent_id}")"
    [[ -z "${variant}" ]] && continue
    echo "${agent_id}|${variant}"
  done < <(list_agent_ids)
}

# ---------------------------------------------------------------------------
# MODE 1: Apply entire theme as a package
# ---------------------------------------------------------------------------
mode_apply_theme() {
  local theme="$1"

  print_header "\nApplying theme package: ${theme}"
  echo ""

  local agent_id variant cur_theme cur_variant changes=()

  while IFS='|' read -r agent_id variant; do
    [[ -z "${agent_id}" ]] && continue
    cur_theme="$(get_active_theme "${agent_id}")"
    cur_variant="$(get_active_variant "${agent_id}")"
    if [[ "${cur_theme}" != "${theme}" || "${cur_variant}" != "${variant}" ]]; then
      changes+=("${agent_id}")
    fi
  done < <(agents_in_theme "${theme}")

  if [[ ${#changes[@]} -eq 0 ]]; then
    echo "  All agents are already using the '${theme}' theme."
    return 0
  fi

  echo "  The following agents will be switched to the '${theme}' theme:"
  local theme_dir="${CUSTOM_AGENTS_DIR}/${theme}"
  for a in "${changes[@]}"; do
    local cur_t cur_v new_var
    cur_t="$(get_active_theme "$a")"
    cur_v="$(get_active_variant "$a")"
    new_var="$(find_variant_for_agent "${theme_dir}" "$a")"
    echo "    ${a}: ${cur_t}/${cur_v} → ${theme}/${new_var}"
  done
  echo ""

  confirm "Apply these changes?" || { echo "  Aborted."; return 0; }

  echo ""
  for a in "${changes[@]}"; do
    local new_var
    new_var="$(find_variant_for_agent "${theme_dir}" "$a")"
    apply_switch "${a}" "${theme}" "${new_var}"
    echo ""
  done

  print_header "Theme '${theme}' applied successfully."
}

# ---------------------------------------------------------------------------
# MODE 2: Switch a single agent
# ---------------------------------------------------------------------------
mode_switch_individual() {
  # Step 1: pick the agent
  print_header "\nSelect an agent to switch:"
  echo ""
  local agent_ids=()
  while IFS= read -r id; do
    agent_ids+=("$id")
  done < <(list_agent_ids)

  # Annotate with current theme/variant
  local display_items=()
  for id in "${agent_ids[@]}"; do
    local cur_t cur_v
    cur_t="$(get_active_theme "$id")"
    cur_v="$(get_active_variant "$id")"
    display_items+=("${id}  (currently: ${cur_t}/${cur_v})")
  done

  numbered_menu "Choose agent" "${display_items[@]}"
  local chosen_agent="${agent_ids[$REPLY_IDX]}"

  # Step 2: build variant options for this agent
  echo ""
  print_header "Select a variant for '${chosen_agent}':"
  echo ""

  local variant_themes=() variant_variants=() variant_labels=()

  # One option per available theme (including "default")
  while IFS= read -r theme; do
    local theme_dir="${CUSTOM_AGENTS_DIR}/${theme}"
    local variant
    variant="$(find_variant_for_agent "${theme_dir}" "${chosen_agent}")"
    [[ -z "${variant}" ]] && continue

    variant_themes+=("${theme}")
    variant_variants+=("${variant}")
    variant_labels+=("[${theme}] ${variant%.md}  (${variant})")
  done < <(list_themes)

  # Mark current choice
  local cur_theme cur_variant
  cur_theme="$(get_active_theme "${chosen_agent}")"
  cur_variant="$(get_active_variant "${chosen_agent}")"
  local labeled_items=()
  for i in "${!variant_labels[@]}"; do
    if [[ "${variant_themes[$i]}" == "${cur_theme}" && "${variant_variants[$i]}" == "${cur_variant}" ]]; then
      labeled_items+=("${variant_labels[$i]}  ← current")
    else
      labeled_items+=("${variant_labels[$i]}")
    fi
  done

  numbered_menu "Choose variant" "${labeled_items[@]}"
  local new_theme="${variant_themes[$REPLY_IDX]}"
  local new_variant="${variant_variants[$REPLY_IDX]}"

  if [[ "${new_theme}" == "${cur_theme}" && "${new_variant}" == "${cur_variant}" ]]; then
    echo "  Already active — nothing to do."
    return 0
  fi

  echo ""
  confirm "Switch '${chosen_agent}' to '${new_theme}/${new_variant}'?" || { echo "  Aborted."; return 0; }
  echo ""
  apply_switch "${chosen_agent}" "${new_theme}" "${new_variant}"
  echo ""
  print_header "Done."
}

# ---------------------------------------------------------------------------
# MODE 3: Initialize active/ from current manifest state
# Run this once after cloning, or to reset to the committed manifest state.
# ---------------------------------------------------------------------------
mode_init() {
  print_header "\nInitializing active/ from manifest..."
  echo ""
  mkdir -p "${ACTIVE_DIR}"

  local agent_id
  while IFS= read -r agent_id; do
    local theme variant src_rel src_abs
    theme="$(get_active_theme "${agent_id}")"
    variant="$(get_active_variant "${agent_id}")"
    src_rel="$(resolve_source_path "${agent_id}" "${theme}" "${variant}")"
    src_abs="${SCRIPT_DIR}/${src_rel}"

    if [[ ! -f "${src_abs}" ]]; then
      print_warn "${agent_id}: source not found (${src_rel}) — skipping"
      continue
    fi

    git -C "${SCRIPT_DIR}" update-index --no-skip-worktree "_bmad/custom_agents/active/${agent_id}.md" 2>/dev/null || true
    cp "${src_abs}" "${ACTIVE_DIR}/${agent_id}.md"
    git -C "${SCRIPT_DIR}" update-index --skip-worktree "_bmad/custom_agents/active/${agent_id}.md" 2>/dev/null || true

    # Update manifest, copilot-instructions.md, and .agent.md files
    python3 "${UPDATE_MANIFEST_PY}" "${MANIFEST}" "${agent_id}" "${theme}" "${variant}"
    print_ok "${agent_id} → ${theme}/${variant}"
  done < <(list_agent_ids)

  # Hide local manifest changes from git status (active_theme/active_variant drift)
  git -C "${SCRIPT_DIR}" update-index --skip-worktree "_bmad/custom_agents/agent_manifest.md" 2>/dev/null || true
  print_ok "agent_manifest.md marked skip-worktree"

  # Hide CSV manifests from git status (persona data varies by active theme)
  local csv_file
  for csv_file in \
    "_bmad/_config/agent-manifest.csv" \
    "_bmad/bmm/teams/default-party.csv" \
    "_bmad/cis/teams/default-party.csv"; do
    git -C "${SCRIPT_DIR}" update-index --skip-worktree "${csv_file}" 2>/dev/null || true
  done
  print_ok "CSV manifests marked skip-worktree"

  echo ""
  print_header "active/ initialized. You're ready to go."
}

# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------
main() {
  echo ""
  print_header "Agent Selector — lens.core"
  echo ""
  echo "  Workspace root : ${WORKSPACE_ROOT}"
  echo "  Manifest       : ${MANIFEST}"
  echo "  Submodule name : ${SUBMODULE_NAME}"
  echo ""

  # Verify manifest exists
  if [[ ! -f "${MANIFEST}" ]]; then
    print_err "Manifest not found: ${MANIFEST}"
    exit 1
  fi

  # Verify Python helper exists
  if [[ ! -f "${UPDATE_MANIFEST_PY}" ]]; then
    print_err "Python helper not found: ${UPDATE_MANIFEST_PY}"
    exit 1
  fi

  print_header "How would you like to switch agents?"
  echo ""
  echo "  1) Apply a theme package  (switch all agents to a theme at once)"
  echo "  2) Switch individual agents"
  echo "  3) Show current agent status"
  echo "  4) Initialize active/  (run once after clone or to reset)"
  echo "  5) Exit"
  echo ""

  local choice
  while true; do
    read -r -p "Choose [1-5]: " choice
    case "$choice" in
      1)
        echo ""
        print_header "Available themes:"
        echo ""
        local themes=()
        while IFS= read -r t; do themes+=("$t"); done < <(list_themes)

        if [[ ${#themes[@]} -eq 0 ]]; then
          print_warn "No themes found in ${CUSTOM_AGENTS_DIR}"
          break
        fi

        # Show themes with agent count
        local theme_items=()
        for t in "${themes[@]}"; do
          local count
          count="$(agents_in_theme "$t" | wc -l | tr -d ' ')"
          theme_items+=("${t}  (${count} agents)")
        done

        numbered_menu "Choose theme" "${theme_items[@]}"
        mode_apply_theme "${themes[$REPLY_IDX]}"
        break
        ;;
      2)
        local more="y"
        while [[ "${more,,}" == "y" ]]; do
          mode_switch_individual
          echo ""
          read -r -p "Switch another agent? [y/n]: " more
        done
        break
        ;;
      3)
        echo ""
        print_header "Current agent assignments:"
        echo ""
        printf "  %-30s %-12s %s\n" "AGENT" "THEME" "VARIANT"
        printf "  %-30s %-12s %s\n" "-----" "-----" "-------"
        while IFS= read -r id; do
          local theme variant
          theme="$(get_active_theme "$id")"
          variant="$(get_active_variant "$id")"
          printf "  %-30s %-12s %s\n" "${id}" "${theme}" "${variant}"
        done < <(list_agent_ids)
        echo ""
        # Re-run main menu
        main
        return
        ;;
      4)
        mode_init
        break
        ;;
      5)
        echo "Exiting."
        exit 0
        ;;
      *)
        print_err "Enter 1, 2, 3, 4, or 5"
        ;;
    esac
  done
}

main
