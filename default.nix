{ runCommand, lib, closureInfo, python3, perl }:

{ rootPaths, script, excludes ? [] }:

let
  excludeArgs = lib.concatMapStrings (e: " -e '${e}'") excludes;
  storePaths = "${closureInfo { inherit rootPaths; }}/store-paths";
in runCommand "nix2go-bundle" {
  buildInputs = [ perl ];
} ''
  ${python3}/bin/python3 ${./nix2go.py} ${script} $out ${excludeArgs} < ${storePaths}

  for path in $(cat ${storePaths}); do
    if grep -qr $path $out; then
      echo "error: found reference to $path in $out"
      exit 1
    fi
  done
''
