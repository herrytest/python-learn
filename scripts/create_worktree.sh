#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <branch-name> <path>"
  exit 1
fi

branch="$1"
path="$2"

git worktree add -b "$branch" "$path"
echo "Worktree created at $path on branch $branch"
