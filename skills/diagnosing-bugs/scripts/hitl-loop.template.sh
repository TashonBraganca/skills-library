#!/usr/bin/env bash
# Human-in-the-loop reproduction loop.
# Copy this file, edit the steps below, and run it.
# The agent runs the script; the user follows prompts in their terminal.
#
# Usage:
#   bash hitl-loop.template.sh
#
# Two helpers:
#   step "<instruction>"          → show instruction, wait for Enter
#   capture VAR "<question>"      → show question, read response into VAR
#
# At the end, captured values are printed as KEY=VALUE for the agent to parse.
#
# `capture` prints its value back to the terminal, where the agent reads it,
# so capture observations, and leave signing in to the user as a `step`.

set -euo pipefail

step() {
  printf '\n>>> %s\n' "$1"
  IFS= read -r -p "    [Enter when done] " _ || { echo "INCOMPLETE: input ended"; exit 3; }
}

# capture VAR "question" [allowed values separated by |]
capture() {
  local var="$1" question="$2" allowed="${3:-}" answer
  while true; do
    printf '\n>>> %s\n' "$question"
    IFS= read -r -p "    > " answer || { echo "INCOMPLETE: input ended before $var was answered"; exit 3; }
    if [ -z "$answer" ]; then echo "    (an answer is required)"; continue; fi
    if [ -n "$allowed" ] && ! printf '%s' "$answer" | grep -Eqx "$allowed"; then
      echo "    (answer one of: $allowed)"; continue
    fi
    break
  done
  printf -v "$var" '%s' "$answer"
}

# --- edit below ---------------------------------------------------------

step "Open the app at http://localhost:3000 and sign in."

capture ERRORED "Click the 'Export' button. Did it throw an error? (y/n)" "y|n"

capture ERROR_MSG "Paste the error message (or 'none'):"

# --- edit above ---------------------------------------------------------

printf '\n--- Captured ---\n'
printf 'ERRORED=%s\n' "$ERRORED"
printf 'ERROR_MSG=%s\n' "$ERROR_MSG"
