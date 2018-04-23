#!/bin/sh

if [ -z "$1" ]; then
    echo "usage: $0 CMD_PATH CMD_ARGS..." >&2
    exit 1
fi

storeDir="$(nix eval --raw '(builtins.storeDir)')"

exec docker run -it --mount type=bind,src="$storeDir",dst="$storeDir",readonly empty $@
