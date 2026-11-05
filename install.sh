#!/bin/sh
# Install the pks command. Running it again updates PKS.
#
#   curl -fsSL https://raw.githubusercontent.com/sudrap/product-knowledge-system/main/install.sh | sh
#
# From a checkout, ./install.sh links that checkout instead of downloading.
set -eu

fail() {
  echo "$1" >&2
  exit 1
}

download() {
  command -v git >/dev/null 2>&1 || fail "PKS needs Git, and git was not found."
  if [ -d "$pks_home/.git" ]; then
    origin=$(git -C "$pks_home" remote get-url origin 2>/dev/null || true)
    [ "$origin" = "$repo_url" ] || fail "$pks_home is a different repository. Remove it or set PKS_HOME."
    echo "Updating PKS in $pks_home"
    git -C "$pks_home" pull --ff-only --quiet || fail "Could not update $pks_home. Remove it and run this again."
  elif [ -e "$pks_home" ]; then
    fail "$pks_home already exists and is not a PKS checkout. Remove it or set PKS_HOME."
  else
    echo "Downloading PKS to $pks_home"
    mkdir -p "$(dirname -- "$pks_home")"
    git clone --quiet --depth 1 "$repo_url" "$pks_home"
  fi
}

main() {
  repo_url=${PKS_REPO_URL:-"https://github.com/sudrap/product-knowledge-system.git"}
  pks_home=${PKS_HOME:-"$HOME/.local/share/pks"}
  bin_dir=${PKS_BIN_DIR:-"$HOME/.local/bin"}
  target="$bin_dir/pks"

  command -v python3 >/dev/null 2>&1 || fail "PKS needs Python 3.9 or newer, and python3 was not found."
  python3 -c 'import sys; sys.exit(sys.version_info < (3, 9))' ||
    fail "PKS needs Python 3.9 or newer; found $(python3 --version)."
  if [ -e "$target" ] && [ ! -L "$target" ]; then
    fail "$target already exists and is not a link. Remove it or set PKS_BIN_DIR."
  fi

  # A piped script has no file of its own, so it downloads PKS.
  if [ -f "$0" ] && [ -f "$(dirname -- "$0")/bin/pks" ]; then
    repo_root=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  else
    download
    repo_root=$pks_home
  fi

  mkdir -p "$bin_dir"
  chmod +x "$repo_root/bin/pks"
  ln -sfn "$repo_root/bin/pks" "$target"
  echo "Installed $("$target" --version): $target -> $repo_root/bin/pks"

  case ":$PATH:" in
    *":$bin_dir:"*) echo "Next: in your project's folder, run 'pks init'." ;;
    *) echo "Add $bin_dir to your PATH, then run 'pks init' in your project's folder." ;;
  esac
}

main "$@"
