#!/usr/bin/env bash
# The power test, both variants (scan = primary, creilly = secondary). One job at a time,
# nice 10, at most 6 workers (search/adfgvx/sharing.py enforces all three).
set -euo pipefail
cd "$(dirname "$0")/../.."
PY="nice -n 10 ~/dev/projects/ciphers/.venv/bin/python"
for V in scan creilly; do
  $PY -I search/adfgvx/power.py --variant $V --families F1
  $PY -I search/adfgvx/power.py --variant $V --extra --families F1 --kinds wrongperiod,shuffled --suffix=-extranull
  $PY -I search/adfgvx/power.py --variant $V --families F2 --kinds planted --suffix=-planted
  $PY -I search/adfgvx/power.py --variant $V --families F2 --kinds wrongperiod,shuffled --suffix=-null
  $PY -I search/adfgvx/power.py --variant $V --extra --families F2 --kinds wrongperiod,shuffled --suffix=-extranull
  ADFGVX_VARIANT=$V $PY -I search/adfgvx/power.py --f3
  $PY -I search/adfgvx/powerreport.py --variant $V >/dev/null
done
