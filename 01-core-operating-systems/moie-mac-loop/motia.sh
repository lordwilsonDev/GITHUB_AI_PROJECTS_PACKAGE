#!/usr/bin/env bash
# Always run motia through the governor
cd "$(dirname "$0")"

export MOTIA_TASK_KIND="${MOTIA_TASK_KIND:-default}"

node motia_governed.cjs "$@"
