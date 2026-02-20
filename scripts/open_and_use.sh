#!/usr/bin/env bash
set -euo pipefail

if ! command -v docker >/dev/null 2>&1; then
  echo "docker is required" >&2
  exit 1
fi

if ! docker compose version >/dev/null 2>&1; then
  echo "docker compose is required" >&2
  exit 1
fi

echo "Starting services..."
docker compose up -d

echo "Waiting for backend health..."
for _ in {1..40}; do
  if curl -fsS http://localhost:8000/api/health >/dev/null 2>&1; then
    break
  fi
  sleep 2
done

curl -fsS http://localhost:8000/api/health

echo
cat <<MSG

Open in browser:
- Frontend dashboard: http://localhost:3000
- Backend docs: http://localhost:8000/docs

To stop:
  docker compose down
MSG
