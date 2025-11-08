#!/usr/bin/env bash
set -euo pipefail

PORT="${PLANTUML_PORT:-}"
if [ -z "${PORT}" ]; then
  for p in 8081 8082 8083 9091 9092; do
    if ! nc -z localhost "$p" >/dev/null 2>&1; then
      PORT="$p"; break
    fi
  done
fi
: "${PORT:?No free port found. Set PLANTUML_PORT explicitly.}"
export PLANTUML_PORT="$PORT"
echo "Using PLANTUML_PORT=$PLANTUML_PORT"
docker compose -f docker-compose.plantuml.yml up -d
echo "PlantUML server on http://localhost:$PLANTUML_PORT"
