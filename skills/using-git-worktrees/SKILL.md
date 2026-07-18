---
name: using-git-worktrees
description: Use when starting feature work that needs isolation from current workspace or before executing implementation plans - creates isolated git worktrees with smart directory selection and safety verification
---
- prefer create git worktree at ./.worktrees/
- add .worktrees/ to .gitignore
- link large files to worktrees
