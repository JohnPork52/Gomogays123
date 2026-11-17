---
name: github-connect
description: Use when the user provides a GitHub URL/ссылка or asks to connect to, clone, inspect, or work with a GitHub repository, profile, or organization. Handles public and private repositories without exposing tokens.
---

# GitHub connection

Use the user's GitHub URL as the source of truth. Never guess the repository
from the project name, and never substitute a different URL.

## 1. Confirm the target

Ask for the URL if it is missing. Recognize these forms:

- `https://github.com/owner/repo`
- `https://github.com/owner/repo.git`
- `git@github.com:owner/repo.git`
- `owner/repo`
- `https://github.com/owner` (profile)
- `https://github.com/orgs/org` (organization)

Determine whether the target is a repository, a user profile, or an
organization, and what the user wants to do: read, clone, modify, or use the
API. Ask before cloning into a non-empty directory.

## 2. Check the environment

```bash
git --version
command -v gh || true
test -n "$GITHUB_TOKEN$GH_TOKEN" && echo "token: present" || echo "token: absent"
```

Do not print token values.

## 3. Verify access

For a public repository:

```bash
git ls-remote "$URL" HEAD
```

For a private repository, prefer an authenticated `gh`:

```bash
gh auth status
gh repo clone owner/repo
```

If `gh` is unavailable but `GITHUB_TOKEN` or `GH_TOKEN` is set, use an askpass
helper so the token never appears in the command line:

```bash
ASKPASS=$(mktemp)
printf '%s\n' '#!/bin/sh' \
  'case "$1" in' \
  '  *Username*) printf "%s\n" "x-access-token" ;;' \
  '  *Password*) printf "%s\n" "$GITHUB_TOKEN" ;;' \
  'esac' > "$ASKPASS"
chmod 700 "$ASKPASS"
GIT_ASKPASS="$ASKPASS" GIT_TERMINAL_PROMPT=0 git ls-remote "$URL" HEAD
rm -f "$ASKPASS"
```

If access fails, report the failure and explain that a valid token is needed.
Never ask the user to paste a token into chat; ask them to expose it as
`GITHUB_TOKEN` in the environment.

## 4. Read repository data

Use local Git operations after cloning:

```bash
git status --short --branch
git log -5 --oneline
git remote -v
```

For profile or organization API requests, use `curl` with the GitHub REST API
and never echo the `Authorization` header:

```bash
curl -fsSL -H "Accept: application/vnd.github+json" \
  "https://api.github.com/users/owner/repos?per_page=100"
```

Use `$GITHUB_TOKEN` in the header only when authenticated access is required.

## 5. Make changes safely

- Work on a feature branch, not directly on the default branch.
- Commit, push, open pull requests, or change repository settings only when the
  user explicitly asks.
- Never force-push, rewrite shared history, or commit secrets.
- Follow the repository's existing conventions and run its checks.
- Report the remote, branch, local path, and every change made.
