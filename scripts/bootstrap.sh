#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
BACKUP_ROOT=${BACKUP_ROOT:-"$HOME/.config-bootstrap-backups/$(date +%Y%m%d-%H%M%S)"}
INSTALL_PACKAGES=0
DRY_RUN=0

usage() {
  cat <<USAGE
Usage: $0 [--packages] [--dry-run]

Installs repo-managed Mac setup files. Existing files are moved to:
  $BACKUP_ROOT

Options:
  --packages  Run Homebrew bundle and restore npm/pipx/cargo/VS Code/Cursor package lists.
  --dry-run   Print actions without changing files.
USAGE
}

while [ $# -gt 0 ]; do
  case "$1" in
    --packages) INSTALL_PACKAGES=1 ;;
    --dry-run) DRY_RUN=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown argument: $1" >&2; usage; exit 2 ;;
  esac
  shift
done

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '+'
    printf ' %q' "$@"
    printf '\n'
  else
    "$@"
  fi
}

backup_path() {
  local target=$1
  [ -e "$target" ] || [ -L "$target" ] || return 0

  local rel backup
  rel=${target#"$HOME"/}
  backup="$BACKUP_ROOT/$rel"
  run mkdir -p "$(dirname "$backup")"
  run mv "$target" "$backup"
  echo "Backed up $target -> $backup"
}

same_symlink() {
  local link=$1 src=$2
  [ -L "$link" ] && [ "$(readlink "$link")" = "$src" ]
}

link_file() {
  local src=$1 dst=$2
  run mkdir -p "$(dirname "$dst")"
  if same_symlink "$dst" "$src"; then
    echo "Already linked $dst"
    return 0
  fi
  backup_path "$dst"
  run ln -s "$src" "$dst"
  echo "Linked $dst -> $src"
}

copy_tree() {
  local src=$1 dst=$2
  run mkdir -p "$(dirname "$dst")"
  backup_path "$dst"
  run cp -R "$src" "$dst"
  echo "Copied $dst"
}

copy_if_missing() {
  local src=$1 dst=$2
  if [ -e "$dst" ]; then
    echo "Keeping existing $dst"
    return 0
  fi
  run mkdir -p "$(dirname "$dst")"
  run cp "$src" "$dst"
  echo "Created $dst"
}

install_dotfiles() {
  link_file "$REPO_ROOT/resources/bash_profile" "$HOME/.bash_profile"
  copy_if_missing "$REPO_ROOT/resources/bash_profile.local.example" "$HOME/.bash_profile.local"
  link_file "$REPO_ROOT/resources/gitconfig" "$HOME/.gitconfig"
  link_file "$REPO_ROOT/resources/.gitignore_global" "$HOME/.gitignore_global"
  link_file "$REPO_ROOT/resources/stCommitMsg" "$HOME/.stCommitMsg"
  link_file "$REPO_ROOT/resources/DefaultKeyBinding.dict" "$HOME/Library/KeyBindings/DefaultKeyBinding.dict"
}

install_services() {
  run mkdir -p "$HOME/Library/Services"
  find "$REPO_ROOT/resources/Services" -maxdepth 1 -name '*.workflow' -print | while IFS= read -r service; do
    copy_tree "$service" "$HOME/Library/Services/$(basename "$service")"
  done
}

install_git_hooks() {
  run mkdir -p "$HOME/.git-hooks" "$HOME/.git-templates/hooks"
  find "$REPO_ROOT/resources/git-hooks" -maxdepth 1 -type f -print | while IFS= read -r hook; do
    link_file "$hook" "$HOME/.git-hooks/$(basename "$hook")"
  done
  find "$REPO_ROOT/resources/git-templates/hooks" -maxdepth 1 -type f -print | while IFS= read -r hook; do
    link_file "$hook" "$HOME/.git-templates/hooks/$(basename "$hook")"
  done
}

install_bin() {
  run mkdir -p "$HOME/bin"
  find "$REPO_ROOT/resources/bin" -maxdepth 1 -type f -print | while IFS= read -r binfile; do
    link_file "$binfile" "$HOME/bin/$(basename "$binfile")"
  done
}

install_packages() {
  if ! command -v brew >/dev/null 2>&1; then
    echo "Homebrew not found; install it first, then rerun $0 --packages" >&2
    return 1
  fi

  run brew bundle --file "$REPO_ROOT/Brewfile"

  if command -v npm >/dev/null 2>&1 && [ -s "$REPO_ROOT/resources/npm/global-packages.txt" ]; then
    while IFS= read -r pkg; do
      [ -n "$pkg" ] && run npm install -g "$pkg"
    done < "$REPO_ROOT/resources/npm/global-packages.txt"
  fi

  if command -v pipx >/dev/null 2>&1 && [ -s "$REPO_ROOT/resources/pipx/apps.txt" ]; then
    while IFS= read -r app; do
      [ -n "$app" ] && run pipx install "$app" || true
    done < "$REPO_ROOT/resources/pipx/apps.txt"
  fi

  if command -v cargo >/dev/null 2>&1 && [ -s "$REPO_ROOT/resources/cargo/packages.txt" ]; then
    while IFS= read -r crate; do
      [ -n "$crate" ] && run cargo install "$crate" || true
    done < "$REPO_ROOT/resources/cargo/packages.txt"
  fi

  if command -v code >/dev/null 2>&1 && [ -s "$REPO_ROOT/resources/vscode/extensions.txt" ]; then
    while IFS= read -r ext; do
      [ -n "$ext" ] && run code --install-extension "$ext" || true
    done < "$REPO_ROOT/resources/vscode/extensions.txt"
  fi

  if command -v cursor >/dev/null 2>&1 && [ -s "$REPO_ROOT/resources/cursor/extensions.txt" ]; then
    while IFS= read -r ext; do
      [ -n "$ext" ] && run cursor --install-extension "$ext" || true
    done < "$REPO_ROOT/resources/cursor/extensions.txt"
  fi
}

install_dotfiles
install_services
install_git_hooks
install_bin

if [ "$INSTALL_PACKAGES" -eq 1 ]; then
  install_packages
fi

echo "Bootstrap complete. Backups, if any, are under: $BACKUP_ROOT"
