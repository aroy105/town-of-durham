#!/usr/bin/env bash
set -e

pids=()
trap 'kill "${pids[@]}" 2>/dev/null' EXIT

(cd backend && .venv/bin/uvicorn app.main:app --reload --port 8000) &
pids+=($!)

(cd frontend && ./node_modules/.bin/vite) &
pids+=($!)

wait
