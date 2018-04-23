#!/bin/sh

if [ -z "$1" -o -z "$2" -o -z "$3" ]; then
    echo "usage: $0 MOUNT_POINT BUNDLE_STORE_PATH CMD_PATH CMD_ARGS" >&2
    exit 1
fi

mount_point="$1"
shift
bundle_store_path="$1"
shift

exec docker run -it --mount type=bind,src="$bundle_store_path/$mount_point",dst="$mount_point",readonly empty $@
