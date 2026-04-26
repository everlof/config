# Mac Setup

This repo captures the parts of this Mac that are useful after a fresh install: packages, dotfiles, git hooks, command-line utilities, Automator Services, and macOS defaults.

The current computer is treated as the source of truth, but secrets must stay out of git.

## Interactive Restore

For a fresh install, the recommended entry point is the interactive restore script:

```bash
cd ~/repo/config
./scripts/restore-interactive.sh
```

It walks through the restore flow one step at a time and asks before running each major action:

1. Show these instructions.
2. Install Xcode Command Line Tools.
3. Check whether Homebrew is installed and open <https://brew.sh> if needed.
4. Preview bootstrap changes with `./scripts/bootstrap.sh --dry-run`.
5. Restore dotfiles, Services, git hooks, and `~/bin` with `./scripts/bootstrap.sh`.
6. Check package restore status with `brew bundle check --file Brewfile --verbose`.
7. Restore Homebrew/App Store/editor/npm/pipx/Cargo packages with `./scripts/bootstrap.sh --packages`.
8. Apply macOS defaults with `./scripts/macos-defaults.sh`.
9. Create or open `~/.bash_profile.local` for private tokens and machine-specific values.

The bootstrap step is non-destructive: existing files are moved to `~/.config-bootstrap-backups/<timestamp>/` before repo-managed files are linked or copied.

## Manual Restore

Use this if you do not want the guided flow.

1. Install Xcode Command Line Tools:

   ```bash
   xcode-select --install
   ```

2. Install Homebrew from <https://brew.sh>.

3. Clone this repo:

   ```bash
   git clone git@github.com:everlof/config.git ~/repo/config
   cd ~/repo/config
   ```

4. Restore dotfiles, Services, git hooks, and `~/bin` utilities:

   ```bash
   ./scripts/bootstrap.sh
   ```

5. Restore Homebrew, App Store, VS Code, npm, pipx, and Cargo packages:

   ```bash
   ./scripts/bootstrap.sh --packages
   ```

6. Add private values to `~/.bash_profile.local`. Use [resources/bash_profile.local.example](resources/bash_profile.local.example) as the template.

7. Apply macOS preferences:

   ```bash
   ./scripts/macos-defaults.sh
   ```

## What Is Managed

- [Brewfile](Brewfile): Homebrew taps, formulae, casks, Mac App Store apps, VS Code extensions, and Cargo packages captured by `brew bundle dump`.
- [resources/bash_profile](resources/bash_profile): public shell setup, aliases, prompt, paths, and tool integration.
- [resources/gitconfig](resources/gitconfig): global Git defaults, aliases, hooks path, Git LFS, rerere, GitHub credential helpers.
- [resources/git-hooks](resources/git-hooks): global Git hooks.
- [resources/git-templates](resources/git-templates): hooks for newly initialized repos.
- [resources/bin](resources/bin): personal command-line utilities linked into `~/bin`.
- [resources/Services](resources/Services): Automator Services installed into `~/Library/Services`.
- [resources/vscode/extensions.txt](resources/vscode/extensions.txt): VS Code extension inventory.
- [resources/cursor/extensions.txt](resources/cursor/extensions.txt): Cursor extension inventory.
- [resources/npm/global-packages.txt](resources/npm/global-packages.txt): npm global packages not represented by Homebrew.
- [resources/pipx/apps.txt](resources/pipx/apps.txt): pipx apps.
- [resources/cargo/packages.txt](resources/cargo/packages.txt): cargo-installed package names.
- [resources/apps/applications.txt](resources/apps/applications.txt): observed `/Applications` inventory for apps not managed by Homebrew or the App Store.

## Updating From This Mac

Run:

```bash
./scripts/capture-current.sh
```

Then review the diff carefully before committing. This script intentionally captures package/tool inventories and safe script directories. It does not copy `~/.bash_profile` or `~/.gitconfig` automatically because those files can contain secrets or machine-specific paths that should be normalized first.

## Secrets

Do not commit tokens, private keys, cloud credentials, or project-specific secrets. Put them in:

```bash
~/.bash_profile.local
```

The managed [resources/bash_profile](resources/bash_profile) sources that file if it exists.

## Current Machine Notes

Observed on this Mac when refreshed:

- macOS `26.0.1`
- Homebrew prefix `/opt/homebrew`
- Shell `/bin/bash`
- Selected Xcode `/Applications/Xcode-26.1.1.app`
- Homebrew services started: `postgresql@17`, `tor`
