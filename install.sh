#!/usr/bin/env bash
# Wire this skills library into every agent tool on this machine.
#
#   ./install.sh              install exactly what skills.txt lists; prune anything stale
#   ./install.sh --dry-run    show what would change, change nothing
#   ./install.sh --vendor     git pull the vendored third-party repos first
#
# skills.txt is the single source of truth. Add or remove a line there and re-run; anything
# previously linked from this library that is no longer listed gets unlinked. Editing a skill's
# files takes effect immediately in every tool (they're symlinks) with no re-run needed.
set -uo pipefail

LIB="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="$LIB/skills.txt"
DRY=0; VENDOR=0
for a in "$@"; do
  [ "$a" = "--dry-run" ] && DRY=1
  [ "$a" = "--vendor" ]  && VENDOR=1
done

say() { printf '%s\n' "$*"; }
run() { if [ "$DRY" = 1 ]; then say "    would: $*"; else "$@"; fi; }

CANDIDATES=(
  "$HOME/.claude"
  "$HOME/.claude-work"
  "$HOME/.claude-personal"
  "$HOME/.codex"
  "$HOME/.cursor"
)

[ -f "$MANIFEST" ] || { say "no skills.txt found at $MANIFEST"; exit 1; }

# ---- vendored sources, fetched BEFORE the manifest is resolved --------------
# A fresh clone has no vendor/ at all (it's gitignored). If resolution ran first, every
# emil:/mattpocock:/superpowers: line would fail with "no SKILL.md" and silently vanish,
# leaving only own: skills installed. Auto-fetch whatever's missing even without --vendor;
# --vendor additionally pulls what's already there to pick up upstream changes.
vendor_pull() {
  local dir="$1" url="$2" name="$3"
  if [ -d "$dir/.git" ]; then
    if [ "$VENDOR" = 1 ]; then
      say "  updating vendor/$name"; run git -C "$dir" pull --quiet --ff-only
    fi
  else
    say "  cloning vendor/$name (first run)"; run mkdir -p "$(dirname "$dir")"
    run git clone --quiet --depth 1 "$url" "$dir"
  fi
}
if grep -qE '^emil:' "$MANIFEST"; then
  vendor_pull "$LIB/vendor/emilkowalski" https://github.com/emilkowalski/skills.git emilkowalski
fi
if grep -qE '^mattpocock:' "$MANIFEST"; then
  vendor_pull "$LIB/vendor/mattpocock" https://github.com/mattpocock/skills.git mattpocock
fi
if grep -qE '^superpowers:' "$MANIFEST"; then
  vendor_pull "$LIB/vendor/superpowers" https://github.com/obra/superpowers.git superpowers
fi
say ""

# ---- resolve the manifest into "name -> source path" ------------------------
declare -a NAMES=() PATHS=()
while IFS= read -r line; do
  line="${line%%#*}"; line="$(printf '%s' "$line" | tr -d '[:space:]')"
  [ -z "$line" ] && continue
  kind="${line%%:*}"; ref="${line#*:}"
  case "$kind" in
    own)        src="$LIB/skills/$ref" ;;
    emil)       src="$LIB/vendor/emilkowalski/skills/$ref" ;;
    mattpocock) src="$LIB/vendor/mattpocock/skills/$ref" ;;
    superpowers) src="$LIB/vendor/superpowers/skills/$ref" ;;
    *) say "  ?? unknown source '$kind' in skills.txt - skipping"; continue ;;
  esac
  if [ ! -f "$src/SKILL.md" ]; then
    say "  !! $line -> no SKILL.md at $src (vendor fetch may have failed - check network/git)"
    continue
  fi
  NAMES+=("$(basename "$ref")"); PATHS+=("$src")
done < "$MANIFEST"

# ---- slash-command wrappers, one per installed skill ------------------------
[ -d "$LIB/commands" ] || run mkdir -p "$LIB/commands"
if [ "$DRY" = 0 ]; then
  # drop wrappers for skills no longer in the manifest
  for f in "$LIB"/commands/*.md; do
    [ -e "$f" ] || continue
    keep=0
    for n in "${NAMES[@]}"; do [ "$(basename "$f" .md)" = "$n" ] && keep=1; done
    [ "$keep" = 0 ] && { rm "$f"; say "  removed stale command $(basename "$f")"; }
  done
  for i in "${!NAMES[@]}"; do
    desc="$(sed -n 's/^description: *//p' "${PATHS[$i]}/SKILL.md" | head -1)"
    cat > "$LIB/commands/${NAMES[$i]}.md" <<EOF
---
description: ${desc:-Invoke the ${NAMES[$i]} skill.}
---

