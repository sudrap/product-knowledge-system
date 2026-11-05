#!/bin/sh
# Link the pks command into a folder on PATH. Safe to run again.
set -eu

repo_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
bin_dir=${PKS_BIN_DIR:-"$HOME/.local/bin"}
target="$bin_dir/pks"

if ! command -v python3 >/dev/null 2>&1; then
  echo "pks needs Python 3.9 or newer, and python3 was not found." >&2
  exit 1
fi
if ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))'; then
  echo "pks needs Python 3.9 or newer; found $(python3 --version)." >&2
  exit 1
fi

if [ -e "$target" ] && [ ! -L "$target" ]; then
  echo "$target already exists and is not a link. Remove it or set PKS_BIN_DIR." >&2
  exit 1
fi

mkdir -p "$bin_dir"
chmod +x "$repo_root/bin/pks"
ln -sfn "$repo_root/bin/pks" "$target"
echo "Linked $target -> $repo_root/bin/pks"

case ":$PATH:" in
  *":$bin_dir:"*) echo "Ready: run 'pks --version'." ;;
  *) echo "Add $bin_dir to your PATH to use 'pks'." ;;
esac
