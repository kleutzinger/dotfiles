---
name: ship
description: >-
  Commit the current changes, push to GitHub, then deploy by pushing to the
  `dokku` git remote. Use when the user says "ship this", "ship it", "commit
  and push and deploy", "deploy this", or "push to dokku". The dokku push is
  fired in the background and its build/deploy output is deliberately not
  streamed or read, to avoid burning tokens on verbose deploy logs.
---

# Ship: commit, push to GitHub, deploy to Dokku

One flow: commit local changes, push to `origin` (GitHub), then trigger a
Dokku deploy without watching it happen.

## Steps

1. **Require a `dokku` remote.** `git remote -v | grep dokku` first, before
   touching anything else. If there's no remote literally named `dokku`,
   this skill doesn't apply to this repo — stop here, say so, and suggest a
   plain commit+push instead. Don't fall back to doing just the GitHub half.

2. **Check status.** `git status` / `git diff`. If there's nothing staged or
   unstaged and no local commits ahead of `origin`, there's nothing to commit
   or push — skip to step 5 only if the user explicitly wants to (re)trigger a
   deploy of what's already pushed.

3. **Commit.**
   - Stage the files relevant to the change. Avoid `git add -A`/`git add .`
     if `git status` shows unrelated untracked files — ask first if unsure.
   - Write a concise commit message focused on *why*, matching the repo's
     existing style (`git log` for tone).
   - Commit via heredoc, per normal commit conventions (attribution line
     included per the active system reminder, if any).

4. **Push to GitHub.** `git push` if the branch already tracks `origin`,
   otherwise `git push -u origin <branch>`.

5. **Deploy to Dokku — fire and forget.**
   - Push to it. Dokku deploys from `master` on its remote by default, so if
     the local branch isn't literally `master` push with a refspec:
     `git push dokku <local-branch>:master` (adjust if this app's Dokku is
     configured for a different deploy branch).
   - **Do not stream, tail, or wait on the output.** Launch it with
     `run_in_background: true` and move on immediately — don't `Monitor` it,
     don't poll it, don't read the log to summarize the build. Just tell the
     user the deploy was kicked off. This is intentional: Dokku's
     build/deploy output is long and reading it back burns tokens for no
     benefit in the common case.
   - Only check on it if the user later asks whether the deploy succeeded —
     e.g. `dokku ps:report <app>` over SSH, or checking the backgrounded
     command's output at that point. Never do this proactively.

## Notes

- Still don't force-push, and still pause if the local branch has diverged
  from `origin` in a way needing a merge/rebase — this skill covers the
  happy path, not conflict resolution.
- If GitHub and Dokku should genuinely get different refs pushed (unusual),
  handle each explicitly instead of assuming one push does both.
