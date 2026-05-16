#!/bin/bash
IFS=$'\t' read -r MODEL DIR CTS PCT < <(jq -r '[.model.display_name, .workspace.current_dir, (.context_window.context_window_size // 0), (.context_window.used_percentage // 0 | floor)] | @tsv')

echo "[$MODEL] 📁 ${DIR##*/} | ${PCT}% of ${CTS} context"
