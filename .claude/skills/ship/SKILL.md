---
name: ship
description: >-
  Commit the current changes, push to GitHub, then deploy by pushing to the
  `dokku` git remote. Use when the user says "ship this", "ship it", "commit
  and push and deploy", "deploy this", or "push to dokku". The dokku push is
  fully detached and its build/deploy output is discarded, to avoid burning
  tokens on verbose deploy logs or a completion-notification turn.
---

# Ship: commit, push to GitHub, deploy to Dokku

One flow: commit local changes, push to `origin` (GitHub), then trigger a
Dokku deploy without watching it happen.

## Steps

1. **Require a `dokku` remote.** `git remote -v | grep dokku` first, before
   touching anything else. If there's no remote literally named `dokku`,
   this skill doesn't apply to this repo — stop here, say so, and suggest a
   plain commit+push instead. Don't fall back to doing just the GitHub half.

2. **Check status — cheaply.** `git status --short` and `git diff --stat`
   (plus `--cached --stat` if anything is staged). Don't dump the full diff:
   if you made these changes earlier in this session you already know what
   they are; otherwise read only the specific files' diffs you need to write
   the message, and never lockfiles or generated files. If there's nothing
   staged or unstaged and no local commits ahead of `origin`, there's nothing
   to commit or push — skip to step 5 only if the user explicitly wants to
   (re)trigger a deploy of what's already pushed.

3. **Commit.**
   - Stage the files relevant to the change. Avoid `git add -A`/`git add .`
     if `git status` shows unrelated untracked files — ask first if unsure.
   - Write a concise commit message focused on *why*, matching the repo's
     existing style (`git log --oneline -10` for tone).
   - Commit via heredoc, per normal commit conventions (attribution line
     included per the active system reminder, if any).

4. **Push to GitHub.** `git push` if the branch already tracks `origin`,
   otherwise `git push -u origin <branch>`.

5. **Deploy to Dokku — fire and forget, fully detached.**
   - Run it as a normal foreground Bash call, detached from the harness:
     ```
     setsid git push dokku >/dev/null 2>&1 < /dev/null &
     ```
     No refspec needed. Do **not** use `run_in_background: true` — the
     harness tracks those and re-invokes you when the command exits, which
     costs a whole extra turn. Don't `Monitor` or poll either. Just tell the
     user the deploy was kicked off.
   - The output is discarded on purpose: Dokku's build/deploy log is long and
     reading it burns tokens for no benefit in the common case.
   - Only check on it if the user later asks whether the deploy succeeded —
     e.g. `ssh dokku@<host> ps:report <app>` or `logs <app> --num 50` (look
     up the host from the `dokku` remote URL). Never do this proactively.

## Notes

- Still don't force-push, and still pause if the local branch has diverged
  from `origin` in a way needing a merge/rebase — this skill covers the
  happy path, not conflict resolution.
- If GitHub and Dokku should genuinely get different refs pushed (unusual),
  handle each explicitly instead of assuming one push does both.
