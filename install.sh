#!/bin/sh
# Installs the `weidian` command (and the `weidan` alias) into ~/.local/bin
set -e
dir="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$HOME/.local/bin"
chmod +x "$dir/weidian.py" "$dir/serve.sh"
ln -sf "$dir/weidian.py" "$HOME/.local/bin/weidian"
ln -sf "$dir/weidian.py" "$HOME/.local/bin/weidan"
ln -sf "$dir/serve.sh" "$HOME/.local/bin/weidian-site"
echo "Готово: weidian <id>, weidan <id>, weidian-site"
case ":$PATH:" in *":$HOME/.local/bin:"*) ;; *) echo "Добавьте ~/.local/bin в PATH";; esac
