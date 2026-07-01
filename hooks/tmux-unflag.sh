#!/usr/bin/env bash
# UserPromptSubmit hook: fallback that strips a trailing yellow "!" marker from
# the tmux window name (in case pane-focus-in didn't fire) and clears the
# one-shot hook.
[ -z "$TMUX" ] && exit 0
pane="${TMUX_PANE:-}"
[ -z "$pane" ] && exit 0

MARK='#[fg=yellow,bold](!)#[default]'

name=$(tmux display-message -p -t "$pane" '#W')
case "$name" in
  *"$MARK")
    tmux rename-window -t "$pane" "${name%"$MARK"}"
    tmux set-hook -pu -t "$pane" pane-focus-in 2>/dev/null
    ;;
esac
exit 0
