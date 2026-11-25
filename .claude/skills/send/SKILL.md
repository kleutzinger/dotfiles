---
name: send
description: >-
  Commit the current changes, push to GitHub, then deploy by pushing to the
  `dokku` git remote. Use when the user says "send it", "send this", "commit
  and push", "commit and push and deploy", "deploy this", or "push to dokku". Repos without a
  `dokku` remote just get commit + push to GitHub. The dokku push is fully
  detached, with its build output written to a log file (not read by Claude)
  and a `tail -f` command handed to the user.
---

# Send: commit, push to GitHub, deploy to Dokku

One flow: commit local changes, push to `origin` (GitHub), then, only if the
repo has a `dokku` remote, trigger a Dokku deploy without watching it happen.

## Steps

1. **Detect Dokku.** `git remote -v | grep dokku` first. Note whether a
   remote literally named `dokku` exists. If not, this is a plain GitHub
   repo: do steps 2–4 only, skip step 5, and just say it was committed and
   pushed.

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

5. **Deploy to Dokku (only if a `dokku` remote exists) — detached, output to a log.**
   - Derive host and app from the remote URL
     (`git remote get-url dokku` -> `dokku@<host>:<app>`), then:
     ```
     mkdir -p ~/.cache/send && nohup git push dokku > ~/.cache/send/<app>.log 2>&1 < /dev/null &
     ```
     Do **not** use `run_in_background: true` (it re-invokes you on exit and
     costs an extra turn). Don't `Monitor` or poll, and never read the log
     yourself unless asked.
   - Finish by printing these for the user to copy:
     - Build output (stdout of the push):
       `tail -f ~/.cache/send/<app>.log`
     - Over ssh, once the build is done, live app logs:
       `ssh dokku@<host> logs <app> -t`
   - If the user later asks whether the deploy succeeded, check the end of
     the log (`tail -n 30`) or `ssh dokku@<host> ps:report <app>`.

## Notes

- Still don't force-push, and still pause if the local branch has diverged
  from `origin` in a way needing a merge/rebase — this skill covers the
  happy path, not conflict resolution.
- If GitHub and Dokku should genuinely get different refs pushed (unusual),
  handle each explicitly instead of assuming one push does both.
