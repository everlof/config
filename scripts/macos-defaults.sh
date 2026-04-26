#!/usr/bin/env bash
set -euo pipefail

# Defaults observed on this machine in April 2026.
defaults write com.apple.dock autohide -bool true
defaults write com.apple.dock autohide-delay -float 0
defaults write com.apple.dock autohide-time-modifier -float 0
defaults write com.apple.finder AppleShowAllFiles -bool true
defaults write NSGlobalDomain AppleShowAllExtensions -bool true

killall Dock 2>/dev/null || true
killall Finder 2>/dev/null || true
