#!/bin/bash

SCRIPT_DIR="./scripts"
RESULT_DIR="./results"

mkdir -p "$RESULT_DIR"

for FILE in *.js; do
  NAME=$(basename "$FILE" .js)
  echo "▶️ Running $FILE..."

  docker run --rm -v "${PWD}:/scripts" grafana/k6 run /scripts/$FILE --summary-export=/results/summary.json --out json=/results/detail.json
done