{ runCommand, lib, closureInfo, python3, perl }:

{ inputs, prefix, suffix ? "", excludes ? [] }:

let

  excludeArgs = lib.concatMapStrings (e: " -e '${e}'") excludes;

in

runCommand "nix2go-bundle" {
  buildInputs = [ perl ];
} ''
  ${python3}/bin/python3 ${./nix2go.py} $out '${prefix}' '${suffix}' ${excludeArgs} < ${closureInfo { rootPaths = inputs; }}/store-paths
''
