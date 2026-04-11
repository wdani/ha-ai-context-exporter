#!/bin/sh
set -eu

export PORT="${PORT:-8099}"
exec python3 /app/main.py
