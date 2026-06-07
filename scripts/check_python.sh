#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

find "${REPO_ROOT}/ros2_ws/src" -path '*/__pycache__' -prune -o -name '*.py' -print0 | \
  xargs -0 -r python3 -m py_compile

find "${REPO_ROOT}/scripts" -maxdepth 1 -name '*.py' -print0 | \
  xargs -0 -r python3 -m py_compile

echo "Python syntax checks passed."
