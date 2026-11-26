#!/bin/sh
# Runs the catalog site locally: http://localhost:${PORT:-8787}
# Files from ~/weidian (or $WEIDIAN_DIR) are served under /data/ and can be opened with
#   http://localhost:8787/?data=data/weidian_<id>.csv
set -e
dir="$(cd "$(dirname "$(readlink -f "$0")")" && pwd)"
data="${WEIDIAN_DIR:-$HOME/weidian}"
port="${PORT:-8787}"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT INT TERM
ln -s "$dir/index.html" "$tmp/index.html"
ln -s "$data" "$tmp/data"
echo "Сайт: http://localhost:$port   (данные из $data → /data/)"
all=$(ls "$data" 2>/dev/null | grep -E '\.csv$' | sed 's|^|data/|' | paste -sd, -)
[ -n "$all" ] && echo "Все выгрузки сразу: http://localhost:$port/?data=$all"
cd "$tmp" && python3 -m http.server "$port" --bind 127.0.0.1
