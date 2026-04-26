#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

ask() {
  local prompt=$1
  local answer
  while true; do
    printf '%s [y/n]: ' "$prompt"
    read -r answer
    case "$answer" in
      y|Y|yes|YES) return 0 ;;
      n|N|no|NO) return 1 ;;
      *) echo "Please answer y or n." ;;
    esac
  done
}

run_step() {
  local title=$1
  shift
  echo
  echo "==> $title"
  printf '+ '
  printf '%q ' "$@"
  printf '\n'
  if ask "Run this step?"; then
    "$@"
  else
    echo "Skipped: $title"
  fi
}

open_private_profile() {
  local file="$HOME/.bash_profile.local"
  if [ ! -e "$file" ]; then
    cp "$REPO_ROOT/resources/bash_profile.local.example" "$file"
  fi

  if command -v code >/dev/null 2>&1; then
    code "$file"
  elif command -v open >/dev/null 2>&1; then
    open -a TextEdit "$file"
  else
    ${EDITOR:-vi} "$file"
  fi
}

cat <<INTRO
Interactive Mac restore

This script walks through the fresh-install restore flow one step at a time.
It is safe to skip steps. The bootstrap step backs up existing files before
linking repo-managed files.

Repo: $REPO_ROOT
INTRO

if ask "Show the restore README section first?"; then
  sed -n '/^## Interactive Restore/,/^## What Is Managed/p' README.md | sed '$d'
fi

run_step "Install Xcode Command Line Tools" xcode-select --install

if ! command -v brew >/dev/null 2>&1; then
  echo
  echo "Homebrew is not installed. Install it from https://brew.sh before package restore."
  if ask "Open Homebrew website?"; then
    open https://brew.sh
  fi
else
  echo
  echo "Homebrew found: $(command -v brew)"
fi

run_step "Preview bootstrap changes" ./scripts/bootstrap.sh --dry-run
run_step "Restore dotfiles, Services, git hooks, and ~/bin" ./scripts/bootstrap.sh

if command -v brew >/dev/null 2>&1; then
  run_step "Check package restore status" brew bundle check --file "$REPO_ROOT/Brewfile" --verbose
  run_step "Restore packages, apps, and editor/tool inventories" ./scripts/bootstrap.sh --packages
else
  echo
  echo "Skipping package restore because Homebrew is not installed."
fi

run_step "Apply macOS defaults" ./scripts/macos-defaults.sh

if ask "Create/open ~/.bash_profile.local for private tokens and machine-specific values?"; then
  open_private_profile
fi

cat <<OUTRO

Restore walkthrough complete.

If this is a fresh Mac, remaining manual checks are usually:
- Sign in to App Store if any mas installs failed.
- Sign in to GitHub CLI: gh auth login
- Restore SSH keys or create new ones.
- Install/select Xcode if it was not restored by package tools.
- Restart Terminal so the managed shell profile is loaded.
OUTRO
