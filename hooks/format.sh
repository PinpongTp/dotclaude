#!/bin/bash
# Auto-format + lint after Edit/Write/MultiEdit (node.js files only)
INPUT=$(cat)
FILE=$(echo "$INPUT" | jq -r '.tool_input.file_path // empty')
[[ -z "$FILE" ]] && exit 0
[[ ! -f "$FILE" ]] && exit 0

case "$FILE" in
  *.js|*.jsx|*.ts|*.tsx|*.mjs|*.cjs|*.json|*.css|*.scss|*.html|*.md|*.yml|*.yaml)
    cd "$(dirname "$FILE")" 2>/dev/null
    npx --no-install prettier --write "$FILE" 2>/dev/null
    npx --no-install eslint --fix "$FILE" 2>/dev/null
    ;;
esac

exit 0
