#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SUBMISSION_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${SUBMISSION_ROOT}"

table2text run examples/weather_sample.csv \
  --request "Describe the dataset and report its strongest supported findings." \
  --no-llm \
  --output-dir demo_runs