Use the \`${NAMES[$i]}\` skill for this request. Read its SKILL.md in full and follow it exactly.

\$ARGUMENTS
EOF
  done
fi

# ---- link + prune per tool --------------------------------------------------
link_one() {
  local dest_dir="$1" src="$2" name="$3"
  local dest="$dest_dir/$name"
  [ -d "$dest_dir" ] || run mkdir -p "$dest_dir"
  if [ -L "$dest" ]; then
    [ "$(readlink "$dest")" = "$src" ] && { say "    ok      $name"; return; }
    run rm "$dest"
  elif [ -e "$dest" ]; then
    say "    SKIP    $name  (real file/dir there - not touching)"; return
  fi
  run ln -s "$src" "$dest"; say "    linked  $name"
}

prune() {
  local dir="$1"
  [ -d "$dir" ] || return 0
  for f in "$dir"/*; do
    [ -L "$f" ] || continue
    local tgt; tgt="$(readlink "$f")"
    case "$tgt" in "$LIB"/*) ;; *) continue ;; esac      # only ours
    local base; base="$(basename "$f")"; base="${base%.md}"
    local keep=0
    for n in "${NAMES[@]}"; do [ "$base" = "$n" ] && keep=1; done
    [ "$keep" = 0 ] && { run rm "$f"; say "    pruned  $(basename "$f")"; }
  done
}

found=0
for root in "${CANDIDATES[@]}"; do
  [ -d "$root" ] || continue
  found=$((found+1))
  say "  $root"
  case "$root" in *codex*) cmd_kind="prompts" ;; *) cmd_kind="commands" ;; esac
  prune "$root/skills"
  prune "$root/$cmd_kind"
  for i in "${!NAMES[@]}"; do link_one "$root/skills" "${PATHS[$i]}" "${NAMES[$i]}"; done
  for i in "${!NAMES[@]}"; do
    link_one "$root/$cmd_kind" "$LIB/commands/${NAMES[$i]}.md" "${NAMES[$i]}.md"
  done
  say ""
done

# ---- inject the shared CLAUDE.md / AGENTS.md block --------------------------
# Between the tashon-skills:begin/end markers only. Everything else in the file (RunPod notes,
# personal hard rules, whatever) is untouched. First run appends the block; every later run
# replaces just what's between the markers, so editing the fragment updates every machine.
inject_block() {
  local file="$1"
  local frag="$LIB/templates/claude-md-fragment.md"
  [ -f "$frag" ] || { say "    !! no fragment at $frag - skipping block"; return; }

  if [ "$DRY" = 1 ]; then
    say "    would: update tashon-skills block in $file"
    return
  fi

  [ -d "$(dirname "$file")" ] || mkdir -p "$(dirname "$file")"
  [ -f "$file" ] || touch "$file"

  local orig_bytes; orig_bytes=$(wc -c < "$file" | tr -d ' ')
  local tmp; tmp="$(mktemp)"
  local rendered; rendered="$(mktemp)"
  # __COUNT__ -> real installed count. sed on a FILE, never through a shell variable:
  # passing a multi-line block via `awk -v` fails outright on BSD awk ("newline in string"),
  # which previously produced an empty temp file and truncated real instruction files to 0 bytes.
  sed "s/__COUNT__/${#NAMES[@]}/g" "$frag" > "$rendered"

  local begin_line end_line
  begin_line=$(grep -n '<!-- tashon-skills:begin -->' "$file" 2>/dev/null | head -1 | cut -d: -f1)
  end_line=$(grep -n '<!-- tashon-skills:end -->' "$file" 2>/dev/null | head -1 | cut -d: -f1)

  if [ -n "$begin_line" ] && [ -n "$end_line" ] && [ "$end_line" -gt "$begin_line" ]; then
    # everything before the block, the fresh block, everything after
    head -n $((begin_line - 1)) "$file" > "$tmp"
    cat "$rendered" >> "$tmp"
    tail -n +$((end_line + 1)) "$file" >> "$tmp"
    local verb="updated"
  else
    cat "$file" > "$tmp"
    [ "$orig_bytes" -gt 0 ] && echo "" >> "$tmp"
    cat "$rendered" >> "$tmp"
    local verb="added"
  fi

  # Safety gate: never let a smaller-than-the-block result overwrite real content.
  # This is the check whose absence destroyed a populated CLAUDE.md.
  local new_bytes frag_bytes
  new_bytes=$(wc -c < "$tmp" | tr -d ' ')
  frag_bytes=$(wc -c < "$rendered" | tr -d ' ')
  if [ "$new_bytes" -lt "$frag_bytes" ] || { [ "$orig_bytes" -gt 0 ] && [ "$new_bytes" -lt "$orig_bytes" ]; }; then
    say "    !! refusing to write $(basename "$file"): result ${new_bytes}b < original ${orig_bytes}b. Left untouched."
    rm -f "$tmp" "$rendered"
    return 1
  fi

  [ "$orig_bytes" -gt 0 ] && cp "$file" "$file.tashon-skills.bak"
  mv "$tmp" "$file"
  rm -f "$rendered"
  say "    $verb tashon-skills block in $(basename "$file")"
}

for root in "${CANDIDATES[@]}"; do
  [ -d "$root" ] || continue
  if [ "$(basename "$root")" = ".codex" ]; then
    inject_block "$root/AGENTS.md"
  else
    inject_block "$root/CLAUDE.md"
  fi
done
say ""

[ "$found" = 0 ] && { say "  no agent tool configs found"; exit 1; }
say "done. ${#NAMES[@]} skill(s) across $found tool config(s)."
