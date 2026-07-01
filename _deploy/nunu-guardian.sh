#!/bin/bash
# NUNU guardian — keeps the `nunu` tmux session (running nunu-loop.sh) alive.
# Mirrors momo-guardian.sh but INSTANCE-SCOPED: the duplicate-bridge check is limited to
# THIS user's processes (pgrep -u), so NUNU's guardian does NOT stand by just because MOMO's
# bridge is running under the momo user. Each instance only guards its own bridge.
#
# Deploy: copy to /Users/nunu/nunu/ops/nunu-guardian.sh, chmod +x, referenced by com.nunu.agent.plist.

export PATH="/opt/homebrew/bin:/Users/nunu/.local/bin:/Users/nunu/.bun/bin:/usr/bin:/bin:/usr/sbin:/sbin"

SESSION=nunu
LOOP=/Users/nunu/nunu/ops/nunu-loop.sh
ME="$(id -un)"

while true; do
  if tmux has-session -t "$SESSION" 2>/dev/null; then
    # Managed session is up — nothing to do; block until it dies.
    sleep 30
  elif pgrep -u "$ME" -f 'claude --channels' >/dev/null 2>&1; then
    # Another bridge for THIS user (e.g. an ad-hoc terminal session) is already serving — don't duplicate.
    echo "[nunu-guardian] $(date '+%F %T') existing bridge for $ME detected; standing by"
    sleep 30
  else
    echo "[nunu-guardian] $(date '+%F %T') starting managed session $SESSION"
    tmux new-session -d -s "$SESSION" "$LOOP"
    sleep 5
  fi
done
