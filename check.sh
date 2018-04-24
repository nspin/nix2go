if [ -z "$1" ]; then
    echo "usage: $0 STORE_PATH" >&2
    exit 1
fi

toScan="$1"

while read path; do
    if grep -qr $path $toScan; then
        echo "error: found reference to $path in store path $toScan"
        exit 1
    fi
    for link in $(find $toScan -type l); do
        if readlink $link | grep -q $path; then
            echo "error: found link referring to $path: $link -> $(readlink $link)"
            exit 1
        fi
    done
done
