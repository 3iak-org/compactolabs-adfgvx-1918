#!/usr/bin/env bash
# Regenerate every comp-adfgvx table from the committed corpus. One command:
#   search/adfgvx/run_all.sh
# Commit search/adfgvx first so the provenance headers name a clean commit.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY="nice -n 10 ~/dev/projects/ciphers/.venv/bin/python"
sha256sum -c search/adfgvx/inputs.sha256
$PY -I search/adfgvx/build_corpus.py >/dev/null
$PY -I search/adfgvx/census.py
$PY -I search/adfgvx/validate.py >/dev/null
$PY -I search/adfgvx/clusters.py
$PY -I search/adfgvx/duplicates.py >/dev/null
$PY -I search/adfgvx/rdecrypt.py >/dev/null
# strand J inputs on the SCAN transcription (primary), from 2026-11-01
$PY -I search/adfgvx/duplicates.py --scan >/dev/null
$PY -I search/adfgvx/clusters.py --scan
$PY -I search/adfgvx/scan.py
# power test: hours of CPU; set POWER=1 to include it (needs the scan clusters and duplicates)
if [ "${POWER:-0}" = 1 ]; then
  search/adfgvx/run_power.sh
fi
echo "done: ciphertexts/adfgvx-1918-log.{tsv,keys.tsv,plaintexts.tsv}, results/adfgvx-*"
