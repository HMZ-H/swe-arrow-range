#!/usr/bin/env bash
set -euo pipefail
cd /workspace/repo
git apply /workspace/solution.patch
