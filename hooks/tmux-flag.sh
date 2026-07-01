#!/usr/bin/env bash
# Stop / Notification hook: append a yellow "!" to the tmux window name when
# Claude finishes (done) or needs input (need help) while you're on a different
# window. A one-shot pane-focus-in hook restores the original name as soon as
# you switch back to this window.
[ -z "$TMUX" ] && exit 0
pane="${TMUX_PANE:-}"
[ -z "$pane" ] && exit 0

# Yellow "!" marker, attached directly to the name (no space).
MARK='#[fg=yellow]!#[default]'

# Already looking at this window? Nothing to flag.
[ "$(tmux display-message -p -t "$pane" '#{window_active}')" = "1" ] && exit 0

name=$(tmux display-message -p -t "$pane" '#W')
case "$name" in
  *"$MARK") exit 0 ;;   # already flagged
esac

tmux rename-window -t "$pane" "$name$MARK"
tmux set-hook -p -t "$pane" pane-focus-in \
  "rename-window -t '$pane' '$name' ; set-hook -pu -t '$pane' pane-focus-in"
exit 0
