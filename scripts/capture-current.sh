#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$REPO_ROOT"

mkdir -p resources/git-hooks resources/git-templates/hooks resources/bin resources/vscode resources/cursor resources/npm resources/pipx resources/cargo resources/apps

if command -v brew >/dev/null 2>&1; then
  brew bundle dump --file="$REPO_ROOT/Brewfile" --force
  # `mas list` can report id 0 for non-restorable apps; keep those in the app inventory instead.
  sed -i '' '/id: 0/d' "$REPO_ROOT/Brewfile"
fi

if [ -d "$HOME/.git-hooks" ]; then
  cp "$HOME/.git-hooks"/* resources/git-hooks/ 2>/dev/null || true
  chmod +x resources/git-hooks/* 2>/dev/null || true
fi

if [ -d "$HOME/.git-templates/hooks" ]; then
  cp "$HOME/.git-templates/hooks"/* resources/git-templates/hooks/ 2>/dev/null || true
  chmod +x resources/git-templates/hooks/* 2>/dev/null || true
fi

if [ -d "$HOME/bin" ]; then
  cp "$HOME/bin"/* resources/bin/ 2>/dev/null || true
  chmod +x resources/bin/* 2>/dev/null || true
fi

command -v code >/dev/null 2>&1 && code --list-extensions | sort > resources/vscode/extensions.txt || true
command -v cursor >/dev/null 2>&1 && cursor --list-extensions | sort > resources/cursor/extensions.txt || true
command -v npm >/dev/null 2>&1 && npm list -g --depth=0 --parseable 2>/dev/null | tail -n +2 | sed 's#.*/node_modules/##' | sort > resources/npm/global-packages.txt || true
command -v pipx >/dev/null 2>&1 && pipx list --short 2>/dev/null | awk '{print $1}' | sort > resources/pipx/apps.txt || true
find /Applications -maxdepth 1 -name '*.app' -print | sed 's#^/Applications/##; s#.app$##' | sort > resources/apps/applications.txt || true

if command -v cargo >/dev/null 2>&1; then
  cargo install --list 2>/dev/null | awk '/^[^[:space:]].*:$/ { name=$1; sub(/ .*/, "", name); print name }' | sort > resources/cargo/packages.txt || true
fi

cat <<MSG
Captured current package/tool inventories and safe script directories.
Review changes before committing, especially resources/bin and generated Brewfile entries.
MSG
