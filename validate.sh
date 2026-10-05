#!/usr/bin/env bash
# Run one scenario in a fresh container and print its reward.
# usage: ./validate.sh <label> [setup-script-inside-container]
set -uo pipefail
label="$1"; setup="${2:-}"

docker run --rm \
  -v "$PWD/grade.py:/workspace/grade.py:ro" \
  -v "$PWD/f2p.txt:/workspace/f2p.txt:ro" \
  -v "$PWD/baseline.json:/workspace/baseline.json:ro" \
  -v "$PWD/hidden_test_arrow.py:/workspace/hidden_test_arrow.py:ro" \
  -v "$PWD/solution.patch:/workspace/solution.patch:ro" \
  -v "$PWD/cheats:/workspace/cheats:ro" \
  swe-arrow-range \
  bash -c "${setup:-true} >/dev/null 2>&1; python /workspace/grade.py" \
  | python3 -c "import sys,json; print('$label'.ljust(28), json.load(sys.stdin)['reward'])"
