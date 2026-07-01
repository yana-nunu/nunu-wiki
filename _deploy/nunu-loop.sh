#!/bin/bash
# NUNU run loop — runs Claude Code with the Discord bridge, restarting on exit/crash.
# Runs INSIDE the `nunu` tmux session (created by nunu-guardian.sh).
# Attach to watch:  tmux attach -t nunu     (detach: Ctrl-b then d)
#
# Deploy: copy to /Users/nunu/nunu/ops/nunu-loop.sh, chmod +x.
# Prereq: NUNU's Discord bot must be paired (via /discord:access in the nunu session) BEFORE
# this loop is useful — otherwise the bridge has no bot to attach to.

export PATH="/Users/nunu/.local/bin:/Users/nunu/.bun/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin"
cd /Users/nunu/nunu || exit 1

while true; do
  echo "[nunu-loop] $(date '+%Y-%m-%d %H:%M:%S') starting claude"
  claude --channels plugin:discord@claude-plugins-official
  code=$?
  echo "[nunu-loop] $(date '+%Y-%m-%d %H:%M:%S') claude exited (code $code); restarting in 3s"
  sleep 3
done
